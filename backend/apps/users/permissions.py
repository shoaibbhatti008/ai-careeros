"""Custom permission classes for AI CareerOS."""

from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Object-level permission: only the owner can access.

    Assumes the model instance has a `user` attribute.
    """

    message = "You do not have permission to access this resource."

    def has_object_permission(self, request, view, obj) -> bool:
        # Read permissions are allowed for owners only
        return getattr(obj, "user", None) == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission: owners can edit, others read-only.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, "user", None) == request.user


class IsAdminUser(permissions.BasePermission):
    """Allow only staff/superusers."""

    message = "Admin access required."

    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_staff)
