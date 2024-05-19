from http import HTTPStatus
from uuid import UUID

import pytest
from django.contrib.messages import INFO, Message  # type: ignore[attr-defined]
from django.core.signing import Signer
from django.test import Client
from django.urls import reverse_lazy
from pytest_django.asserts import assertContains, assertMessages, assertRedirects, assertTemplateUsed

from gchqnet.accounts.factories import UserFactory
from gchqnet.accounts.models.user import User
from gchqnet.quest.factories import LeaderboardFactory


@pytest.mark.django_db
class TestLeaderboardListView:
    url = reverse_lazy("quest:leaderboard_list")

    def test_unauthenticated(self, client: Client) -> None:
        resp = client.get(self.url)
        assertRedirects(
            resp,
            f"/accounts/login/?next={self.url}",
            302,
            fetch_redirect_response=False,
        )

    def test_get_no_leaderboards(self, client: Client, user: User) -> None:
        # Arrange
        client.force_login(user)

        # Act
        resp = client.get(self.url)

        # Assert
        assert resp.status_code == HTTPStatus.OK
        assertTemplateUsed(resp, "pages/quest/leaderboard_list.html")
        assertContains(resp, "You aren't a member of any leaderboards.")

    def test_get_leaderboard_not_member(self, client: Client, user: User) -> None:
        # Arrange
        LeaderboardFactory()
        client.force_login(user)

        # Act
        resp = client.get(self.url)

        # Assert
        assert resp.status_code == HTTPStatus.OK
        assertTemplateUsed(resp, "pages/quest/leaderboard_list.html")
        assertContains(resp, "You aren't a member of any leaderboards.")

    def test_get_leaderboard_member(self, client: Client, user: User) -> None:
        # Arrange
        leaderboard = LeaderboardFactory(owner=user)
        leaderboard.members.add(user)
        client.force_login(user)

        # Act
        resp = client.get(self.url)

        # Assert
        assert resp.status_code == HTTPStatus.OK
        assertTemplateUsed(resp, "pages/quest/leaderboard_list.html")
        assertContains(resp, leaderboard.display_name)


@pytest.mark.django_db
class TestLeaderboardDetailView:
    def _url(self, leaderboard_id: UUID) -> str:
        return reverse_lazy("quest:leaderboard_detail", args=[leaderboard_id])

    def test_unauthenticated(self, client: Client) -> None:
        url = self._url(UUID(int=0))
        resp = client.get(url)
        assertRedirects(
            resp,
            f"/accounts/login/?next={url}",
            302,
            fetch_redirect_response=False,
        )

    def test_not_found(self, client: Client, user: User) -> None:
        # Arrange
        client.force_login(user)

        # Act
        resp = client.get(self._url(UUID(int=0)))

        # Assert
        assert resp.status_code == HTTPStatus.NOT_FOUND
        assertTemplateUsed(resp, "404.html")

    def test_get_leaderboard_not_member(self, client: Client, user: User) -> None:
        # Arrange
        leaderboard = LeaderboardFactory()
        client.force_login(user)

        # Act
        resp = client.get(self._url(leaderboard.id))

        # Assert
        assert resp.status_code == HTTPStatus.FORBIDDEN
        assertTemplateUsed(resp, "403.html")

    def test_get_leaderboard_member(self, client: Client, user: User) -> None:
        # Arrange
        leaderboard = LeaderboardFactory()
        leaderboard.members.add(user)
        client.force_login(user)

        # Act
        resp = client.get(self._url(leaderboard.id) + "?page=notanumber")

        # Assert
        assert resp.status_code == HTTPStatus.OK
        assertTemplateUsed(resp, "pages/quest/leaderboard_detail.html")
        assertContains(resp, f"Leaderboard: {leaderboard.display_name}")

        assert list(resp.context["page_obj"]) == [user]

    def test_get_leaderboard_owner(self, client: Client, user: User) -> None:
        # Arrange
        leaderboard = LeaderboardFactory(owner=user)
        other_user = UserFactory()
        leaderboard.members.add(user)
        leaderboard.members.add(other_user)
        client.force_login(user)

        # Act
        resp = client.get(self._url(leaderboard.id))

        # Assert
        assert resp.status_code == HTTPStatus.OK
        assertTemplateUsed(resp, "pages/quest/leaderboard_detail.html")
        assertContains(resp, f"Leaderboard: {leaderboard.display_name}")
        assertContains(resp, "Settings")

        assert set(resp.context["page_obj"]) == {user, other_user}


