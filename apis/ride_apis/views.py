from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from rest_framework.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from io import BytesIO
from django.db.models import Q
from .serializers import RideListSerializer, RideDetailSerializer, RideUpdateSerializer, LocationSerializer, RideCreateSerializer
from rides.models import Ride, Location
from apis.permissions import IsUserOrReadOnly, IsDriverOrReadOnly
from ..views import EmptySerializer
from book_rate.models import RideBooking
from utilities.qr_code_module import QRCodeGenerator
from apis.book_rate_apis.serializers import RideBookingSerializer, RideBookingDetailSerializer


class LocationListView(generics.ListCreateAPIView):
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        q = self.request.query_params.get('q')
        if q:
            return Location.objects.filter(name__icontains=q)
        return Location.objects.all()

    def perform_create(self, serializer):
        serializer.save()

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response({'success': 'Location Created Successfully', **response.data}, status=status.HTTP_201_CREATED)

class RideListView(generics.ListCreateAPIView):
    """
    Ride list and creation view.
    For POST requests, provide:
      - pick_up_id: Primary key of the pick_up Location
      - drop_off_id: Primary key of the drop_off Location
      - seats_available, price_per_seat, etc.
      - departure_time
      - Optional: arrival_time
      - etc.
    """
    serializer_class = RideListSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RideCreateSerializer
        return RideListSerializer


    def get_permissions(self):
        if self.request.method in ['POST']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_driver and user.is_staff:
                return Ride.objects.all()
            elif user.is_driver:
                return Ride.objects.filter(driver=user.driver)
            elif user.is_superuser:
                return Ride.objects.all()
            else:
                return Ride.objects.all()
        return Ride.objects.none()

    def perform_create(self, serializer):
        serializer.save(driver=self.request.user.driver)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        if not request.user.is_driver:
            return Response(
                {'detail': 'You must be a driver to create a ride.'},
                status=status.HTTP_403_FORBIDDEN
            )
        response = super().post(request, *args, **kwargs)
        return Response({'success': 'Ride Created Successfully', **response.data}, status=status.HTTP_201_CREATED)

class RideSearchView(generics.ListAPIView):
    """
    Mobile-friendly ride search by location names.
    Query params:
      - q: matches either pick_up or drop_off location name (case-insensitive)
      - pick_up: matches pick_up location name (case-insensitive)
      - drop_off: matches drop_off location name (case-insensitive)
    If none of the above params are provided, returns an empty queryset.
    """
    serializer_class = RideListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Expecting Ride to have ForeignKeys: pick_up and drop_off to Location
        pickup_param = self.request.query_params.get('pick_up')
        dropoff_param = self.request.query_params.get('drop_off')
        q_param = self.request.query_params.get('q')

        qs = Ride.objects.all()
        filters = Q()

        if q_param:
            filters |= Q(pick_up__name__icontains=q_param)
            filters |= Q(drop_off__name__icontains=q_param)

        if pickup_param:
            filters &= Q(pick_up__name__icontains=pickup_param)

        if dropoff_param:
            filters &= Q(drop_off__name__icontains=dropoff_param)

        if not (q_param or pickup_param or dropoff_param):
            return Ride.objects.none()

        return qs.filter(filters).distinct()

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_200_OK)

class RideDetailView(generics.RetrieveAPIView):
    serializer_class = RideDetailSerializer
    queryset = Ride.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsUserOrReadOnly | permissions.IsAdminUser]

class RideUpdateView(generics.GenericAPIView):
    serializer_class = RideUpdateSerializer
    queryset = Ride.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        ride = self.get_object()
        serializer = self.get_serializer(ride)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        ride = self.get_object()
        serializer = self.get_serializer(ride, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        ride = self.get_object()
        serializer = self.get_serializer(ride, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        ride = self.get_object()
        ride.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RideBookingValidationMixin:

    def validate_ride_booking(self, request, ride_uuid):
        user = request.user

        # 1. Check if ride exists
        try:
            ride = Ride.objects.get(uuid=ride_uuid)
        except Ride.DoesNotExist:
            raise serializers.ValidationError("Ride does not exist.")

        # 2. Prevent the driver from booking their own ride
        if hasattr(user, 'driver') and ride.driver == user.driver:
            raise serializers.ValidationError("You cannot book your own ride.")

        # 3. Prevent duplicate booking
        if RideBooking.objects.filter(passenger=user, ride=ride).exists():
            raise serializers.ValidationError("You have already booked this ride.")

        # 4. Check if ride is full
        if ride.passengers.count() >= ride.seats_available:
            raise serializers.ValidationError("This ride is already full.")

        # 5. Ride must not have already departed
        if ride.departure_time <= timezone.now():
            raise serializers.ValidationError("This ride has already departed.")

        # 6. Ride must not be cancelled or completed
        if hasattr(ride, 'status') and ride.status.lower() in ['cancelled', 'completed']:
            raise serializers.ValidationError("This ride is not available for booking.")

        return ride, user

    def generate_booking_qr(self, request, user_id: int, ride_uuid: str, booking_qrcode_uuid: str) -> BytesIO:
        """
        Generate a base64-encoded QR code pointing to a booking verification URL.
        """
        # Reverse the verification route name (must exist in urls.py)
        relative_url = reverse(
            'booking-verification', 
            kwargs={
                'user_id': user_id, 
                'ride_uuid': ride_uuid, 
                'booking_qrcode_uuid': booking_qrcode_uuid
            }
        )
        full_url = request.build_absolute_uri(relative_url)

        qr_generator = QRCodeGenerator()
        return qr_generator.generate(full_url)

class BookRideAPIView(RideBookingValidationMixin, generics.CreateAPIView):
    serializer_class = RideBookingDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = RideBooking.objects.all()

    def create(self, request, *args, **kwargs):
        ride_uuid = self.kwargs.get('pk')
        ride, passenger = self.validate_ride_booking(request, ride_uuid)

        booking = RideBooking.objects.create(passenger=passenger, ride=ride)
        ride.passengers.add(passenger)  # Add user to ride's passengers list
        ride.status = 'Requested' # Update ride status to 'Requested'

        # Generate QR code and assign it
        qr_code_buffer = self.generate_booking_qr(
            request=request,
            user_id=passenger.id,
            ride_uuid=str(ride.uuid),
            booking_qrcode_uuid=str(booking.qrcode_uuid)
        )
        
        # Create the filename
        filename = f"booking_{booking.qrcode_uuid}_ride_{ride.uuid}_user_{passenger.id}.png"

        # Save the QR code image to the booking instance
        booking.qr_code.save(filename, ContentFile(qr_code_buffer.read()), save=True)

        serializer = self.get_serializer(booking)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class BookRideVerificationAPIView(generics.GenericAPIView):
    """
    API endpoint to verify a ride booking using QR code.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmptySerializer

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        ride_uuid = self.kwargs.get('ride_uuid')
        booking_qrcode_uuid = self.kwargs.get('booking_qrcode_uuid')

        try:
            booking = RideBooking.objects.get(qrcode_uuid=booking_qrcode_uuid, passenger__id=user_id, ride__uuid=ride_uuid)
        except RideBooking.DoesNotExist:
            return Response({'detail': 'Invalid booking details.'}, status=status.HTTP_404_NOT_FOUND)

        # If the booking exists and is valid
        return Response({'detail': 'Booking verified successfully.'}, status=status.HTTP_200_OK)


# Root View for Ride APIs
class RideRootView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmptySerializer

    def get(self, request, *args, **kwargs):
        return Response({
            'rides': reverse_lazy('ride-list', request=request),
            'locations': reverse_lazy('location-list', request=request),
        })