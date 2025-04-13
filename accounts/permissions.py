from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """
    Allows access only to Super Admin users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superadmin)


class IsAdmin(permissions.BasePermission):
    """
    Allows access only to Admin users (including Super Admins).
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to allow owners of an object or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Admin permissions
        if request.user.is_admin:
            return True
            
        # Instance must have an attribute named `user`
        return obj.user == request.user
