from rest_framework import permissions

from accounts.models import Role


def _has_role_admin(user):
    if not user or not user.is_authenticated:
        return False
    return Role.objects.filter(name="admin", userrole__user=user).exists()


class IsAdmin(permissions.BasePermission):
    """Tylko użytkownicy z rolą 'admin'."""

    def has_permission(self, request, view):
        return _has_role_admin(request.user)

    def has_object_permission(self, request, view, obj):
        return _has_role_admin(request.user)


class IsOwnerOrAdmin(permissions.BasePermission):
    """Właściciel obiektu (obj.user) lub użytkownik z rolą 'admin'. Dla modeli bez .user (np. Room) de facto IsAdmin."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, "user", None)
        if owner is not None and request.user == owner:
            return True
        return _has_role_admin(request.user)
