from rest_framework.permissions import BasePermission
from SoftDesk.models import Project, Issue, Comment


class IsProjectContributor(BasePermission):
    """
    Permission personnalisé pour s'assuré
    que l'utilisateur est bien contributeur du projet
    """

    def has_permission(self, request, view):
        project_id = view.kwargs.get("project_pk")
        if project_id:
            return request.user in view.get_project().contributors.all()
        return False

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Project):
            return request.user in obj.contributors.all()
        elif isinstance(obj, Issue):
            return request.user in obj.project.contributors.all()
        elif isinstance(obj, Comment):
            return request.user in obj.issue.project.contributors.all()
        return False


class IsAuthorOrReadOnly(BasePermission):
    """
    Permission personnalisé pour s'assuré
    que l'utilisateur est bien authore de l'objet
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        return obj.author == request.user
