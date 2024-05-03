from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import UserProfileSerializer


@extend_schema_view(
    get=extend_schema(summary='Get current user', responses=UserProfileSerializer),
    patch=extend_schema(summary='Partially update current user', request=UserProfileSerializer, responses=UserProfileSerializer),
    put=extend_schema(summary='Update current user', request=UserProfileSerializer, responses=UserProfileSerializer),
)
@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile(request: Request) -> Response:
    if request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = UserProfileSerializer(
            instance=request.user,
            data=request.data,
            partial=partial,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
    else:
        serializer = UserProfileSerializer(
            instance=request.user,
            context={'request': request},
        )

    return Response(serializer.data)
