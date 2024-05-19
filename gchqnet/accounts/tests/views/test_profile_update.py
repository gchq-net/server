from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.contrib.messages import SUCCESS, Message  # type: ignore[attr-defined]
from django.urls import reverse_lazy
from pytest_django.asserts import assertMessages, assertRedirects, assertTemplateUsed

from gchqnet.accounts.totp import CustomTOTP

if TYPE_CHECKING:  # pragma: nocover
    from django.test import Client

    from gchqnet.accounts.models import User


@pytest.mark.django_db
class TestAccountSettingsView:
    url = reverse_lazy("accounts:settings")

    def test_unauthenticated(self, client: Client) -> None:
        resp = client.get(self.url)
        assertRedirects(
            resp,
            "/accounts/login/?next=/profile/settings/",
            302,
            fetch_redirect_response=False,
        )

    def test_get__security_code(self, client: Client, user: User) -> None:
        # Arrange
        client.force_login(user)

        # Act
        resp = client.get(self.url)

        # Assert
        assert resp.status_code == HTTPStatus.OK
        assertTemplateUsed(resp, "pages/accounts/settings.html")

        form = resp.context["form"]
        assert form.fields.keys() == {
            "username",
            "display_name",
            "security_code",
            "new_password1",
            "new_password2",
        }
        assert form.initial == {
            "username": user.username,
            "display_name": user.display_name,
        }

    def test_get__password(self, client: Client, user: User) -> None:
        # Arrange
        user.set_password("foo")
        user.save()
        client.force_login(user)

        # Act
        resp = client.get(self.url)

        # Assert
        assert resp.status_code == HTTPStatus.OK
        assertTemplateUsed(resp, "pages/accounts/settings.html")

        form = resp.context["form"]
        assert form.fields.keys() == {
            "username",
            "display_name",
            "current_password",
            "new_password1",
            "new_password2",
        }
        assert form.initial == {
            "username": user.username,
            "display_name": user.display_name,
        }

    @pytest.mark.parametrize(
        ("input_display_name", "saved_display_name"),
        [
            pytest.param("bees", "bees", id="unrelated"),
            pytest.param("foo-username", "foo-username", id="username"),
            pytest.param("  whitespace  ", "whitespace", id="whitespace-is-stripped"),
        ],
    )
    def test_post(
        self,
        client: Client,
        user: User,
        *,
        input_display_name: str,
        saved_display_name: str,
    ) -> None:
        # Arrange
        client.force_login(user)

        # Act
        resp = client.post(
            self.url,
            data={
                "username": user.username,
                "display_name": input_display_name,
            },
        )

        # Assert
        assertRedirects(resp, self.url)
        assertMessages(resp, [Message(SUCCESS, "Updated account successfully.")])

        user.refresh_from_db()
        assert user.display_name == saved_display_name

    def test_post__cannot_change_username(self, client: Client, user: User) -> None:
        # Arrange
        client.force_login(user)

        # Act
        resp = client.post(self.url, data={"username": "bees", "display_name": "bees"})

        # Assert
        assertRedirects(resp, self.url, 302, 200)

        # We expect the username change to be silently ignored
        user.refresh_from_db()
        assert user.username == "foo-username"

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

    @pytest.mark.parametrize(
        ("display_name", "field_error"),
        [
            pytest.param("foo2-username", True, id="same-case"),
            pytest.param("FOO2-username", False, id="different-case"),
        ],
    )
    @pytest.mark.usefixtures("user_2")
    def test_post__cannot_use_other_users_account_name(
        self, client: Client, user: User, *, display_name: str, field_error: bool
    ) -> None:
        # Arrange
        client.force_login(user)

        # Act
        resp = client.post(self.url, data={"username": "bees", "display_name": display_name})

        # Assert
        assert resp.status_code == 200
        assert resp.context["form"].errors["display_name"] == ["That name is not available, sorry."]

    def test_post__change_password__security_code_invalid(
        self,
        client: Client,
        user: User,
    ) -> None:
        # Arrange
        client.force_login(user)

        # Act
        resp = client.post(
            self.url,
            data={
                "username": user.username,
                "display_name": user.display_name,
                "security_code": "000000",
                "new_password1": "beeeeees",
                "new_password2": "beeeeees",
            },
        )

        # Assert
        assert resp.status_code == HTTPStatus.OK
        assert resp.context["form"].errors == {"security_code": ["That isn't the correct code."]}

    def test_post__change_password__security_code_valid(
        self,
        client: Client,
        user: User,
    ) -> None:
        # Arrange
        client.force_login(user)

        # Act
        resp = client.post(
            self.url,
            data={
                "username": user.username,
                "display_name": user.display_name,
                "security_code": CustomTOTP(user.badges.get().mac_address).now(),
                "new_password1": "beeeeees",
                "new_password2": "beeeeees",
            },
        )

        # Assert
        assertRedirects(resp, self.url)
        assertMessages(resp, [Message(SUCCESS, "Your password has been changed.")])

        user.refresh_from_db()
        assert user.check_password("beeeeees")

    def test_post__change_password__security_code_new_dont_match(
        self,
        client: Client,
        user: User,
    ) -> None:
        # Arrange
        client.force_login(user)

        # Act
        resp = client.post(
            self.url,
            data={
                "username": user.username,
                "display_name": user.display_name,
                "security_code": CustomTOTP(user.badges.get().mac_address).now(),
                "new_password1": "beeeeees",
                "new_password2": "beeeeees2",
            },
        )

        # Assert
        assert resp.status_code == 200
        assert resp.context["form"].errors == {"new_password2": ["The new passwords do not match."]}

    def test_post__change_password__password_invalid(
        self,
        client: Client,
        user: User,
    ) -> None:
        # Arrange
        user.set_password("bees")
        user.save()
        client.force_login(user)

        # Act
        resp = client.post(
            self.url,
            data={
                "username": user.username,
                "display_name": user.display_name,
                "current_password": "wasps",
                "new_password1": "beeeeees",
                "new_password2": "beeeeees",
            },
        )

        # Assert
        assert resp.status_code == HTTPStatus.OK
        assert resp.context["form"].errors == {"current_password": ["That password is incorrect."]}

    def test_post__change_password__password_valid(
        self,
        client: Client,
        user: User,
    ) -> None:
        # Arrange
        user.set_password("bees")
        user.save()
        client.force_login(user)

        # Act
        resp = client.post(
            self.url,
            data={
                "username": user.username,
                "display_name": user.display_name,
                "current_password": "bees",
                "new_password1": "beeeeees",
                "new_password2": "beeeeees",
            },
        )

        # Assert
        assertRedirects(resp, self.url)
        assertMessages(resp, [Message(SUCCESS, "Your password has been changed.")])

        user.refresh_from_db()
        assert user.check_password("beeeeees")

    def test_post__change_password__password_new_dont_match(
        self,
        client: Client,
        user: User,
    ) -> None:
        # Arrange
        user.set_password("bees")
        user.save()
        client.force_login(user)

        # Act
        resp = client.post(
            self.url,
            data={
                "username": user.username,
                "display_name": user.display_name,
                "current_password": "bees",
                "new_password1": "beeeeees",
                "new_password2": "beeeeees2",
            },
        )

        # Assert
        assert resp.status_code == 200
        assert resp.context["form"].errors == {"new_password2": ["The new passwords do not match."]}
