from rest_framework.permissions import BasePermission
from SoftDesk.models import Project, Contributor, Issue, Comment


class BaseProjectPermission(BasePermission):
    """
    Classe de base pour les permissions liées aux projets.
    Fournit des vérifications communes pour les contributeurs et auteurs.
    """

    def is_contributor_or_author(self, request, obj):
        """
        Check if the user is a contributor or author.
        """

        if hasattr(obj, 'project'):
            project = obj.project
        else:
            project = getattr(obj, 'project', obj)

        return (
            project.author == request.user
            or project.contributors.filter(user=request.user).exists()
        )


class IsContributorOrAuthor(BaseProjectPermission):
    """
    Permission pour les projets.
    - Lecture : Contributeurs et auteurs du projet.
    - Écriture : Seul l'auteur du projet.
    """
    def has_permission(self, request, view):
        if view.action in ["create", "list", "retrieve"]:
            return request.user.is_authenticated

        project_pk = view.kwargs.get('project_pk') or view.kwargs.get('pk')

        if project_pk:
            return (
                Contributor.objects.filter(
                    project_id=project_pk,
                    user=request.user
                ).exists() or
                Project.objects.filter(
                    id=project_pk,
                    author=request.user
                ).exists()
            )
        return False

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Project):
            return (
                obj.author == request.user
                or
                obj.contributors.filter(user=request.user).exists()
            )

        if isinstance(obj, (Issue, Comment)):
            return self.is_contributor_or_author(request, obj.project)

        return False


class IsContributorForRemoval(BasePermission):
    """
    Permission personalisé pour controlé la suppression des contributeurs
    Seul l'auteur du projet peut supprimer un contributeur
    """
    def has_permission(self, request, view):
        if 'project_pk' in view.kwargs:
            try:
                project = Project.objects.get(id=view.kwargs['project_pk'])
                return project.author == request.user
            except Project.DoesNotExist:
                return False
        return False

    def has_object_permission(self, request, view, obj):
        return obj.project.author == request.user


class IsContributorOrAuthorForIssue(BaseProjectPermission):
    """
    Permission pour les issues.
    - Lecture : contributeurs, auteur du projet ou auteur de l'issue.
    - Écriture : uniquement auteur de l'issue.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return (
                self.is_contributor_or_author(request, obj.project)
                or obj.author == request.user
            )
        return obj.author == request.user


class IsContributorOrAuthorForComment(BaseProjectPermission):
    """
    Permission pour les commentaires.
    - Lecture : contributeurs, auteur du projet ou auteur du commentaire.
    - Écriture : uniquement auteur du commentaire.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return (
                self.is_contributor_or_author(request, obj.issue.project)
                or obj.author == request.user
            )
        return obj.author == request.user
