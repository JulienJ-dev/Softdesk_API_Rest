from django.urls import path
from rest_framework.routers import DefaultRouter

from projects.views import ContributorViewSet, ProjectViewSet


router = DefaultRouter()
router.register('projects', ProjectViewSet, basename='project')

contributor_list = ContributorViewSet.as_view(
    {'get': 'list', 'post': 'create'}
)
contributor_detail = ContributorViewSet.as_view(
    {'get': 'retrieve', 'delete': 'destroy'}
)

urlpatterns = router.urls + [
    path(
        'projects/<int:project_pk>/contributors/',
        contributor_list,
        name='contributor-list',
    ),
    path(
        'projects/<int:project_pk>/contributors/<int:pk>/',
        contributor_detail,
        name='contributor-detail',
    ),
]
