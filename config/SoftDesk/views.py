from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Contributor, Project, Issue, Comment
from django.db.models import Q
from .serializers import (
    ContributorSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
    IssueListSerializer,
    IssueDetailSerializer,
    CommentSerializer,
)
from .permissions import IsAuthorOrReadOnly, IsProjectContributor


class ProjectViewset(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        # IsProjectContributor,
        # IsAuthorOrReadOnly
    ]

    def get_queryset(self):
        return Project.objects.filter(
            Q(author=self.request.user)
            |
            Q(contributors__user=self.request.user)
        ).distinct()

    def get_serializer_class(self):
        if self.action in ["list", "create"]:
            return ProjectListSerializer
        return ProjectDetailSerializer

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(
            user=self.request.user,
            project=project,
            role="AUTHOR",
            permission="WRITE",
        )
        return project

    def update(self, request, *args, **kwargs):
        project = self.get_object()
        if not project.autor == request.iser:
            return Response(
                {"error": "Only the project author can update the project."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        if not project.author != request.user:
            return Response(
                {"error": "Only the project author can delete it."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class ContributorViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        # IsProjectContributor,
        # IsAuthorOrReadOnly
    ]
    serializer_class = ContributorSerializer

    def get_queryset(self):
        return Contributor.objects.filter(
            project__id=self.kwargs["project_pk"])

    def perform_create(self, serializer):
        project = Project.objects.get(id=self.kwargs["project_pk"])
        serializer.save(project=project)


class IssueViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        # IsProjectContributor,
        # IsAuthorOrReadOnly
    ]

    def get_queryset(self):
        return Issue.objects.filter(project__id=self.kwargs["project_pk"])

    def get_serializer_class(self):
        if self.action in ["list", "create"]:
            return IssueListSerializer
        return IssueDetailSerializer

    def perform_create(self, serializer):
        project = Project.objects.get(id=self.kwargs["project_pk"])
        serializer.save(author=self.request.user, project=project)

    def update(self, request, *args, **kwargs):
        issue = self.get_object()
        if not issue.autor == request.iser:
            return Response(
                {"error": "Only the project issue can update the issue."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        issue = self.get_object()
        if not issue.author != request.user:
            return Response(
                {"error": "Only the issue author can delete it."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        # IsProjectContributor,
        # IsAuthorOrReadOnly
    ]

    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(issue__id=self.kwargs["issue_pk"])

    def perform_create(self, serializer):
        issue = Issue.objects.get(id=self.kwargs["issue_pk"])
        serializer.save(author=self.request.user, issue=issue)

    def update(self, request, *args, **kwargs):
        comment = self.get_object()
        if not comment.autor == request.iser:
            return Response(
                {"error": "Only the comment author can update the comment."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return Response(
                {"error": "Only the comment author can delete it."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)
