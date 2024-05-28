from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from gchqnet.logistics.models import PlannedLocation
from gchqnet.quest.api.serializers import (
    LocationGeoJSONSerializer,
)
from gchqnet.quest.models import LocationDifficulty
from gchqnet.quest.models.location import Location


class PlannedLocationViewset(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAdminUser,)

    @extend_schema(
        summary="Get planned locations as GeoJSON",
        exclude=settings.HIDE_PRIVATE_API_ENDPOINTS,
        tags=["Planned Locations"],
        responses={
            200: LocationGeoJSONSerializer,
        },
    )
    @action(methods=["GET"], detail=False)
    def geojson(self, request: Request) -> Response:
        assert request.user.is_authenticated

        planned_locations = PlannedLocation.objects.filter(is_installed=False)

        exclude_id = self.request.GET.get("exclude")
        planned_locations = planned_locations.exclude(id=exclude_id)

        def _difficulty_label(location: PlannedLocation) -> str:
            if not location.difficulty:
                return "Unknown"

            try:
                return LocationDifficulty(location.difficulty).label
            except ValueError:
                return "Unknown"

        def _colour_for_difficulty(location: PlannedLocation) -> str:
            if not location.difficulty:
                return "#FFFFFF"

            lut = {
                LocationDifficulty.EASY.value: "#648FFF",
                LocationDifficulty.MEDIUM.value: "#785EF0",
                LocationDifficulty.HARD.value: "#DC267F",
                LocationDifficulty.INSANE.value: "#FE6100",
                LocationDifficulty.IMPOSSIBLE.value: "#1AFF1A",
            }
            return lut.get(location.difficulty, "#FFFFFF")

        def _has_coords(location: PlannedLocation) -> bool:
            return bool(location.lat and location.long)

        data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "id": idx,
                        "name": location.internal_name,
                        "difficulty": _difficulty_label(location),
                        "colour": _colour_for_difficulty(location),
                    },
                    "geometry": {
                        "coordinates": [
                            location.long,
                            location.lat,
                        ],
                        "type": "Point",
                    },
                    "id": 0,
                }
                for idx, location in enumerate(planned_locations)
                if _has_coords(location)
            ],
        }
        serializer = LocationGeoJSONSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, content_type="application/geo+json")


class AllLocationViewset(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAdminUser,)

    @extend_schema(
        summary="Get all locations as GeoJSON",
        exclude=settings.HIDE_PRIVATE_API_ENDPOINTS,
        tags=["Locations"],
        responses={
            200: LocationGeoJSONSerializer,
        },
    )
    @action(methods=["GET"], detail=False)
    def geojson(self, request: Request) -> Response:
        assert request.user.is_authenticated

        locations = Location.objects.all()

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
