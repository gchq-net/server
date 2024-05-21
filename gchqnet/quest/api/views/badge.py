from uuid import UUID

from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import exceptions, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from gchqnet.accounts.api.serializers import UserProfileSerializer
from gchqnet.accounts.repository import check_badge_credentials
from gchqnet.accounts.totp import CustomTOTP
from gchqnet.hexpansion.models import Hexpansion
from gchqnet.quest.api.serializers import (
    BadgeAPIRequestSerializer,
    BadgeCaptureSubmissionSerializer,
    BadgeOTPResponseSerializer,
)
from gchqnet.quest.api.serializers.badge import BadgeCaptureFailureSerializer, BadgeCaptureSuccessSerializer
from gchqnet.quest.repository.captures import record_attempted_capture


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

    @extend_schema(
        summary="Submit cryptographic proof of capture",
        exclude=settings.HIDE_PRIVATE_API_ENDPOINTS,
        request=BadgeCaptureSubmissionSerializer,
        responses={200: BadgeCaptureSuccessSerializer, 400: BadgeCaptureFailureSerializer},
        tags=["Badge Internal API"],
    )
    @action(methods=["POST"], detail=False)
    def capture(self, request: Request) -> Response:
        serializer = BadgeCaptureSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = check_badge_credentials(
            serializer.validated_data["mac_address"],
            serializer.validated_data["badge_secret"],
        )

        if result["result"] == "failure":
            raise exceptions.AuthenticationFailed()

        try:
            hex_uuid = UUID(int=serializer.validated_data["capture"]["sn"])
        except ValueError as e:
            raise exceptions.ValidationError(detail="Invalid serial number for capture") from e

        try:
            hexpansion = Hexpansion.objects.get(serial_number=hex_uuid)
        except Hexpansion.DoesNotExist as e:
            raise exceptions.ValidationError(detail="Unable to find that hexpansion") from e

        capture_result = record_attempted_capture(
            result["badge"],
            hexpansion,
            rand=serializer.validated_data["capture"]["rand"],
            hmac=serializer.validated_data["capture"]["hmac"],
            app_rev=serializer.validated_data["app-rev"],
            fw_rev=serializer.validated_data["fw-rev"],
            wifi_bssid=serializer.validated_data["wifi"]["bssid"],
            wifi_channel=serializer.validated_data["wifi"]["channel"],
            wifi_rssi=serializer.validated_data["wifi"]["rssi"],
        )

        if capture_result["result"] == "fail":
            return Response(capture_result, status=400)

        return Response(capture_result)
