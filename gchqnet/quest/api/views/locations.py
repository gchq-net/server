from __future__ import annotations

from typing import TYPE_CHECKING, Any

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from gchqnet.achievements.models import LocationGroup
from gchqnet.quest.api.serializers import (
    LocationGeoJSONSerializer,
    LocationSerializer,
)
from gchqnet.quest.models import CaptureEvent, LocationDifficulty
from gchqnet.quest.models.location import Location

if TYPE_CHECKING:  # pragma: nocover
    from django.db.models.query import QuerySet


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
        exclude=settings.HIDE_PRIVATE_API_ENDPOINTS,
        tags=["Locations"],
        responses={
            200: LocationGeoJSONSerializer,
        },
    )
    @action(url_path="my-finds", methods=["GET"], detail=False, permission_classes=[permissions.AllowAny])
    def geojson(self, request: Request) -> Response:
        if settings.GAME_MODE == "post":
            locations = Location.objects.all()
        else:
            if request.user.is_authenticated:
                locations = Location.objects.filter(capture_events__in=request.user.capture_events.values("id"))
            else:
                locations = Location.objects.none()

        if group_query := request.GET.get("group"):
            try:
                group = LocationGroup.objects.get(id=group_query)
                locations = locations.filter(groups=group)
            except LocationGroup.DoesNotExist:
                raise

        def _difficulty_label(location: Location) -> str:
            return LocationDifficulty(location.difficulty).label

        def _colour_for_difficulty(location: Location) -> str:
            lut = {
                LocationDifficulty.EASY.value: "#648FFF",
                LocationDifficulty.MEDIUM.value: "#785EF0",
                LocationDifficulty.HARD.value: "#DC267F",
                LocationDifficulty.INSANE.value: "#FE6100",
                LocationDifficulty.IMPOSSIBLE.value: "#1AFF1A",
            }
            return lut[location.difficulty]

        def _has_coords(location: Location) -> bool:
            try:
                _ = location.coordinates
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
                        "name": location.display_name,
                        "difficulty": _difficulty_label(location),
                        "colour": _colour_for_difficulty(location),
                    },
                    "geometry": {
                        "coordinates": [
                            location.coordinates.long,
                            location.coordinates.lat,
                        ],
                        "type": "Point",
                    },
                    "id": 0,
                }
                for idx, location in enumerate(locations)
                if _has_coords(location)
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
