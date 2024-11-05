from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
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


class ProjectViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(
            Q(author=self.request.user)
            |
            Q(contributors__user=self.request.user)
        )

    def get_serializer_class(self):
        if self.action in ["list", "create"]:
            return ProjectListSerializer
        return ProjectDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ContributorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ContributorSerializer

    def get_queryset(self):
        return Contributor.objects.filter(
            project__id=self.kwargs["project_pk"])

    def perform_create(self, serializer):
        project = Project.objects.get(id=self.kwargs["project_pk"])
        serializer.save(project=project, user=self.request.user)


class IssueViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Issue.objects.filter(project__id=self.kwargs["project_pk"])

    def get_serializer_class(self):
        if self.action in ["list", "create"]:
            return IssueListSerializer
        return IssueDetailSerializer

    def get_perform_create(self, serializer):
        project = Project.objects.get(id=self.kwargs["project_pk"])
        serializer.save(author=self.request.user, project=project)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(issue__id=self.kwargs["issue_pk"])

    def perform_create(self, serializer):
        issue = Issue.objects.get(id=self.kwargs["issue_pk"])
        serializer.save(author=self.request.user, issue=issue)