@pytest.mark.django_db
class TestLeaderboardDetailSettingsView:
    def _url(self, leaderboard_id: UUID) -> str:
        return reverse_lazy("quest:leaderboard_detail_settings", args=[leaderboard_id])

    def test_unauthenticated(self, client: Client) -> None:
        url = self._url(UUID(int=0))
        resp = client.get(url)
        assertRedirects(
            resp,
            f"/accounts/login/?next={url}",
            302,
            fetch_redirect_response=False,
        )

    def test_not_found(self, client: Client, user: User) -> None:
        # Arrange
        client.force_login(user)

        # Act
        resp = client.get(self._url(UUID(int=0)))

        # Assert
        assert resp.status_code == HTTPStatus.NOT_FOUND
        assertTemplateUsed(resp, "404.html")

    def test_get_leaderboard_not_member(self, client: Client, user: User) -> None:
        # Arrange
        leaderboard = LeaderboardFactory()
        client.force_login(user)

        # Act
        resp = client.get(self._url(leaderboard.id))

        # Assert
        assert resp.status_code == HTTPStatus.FORBIDDEN
        assertTemplateUsed(resp, "403.html")

    def test_get_leaderboard_member(self, client: Client, user: User) -> None:
        # Arrange
        leaderboard = LeaderboardFactory()
        leaderboard.members.add(user)
        client.force_login(user)

        # Act
        resp = client.get(self._url(leaderboard.id))

        # Assert
        assert resp.status_code == HTTPStatus.FORBIDDEN
        assertTemplateUsed(resp, "403.html")

    def test_get_leaderboard_owner(self, client: Client, user: User) -> None:
        # Arrange
        leaderboard = LeaderboardFactory(owner=user)
        leaderboard.members.add(user)
        client.force_login(user)

        # Act
        resp = client.get(self._url(leaderboard.id))

        # Assert
        assert resp.status_code == HTTPStatus.OK
        assertTemplateUsed(resp, "pages/quest/leaderboard_detail_settings.html")
        assert resp.context["invite_link"].startswith("http://testserver/leaderboards/invite/")

        invite_code = resp.context["invite_link"].split("http://testserver/leaderboards/invite/")[1].strip("/")
        signer = Signer()
        obj = signer.unsign_object(invite_code)
        assert obj["u"] == user.id
        assert obj["l"] == str(leaderboard.id)

        assert resp.context["form"].initial == {
            "display_name": leaderboard.display_name,
            "enable_invites": leaderboard.enable_invites,
        }

    def test_post(self, client: Client, user: User) -> None:
        # Arrange
        leaderboard = LeaderboardFactory(owner=user)
        leaderboard.members.add(user)
        client.force_login(user)

        # Act
        resp = client.post(self._url(leaderboard.id), data={"display_name": "foo", "enable_invites": False})

        # Assert
        assert resp.status_code == HTTPStatus.FOUND
        assertRedirects(resp, self._url(leaderboard.id))

        leaderboard.refresh_from_db()

        assert leaderboard.display_name == "foo"
        assert leaderboard.enable_invites is False


@pytest.mark.django_db
class TestLeaderboardCreateView:
    url = reverse_lazy("quest:leaderboard_create")

    def test_unauthenticated(self, client: Client) -> None:
        resp = client.get(self.url)
        assertRedirects(
            resp,
            f"/accounts/login/?next={self.url}",
            302,
            fetch_redirect_response=False,
        )

    def test_get(self, client: Client, user: User) -> None:
        # Arrange
        client.force_login(user)

        # Act
        resp = client.get(self.url)

        # Assert
        assert resp.status_code == HTTPStatus.OK
        assertTemplateUsed(resp, "pages/quest/leaderboard_create.html")

        assert resp.context["form"].initial == {}

    def test_post_no_data(self, client: Client, user: User) -> None:
        # Arrange
        client.force_login(user)

        # Act
        resp = client.post(self.url)

        # Assert
        assert resp.status_code == HTTPStatus.OK
        assertTemplateUsed(resp, "pages/quest/leaderboard_create.html")

        assert resp.context["form"].errors == {"display_name": ["This field is required."]}

    def test_post_too_long(self, client: Client, user: User) -> None:
        # Arrange
        client.force_login(user)

        # Act
        resp = client.post(self.url, data={"display_name": "a" * 41})

        # Assert
        assert resp.status_code == HTTPStatus.OK
        assertTemplateUsed(resp, "pages/quest/leaderboard_create.html")

        assert resp.context["form"].errors == {
            "display_name": ["Ensure this value has at most 40 characters (it has 41)."]
        }

    def test_post(self, client: Client, user: User) -> None:
        # Arrange
        client.force_login(user)

        # Act
        resp = client.post(self.url, data={"display_name": "foo"})

        # Assert
        assert resp.status_code == HTTPStatus.FOUND

        leaderboard = user.leaderboards_created.get()
        assertRedirects(resp, reverse_lazy("quest:leaderboard_detail", args=[leaderboard.id]))
        assertMessages(resp, [Message(INFO, "Welcome. Increase your social credit score by inviting other humans.")])

        assert leaderboard.display_name == "foo"
        assert leaderboard.owner == user
        assert list(leaderboard.members.all()) == [user]
        assert leaderboard.enable_invites is True
        assert leaderboard.created_by == user


