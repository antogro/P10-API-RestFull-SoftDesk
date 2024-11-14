from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from SoftDesk.permissions import IsAuthorOrReadOnly
from rest_framework.response import Response
from django.core.cache import cache
from .models import Contributor, Project, Issue, Comment
from django.db.models import Q
from .serializers import (
    ProjectDetailSerializer,
    IssueCreateSerializer,
    ContributorSerializer,
    ProjectListSerializer,
    IssueDetailSerializer,
    IssueListSerializer,
    CommentSerializer,
)


class BaseViewSet(viewsets.ModelViewSet):
    """
    Classe de base pour les vues avec gestion des
    messages de succès et vérification de l'auteur pour
    les actions de mise à jour et de suppression.
    """
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if (hasattr(instance, 'author')
                and instance.author != self.request.user):
            self.permission_denied(
                self.request,
                message="You do not have permission to perform this action."
            )

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        model_name = self.get_queryset().model.__name__

        cache_key = f"{model_name}_{instance.id}"
        cache.delete(cache_key)

        return Response(
            {"message": f"{model_name} was successfully updated."},
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if (hasattr(instance, 'author')
                and instance.author != self.request.user):
            self.permission_denied(
                self.request,
                message="You do not have permission to perform this action."
            )

        self.perform_destroy(instance)
        model_name = self.get_queryset().model.__name__

        cache_key = f"{model_name}_{instance.id}"
        cache.delete(cache_key)

        return Response(
            {"message": f"{model_name} was successfully deleted."},
            status=status.HTTP_204_NO_CONTENT
        )

    def perform_destroy(self, instance):
        instance.delete()


class ProjectViewset(BaseViewSet):
    """
    Gère les projets SoftDesk.

    - Les utilisateurs authentifiés peuvent lire tous les projets.
    - Seul l'auteur du projet peut le mettre à jour ou le supprimer.
    - Le cache est utilisé pour optimiser la récupération des projets.
    """
    permission_classes = [
        IsAuthenticated,
        IsAuthorOrReadOnly
    ]

    def get_queryset(self):
        cache_key = f"projects_{self.request.user.id}"
        cached_projects = cache.get(cache_key)

        if not cached_projects:
            cached_projects = Project.objects.filter(
                Q(author=self.request.user)
                |
                Q(contributors__user=self.request.user)
            ).distinct()
            cache.set(cache_key, cached_projects, timeout=60)

        return cached_projects

    def get_serializer_class(self):
        if self.action in ["list", "create"]:
            return ProjectListSerializer
        return ProjectDetailSerializer

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(
            user=self.request.user,
            project=project,
            role="AUTHOR"
        )
        cache.clear()


class ContributorViewSet(BaseViewSet):
    """
    Gère les contributeurs d'un projet.

    - Accès : l'auteur du projet peut ajouter ou supprimer des contributeurs.
    """
    permission_classes = [
        IsAuthenticated,
        IsAuthorOrReadOnly
    ]
    serializer_class = ContributorSerializer

    def get_queryset(self):
        return Contributor.objects.filter(
            project__id=self.kwargs["project_pk"])

    def perform_create(self, serializer):
        project = Project.objects.get(id=self.kwargs["project_pk"])
        user = serializer.validated_data['user']
        if Contributor.objects.filter(project=project, user=user).exists():
            raise ValidationError(
                "This user is already a contributor to this project."
            )
        serializer.save(project=project)
        cache.delete(f"projects_{self.request.user.id}")


class IssueViewSet(BaseViewSet):
    """
    Vue pour gérer les issues (tickets) associés à un projet.

    - Accès : les contributeurs du projet peuvent voir et créer des issues.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs["project_pk"]
        cache_key = f"issues_{project_id}"
        cached_issues = cache.get(cache_key)

        if not cached_issues:
            cached_issues = Issue.objects.filter(project__id=project_id)
            cache.set(cache_key, cached_issues, timeout=60)

        return cached_issues

    def get_serializer_class(self):
        if self.action == "create":
            return IssueCreateSerializer
        elif self.action in ["list", "retrieve"]:
            return IssueListSerializer
        return IssueDetailSerializer

    def perform_create(self, serializer):
        project = Project.objects.get(id=self.kwargs["project_pk"])
        serializer.save(author=self.request.user, project=project)
        cache.clear()


class CommentViewSet(BaseViewSet):
    """
    Vue pour gérer les commentaires associés à une issue.

    - Accès : les contributeurs peuvent ajouter des commentaires,
      seul l'auteur d'un commentaire peut le modifier ou le supprimer.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        issue_id = self.kwargs["issue_pk"]
        cache_key = f"comments_{issue_id}"
        cached_comments = cache.get(cache_key)

        if not cached_comments:
            cached_comments = Comment.objects.filter(issue__id=issue_id)
            cache.set(cache_key, cached_comments, timeout=60)

        return cached_comments

    def perform_create(self, serializer):
        issue = Issue.objects.get(id=self.kwargs["issue_pk"])
        serializer.save(author=self.request.user, issue=issue)
        cache.delete(f"comments_{issue.id}")
