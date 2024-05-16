from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse_lazy
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from gchqnet.accounts.totp import CustomTOTP

if TYPE_CHECKING:  # pragma: nocover
    from django.test import Client

    from gchqnet.accounts.models import User


@pytest.mark.django_db
class TestBadgeLoginLanding:
    url = reverse_lazy("accounts:login_badge")
    template_name = "pages/accounts/login_badge_landing.html"

    def test_get(self, client: Client) -> None:
        resp = client.get(self.url)
        assert resp.status_code == HTTPStatus.OK
        assertTemplateUsed(resp, self.template_name)

    def test_redirects_if_already_logged_in(self, client: Client, user: User) -> None:
        client.force_login(user)

        resp = client.get(self.url)

        assert resp.status_code == HTTPStatus.FOUND
        assertRedirects(resp, "/")


class TestBadgeLoginUsernamePromptView(TestBadgeLoginLanding):
    url = reverse_lazy("accounts:login_badge_username")
    template_name = "pages/accounts/login_badge_username.html"

    def test_post(self, client: Client, user: User) -> None:
        resp = client.post(self.url, data={"account_name": user.username})

        assert resp.status_code == HTTPStatus.FOUND
        assertRedirects(resp, reverse_lazy("accounts:login_badge_challenge"))
        assert client.session["badge_login__user_id"] == user.id

    def test_post_replace_existing_session(self, client: Client, user: User) -> None:
        client.session["badge_login__user_id"] = 1

        resp = client.post(self.url, data={"account_name": user.username})

        assert resp.status_code == HTTPStatus.FOUND
        assertRedirects(resp, reverse_lazy("accounts:login_badge_challenge"))
        assert client.session["badge_login__user_id"] == user.id

    def test_post_passes_next_get_param(self, client: Client, user: User) -> None:
        resp = client.post(self.url, data={"account_name": user.username}, QUERY_STRING="next=/bees/")

        assert resp.status_code == HTTPStatus.FOUND
        assertRedirects(resp, reverse_lazy("accounts:login_badge_challenge") + "?next=/bees/")
        assert client.session["badge_login__user_id"] == user.id

    def test_post_missing_username(self, client: Client) -> None:
        resp = client.post(self.url, data={"account_name": ""})

        assert resp.status_code == HTTPStatus.OK
        assert resp.context["form"].errors == {"account_name": ["This field is required."]}
        assert "badge_login__user_id" not in client.session

    def test_post_invalid_username(self, client: Client) -> None:
        resp = client.post(self.url, data={"account_name": "foo"})

        assert resp.status_code == HTTPStatus.OK
        assert resp.context["form"].errors == {
            "account_name": ["Unable to find your account name. Have you spelled it correctly?"]
        }
        assert "badge_login__user_id" not in client.session


@pytest.mark.django_db
class TestBadgeLoginChallengePromptView:
    url = reverse_lazy("accounts:login_badge_challenge")
    template_name = "pages/accounts/login_badge_challenge.html"

    def _setup_session(self, client: Client, user: User) -> None:
        session = client.session
        session["badge_login__user_id"] = user.id
        session.save()

    def test_get(self, client: Client, user: User) -> None:
        self._setup_session(client, user)

        # Act
        resp = client.get(self.url)

        # Assert
        assert resp.status_code == HTTPStatus.OK
        assertTemplateUsed(resp, self.template_name)

    def test_redirects_if_already_logged_in(self, client: Client, user: User) -> None:
        client.force_login(user)

        resp = client.get(self.url)
        assert resp.status_code == HTTPStatus.FOUND
        assertRedirects(resp, reverse_lazy("accounts:login_badge"), target_status_code=HTTPStatus.FOUND)

    def test_redirects_if_no_session(self, client: Client) -> None:
        resp = client.get(self.url)
        assert resp.status_code == HTTPStatus.FOUND
        assertRedirects(resp, reverse_lazy("accounts:login_badge"))

    def test_post(self, client: Client, user: User) -> None:
        # Arrange
        mac_address = "00-00-00-00-00-00"
        user.badges.create(mac_address=mac_address)
        self._setup_session(client, user)

        totp = CustomTOTP(mac_address)

        # Act
        resp = client.post(self.url, data={"security_code": totp.now()})
        assert resp.status_code == HTTPStatus.FOUND
        assertRedirects(resp, "/")
        assert client.session["_auth_user_id"] == str(user.id)

    def test_post_missing_code(self, client: Client, user: User) -> None:
        self._setup_session(client, user)
        resp = client.post(self.url)
        assert resp.status_code == HTTPStatus.OK
        assert resp.context["form"].errors == {"security_code": ["This field is required."]}

    def test_post_invalid_length_code(self, client: Client, user: User) -> None:
        self._setup_session(client, user)
        resp = client.post(self.url, data={"security_code": "1"})
        assert resp.status_code == HTTPStatus.OK
        assert resp.context["form"].errors == {
            "security_code": ["Ensure this value has at least 6 characters (it has 1)."]
        }

    def test_post_invalid_code(self, client: Client, user: User) -> None:
        self._setup_session(client, user)
        resp = client.post(self.url, data={"security_code": "000000"})
        assert resp.status_code == HTTPStatus.OK
        assert resp.context["form"].errors == {"security_code": ["That isn't the correct code."]}
