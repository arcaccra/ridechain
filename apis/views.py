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
            'accounts': reverse_lazy('account-root', request=request, format=None),
            'rides_apis': reverse_lazy('ride-list-root', request=request, format=None),
        }
        return Response(data)