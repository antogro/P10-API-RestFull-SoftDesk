from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisé pour s'assuré
    que l'utilisateur est bien l'autheur de l'objet
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
