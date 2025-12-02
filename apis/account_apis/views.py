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
from apis.ride_apis.urls import  RideDetailSerializer
from rides.models import Ride
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
import logging
logger = logging.getLogger(__name__)
from utilities.blockfrost_config import BlockfrostConfig

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

        avatar_file = request.FILES.get('avatar')
        save_kwargs = {'avatar': avatar_file} if avatar_file else {}
        user = serializer.save(**save_kwargs)

        token, _ = Token.objects.get_or_create(user=user)
        user_serializer = self.get_serializer(user, context={'request': request})
        headers = self.get_success_headers(serializer.data)
        data = {
            'message': 'Registration successful.',
            'token': token.key,
            'user': user_serializer.data,
        }
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


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

        # Add the driver id to the response if the user is an event manager
        if user.is_driver:
            driver_serializer = DriverSerializer(user.driver)
            driver_data = driver_serializer.data
            # Exclude the 'user' field from driver data
            driver_data.pop('user', None)
            response.data['driver'] = driver_data
        #Add rides where user is a passenger by checking if user in ride.passengers
        passenger_rides = Ride.objects.filter(passengers=user)
        ride_serializer = RideDetailSerializer(passenger_rides, many=True)
        response.data['user_rides'] = ride_serializer.data
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
    permission_classes = [permissions.IsAuthenticated]

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
        """List wallets (admin) or return current user's/specific wallet, including balance for single-wallet responses."""
        # If a specific wallet was requested (detail view)
        if 'pk' in kwargs:
            wallet = self.get_object()
            serializer = self.get_serializer(wallet)
            data = serializer.data
            address = data.get('address') or getattr(wallet, 'address', None)
            if address:
                try:
                    bf = BlockfrostConfig()
                    data['balance'] = bf.get_wallet_balance(address)
                except Exception as e:
                    logger.exception("Failed to fetch balance for wallet %s: %s", address, e)
                    data['balance_error'] = "Unable to fetch balance at this time."
            return Response(data, status=status.HTTP_200_OK)

        qs = self.get_queryset()
        # Admin: return all wallets with balances attached
        if request.user.is_staff:
            serializer = self.get_serializer(qs, many=True)
            data = serializer.data
            try:
                bf = BlockfrostConfig()
            except Exception:
                bf = None
            # Zip serializer data with queryset to reliably access model instances (for fallback address)
            for idx, item in enumerate(data):
                # Try serializer address first, then model instance
                try:
                    instance = list(qs)[idx]
                except Exception:
                    instance = None
                address = item.get('address') or (getattr(instance, 'address', None) if instance is not None else None)
                if address and bf is not None:
                    try:
                        item['balance'] = bf.get_wallet_balance(address)
                    except Exception as e:
                        logger.exception("Failed to fetch balance for wallet %s: %s", address, e)
                        item['balance_error'] = "Unable to fetch balance at this time."
            return Response(data, status=status.HTTP_200_OK)

        # Non-admin: return the current user's wallet or (if multiple) a list of their wallets with balances
        try:
            # If there's exactly one wallet, qs.get() will succeed; if multiple exist, handle below
            wallet = qs.get()
        except Wallet.DoesNotExist:
            return Response({"detail": "Wallet not found for current user."}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            # Could be MultipleObjectsReturned or other issues; fall back to returning a list of wallets
            serializer = self.get_serializer(qs, many=True)
            data = serializer.data
            try:
                bf = BlockfrostConfig()
            except Exception:
                bf = None
            for idx, item in enumerate(data):
                try:
                    instance = list(qs)[idx]
                except Exception:
                    instance = None
                address = item.get('address') or (getattr(instance, 'address', None) if instance is not None else None)
                if address and bf is not None:
                    try:
                        item['balance'] = bf.get_wallet_balance(address)
                    except Exception as e:
                        logger.exception("Failed to fetch balance for wallet %s: %s", address, e)
                        item['balance_error'] = "Unable to fetch balance at this time."
            return Response(data, status=status.HTTP_200_OK)

        # Single wallet path (non-admin)
        serializer = self.get_serializer(wallet)
        data = serializer.data
        address = data.get('address') or getattr(wallet, 'address', None)
        if address:
            try:
                bf = BlockfrostConfig()
                data['balance'] = bf.get_wallet_balance(address)
            except Exception as e:
                logger.exception("Failed to fetch balance for wallet %s: %s", address, e)
                data['balance_error'] = "Unable to fetch balance at this time."
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """Create a wallet for the authenticated user.

        Simplified behavior:
        - Only the requesting user can create their wallet.
        - Validates required `address` and that the user doesn't already have a wallet.
        - Saves the wallet with user=request.user.
        """
        data = request.data.copy()

        # Require an address
        address = data.get('address')
        if not address:
            raise ValidationError({'address': 'This field is required.'})

        # Check if the address is already in use
        if Wallet.objects.filter(address=address).exists():
            raise ValidationError({'address': 'A wallet with this address already exists.'})

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """Full update of a wallet (owner or admin)."""
        wallet = self.get_object()
        # Non-admins cannot reassign wallet ownership; enforce owner stays the same
        data = request.data.copy()
        if not request.user.is_staff:
            data.pop('user', None)
        serializer = self.get_serializer(wallet, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        """Partial update of a wallet (owner or admin)."""
        wallet = self.get_object()
        data = request.data.copy()
        if not request.user.is_staff:
            data.pop('user', None)
        serializer = self.get_serializer(wallet, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
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