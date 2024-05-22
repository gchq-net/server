from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import exceptions, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from gchqnet.accounts.api.serializers import UserProfileSerializer
from gchqnet.accounts.repository import check_badge_credentials
from gchqnet.accounts.totp import CustomTOTP
from gchqnet.quest.api.serializers import BadgeAPIRequestSerializer, BadgeOTPResponseSerializer


class BadgeAPIViewset(viewsets.GenericViewSet):
    permission_classes = (permissions.AllowAny,)

    @extend_schema(
        summary="Get player info for current badge",
        exclude=settings.HIDE_PRIVATE_API_ENDPOINTS,
        request=BadgeAPIRequestSerializer,
        responses={200: UserProfileSerializer, 201: UserProfileSerializer},
        tags=["Badge Internal API"],
    )
    @action(methods=["POST"], detail=False)
    def player(self, request: Request) -> Response:
        serializer = BadgeAPIRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = check_badge_credentials(
            serializer.validated_data["mac_address"],
            serializer.validated_data["badge_secret"],
        )

        if result["result"] == "failure":
            raise exceptions.AuthenticationFailed()

        resp_serializer = UserProfileSerializer(
            instance=result["user"],
        )
        status = 201 if result["new_user"] else 200
        return Response(resp_serializer.data, status=status)

    @extend_schema(
        summary="Get OTP for current badge",
        exclude=settings.HIDE_PRIVATE_API_ENDPOINTS,
        request=BadgeAPIRequestSerializer,
        responses={200: BadgeOTPResponseSerializer},
        tags=["Badge Internal API"],
    )
    @action(methods=["POST"], detail=False)
    def otp(self, request: Request) -> Response:
        serializer = BadgeAPIRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = check_badge_credentials(
            serializer.validated_data["mac_address"],
            serializer.validated_data["badge_secret"],
        )

        if result["result"] == "failure":
            raise exceptions.AuthenticationFailed()

        totp = CustomTOTP(result["badge"].mac_address)

        resp_serializer = BadgeOTPResponseSerializer(data={"username": result["user"].username, "otp": totp.now()})
        assert resp_serializer.is_valid()
        return Response(resp_serializer.data, status=200)
