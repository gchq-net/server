from http import HTTPStatus

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse_lazy

from gchqnet.accounts.models.badge import Badge
from gchqnet.accounts.models.user import User
from gchqnet.accounts.totp import CustomTOTP
from gchqnet.hexpansion.crypto import badge_response_calculation
from gchqnet.quest.factories import LocationFactory
from gchqnet.quest.models.location import LocationDifficulty


class BadgeAuthTestMixin:
    url: str

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

    def test_post__existing_badge__bad_token(self, client: Client, user: User) -> None:
        badge = user.badges.get()

        resp = client.post(
            self.url,
            data={"mac_address": badge.mac_address, "badge_secret": "e" * 64},
            content_type="application/json",
        )

        assert resp.status_code == HTTPStatus.FORBIDDEN

        assert resp.json() == {"detail": "Incorrect authentication credentials."}


@pytest.mark.django_db
class TestBadgeGetCurrentPlayerView(BadgeAuthTestMixin):
    url = reverse_lazy("api:badge-player")

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


@pytest.mark.django_db
class TestBadgeGetCurrentOTPView(BadgeAuthTestMixin):
    url = reverse_lazy("api:badge-otp")

    def test_post__new_badge_registration(self, client: Client) -> None:
        resp = client.post(
            self.url,
            data={"mac_address": "AA-AA-AA-AA-AA-AA", "badge_secret": "a" * 64},
            content_type="application/json",
        )

        assert resp.status_code == HTTPStatus.OK

        new_badge = Badge.objects.get(mac_address="AA-AA-AA-AA-AA-AA")
        user = new_badge.user

        totp = CustomTOTP(new_badge.mac_address).now()

        assert resp.json() == {
            "username": user.username,
            "otp": totp,
        }

    def test_post__existing_badge__good_token(self, client: Client, user: User) -> None:
        badge = user.badges.get()

        resp = client.post(
            self.url,
            data={"mac_address": badge.mac_address, "badge_secret": badge.secret},
            content_type="application/json",
        )

        assert resp.status_code == HTTPStatus.OK

        totp = CustomTOTP(badge.mac_address).now()

        assert resp.json() == {
            "username": user.username,
            "otp": totp,
        }

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

        totp = CustomTOTP(badge.mac_address).now()

        assert resp.json() == {
            "username": user.username,
            "otp": totp,
        }

        badge.refresh_from_db()
        assert badge.secret == "a" * 64


