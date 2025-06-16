from rest_framework import generics, permissions, serializers
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy

class EmptySerializer(serializers.Serializer):
    pass

class ApiRootView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = EmptySerializer

    @staticmethod
    def get(request, *args, **kwargs):
        data = {
            'users': reverse_lazy('user-list', request=request, format=None),
            'drivers': reverse_lazy('driver-list', request=request, format=None),
            'register': reverse_lazy('register', request=request, format=None),
            'login': reverse_lazy('login', request=request, format=None),
            'logout': reverse_lazy('logout', request=request, format=None),
        }
        return Response(data)