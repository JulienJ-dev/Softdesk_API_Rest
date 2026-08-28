from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_home(request):
    return Response(
        {
            'message': 'API SoftDesk Support',
            'users': '/api/users/',
            'projects': '/api/projects/',
            'token': '/api/token/',
            'token_refresh': '/api/token/refresh/',
        }
    )
