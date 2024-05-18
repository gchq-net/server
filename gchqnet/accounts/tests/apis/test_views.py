from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.test import Client
from django.urls import reverse

from gchqnet.quest.models.scores import UserScore

if TYPE_CHECKING:  # pragma: nocover
    from gchqnet.accounts.models import User


@pytest.mark.django_db
class TestGetCurrentUserAPIView:
    url = reverse("api:users_me")

    def test_get_unauthenticated(self, client: Client) -> None:
        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.FORBIDDEN
        assert resp.json() == {"detail": "Authentication credentials were not provided."}

    def test_get__no_score(self, client: Client, user: User) -> None:
        client.force_login(user)
        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.OK
        assert resp.json() == {"current_score": 0, "display_name": "foo", "username": "foo-username"}

    def test_get__has_score(self, client: Client, user: User) -> None:
        # Mock the user's current score
        UserScore.objects.create(user=user, current_score=103)

        client.force_login(user)
        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.OK
        assert resp.json() == {"current_score": 103, "display_name": "foo", "username": "foo-username"}
