from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from book_rate.models import RideBooking, Rating
from .serializers import RideBookingSerializer, RideBookingDetailSerializer, RatingSerializer
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


class RatingAPIView(generics.GenericAPIView):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    queryset = Rating.objects.all()
    pagination_class = None  # You can set a pagination class if needed
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        passenger = request.user
        ride = serializer.validated_data['ride']

        # Prevent duplicate ratings
        if Rating.objects.filter(passenger=passenger, ride=ride).exists():
            return Response({"detail": "You have already rated this ride."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the rating instance
        rating = Rating.objects.create(
            passenger=passenger,
            ride=ride,
            score=serializer.validated_data['score'],
            impression_option=serializer.validated_data.get('impression_option', ''),
            comment=serializer.validated_data.get('comment', '')
        )

        return Response(self.get_serializer(rating).data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            queryset = Rating.objects.all()
        else:
            queryset = Rating.objects.filter(passenger=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)






class BookingRootView(generics.GenericAPIView):
    serializer_class = EmptySerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    @staticmethod
    def get(request, *args, **kwargs):
        data = {
            'booking_list_create': reverse_lazy('booking-list', request=request, format=None),
            'rating_list': reverse_lazy('rating-list', request=request, format=None),
        }
        return Response(data)
