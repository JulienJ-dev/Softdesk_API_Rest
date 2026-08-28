from django.urls import path

from issues.views import CommentViewSet, IssueViewSet


issue_list = IssueViewSet.as_view({'get': 'list', 'post': 'create'})
issue_detail = IssueViewSet.as_view(
    {
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }
)
comment_list = CommentViewSet.as_view({'get': 'list', 'post': 'create'})
comment_detail = CommentViewSet.as_view(
    {
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }
)

urlpatterns = [
    path(
        'projects/<int:project_pk>/issues/',
        issue_list,
        name='issue-list',
    ),
    path(
        'projects/<int:project_pk>/issues/<int:pk>/',
        issue_detail,
        name='issue-detail',
    ),
    path(
        'projects/<int:project_pk>/issues/<int:issue_pk>/comments/',
        comment_list,
        name='comment-list',
    ),
    path(
        'projects/<int:project_pk>/issues/'
        '<int:issue_pk>/comments/<uuid:pk>/',
        comment_detail,
        name='comment-detail',
    ),
]
