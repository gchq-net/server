from http import HTTPStatus
from uuid import UUID
from zoneinfo import ZoneInfo

import pytest
from django.test import Client
from django.urls import reverse_lazy

from gchqnet.accounts.models.user import User
from gchqnet.quest.factories import CoordinatesFactory, LocationFactory
from gchqnet.quest.models.location import LocationDifficulty
from gchqnet.quest.repository.captures import record_attempted_capture


@pytest.mark.django_db
class TestLocationListAPI:
    url = reverse_lazy("api:locations-list")

    def test_get_unauthenticated(self, client: Client) -> None:
        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.FORBIDDEN
        assert resp.json() == {"detail": "Authentication credentials were not provided."}

    def test_get_no_locations(self, client: Client, user: User) -> None:
        client.force_login(user)

        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.OK
        assert resp.json() == {"count": 0, "next": None, "previous": None, "results": []}

    def test_get_unfound_location(self, client: Client, user: User) -> None:
        location = LocationFactory(created_by=user)
        client.force_login(user)

        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.OK
        assert resp.json() == {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": str(location.id),
                    "display_name": "???",
                    "found_at": None,
                    "hint": location.hint,
                    "difficulty": location.difficulty.value,
                }
            ],
        }

    def test_get_found_location(self, client: Client, user: User) -> None:
        location = LocationFactory(created_by=user)
        record_attempted_capture(user.badges.get(), location.hexpansion)
        client.force_login(user)

        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.OK
        assert resp.json() == {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": str(location.id),
                    "display_name": location.display_name,
                    "found_at": location.capture_events.get()
                    .created_at.astimezone(ZoneInfo("Europe/London"))
                    .isoformat(),
                    "hint": location.hint,
                    "difficulty": location.difficulty.value,
                }
            ],
        }

    def test_get_paginated_locations(self, client: Client, user: User) -> None:
        LocationFactory.create_batch(size=21, created_by=user)
        client.force_login(user)

        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.OK
        data = resp.json()

        assert data["count"] == 21
        assert data["next"] == "http://testserver/api/locations/?limit=20&offset=20"
        assert len(data["results"]) == 20

        # Check sorted by ID, we do not want to reveal info about the display names
        results_ids = [e["id"] for e in data["results"]]
        assert results_ids == sorted(results_ids)


@pytest.mark.django_db
class TestLocationDetailAPI:
    def _url(self, location_id: str) -> str:
        return reverse_lazy("api:locations-detail", args=[location_id])

    def test_get_unauthenticated(self, client: Client, user: User) -> None:
        location = LocationFactory(created_by=user)
        resp = client.get(self._url(location.id))

        assert resp.status_code == HTTPStatus.FORBIDDEN
        assert resp.json() == {"detail": "Authentication credentials were not provided."}

    def test_get_not_found(self, client: Client, user: User) -> None:
        client.force_login(user)

        resp = client.get(self._url(UUID(int=0)))

        assert resp.status_code == HTTPStatus.NOT_FOUND
        assert resp.json() == {"detail": "No Location matches the given query."}

    def test_get_unfound_location(self, client: Client, user: User) -> None:
        location = LocationFactory(created_by=user)
        client.force_login(user)

        resp = client.get(self._url(location.id))

        assert resp.status_code == HTTPStatus.OK
        assert resp.json() == {
            "id": str(location.id),
            "display_name": "???",
            "found_at": None,
            "hint": location.hint,
            "difficulty": location.difficulty.value,
        }

    def test_get_found_location(self, client: Client, user: User) -> None:
        location = LocationFactory(created_by=user)
        record_attempted_capture(user.badges.get(), location.hexpansion)
        client.force_login(user)

        resp = client.get(self._url(location.id))

        assert resp.status_code == HTTPStatus.OK
        assert resp.json() == {
            "id": str(location.id),
            "display_name": location.display_name,
            "found_at": location.capture_events.get().created_at.astimezone(ZoneInfo("Europe/London")).isoformat(),
            "hint": location.hint,
            "difficulty": location.difficulty.value,
        }


@pytest.mark.django_db
class TestLocationGeoJSONAPI:
    url = reverse_lazy("api:locations-geojson")

    def test_get_unauthenticated(self, client: Client) -> None:
        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.FORBIDDEN
        assert resp.json() == {"detail": "Authentication credentials were not provided."}

    def test_get_no_locations(self, client: Client, user: User) -> None:
        client.force_login(user)

        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.OK
        assert resp.json() == {"features": [], "type": "FeatureCollection"}

    def test_get_unfound_location(self, client: Client, user: User) -> None:
        LocationFactory(created_by=user)
        client.force_login(user)

        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.OK
        assert resp.json() == {"features": [], "type": "FeatureCollection"}

    def test_get_found_location_no_coords(self, client: Client, user: User) -> None:
        location = LocationFactory(created_by=user, coordinates=None)
        record_attempted_capture(user.badges.get(), location.hexpansion)
        client.force_login(user)

        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.OK
        assert resp.json() == {"features": [], "type": "FeatureCollection"}

    def test_get_found_location(self, client: Client, user: User) -> None:
        location = LocationFactory(created_by=user, coordinates=None)
        CoordinatesFactory(lat=52, long=2, created_by=user, location=location)
        record_attempted_capture(user.badges.get(), location.hexpansion)
        client.force_login(user)

        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.OK
        difficulty = LocationDifficulty(location.difficulty).label
        assert resp.json() == {
            "type": "FeatureCollection",
            "features": [
                {
                    "geometry": {
                        "coordinates": ["2.0000000000000", "52.0000000000000"],
                        "type": "Point",
                    },
                    "id": 0,
                    "properties": {"id": 0, "name": f"{location.display_name} ({difficulty})"},
                    "type": "Feature",
                }
            ],
        }
