from uuid import UUID

from django.conf import settings
from django.core.signing import BadSignature, Signer
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import exceptions, permissions, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from gchqnet.accounts.models.user import User
from gchqnet.achievements.models import BasicAchievement, BasicAchievementAwardType
from gchqnet.achievements.repository import award_builtin_basic_achievement

from .serializers import AchievementSubmissionSerializer


class AchievementViewset(viewsets.GenericViewSet):
    permission_classes = (permissions.AllowAny,)

    @extend_schema(
        summary="Submit an achievement gained on another server",
        exclude=settings.HIDE_PRIVATE_API_ENDPOINTS,
        request=AchievementSubmissionSerializer,
        responses={200: serializers.Serializer, 201: serializers.Serializer},
        tags=["Achievements"],
    )
    @action(methods=["POST"], detail=True)
    def submit(self, request: Request, pk: UUID) -> Response:
        serializer = AchievementSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        achievement = get_object_or_404(BasicAchievement, pk=pk)

        if achievement.award_type != BasicAchievementAwardType.EXTERNAL:
            raise exceptions.ValidationError(
                detail={"detail": ["That achievement cannot be awarded using this endpoint."]}
            )

        signer = Signer()

        try:
            obj = signer.unsign_object(serializer.validated_data["token"])
        except BadSignature:
            raise exceptions.AuthenticationFailed() from None

        if str(achievement.id) != obj["ba"]:
            raise exceptions.ValidationError(detail={"detail": ["That token isn't allowed to award that achievement"]})

        try:
            user = User.objects.get(username=serializer.validated_data["username"])
        except User.DoesNotExist:
            raise exceptions.ValidationError(detail={"detail": ["That user cannot be found."]}) from None

        result = award_builtin_basic_achievement(achievement.id, user)

        resp_code_lut = {"success": 201, "already_obtained": 200, "failure": 500}

        return Response(status=resp_code_lut[result])
