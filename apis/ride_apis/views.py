from django.urls import reverse
from django.utils import timezone
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from rest_framework.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from io import BytesIO
from .serializers import RideListSerializer, RideDetailSerializer, RideUpdateSerializer
from rides.models import Ride
from apis.permissions import IsUserOrReadOnly, IsDriverOrReadOnly
from ..views import EmptySerializer
from book_rate.models import RideBooking
from utilities.qr_code_module import QRCodeGenerator
from apis.book_rate_apis.serializers import RideBookingSerializer, RideBookingDetailSerializer


class RideListView(generics.ListCreateAPIView):
    serializer_class = RideListSerializer

    def get_permissions(self):
        if self.request.method in ['POST']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_driver:
                return Ride.objects.filter(driver=user.driver)
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


class RideDetailView(generics.RetrieveAPIView):
    serializer_class = RideDetailSerializer
    queryset = Ride.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsUserOrReadOnly | permissions.IsAdminUser]


class RideUpdateView(generics.GenericAPIView):
    serializer_class = RideUpdateSerializer
    queryset = Ride.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsDriverOrReadOnly | permissions.IsAdminUser]

    @staticmethod
    def check_driver_permission(instance, user):
        # Ensure the user is the driver of the ride
        if instance.driver != user.driver:
            raise PermissionDenied("You can only update your own rides.")

    def get (self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_driver_permission(instance, request.user)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


    def put(self, request, *args, **kwargs):
        self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs, partial=True)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        self.check_driver_permission(instance, request.user)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'success': 'Ride Updated Successfully', **serializer.data}, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        instance = serializer.instance
        serializer = self.get_serializer(instance)
        return Response (serializer.data, status=status.HTTP_200_OK)


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
        })