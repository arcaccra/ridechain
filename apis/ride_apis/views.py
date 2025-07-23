from functools import partial

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from rest_framework.exceptions import PermissionDenied
from .serializers import RideListSerializer, RideDetailSerializer, RideUpdateSerializer
from rides.models import Ride
from apis.permissions import IsUserOrReadOnly, IsDriverOrReadOnly
from ..views import EmptySerializer


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


class RideBookingAPIView(generics.GenericAPIView):
    serializer_class = RideListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        ride_id = kwargs.get('ride_id')
        try:
            ride = Ride.objects.get(uuid=ride_id)
        except Ride.DoesNotExist:
            return Response({'detail': 'Ride not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.is_authenticated and not request.user.is_driver:
            ride.passengers.add(request.user)
            ride.seats_available -= 1
            ride.save()
            return Response({'success': 'Ride booked successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'You must be a registered user to book a ride.'}, status=status.HTTP_403_FORBIDDEN)




# Root View for Ride APIs
class RideRootView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmptySerializer

    def get(self, request, *args, **kwargs):
        return Response({
            'rides': reverse_lazy('ride-list', request=request),
        })