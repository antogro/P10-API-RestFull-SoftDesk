from rest_framework import permissions


class IsUserOwner(permissions.BasePermission):
    """
    Permission personnalisée pour permettre à un utilisateur
    de modifier uniquement son propre compte.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.id == request.user.id