@pytest.mark.django_db
class TestBadgeCaptureSubmissionView:
    url = reverse_lazy("api:badge-capture")

    def _hmac_for_hexpansion(self, badge_mac: str, hexpansion_sn: int, rand: bytes) -> str:
        hmac_bytes = badge_response_calculation(
            hexpansion_sn.to_bytes(9, "little"),
            rand,
            badge_mac,
            settings.HEXPANSION_ROOT_KEY,
        )
        return "".join(f"{x:02x}" for x in hmac_bytes)

    def test_get(self, client: Client) -> None:
        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED
        assert resp.json() == {"detail": 'Method "GET" not allowed.'}

    def test_post__no_data(self, client: Client) -> None:
        resp = client.post(self.url)

        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {
            "mac_address": ["This field is required."],
            "badge_secret": ["This field is required."],
            "capture": ["This field is required."],
            "app_rev": ["This field is required."],
            "fw_rev": ["This field is required."],
        }

    def test_post__no_mac_address(self, client: Client) -> None:
        resp = client.post(
            self.url,
            data={
                "badge_secret": "a" * 64,
                "capture": {
                    "sn": 1234567890,
                    "rand": "a" * 64,
                    "hmac": "b" * 64,
                },
                "app_rev": "0",
                "fw_rev": "bees",
            },
            content_type="application/json",
        )

        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {
            "mac_address": ["This field is required."],
        }

    def test_post__capture_not_dict(self, client: Client) -> None:
        resp = client.post(
            self.url,
            data={
                "mac_address": "AA-AA-AA-AA-AA-AA",
                "badge_secret": "a" * 64,
                "capture": 12,
                "app_rev": "0",
                "fw_rev": "bees",
            },
            content_type="application/json",
        )

        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {
            "capture": {"non_field_errors": ["Invalid data. Expected a dictionary, but " "got int."]}
        }

    def test_post__bad_mac_address(self, client: Client) -> None:
        resp = client.post(
            self.url,
            data={
                "mac_address": "AA-AA-AA-AA-AA-",
                "badge_secret": "a" * 64,
                "capture": {
                    "sn": 1234567890,
                    "rand": "a" * 64,
                    "hmac": "b" * 64,
                },
                "app_rev": "0",
                "fw_rev": "bees",
            },
            content_type="application/json",
        )

        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {
            "mac_address": [
                "The MAC address does not appear to be in the correct format.",
                "Ensure this field has at least 17 characters.",
            ],
        }

    def test_post__no_token(self, client: Client) -> None:
        resp = client.post(
            self.url,
            data={
                "mac_address": "AA-AA-AA-AA-AA-AA",
                "capture": {
                    "sn": 1234567890,
                    "rand": "a" * 64,
                    "hmac": "b" * 64,
                },
                "app_rev": "0",
                "fw_rev": "bees",
            },
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {
            "badge_secret": ["This field is required."],
        }

    def test_post__bad_token_too_short(self, client: Client) -> None:
        resp = client.post(
            self.url,
            data={
                "mac_address": "AA-AA-AA-AA-AA-AA",
                "badge_secret": "a",
                "capture": {
                    "sn": 1234567890,
                    "rand": "a" * 64,
                    "hmac": "b" * 64,
                },
                "app_rev": "0",
                "fw_rev": "bees",
            },
            content_type="application/json",
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
            data={
                "mac_address": "AA-AA-AA-AA-AA-AA",
                "badge_secret": "a" * 65,
                "capture": {
                    "sn": 1234567890,
                    "rand": "a" * 64,
                    "hmac": "b" * 64,
                },
                "app_rev": "0",
                "fw_rev": "bees",
            },
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {
            "badge_secret": [
                "The badge secret does not appear to be in the correct format.",
                "Ensure this field has no more than 64 characters.",
            ],
        }

    def test_post__existing_badge__bad_token(self, client: Client, user: User) -> None:
        badge = user.badges.get()

        resp = client.post(
            self.url,
            data={
                "mac_address": badge.mac_address,
                "badge_secret": "e" * 64,
                "capture": {
                    "sn": 1234567890,
                    "rand": "a" * 64,
                    "hmac": "b" * 64,
                },
                "app_rev": "0",
                "fw_rev": "bees",
            },
            content_type="application/json",
        )

        assert resp.status_code == HTTPStatus.FORBIDDEN

        assert resp.json() == {"detail": "Incorrect authentication credentials."}

    def test_post__new_badge_registration(self, client: Client, user_2: User) -> None:
        location = LocationFactory(created_by=user_2)
        resp = client.post(
            self.url,
            data={
                "mac_address": "AA-AA-AA-AA-AA-AA",
                "badge_secret": "a" * 64,
                "capture": {
                    "sn": location.hexpansion.serial_number.int,
                    "rand": "a" * 64,
                    "hmac": self._hmac_for_hexpansion(
                        "AA-AA-AA-AA-AA-AA",
                        location.hexpansion.serial_number.int,
                        b"\xaa" * 32,
                    ),
                },
                "app_rev": "0",
                "fw_rev": "bees",
            },
            content_type="application/json",
        )

        assert resp.status_code == HTTPStatus.OK

        assert resp.json() == {
            "result": "success",
            "repeat": False,
            "location_name": location.display_name,
            "difficulty": LocationDifficulty(location.difficulty).label,
        }

    def test_post__existing_badge__good_token(self, client: Client, user: User, user_2: User) -> None:
        location = LocationFactory(created_by=user_2)
        badge = user.badges.get()

        resp = client.post(
            self.url,
            data={
                "mac_address": badge.mac_address,
                "badge_secret": badge.secret,
                "capture": {
                    "sn": location.hexpansion.serial_number.int,
                    "rand": "a" * 64,
                    "hmac": self._hmac_for_hexpansion(
                        badge.mac_address,
                        location.hexpansion.serial_number.int,
                        b"\xaa" * 32,
                    ),
                },
                "app_rev": "0",
                "fw_rev": "bees",
            },
            content_type="application/json",
        )

        assert resp.status_code == HTTPStatus.OK

        assert resp.json() == {
            "result": "success",
            "repeat": False,
            "location_name": location.display_name,
            "difficulty": LocationDifficulty(location.difficulty).label,
        }

    def test_post__existing_badge__blank_token(self, client: Client, user: User, user_2: User) -> None:
        location = LocationFactory(created_by=user_2)

        badge = user.badges.get()
        badge.secret = ""
        badge.save()

        resp = client.post(
            self.url,
            data={
                "mac_address": badge.mac_address,
                "badge_secret": "a" * 64,
                "capture": {
                    "sn": location.hexpansion.serial_number.int,
                    "rand": "a" * 64,
                    "hmac": self._hmac_for_hexpansion(
                        badge.mac_address,
                        location.hexpansion.serial_number.int,
                        b"\xaa" * 32,
                    ),
                },
                "app_rev": "0",
                "fw_rev": "bees",
            },
            content_type="application/json",
        )

        assert resp.status_code == HTTPStatus.OK

        assert resp.json() == {
            "result": "success",
            "repeat": False,
            "location_name": location.display_name,
            "difficulty": LocationDifficulty(location.difficulty).label,
        }

        badge.refresh_from_db()
        assert badge.secret == "a" * 64

    def test_post__existing_badge__bad_hmac(self, client: Client, user: User, user_2: User) -> None:
        location = LocationFactory(created_by=user_2)
        badge = user.badges.get()

        resp = client.post(
            self.url,
            data={
                "mac_address": badge.mac_address,
                "badge_secret": badge.secret,
                "capture": {
                    "sn": location.hexpansion.serial_number.int,
                    "rand": "a" * 64,
                    "hmac": "b" * 64,
                },
                "app_rev": "0",
                "fw_rev": "bees",
            },
            content_type="application/json",
        )

        assert resp.status_code == HTTPStatus.BAD_REQUEST

        assert resp.json() == {"result": "fail", "message": "Invalid HMAC - Contact Support"}

    def test_post__repeat(self, client: Client, user: User, user_2: User) -> None:
        location = LocationFactory(created_by=user_2)
        badge = user.badges.get()

        resp = client.post(
            self.url,
            data={
                "mac_address": badge.mac_address,
                "badge_secret": badge.secret,
                "capture": {
                    "sn": location.hexpansion.serial_number.int,
                    "rand": "a" * 64,
                    "hmac": self._hmac_for_hexpansion(
                        badge.mac_address,
                        location.hexpansion.serial_number.int,
                        b"\xaa" * 32,
                    ),
                },
                "app_rev": "0",
                "fw_rev": "bees",
            },
            content_type="application/json",
        )

        assert resp.status_code == HTTPStatus.OK

        resp = client.post(
            self.url,
            data={
                "mac_address": badge.mac_address,
                "badge_secret": badge.secret,
                "capture": {
                    "sn": location.hexpansion.serial_number.int,
                    "rand": "a" * 64,
                    "hmac": self._hmac_for_hexpansion(
                        badge.mac_address,
                        location.hexpansion.serial_number.int,
                        b"\xaa" * 32,
                    ),
                },
                "app_rev": "0",
                "fw_rev": "bees",
            },
            content_type="application/json",
        )

        assert resp.status_code == HTTPStatus.OK

        assert resp.json() == {
            "result": "success",
            "repeat": True,
            "location_name": location.display_name,
            "difficulty": LocationDifficulty(location.difficulty).label,
        }

    def test_post__unknown_hexpansion(self, client: Client, user: User, user_2: User) -> None:
        badge = user.badges.get()

        resp = client.post(
            self.url,
            data={
                "mac_address": badge.mac_address,
                "badge_secret": badge.secret,
                "capture": {
                    "sn": 123,
                    "rand": "a" * 64,
                    "hmac": "b" * 64,
                },
                "app_rev": "0",
                "fw_rev": "bees",
            },
            content_type="application/json",
        )

        assert resp.status_code == HTTPStatus.BAD_REQUEST

        assert resp.json() == {"detail": ["Unable to find that hexpansion"]}
