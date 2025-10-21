from functools import partial

from django.http import Http404
from rest_framework.reverse import reverse_lazy
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from apis.permissions import IsUserOrReadOnly, IsDriverOrReadOnly
from rest_framework.exceptions import PermissionDenied, ValidationError
from .serializers import UserSerializer, UserUpdateSerializer, LoginSerializer, LogoutSerializer, DriverSerializer, WalletSerializer
from accounts.models import User, Driver, Wallet
from ..views import EmptySerializer
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny


# Reusable file handling for Driver file fields
DRIVER_FILE_FIELDS = [
    'vehicle_image', 'licence_image', 'id_front_image', 'id_back_image', 'insurance_cert'
]


def get_driver_file_updates(request):
    """Return a dict of file field updates present in request.FILES for Driver instances."""
    updates = {}
    for field in DRIVER_FILE_FIELDS:
        if field in request.FILES:
            updates[field] = request.FILES[field]
    return updates


# User List
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user:
            token, created = Token.objects.get_or_create(user=user)
            user_serializer = self.get_serializer(user)
            headers = self.get_success_headers(serializer.data)
            data = {
                'message': 'Registration successful.',
                'token': token.key,
                'user': user_serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED, headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login View

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        user = authenticate(request, username=request.data.get('email'), password=request.data.get('password'))
        if user is not None:
            login(request, user)  # This sets the session for browser use
            token, created = Token.objects.get_or_create(user=user)
            user_serializer = UserSerializer(user, context={"request": request})
            return Response({
                "success": "You successfully logged in",
                "token": token.key,
                "user": user_serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)


# Logout View
class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permissions_classes = [permissions.IsAuthenticated]

    @staticmethod
    def get(request, *args, **kwargs):
        try:
            logout(request)
            request.session.clear()  # Clear the session
            msg = {'message': 'You have logged out now'}
            return Response(msg, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser | IsUserOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        # Call the superclass method to get the standard retrieval of the user instance,
        # which also applies the serializer defined in serializer_class
        response = super(UserDetailView, self).retrieve(request, *args, **kwargs)

        # Get the user instance. self.get_object() is available in RetrieveAPIView
        user = self.get_object()

        # Add the event manager id to the response if the user is an event manager
        if user.is_driver:
            driver_serializer = DriverSerializer(user.driver)
            driver_data = driver_serializer.data
            # Exclude the 'user' field from driver data
            driver_data.pop('user', None)
            response.data['driver'] = driver_data

        return response

# User Update View
class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsUserOrReadOnly | permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        instance = serializer.instance
        if 'avatar' in self.request.FILES:
            avatar_file = self.request.FILES['avatar']
            serializer.save(avatar=avatar_file)
        else:
            # Set the avatar to the current file before saving
            current_avatar = instance.avatar
            serializer.save(avatar=current_avatar)

    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)


# Driver List View
class DriverListView(generics.ListCreateAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        user = self.request.user

        if user.is_driver:
            raise PermissionDenied({
                "error": "You are already a driver.",
                "message": "You cannot create a driver profile if you are already a driver."
            })

        if not user.is_authenticated:
            raise PermissionDenied({
                "error": "You must be logged in to create a driver profile.",
                "message": "You are not logged in."
            })

        # Set the user's is_driver field to True
        user.is_driver = True
        user.save()

        # Set the driver's status to 'Documents Submitted'
        driver_status = 'Documents Submitted'

        # Save the driver instance with the user and status
        serializer.save(user=user, status=driver_status)

        # Apply any uploaded file fields and persist
        file_updates = get_driver_file_updates(self.request)
        if file_updates:
            for field, value in file_updates.items():
                setattr(serializer.instance, field, value)
            # Persist only the updated file fields to avoid unintended changes
            serializer.instance.save(update_fields=list(file_updates.keys()))

        return Response({
            "success": "Driver profile created successfully.",
            "message": "You have successfully created a driver profile.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


# Driver Detail View
class DriverDetailView(generics.RetrieveAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated, IsDriverOrReadOnly | permissions.IsAdminUser]


# Driver Update View
class DriverUpdateView(generics.GenericAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated, IsDriverOrReadOnly | permissions.IsAdminUser]

    def get_object(self):
        pk = self.kwargs.get('pk')
        try:
            driver = Driver.objects.get(pk=pk)
            self.check_object_permissions(self.request, driver)
            return driver
        except Driver.DoesNotExist:
            raise Http404("Driver not found")

    def check_object_permissions(self, request, driver):
        if driver.user != request.user:
            raise PermissionDenied("You do not have permission to update this driver profile.")

    def get(self, request, *args, **kwargs):
        driver = self.get_object()
        serializer = self.get_serializer(driver)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        driver = self.get_object()
        data = request.data.copy()
        # Merge only provided file updates; partial=True preserves others
        data.update(get_driver_file_updates(request))
        serializer = self.get_serializer(driver, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        driver = self.get_object()
        data = request.data.copy()
        # Merge only provided file updates; partial=True preserves others
        data.update(get_driver_file_updates(request))
        serializer = self.get_serializer(driver, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        driver = self.get_object()
        if driver.user == request.user or request.user.is_staff:
            driver.delete()
            return Response({"message": "Driver profile deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied("You do not have permission to delete this driver profile.")


class WalletAPIVew(generics.GenericAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Admins see all wallets; regular users see only their own."""
        user = self.request.user
        if user.is_staff:
            return Wallet.objects.all()
        return Wallet.objects.filter(user=user)

    def get_object(self):
        """Return a specific wallet. If no pk is provided, default to the current user's wallet."""
        pk = self.kwargs.get('pk')
        if pk is not None:
            try:
                wallet = Wallet.objects.get(pk=pk)
            except Wallet.DoesNotExist:
                raise Http404("Wallet not found")
        else:
            try:
                wallet = Wallet.objects.get(user=self.request.user)
            except Wallet.DoesNotExist:
                raise Http404("Wallet for current user not found")

        # Permissions: only owner or admin can access a specific wallet
        if not (self.request.user.is_staff or wallet.user == self.request.user):
            raise PermissionDenied("You do not have permission to access this wallet.")
        return wallet

    def get(self, request, *args, **kwargs):
        """List wallets (admin) or return current user's/specific wallet."""
        if 'pk' in kwargs:
            wallet = self.get_object()
            serializer = self.get_serializer(wallet)
            return Response(serializer.data, status=status.HTTP_200_OK)
        # No pk: list if admin, else return single current user's wallet as an object
        qs = self.get_queryset()
        if request.user.is_staff:
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        # Non-admin: return (or lazily create) the current user's wallet
        try:
            wallet = qs.get()
        except Wallet.DoesNotExist:
            return Response({"detail": "Wallet not found for current user."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(wallet)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """Create a wallet for the current user. Admins may create for another user if `user` is provided."""
        data = request.data.copy()
        # Force ownership for non-admins
        if not request.user.is_staff:
            data['user'] = getattr(request.user, 'id', None)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Prevent duplicates per user
        user_id = serializer.validated_data.get('user').id if request.user.is_staff else request.user.id
        if Wallet.objects.filter(user_id=user_id).exists():
            raise ValidationError("A wallet already exists for this user.")

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """Full update of a wallet (owner or admin)."""
        wallet = self.get_object()
        serializer = self.get_serializer(wallet, data=request.data)
        serializer.is_valid(raise_exception=True)
        # Non-admins cannot reassign wallet ownership
        if not request.user.is_staff and 'user' in serializer.validated_data:
            serializer.validated_data.pop('user', None)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        """Partial update of a wallet (owner or admin)."""
        wallet = self.get_object()
        serializer = self.get_serializer(wallet, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if not request.user.is_staff and 'user' in serializer.validated_data:
            serializer.validated_data.pop('user', None)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """Delete a wallet (owner or admin)."""
        wallet = self.get_object()
        wallet.delete()
        return Response({"message": "Wallet deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class AccountRootView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmptySerializer

    def get(self, request, *args, **kwargs):
        data = {
            'users': reverse_lazy('user-list', request=request, format=None),
            'register': reverse_lazy('user-register', request=request, format=None),
            'login': reverse_lazy('user-login', request=request, format=None),
            'logout': reverse_lazy('user-logout', request=request, format=None),
            'drivers': reverse_lazy('driver-list', request=request, format=None),
            'wallets': reverse_lazy('wallet-list', request=request, format=None),
        }
        return Response(data)
