from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from api.permissions import (
    IsAuthorOrReadOnly,
    IsProjectAuthorOrReadOnly,
    IsProjectContributor,
)
from projects.models import Contributor, Project
from projects.serializers import ContributorSerializer, ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [
        IsAuthenticated,
        IsProjectContributor,
        IsAuthorOrReadOnly,
    ]

    def get_queryset(self):
        return (
            Project.objects.filter(contributors=self.request.user)
            .order_by('id')
        )

    @transaction.atomic
    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(
            user=self.request.user,
            project=project,
        )


class ContributorViewSet(viewsets.ModelViewSet):
    serializer_class = ContributorSerializer
    permission_classes = [
        IsAuthenticated,
        IsProjectContributor,
        IsProjectAuthorOrReadOnly,
    ]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_project(self):
        if not hasattr(self, '_project'):
            self._project = get_object_or_404(
                Project,
                pk=self.kwargs['project_pk'],
            )
        return self._project

    def get_queryset(self):
        return (
            Contributor.objects.filter(project=self.get_project())
            .order_by('id')
        )

    def perform_create(self, serializer):
        project = self.get_project()
        user = serializer.validated_data['user']
        if Contributor.objects.filter(project=project, user=user).exists():
            raise ValidationError(
                {'user': 'Cet utilisateur contribue déjà à ce projet.'}
            )
        serializer.save(project=project)

    @transaction.atomic
    def perform_destroy(self, instance):
        project = self.get_project()
        if instance.user == project.author:
            raise ValidationError(
                {'user': "L'auteur doit rester contributeur du projet."}
            )
        project.issues.filter(assignee=instance.user).update(assignee=None)
        instance.delete()
