from __future__ import annotations

from typing import TYPE_CHECKING, Any

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from drf_spectacular.utils import extend_schema
from rest_framework import filters, permissions, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from gchqnet.accounts.models.user import UserQuerySet
from gchqnet.quest.models import CaptureEvent, Leaderboard, LocationDifficulty
from gchqnet.quest.models.location import Location
from gchqnet.quest.repository import get_global_scoreboard

from .serializers import (
    LeaderboardSerializer,
    LeaderboardWithScoresSerializer,
    LocationGeoJSONSerializer,
    LocationSerializer,
    ScoreboardEntrySerializer,
)

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


VILLAGE_CACHE_KEY = "map__village__geodata"


class LocationViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LocationSerializer

    def get_queryset(self) -> QuerySet[Location]:
        assert self.request.user.is_authenticated
        return Location.objects.order_by("id").annotate(
            found_at=models.Subquery(
                CaptureEvent.objects.filter(location=models.OuterRef("id"), created_by=self.request.user).values(
                    "created_at"
                ),
            ),
        )

    def get_serializer_context(self) -> dict[str, Any]:
        assert self.request.user.is_authenticated
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    @extend_schema(summary="List locations", tags=["Locations"])
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Get a list of all locations.

        If the user has found the location, include the timestamp.
        """
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Get a location", tags=["Locations"])
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Get the details of a location.

        If the user has found the location, include the timestamp.
        """
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Get currently found locations as GeoJSON",
        tags=["Locations"],
        responses={
            200: LocationGeoJSONSerializer,
        },
    )
    @action(url_path="my-finds", methods=["GET"], detail=False)
    def geojson(self, request: Request) -> Response:
        assert request.user.is_authenticated

        captures = request.user.capture_events.select_related("location", "location__coordinates")

        def _difficulty_label(capture: CaptureEvent) -> str:
            return LocationDifficulty(capture.location.difficulty).label

        def _colour_for_difficulty(capture: CaptureEvent) -> str:
            lut = {
                LocationDifficulty.EASY.value: "#648FFF",
                LocationDifficulty.MEDIUM.value: "#785EF0",
                LocationDifficulty.HARD.value: "#DC267F",
                LocationDifficulty.INSANE.value: "#FE6100",
                LocationDifficulty.IMPOSSIBLE.value: "#1AFF1A",
            }
            return lut[capture.location.difficulty]

        def _has_coords(capture: CaptureEvent) -> bool:
            try:
                _ = capture.location.coordinates
                return True
            except ObjectDoesNotExist:
                return False

        data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "id": idx,
                        "name": capture.location.display_name,
                        "difficulty": _difficulty_label(capture),
                        "colour": _colour_for_difficulty(capture),
                    },
                    "geometry": {
                        "coordinates": [
                            capture.location.coordinates.long,
                            capture.location.coordinates.lat,
                        ],
                        "type": "Point",
                    },
                    "id": 0,
                }
                for idx, capture in enumerate(captures)
                if _has_coords(capture)
            ],
        }
        serializer = LocationGeoJSONSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, content_type="application/geo+json")

    @extend_schema(
        summary="Get villages as GeoJSON",
        tags=["Locations"],
        exclude=settings.HIDE_PRIVATE_API_ENDPOINTS,
        responses={
            200: LocationGeoJSONSerializer,
        },
    )
    @action(methods=["GET"], detail=False, permission_classes=[permissions.AllowAny])
    def villages(self, request: Request) -> Response:
        if not (village_data := cache.get(VILLAGE_CACHE_KEY)):
            resp = requests.get("https://www.emfcamp.org/api/villages.geojson", timeout=2)
            resp.raise_for_status()
            village_data = resp.json()
            cache.set(VILLAGE_CACHE_KEY, village_data, timeout=600)

        return Response(village_data, content_type="application/geo+json")
