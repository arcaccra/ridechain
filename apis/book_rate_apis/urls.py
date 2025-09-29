from django.urls import path
from .views import BookingRootView, BookingListCreateView, BookingDetailView, RatingAPIView

urlpatterns = [
    path('', BookingRootView.as_view(), name='booking-root'),
    path('bookings/', BookingListCreateView.as_view(), name='booking-list'),
    path('bookings/<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('ratings/', RatingAPIView.as_view(), name='rating-list'),

]