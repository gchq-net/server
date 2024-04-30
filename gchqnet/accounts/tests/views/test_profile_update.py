from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.contrib.messages import SUCCESS, Message  # type: ignore[attr-defined]
from django.urls import reverse_lazy
from pytest_django.asserts import assertMessages, assertRedirects, assertTemplateUsed

if TYPE_CHECKING:
    from django.test import Client

    from gchqnet.accounts.models import User


@pytest.mark.django_db
class TestProfileUpdateView:
    url = reverse_lazy("accounts:profile")

    def test_unauthenticated(self, client: Client) -> None:
        resp = client.get(self.url)
        assertRedirects(resp, "/accounts/login/?next=/accounts/profile", 302, fetch_redirect_response=False)

    def test_get(self, client: Client, user: User) -> None:
        # Arrange
        client.force_login(user)

        # Act
        resp = client.get(self.url)

        # Assert
        assert resp.status_code == HTTPStatus.OK
        assertTemplateUsed(resp, "pages/accounts/profile.html")

        form = resp.context["form"]
        assert form.fields.keys() == {"username", "display_name"}
        assert form.initial == {"username": user.username, "display_name": user.display_name}

    def test_post(self, client: Client, user: User) -> None:
        # Arrange
        client.force_login(user)

        # Act
        resp = client.post(self.url, data={"username": user.username, "display_name": "bees"})

        # Assert
        assertRedirects(resp, self.url, 302, 200)
        assertMessages(resp, [Message(SUCCESS, "Updated profile successfully.")])

        user.refresh_from_db()
        assert user.display_name == "bees"

    def test_post__cannot_change_username(self, client: Client, user: User) -> None:
        # Arrange
        client.force_login(user)

        # Act
        resp = client.post(self.url, data={"username": "bees", "display_name": "bees"})

        # Assert
        assertRedirects(resp, self.url, 302, 200)

        # We expect the username change to be silently ignored
        user.refresh_from_db()
        assert user.username == "foo"

    @pytest.mark.parametrize(
        ("display_name", "field_error"),
        [
            pytest.param("foo2", True, id="same-case"),
            pytest.param("FOO2", False, id="different-case"),
        ],
    )
    @pytest.mark.usefixtures("user_2")
    def test_post__duplicate_display_name(
        self, client: Client, user: User, *, display_name: str, field_error: bool
    ) -> None:
        # Arrange
        client.force_login(user)

        # Act
        resp = client.post(self.url, data={"username": "bees", "display_name": display_name})

        # Assert
        assert resp.status_code == 200
        assert resp.context["form"].errors["__all__"] == ["Another player already has that display name"]

        # Due to the behaviour of having a unique constraint on the table and on the column, we will
        # sometimes see two errors. This is fine.
        if field_error:
            assert resp.context["form"].errors["display_name"] == ["Another player already has that display name"]