@pytest.mark.django_db
class TestLeaderboardInviteDetailView:
    def _url(self, invite_code: str) -> str:
        return reverse_lazy("quest:leaderboard_invite", args=[invite_code])

    def _get_invite_code(self, inviter_id: int, leaderboard_id: UUID) -> str:
        signer = Signer()
        return signer.sign_object({"u": inviter_id, "l": str(leaderboard_id)})

    def test_unauthenticated(self, client: Client) -> None:
        url = self._url("bees")
        resp = client.get(url)
        assertRedirects(
            resp,
            f"/accounts/login/?next={url}",
            302,
            fetch_redirect_response=False,
        )

    def test_get_bad_invite(self, client: Client, user: User) -> None:
        # Arrange
        client.force_login(user)

        # Act
        resp = client.get(self._url("bees"))

        # Assert
        assert resp.status_code == HTTPStatus.FOUND
        assertRedirects(resp, reverse_lazy("quest:home"))
        assertMessages(resp, [Message(INFO, "Sorry, that invitation link is not valid.")])

    def test_get(self, client: Client, user: User) -> None:
        # Arrange
        leaderboard = LeaderboardFactory()
        invite_code = self._get_invite_code(leaderboard.owner.id, leaderboard.id)
        client.force_login(user)

        # Act
        resp = client.get(self._url(invite_code))

        # Assert
        assert resp.status_code == HTTPStatus.OK
        assertTemplateUsed(resp, "pages/quest/leaderboard_invite.html")
        assertContains(
            resp,
            f'You have been invited to the private leaderboard: "{leaderboard.display_name}" by {leaderboard.owner.display_name}.',  # noqa: E501
        )
        assert resp.context["form"].fields == {}

    def test_get_invite_disabled(self, client: Client, user: User) -> None:
        # Arrange
        leaderboard = LeaderboardFactory(enable_invites=False)
        invite_code = self._get_invite_code(leaderboard.owner.id, leaderboard.id)
        client.force_login(user)

        # Act
        resp = client.get(self._url(invite_code))

        # Assert
        assert resp.status_code == HTTPStatus.FOUND
        assertRedirects(resp, reverse_lazy("quest:home"))
        assertMessages(resp, [Message(INFO, "Sorry, that invitation link is no longer valid.")])

    def test_post_accept(self, client: Client, user: User) -> None:
        # Arrange
        leaderboard = LeaderboardFactory()
        invite_code = self._get_invite_code(leaderboard.owner.id, leaderboard.id)
        client.force_login(user)

        # Act
        resp = client.post(self._url(invite_code) + "?accept=true")

        # Assert
        assert resp.status_code == HTTPStatus.FOUND
        assertRedirects(resp, reverse_lazy("quest:leaderboard_detail", args=[leaderboard.id]))

        leaderboard.refresh_from_db()
        assert user in leaderboard.members.all()

    def test_post_accept_already_member(self, client: Client, user: User) -> None:
        # Arrange
        leaderboard = LeaderboardFactory()
        leaderboard.members.add(user)
        invite_code = self._get_invite_code(leaderboard.owner.id, leaderboard.id)
        client.force_login(user)

        # Act
        resp = client.post(self._url(invite_code) + "?accept=true")

        # Assert
        assert resp.status_code == HTTPStatus.FOUND
        assertRedirects(resp, reverse_lazy("quest:leaderboard_detail", args=[leaderboard.id]))
        assertMessages(resp, [Message(INFO, "You are already a member of this leaderboard.")])

    def test_post_accept_invite_disabled(self, client: Client, user: User) -> None:
        # Arrange
        leaderboard = LeaderboardFactory(enable_invites=False)
        invite_code = self._get_invite_code(leaderboard.owner.id, leaderboard.id)
        client.force_login(user)

        # Act
        resp = client.post(self._url(invite_code) + "?accept=true")

        # Assert
        assert resp.status_code == HTTPStatus.FOUND
        assertRedirects(resp, reverse_lazy("quest:home"))
        assertMessages(resp, [Message(INFO, "Sorry, that invitation link is no longer valid.")])

    def test_post_decline(self, client: Client, user: User) -> None:
        # Arrange
        leaderboard = LeaderboardFactory()
        invite_code = self._get_invite_code(leaderboard.owner.id, leaderboard.id)
        client.force_login(user)

        # Act
        resp = client.post(self._url(invite_code) + "?accept=false")

        # Assert
        assert resp.status_code == HTTPStatus.FOUND
        assertRedirects(resp, reverse_lazy("quest:home"))
        assertMessages(resp, [Message(INFO, "Invitation declined.")])

        leaderboard.refresh_from_db()
        assert user not in leaderboard.members.all()
