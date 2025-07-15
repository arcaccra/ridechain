from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from .serializers import RideListSerializer, RideDetailSerializer
from rides.models import Ride
from apis.permissions import IsUserOrReadOnly


class RideListView(generics.ListCreateAPIView):
    serializer_class = RideListSerializer
    permission_classes = [permissions.IsAuthenticated]

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


class RideDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RideDetailSerializer
    queryset = Ride.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsUserOrReadOnly | permissions.IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(driver=self.request.user.driver)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        response = super().put(request, *args, **kwargs)
        return Response(response.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return Response({}, status=status.HTTP_204_NO_CONTENT)


# Root View for Ride APIs
class RideRootView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({
            'rides': reverse_lazy('ride-list', request=request),
        })