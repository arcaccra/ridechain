from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from book_rate.models import RideBooking
from .serializers import RideBookingSerializer, RideBookingDetailSerializer
from ..views import EmptySerializer
from rest_framework.reverse import reverse_lazy


class BookingListCreateView(generics.ListAPIView):
    serializer_class = RideBookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            return RideBooking.objects.all()
        elif user.is_authenticated:
            return RideBooking.objects.filter(passenger=user)
        return RideBooking.objects.none()



class BookingDetailView(generics.RetrieveAPIView):
    serializer_class = RideBookingDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return RideBooking.objects.all()
        elif hasattr(user, 'is_driver') and user.is_driver:
            return RideBooking.objects.filter(ride__driver=user.driver)
        elif user.is_authenticated:
            return RideBooking.objects.filter(passenger=user)
        return RideBooking.objects.none()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if not user.is_superuser:
            if hasattr(user, 'is_driver') and user.is_driver:
                if instance.ride.driver != user.driver:
                    raise PermissionDenied("You do not have permission to view this booking.")
            elif instance.passenger != user:
                raise PermissionDenied("You do not have permission to view this booking.")
        serializer = self.get_serializer(instance)
        return Response(serializer.data)




class BookingRootView(generics.GenericAPIView):
    serializer_class = EmptySerializer
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def get(request, *args, **kwargs):
        data = {
            'booking_list_create': reverse_lazy('booking-list-create', request=request, format=None),
        }
        return Response(data)
