from django.urls import path
from requests import delete

from .views import (
    UserListView,
    UserDetailView,
    RegisterView,
    LoginView,
    LogoutView,
    UserUpdateView,
    UserDeleteView,
    DriverListView,
    DriverDetailView,
    DriverUpdateView, AccountRootView,
    WalletAPIVew,
)

urlpatterns = [
    path('', AccountRootView.as_view(), name='account-root'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/update/', UserUpdateView.as_view(), name='user-update'),
    path('register/', RegisterView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('logout/', LogoutView.as_view(), name='user-logout'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('drivers/', DriverListView.as_view(), name='driver-list'),
    path('drivers/<int:pk>/', DriverDetailView.as_view(), name='driver-detail'),
    path('drivers/<int:pk>/update/', DriverUpdateView.as_view(), name='driver-update'),
    path('wallets/', WalletAPIVew.as_view(), name='wallet-list'),
    path('wallets/<int:pk>/', WalletAPIVew.as_view(), name='wallet-detail'),
]