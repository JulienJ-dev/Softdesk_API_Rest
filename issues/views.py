from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from api.permissions import IsAuthorOrReadOnly, IsProjectContributor
from issues.models import Comment, Issue
from issues.serializers import CommentSerializer, IssueSerializer
from projects.models import Contributor, Project


class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [
        IsAuthenticated,
        IsProjectContributor,
        IsAuthorOrReadOnly,
    ]

    def get_project(self):
        if not hasattr(self, '_project'):
            self._project = get_object_or_404(
                Project,
                pk=self.kwargs['project_pk'],
            )
        return self._project

    def get_queryset(self):
        return (
            Issue.objects.filter(project=self.get_project())
            .order_by('id')
        )

    def validate_assignee(self, project, assignee):
        if assignee and not Contributor.objects.filter(
            project=project,
            user=assignee,
        ).exists():
            raise ValidationError(
                {'assignee': 'Cet utilisateur ne contribue pas au projet.'}
            )

    def perform_create(self, serializer):
        project = self.get_project()
        assignee = serializer.validated_data.get('assignee')
        self.validate_assignee(project, assignee)
        serializer.save(project=project, author=self.request.user)

    def perform_update(self, serializer):
        assignee = serializer.validated_data.get(
            'assignee',
            serializer.instance.assignee,
        )
        self.validate_assignee(self.get_project(), assignee)
        serializer.save()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticated,
        IsProjectContributor,
        IsAuthorOrReadOnly,
    ]

    def get_project(self):
        if not hasattr(self, '_project'):
            self._project = get_object_or_404(
                Project,
                pk=self.kwargs['project_pk'],
            )
        return self._project

    def get_issue(self):
        if not hasattr(self, '_issue'):
            self._issue = get_object_or_404(
                Issue,
                project=self.get_project(),
                pk=self.kwargs['issue_pk'],
            )
        return self._issue

    def get_queryset(self):
        return (
            Comment.objects.filter(issue=self.get_issue())
            .order_by('created_time', 'id')
        )

    def perform_create(self, serializer):
        serializer.save(
            issue=self.get_issue(),
            author=self.request.user,
        )
