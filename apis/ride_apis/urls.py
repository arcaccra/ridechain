from django.urls import path
from .views import RideListView, RideDetailView, RideRootView, RideUpdateView, BookRideAPIView

urlpatterns = [
    # Ride APIs
    path('', RideRootView.as_view(), name='ride-root'),
    path('rides/', RideListView.as_view(), name='ride-list'),
    path('rides/<uuid:pk>/', RideDetailView.as_view(), name='ride-detail'),
    path('rides/<uuid:pk>/update/', RideUpdateView.as_view(), name='ride-update'),

    path ('rides/<uuid:pk>/book/', BookRideAPIView.as_view(), name='book-ride'),

    # Add more ride-related URLs as needed
]