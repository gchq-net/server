from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

from gchqnet.accounts.models.user import User


@pytest.mark.django_db
class TestPlannedLocationsGeoJSONAPI:
    url = reverse("api:planned_locations-geojson")

    def test_get_unauthenticated(self, client: Client) -> None:
        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.FORBIDDEN
        assert resp.json() == {"detail": "Authentication credentials were not provided."}

    def test_get_standard_user(self, client: Client, user: User) -> None:
        client.force_login(user)
        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.FORBIDDEN
        assert resp.json() == {"detail": "You do not have permission to perform this action."}

    def test_get_superuser(self, client: Client, superuser: User) -> None:
        client.force_login(superuser)
        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.OK
        assert resp.json() == {"features": [], "type": "FeatureCollection"}
