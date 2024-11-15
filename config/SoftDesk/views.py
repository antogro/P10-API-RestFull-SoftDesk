from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from SoftDesk.permissions import IsAuthorOrReadOnly
from rest_framework.response import Response
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


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class BaseViewSet(viewsets.ModelViewSet):
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"message": f"{self.get_queryset().model.__name__} "
                    "was successfully updated."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {"message": f"{self.get_queryset().model.__name__} "
                    "was successfully deleted."},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProjectViewset(BaseViewSet):
    """
    Gère les projets SoftDesk.
    - Les utilisateurs authentifiés peuvent lire tous les projets.
    - Seul l'auteur du projet peut le mettre à jour ou le supprimer.
    """
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Project.objects.filter(
            Q(author=self.request.user)
            |
            Q(contributors__user=self.request.user)
        ).distinct().order_by('created_time')

    def get_serializer_class(self):
        if self.action in ["list", "create"]:
            return ProjectListSerializer
        return ProjectDetailSerializer

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(
            user=self.request.user,
            project=project,
        )


class ContributorViewSet(BaseViewSet):
    """
    Gère les contributeurs d'un projet.
    - Accès : l'auteur du projet peut ajouter ou supprimer des contributeurs.
    - L'auteur ne peut pas être ajouté comme contributeur.
    """
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    serializer_class = ContributorSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Contributor.objects.filter(
            project__id=self.kwargs["project_pk"])

    def perform_create(self, serializer):
        project = Project.objects.get(id=self.kwargs["project_pk"])
        user = serializer.validated_data['user']

        # Vérifier si l'utilisateur est l'auteur du projet
        if project.author == user:
            raise ValidationError(
                "The project author cannot be added as a contributor."
            )

        # Vérifier si l'utilisateur est déjà contributeur
        if Contributor.objects.filter(project=project, user=user).exists():
            raise ValidationError(
                "This user is already a contributor to this project."
            )

        serializer.save(project=project)


class IssueViewSet(BaseViewSet):
    """
    Vue pour gérer les issues (tickets) associés à un projet.
    - Accès : les contributeurs du projet peuvent voir et créer des issues.
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Issue.objects.filter(
            project__id=self.kwargs["project_pk"]
        ).order_by('created_time')

    def get_serializer_class(self):
        if self.action == "create":
            return IssueCreateSerializer
        elif self.action in ["list", "retrieve"]:
            return IssueListSerializer
        return IssueDetailSerializer

    def perform_create(self, serializer):
        project = Project.objects.get(id=self.kwargs["project_pk"])
        serializer.save(author=self.request.user, project=project)


class CommentViewSet(BaseViewSet):
    """
    Vue pour gérer les commentaires associés à une issue.
    - Accès : les contributeurs peuvent ajouter des commentaires,
      seul l'auteur d'un commentaire peut le modifier ou le supprimer.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer
    pagination_class = StandardResultsSetPagination

    def retrieve(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        try:
            comment = Comment.objects.get(uuid=uuid)
            serializer = self.get_serializer(comment)
            return Response(serializer.data)
        except Comment.DoesNotExist:
            return Response(
                {"error": "Comment not found."},
                status=status.HTTP_404_NOT_FOUND
            )

    def get_queryset(self):
        return Comment.objects.filter(
            issue__id=self.kwargs["issue_pk"]
        ).order_by('created_time')

    def perform_create(self, serializer):
        issue = Issue.objects.get(id=self.kwargs["issue_pk"])
        serializer.save(author=self.request.user, issue=issue)
