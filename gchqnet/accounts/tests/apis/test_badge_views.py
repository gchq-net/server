from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse_lazy

from gchqnet.accounts.models.badge import Badge
from gchqnet.accounts.models.user import User


@pytest.mark.django_db
class TestBadgeGetCurrentPlayerView:
    url = reverse_lazy("api:badge_get_current_player")

    def test_get(self, client: Client) -> None:
        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED
        assert resp.json() == {"detail": 'Method "GET" not allowed.'}

    def test_post__no_data(self, client: Client) -> None:
        resp = client.post(self.url)

        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {
            "badge_secret": ["This field is required."],
            "mac_address": ["This field is required."],
        }

    def test_post__no_mac_address(self, client: Client) -> None:
        resp = client.post(self.url, data={"badge_secret": "a" * 64}, content_type="application/json")

        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {
            "mac_address": ["This field is required."],
        }

    def test_post__bad_mac_address(self, client: Client) -> None:
        resp = client.post(
            self.url, data={"mac_address": "AA-AA-AA-AA-AA-", "badge_secret": "a" * 64}, content_type="application/json"
        )

        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {
            "mac_address": [
                "The MAC address does not appear to be in the correct format.",
                "Ensure this field has at least 17 characters.",
            ],
        }

    def test_post__no_token(self, client: Client) -> None:
        resp = client.post(self.url, data={"mac_address": "AA-AA-AA-AA-AA-AA"}, content_type="application/json")
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {
            "badge_secret": ["This field is required."],
        }

    def test_post__bad_token_too_short(self, client: Client) -> None:
        resp = client.post(
            self.url, data={"mac_address": "AA-AA-AA-AA-AA-AA", "badge_secret": "a"}, content_type="application/json"
        )
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {
            "badge_secret": [
                "The badge secret does not appear to be in the correct format.",
                "Ensure this field has at least 64 characters.",
            ],
        }

    def test_post__bad_token_too_long(self, client: Client) -> None:
        resp = client.post(
            self.url,
            data={"mac_address": "AA-AA-AA-AA-AA-AA", "badge_secret": "a" * 65},
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {
            "badge_secret": [
                "The badge secret does not appear to be in the correct format.",
                "Ensure this field has no more than 64 characters.",
            ],
        }

    def test_post__new_badge_registration(self, client: Client) -> None:
        resp = client.post(
            self.url,
            data={"mac_address": "AA-AA-AA-AA-AA-AA", "badge_secret": "a" * 64},
            content_type="application/json",
        )

        assert resp.status_code == HTTPStatus.CREATED

        new_badge = Badge.objects.get(mac_address="AA-AA-AA-AA-AA-AA")
        user = new_badge.user

        assert resp.json() == {
            "display_name": user.display_name,
            "username": user.username,
            "current_score": 0,
        }

    def test_post__existing_badge__good_token(self, client: Client, user: User) -> None:
        badge = user.badges.get()

        resp = client.post(
            self.url,
            data={"mac_address": badge.mac_address, "badge_secret": badge.secret},
            content_type="application/json",
        )

        assert resp.status_code == HTTPStatus.OK

        assert resp.json() == {
            "display_name": user.display_name,
            "username": user.username,
            "current_score": 0,
        }

    def test_post__existing_badge__bad_token(self, client: Client, user: User) -> None:
        badge = user.badges.get()

        resp = client.post(
            self.url,
            data={"mac_address": badge.mac_address, "badge_secret": "e" * 64},
            content_type="application/json",
        )

        assert resp.status_code == HTTPStatus.FORBIDDEN

        assert resp.json() == {"detail": "Incorrect authentication credentials."}

    def test_post__existing_badge__blank_token(self, client: Client, user: User) -> None:
        badge = user.badges.get()
        badge.secret = ""
        badge.save()

        resp = client.post(
            self.url,
            data={"mac_address": badge.mac_address, "badge_secret": "a" * 64},
            content_type="application/json",
        )

        assert resp.status_code == HTTPStatus.OK

        assert resp.json() == {
            "display_name": user.display_name,
            "username": user.username,
            "current_score": 0,
        }

        badge.refresh_from_db()
        assert badge.secret == "a" * 64
