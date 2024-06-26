from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import exceptions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from gchqnet.accounts.models.user import User
from gchqnet.accounts.totp import CustomTOTP

from .serializers import (
    UserProfileSerializer,
    UserTokenRequestSerializer,
    UserTokenSerializer,
)


@extend_schema(summary="Get current user", responses=UserProfileSerializer, tags=["Users"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request: Request) -> Response:
    serializer = UserProfileSerializer(
        instance=request.user,
        context={"request": request},
    )
    return Response(serializer.data)


@extend_schema(
    summary="Get API token",
    exclude=settings.HIDE_PRIVATE_API_ENDPOINTS,
    request=UserTokenRequestSerializer,
    responses={200: UserTokenSerializer},
    tags=["Users"],
)
@permission_classes([AllowAny])
@api_view(["POST"])
def get_auth_token(request: Request) -> Response:
    serializer = UserTokenRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        user = User.objects.prefetch_related("badges").get(
            username=serializer.validated_data["username"],
            is_active=True,
        )
    except User.DoesNotExist:
        raise exceptions.AuthenticationFailed() from None

    if "otp" in serializer.validated_data:
        security_code = serializer.validated_data["otp"]
        is_valid = any(
            CustomTOTP(mac_address).verify(security_code, valid_window=1)
            for mac_address in user.badges.values_list("mac_address", flat=True)
        )

        if not is_valid or user.is_superuser:
            raise exceptions.AuthenticationFailed()
    else:
        # Password Auth
        if not user.check_password(serializer.validated_data["password"]):
            raise exceptions.AuthenticationFailed()

    # For now, return the static token that every user has.
    response = UserTokenSerializer(
        instance=user,
        context={"request": request},
    )
    return Response(response.data)
