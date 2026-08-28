from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from api.permissions import IsOwner
from users.models import User
from users.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return User.objects.filter(pk=self.request.user.pk).order_by('id')
        return User.objects.none()

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated(), IsOwner()]
