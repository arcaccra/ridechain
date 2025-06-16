from django.urls import path
from .views import (
    UserListView,
    UserDetailView,
    RegisterView,
    LoginView,
    LogoutView,
    UserUpdateView,
    DriverListView,
    DriverDetailView,
    DriverUpdateView,
)

urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/update', UserUpdateView.as_view(), name='user-update'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('drivers/', DriverListView.as_view(), name='driver-list'),
    path('drivers/<int:pk>/', DriverDetailView.as_view(), name='driver-detail'),
    path('drivers/<int:pk>/update', DriverUpdateView.as_view(), name='driver-update'),
]