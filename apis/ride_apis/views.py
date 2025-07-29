from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from rest_framework.exceptions import PermissionDenied
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


class BookRideAPIView(generics.CreateAPIView):
    serializer_class = RideBookingDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = RideBooking.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Pass ride_id from URL to the serializer
        ride_uuid = self.kwargs.get('pk')
        try:
            ride = Ride.objects.get(uuid=ride_uuid)
        except Ride.DoesNotExist:
            raise serializers.ValidationError("Ride does not exist.")

        # The serializer's create method now handles the booking logic
        booking = serializer.save(ride=ride)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# Root View for Ride APIs
class RideRootView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmptySerializer

    def get(self, request, *args, **kwargs):
        return Response({
            'rides': reverse_lazy('ride-list', request=request),
        })