from rest_framework import permissions


class IsStaffOrSuperuser(permissions.BasePermission):
    """
    Allows access to only staff or admin users
    """

    def has_permission(self, request, view) -> bool:
        return bool(request.user.is_staff or request.user.is_superuser)
