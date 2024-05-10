from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import UserProfileSerializer


@extend_schema(summary="Get current user", responses=UserProfileSerializer, tags=["Users"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request: Request) -> Response:
    serializer = UserProfileSerializer(
        instance=request.user,
        context={"request": request},
    )
    return Response(serializer.data)
