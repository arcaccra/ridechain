from django.urls import path
from .views import CommunityView, BlogView


urlpatterns = [
    path('', CommunityView.as_view(), name='community'),
    path('blog/', BlogView.as_view(), name='blog'),
]