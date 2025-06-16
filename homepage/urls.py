from django.urls import path
from homepage.views import HomePageView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    # Add more URL patterns here as needed
]