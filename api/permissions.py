from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author_id == request.user.pk


class IsProjectContributor(BasePermission):
    def has_permission(self, request, view):
        if 'project_pk' not in view.kwargs:
            return True
        project = view.get_project()
        return project.contributors.filter(pk=request.user.pk).exists()

    def has_object_permission(self, request, view, obj):
        if 'project_pk' in view.kwargs:
            return True
        if hasattr(obj, 'project'):
            project = obj.project
        elif hasattr(obj, 'issue'):
            project = obj.issue.project
        else:
            project = obj
        return project.contributors.filter(pk=request.user.pk).exists()


class IsProjectAuthorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return view.get_project().author_id == request.user.pk

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return view.get_project().author_id == request.user.pk
