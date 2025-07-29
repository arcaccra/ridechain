from django.urls import path
from .views import RideListView, RideDetailView, RideRootView, RideUpdateView, BookRideAPIView, BookRideVerificationAPIView

urlpatterns = [
    # Ride APIs
    path('', RideRootView.as_view(), name='ride-root'),
    path('rides/', RideListView.as_view(), name='ride-list'),
    path('rides/<uuid:pk>/', RideDetailView.as_view(), name='ride-detail'),
    path('rides/<uuid:pk>/update/', RideUpdateView.as_view(), name='ride-update'),

    path ('rides/<uuid:pk>/book/', BookRideAPIView.as_view(), name='book-ride'),

    path('apis/<uuid:r>/bookings/', BookRideAPIView.as_view(), name='ride-booking-list'),

    path('verify-booking/<int:user_id>/<uuid:ride_uuid>/<uuid:booking_qrcode_uuid>/', BookRideVerificationAPIView.as_view(), name='booking-verification'),

    # Add more ride-related URLs as needed
]