from django.http import Http404
from rest_framework.reverse import reverse_lazy
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from apis.permissions import IsUserOrReadOnly, IsDriverOrReadOnly
from rest_framework.exceptions import PermissionDenied, ValidationError
from .serializers import UserSerializer, UserUpdateSerializer, LoginSerializer, LogoutSerializer, DriverSerializer
from accounts.models import User, Driver
from ..views import EmptySerializer


# User List
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


# Registration View
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = self.serializer_class.Meta.model.objects.get(pk=response.data['id'])
        token, created = Token.objects.get_or_create(user=user)
        user_serializer = self.get_serializer(user)
        data = {
            'message': 'Registration successful.',
            'token': token.key,
            'user': user_serializer.data
        }
        response.data = data
        return response


# Login View
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

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

    @staticmethod
    def get(request, *args, **kwargs):
        try:
            logout(request)
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
            driver_id = user.driver.id
            response.data['driver'] = driver_id

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

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_driver:
            raise PermissionDenied("You are already a driver.")

        if not user.is_authenticated:
                raise PermissionDenied("You must be logged in to create a driver profile.")

        user.is_driver = True
        user.save()
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Driver Detail View
class DriverDetailView(generics.RetrieveAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated, IsUserOrReadOnly | permissions.IsAdminUser]


# Driver Update View
class DriverUpdateView(generics.GenericAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated, IsUserOrReadOnly | permissions.IsAdminUser]

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
        serializer = self.get_serializer(driver, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        driver = self.get_object()
        serializer = self.get_serializer(driver, data=request.data, partial=True)
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
        }
        return Response(data)



