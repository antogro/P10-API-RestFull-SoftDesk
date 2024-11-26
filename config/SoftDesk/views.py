from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from SoftDesk.permissions import (
    IsContributorOrAuthor,
    IsContributorOrAuthorForComment,
    IsContributorOrAuthorForIssue,
    IsContributorForRemoval
)
from rest_framework.response import Response
from .models import Contributor, Project, Issue, Comment
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
    permission_classes = [
        IsAuthenticated,
        IsContributorOrAuthor
    ]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Project.objects.filter(
            contributors__user=self.request.user
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
    Vue pour gérer les commentaires associés à une issue.
    - Accès : les contributeurs peuvent ajouter des commentaires,
      seul l'auteur d'un commentaire peut le modifier ou le supprimer.
    """
    permission_classes = [IsAuthenticated, IsContributorForRemoval]
    serializer_class = ContributorSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Contributor.objects.filter(
            project__id=self.kwargs["project_pk"]
        ).order_by('id')

    def perform_create(self, serializer):
        project = Project.objects.get(id=self.kwargs["project_pk"])
        user = serializer.validated_data['user']

        if project.author != self.request.user:
            raise PermissionDenied(
                "Only the project author can add contributors."
            )

        if project.author == user:
            raise PermissionDenied(
                "The project author cannot be added as a contributor."
            )

        if Contributor.objects.filter(project=project, user=user).exists():
            raise PermissionDenied(
                "This user is already a contributor to this project."
            )

        serializer.save(project=project)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            project = instance.project

            if request.user != project.author:
                return Response(
                    {
                        "error": "Only the project "
                        "author can remove contributors."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            user_name = instance.user.username
            self.perform_destroy(instance)
            return Response(
                {
                    "message": f"Contributor {user_name} "
                    "was successfully removed from the project."
                },
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class IssueViewSet(BaseViewSet):
    """
    Vue pour gérer les issues (tickets) associés à un projet.
    - Accès : les contributeurs du projet peuvent voir et créer des issues.
    """
    permission_classes = [
        IsAuthenticated,
        IsContributorOrAuthorForIssue
    ]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        project_id = self.kwargs["project_pk"]

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise PermissionDenied("No Project matches the given query.")

        if not (
            project.author == self.request.user or
            project.contributors.filter(user=self.request.user).exists()
        ):
            raise PermissionDenied(
                "You do not have permission to view issues for this project."
            )

        return Issue.objects.filter(project=project).order_by('created_time')

    def get_serializer_class(self):
        if self.action == "create":
            return IssueCreateSerializer
        elif self.action == "list":
            return IssueListSerializer
        elif self.action == "retrieve":
            return IssueDetailSerializer
        return IssueDetailSerializer

    def perform_create(self, serializer):
        try:
            project = Project.objects.get(id=self.kwargs["project_pk"])
        except Project.DoesNotExist:
            raise PermissionDenied("No Project matches the given query.")

        serializer.save(author=self.request.user, project=project)


class CommentViewSet(BaseViewSet):
    """
    Vue pour gérer les commentaires associés à une issue.
    - Accès : les contributeurs peuvent ajouter des commentaires,
      seul l'auteur d'un commentaire peut le modifier ou le supprimer.
    """
    permission_classes = [
        IsAuthenticated,
        IsContributorOrAuthorForComment
    ]
    serializer_class = CommentSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'uuid'

    def get_queryset(self):
        """
        Récupère les commentaires d'une issue en vérifiant les permissions
        """
        project_id = self.kwargs.get("project_pk")
        issue_id = self.kwargs.get("issue_pk")

        try:
            project = Project.objects.get(id=project_id)

            issue = Issue.objects.get(
                id=issue_id,
                project=project
            )

            if not (
                project.author == self.request.user or
                project.contributors.filter(user=self.request.user).exists()
            ):
                raise PermissionDenied(
                    "You don't have the permission to modify this comment."
                )

            return Comment.objects.filter(
                issue=issue
            ).order_by('created_time')

        except (Project.DoesNotExist, Issue.DoesNotExist):
            raise PermissionDenied("Project or issue not found.")

    def perform_create(self, serializer):
        """
        Création d'un commentaire avec vérifications
        """
        project_id = self.kwargs.get("project_pk")
        issue_id = self.kwargs.get("issue_pk")

        try:
            project = Project.objects.get(id=project_id)

            if not (
                project.author == self.request.user or
                project.contributors.filter(user=self.request.user).exists()
            ):
                raise PermissionDenied(
                    "You don't have the permission to comment this ."
                )

            issue = Issue.objects.get(
                id=issue_id,
                project=project
            )

            serializer.save(
                author=self.request.user,
                issue=issue
            )

        except (Project.DoesNotExist, Issue.DoesNotExist):
            raise PermissionDenied("Project or issue not found.")
