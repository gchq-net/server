from random import randint

import pytest

from gchqnet.accounts.models import User
from gchqnet.hexpansion.factories import HexpansionFactory
from gchqnet.quest.factories import LocationFactory
from gchqnet.quest.models import Location
from gchqnet.quest.models.leaderboard import Leaderboard
from gchqnet.quest.repository import get_global_scoreboard, get_private_scoreboard, record_attempted_capture
from gchqnet.quest.repository.scores import update_score_for_user


def _generate_capture(user: User) -> Location:
    hexpansion = HexpansionFactory(created_by=user)
    location = LocationFactory(hexpansion=hexpansion, created_by=user)
    badge = user.badges.first()
    assert badge

    record_attempted_capture(
        badge,
        hexpansion,
        rand=1234567890,
        hmac="a" * 64,
        app_rev="0.0.0",
        fw_rev="0.0.0",
    )
    location.first_capture_event.delete()
    update_score_for_user(user)
    return location


SCOREBOARD_FIELDS = ["id", "username", "display_name", "rank", "capture_count", "current_score"]


@pytest.mark.django_db
class TestGetGlobalScoreboard:
    @pytest.mark.usefixtures("superuser")
    def test_no_capture(self, user: User, user_2: User) -> None:
        scoreboard = get_global_scoreboard()

        assert list(scoreboard.values(*SCOREBOARD_FIELDS)) == [
            {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "rank": 1,
                "capture_count": 0,
                "current_score": 0,
            },
            {
                "id": user_2.id,
                "username": user_2.username,
                "display_name": user_2.display_name,
                "rank": 1,
                "capture_count": 0,
                "current_score": 0,
            },
        ]

    def test_one_capture(self, user: User, user_2: User) -> None:
        location = _generate_capture(user)

        scoreboard = get_global_scoreboard()

        assert list(scoreboard.values(*SCOREBOARD_FIELDS)) == [
            {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "rank": 1,
                "capture_count": 1,
                "current_score": int(location.difficulty),
            },
            {
                "id": user_2.id,
                "username": user_2.username,
                "display_name": user_2.display_name,
                "rank": 2,
                "capture_count": 0,
                "current_score": 0,
            },
        ]

    def test_multiple_captures(self, user: User, user_2: User) -> None:
        u1_locations = [_generate_capture(user) for _ in range(randint(3, 7))]  # noqa: S311
        u2_locations = [_generate_capture(user_2) for _ in range(randint(3, 7))]  # noqa: S311

        u1_score = sum(lo.difficulty for lo in u1_locations)
        u2_score = sum(lo.difficulty for lo in u2_locations)

        scoreboard = get_global_scoreboard()

        assert list(scoreboard.values(*SCOREBOARD_FIELDS)) == sorted(
            [
                {
                    "id": user.id,
                    "username": user.username,
                    "display_name": user.display_name,
                    "rank": 1 if u1_score >= u2_score else 2,
                    "capture_count": len(u1_locations),
                    "current_score": u1_score,
                },
                {
                    "id": user_2.id,
                    "username": user_2.username,
                    "display_name": user_2.display_name,
                    "rank": 1 if u2_score >= u1_score else 2,
                    "capture_count": len(u2_locations),
                    "current_score": u2_score,
                },
            ],
            key=lambda o: (o["rank"], o["capture_count"]),
        )


@pytest.mark.django_db
class TestPrivateScoreboard:
    @pytest.mark.usefixtures("superuser")
    def test_no_members(self, user: User) -> None:
        leaderboard = Leaderboard.objects.create(display_name="foo", owner=user, created_by=user)
        scoreboard = get_private_scoreboard(leaderboard)
        assert list(scoreboard.values(*SCOREBOARD_FIELDS)) == []

    @pytest.mark.usefixtures("superuser")
    def test_one_member(self, user: User) -> None:
        leaderboard = Leaderboard.objects.create(display_name="foo", owner=user, created_by=user)
        leaderboard.members.add(user)
        scoreboard = get_private_scoreboard(leaderboard)
        assert list(scoreboard.values(*SCOREBOARD_FIELDS)) == [
            {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "rank": 1,
                "capture_count": 0,
                "current_score": 0,
            },
        ]

    @pytest.mark.usefixtures("user_2")
    def test_superuser_member(self, user: User, superuser: User) -> None:
        leaderboard = Leaderboard.objects.create(display_name="foo", owner=user, created_by=user)
        leaderboard.members.set([user, superuser])
        scoreboard = get_private_scoreboard(leaderboard)
        assert list(scoreboard.values(*SCOREBOARD_FIELDS)) == [
            {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "rank": 1,
                "capture_count": 0,
                "current_score": 0,
            },
            {
                "id": superuser.id,
                "username": superuser.username,
                "display_name": superuser.display_name,
                "rank": 1,
                "capture_count": 0,
                "current_score": 0,
            },
        ]

    @pytest.mark.usefixtures("user_2")
    def test_one_capture(self, user: User, superuser: User) -> None:
        leaderboard = Leaderboard.objects.create(display_name="foo", owner=user, created_by=user)
        leaderboard.members.set([user, superuser])

        location = _generate_capture(user)

        scoreboard = get_private_scoreboard(leaderboard)
        assert list(scoreboard.values(*SCOREBOARD_FIELDS)) == [
            {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "rank": 1,
                "capture_count": 1,
                "current_score": int(location.difficulty),
            },
            {
                "id": superuser.id,
                "username": superuser.username,
                "display_name": superuser.display_name,
                "rank": 2,
                "capture_count": 0,
                "current_score": 0,
            },
        ]

    def test_multiple_captures(self, user: User, superuser: User) -> None:
        leaderboard = Leaderboard.objects.create(display_name="foo", owner=user, created_by=user)
        leaderboard.members.set([user, superuser])

        u1_locations = [_generate_capture(user) for _ in range(randint(3, 7))]  # noqa: S311
        u2_locations = [_generate_capture(superuser) for _ in range(randint(3, 7))]  # noqa: S311

        u1_score = sum(lo.difficulty for lo in u1_locations)
        u2_score = sum(lo.difficulty for lo in u2_locations)

        scoreboard = get_private_scoreboard(leaderboard)
        assert list(scoreboard.values(*SCOREBOARD_FIELDS)) == sorted(
            [
                {
                    "id": user.id,
                    "username": user.username,
                    "display_name": user.display_name,
                    "rank": 1 if u1_score >= u2_score else 2,
                    "capture_count": len(u1_locations),
                    "current_score": u1_score,
                },
                {
                    "id": superuser.id,
                    "username": superuser.username,
                    "display_name": superuser.display_name,
                    "rank": 1 if u2_score >= u1_score else 2,
                    "capture_count": len(u2_locations),
                    "current_score": u2_score,
                },
            ],
            key=lambda o: (o["rank"], o["capture_count"]),
        )
