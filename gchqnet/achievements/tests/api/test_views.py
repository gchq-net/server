from http import HTTPStatus
from uuid import UUID

import pytest
from django.core.signing import Signer
from django.test import Client
from django.urls import reverse

from gchqnet.accounts.models.user import User
from gchqnet.achievements.models import BasicAchievement
from gchqnet.achievements.repository import award_builtin_basic_achievement


@pytest.mark.django_db
class TestAchievementSubmitAPI:
    def _url(self, achievement_id: UUID | str) -> str:
        return reverse("api:achievements-submit", args=[achievement_id])

    def _sign_token(self, achievement_id: UUID | str) -> str:
        signer = Signer()
        obj = {
            "ba": str(achievement_id),
            "s": 1,
            "u": 1,
        }
        return signer.sign_object(obj)

    def test_get(self, client: Client, external_achievement: BasicAchievement) -> None:
        resp = client.get(self._url(external_achievement.id))
        assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED
        assert resp.json() == {"detail": 'Method "GET" not allowed.'}

    def test_post__404(self, client: Client) -> None:
        resp = client.post(self._url(UUID(int=0)), data={"username": "foo", "token": "bar"})
        assert resp.status_code == HTTPStatus.NOT_FOUND
        assert resp.json() == {"detail": "No BasicAchievement matches the given query."}

    def test_post__missing_username(self, client: Client, external_achievement: BasicAchievement) -> None:
        resp = client.post(self._url(external_achievement.id), data={"token": "bar"})
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {"username": ["This field is required."]}

    def test_post__missing_token(self, client: Client, external_achievement: BasicAchievement) -> None:
        resp = client.post(self._url(external_achievement.id), data={"username": "foo"})
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {"token": ["This field is required."]}

    def test_post__internal(self, client: Client, internal_achievement: BasicAchievement) -> None:
        resp = client.post(self._url(internal_achievement.id), data={"username": "foo", "token": "bar"})
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {"detail": ["That achievement cannot be awarded using this endpoint."]}

    def test_post__bad_token(self, client: Client, external_achievement: BasicAchievement, user: User) -> None:
        resp = client.post(self._url(external_achievement.id), data={"username": user.username, "token": "bar"})
        assert resp.status_code == HTTPStatus.FORBIDDEN
        assert resp.json() == {"detail": "Incorrect authentication credentials."}

    def test_post__token_for_other_achievement(
        self, client: Client, external_achievement: BasicAchievement, user: User
    ) -> None:
        resp = client.post(
            self._url(external_achievement.id), data={"username": user.username, "token": self._sign_token(UUID(int=0))}
        )
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {"detail": ["That token isn't allowed to award that achievement"]}

    def test_post__user_not_found(self, client: Client, external_achievement: BasicAchievement) -> None:
        resp = client.post(
            self._url(external_achievement.id),
            data={"username": "foo", "token": self._sign_token(external_achievement.id)},
        )
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {"detail": ["That user cannot be found."]}

    def test_post__first_achievement(self, client: Client, external_achievement: BasicAchievement, user: User) -> None:
        resp = client.post(
            self._url(external_achievement.id),
            data={"username": user.username, "token": self._sign_token(external_achievement.id)},
        )
        assert resp.status_code == HTTPStatus.CREATED
        assert resp.content == b""

    def test_post__second_achievement(self, client: Client, external_achievement: BasicAchievement, user: User) -> None:
        award_builtin_basic_achievement(external_achievement.id, user)

        resp = client.post(
            self._url(external_achievement.id),
            data={"username": user.username, "token": self._sign_token(external_achievement.id)},
        )
        assert resp.status_code == HTTPStatus.OK
        assert resp.content == b""
