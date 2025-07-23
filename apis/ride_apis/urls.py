from django.urls import path
from .views import RideListView, RideDetailView, RideRootView, RideUpdateView, RideBookingAPIView

urlpatterns = [
    # Ride APIs
    path('', RideRootView.as_view(), name='ride-list-root'),
    path('rides/', RideListView.as_view(), name='ride-list'),
    path('rides/<uuid:pk>/', RideDetailView.as_view(), name='ride-detail'),
    path('rides/<uuid:pk>/update/', RideUpdateView.as_view(), name='ride-update'),
]