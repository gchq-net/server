from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.test import Client
from django.urls import reverse

if TYPE_CHECKING:
    from gchqnet.accounts.models import User


@pytest.mark.django_db
class TestGetCurrentUserAPIView:
    url = reverse("api:users_me")

    def test_get_unauthenticated(self, client: Client) -> None:
        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.FORBIDDEN
        assert resp.json() == {"detail": "Authentication credentials were not provided."}

    def test_get(self, client: Client, user: User) -> None:
        client.force_login(user)
        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.OK
        assert resp.json() == {"display_name": "foo", "username": "foo-username"}
