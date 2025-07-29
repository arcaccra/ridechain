from rest_framework import permissions
from accounts.models import Driver


class IsUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj == request.user


class IsDriverOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow the driver associated with the object to edit it.
    Assumes the object has a `.driver` attribute with a related `user`.
    """

    def has_object_permission(self, request, view, obj):
        # Allow read-only access for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow write permissions only to the driver’s user
        driver_user = getattr(getattr(obj, 'driver', None), 'user', None)
        return driver_user == request.user
