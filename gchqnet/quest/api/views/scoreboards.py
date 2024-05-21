from __future__ import annotations

from typing import TYPE_CHECKING, Any

from drf_spectacular.utils import extend_schema
from rest_framework import filters, permissions, serializers, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from gchqnet.accounts.models.user import UserQuerySet
from gchqnet.quest.api.serializers import (
    LeaderboardSerializer,
    LeaderboardWithScoresSerializer,
    ScoreboardEntrySerializer,
)
from gchqnet.quest.models import Leaderboard
from gchqnet.quest.repository import get_global_scoreboard

if TYPE_CHECKING:  # pragma: nocover
    from django.db.models.query import QuerySet


class GlobalScoreboardAPIView(ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ScoreboardEntrySerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["rank", "capture_count", "current_score", "display_name"]
    ordering = ["rank", "capture_count", "display_name"]

    def get_queryset(self) -> UserQuerySet:
        return get_global_scoreboard()

    @extend_schema(summary="Get the global scoreboard", tags=["Scoreboards"])
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Get the entries on the global scoreboard.

        By default, returns the users with the highest rank first.
        """
        return super().list(request, *args, **kwargs)


class PrivateScoreboardAPIViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["display_name", "created_at", "updated_at"]
    ordering = ["display_name"]

    def get_queryset(self) -> QuerySet[Leaderboard]:
        if self.request.user.is_authenticated:
            return self.request.user.leaderboards.all()
        else:
            return Leaderboard.objects.none()

    def get_serializer_class(self) -> type[serializers.ModelSerializer]:
        if self.action == "retrieve":
            return LeaderboardWithScoresSerializer
        elif self.action == "list":
            return LeaderboardSerializer
        raise RuntimeError("Unknown action.")

    @extend_schema(summary="List private scoreboards", tags=["Scoreboards"])
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Get a list of private scoreboards that you are a member of.

        By default, returns in order of display_name.
        """
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Get a private scoreboard", tags=["Scoreboards"])
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Get the details of a private scoreboard, including scores.

        Scores are returned in order of rank.
        """
        return super().retrieve(request, *args, **kwargs)
