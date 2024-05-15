import pytest

from gchqnet.accounts.models import User
from gchqnet.hexpansion.factories import HexpansionFactory
from gchqnet.quest.factories import LocationFactory
from gchqnet.quest.models import CaptureEvent, Location, RawCaptureEvent


@pytest.mark.django_db
class TestUserScoreBoardAnnotation:
    def _generate_capture(self, user: User) -> Location:
        hexpansion = HexpansionFactory(created_by=user)
        location = LocationFactory(created_by=user)
        badge = user.badges.first()
        assert badge

        raw_capture = RawCaptureEvent.objects.create(badge=badge, hexpansion=hexpansion, created_by=user)
        CaptureEvent.objects.create(
            raw_capture_event=raw_capture, location=location, score=location.difficulty, created_by=user
        )

        return location

    def test_no_capture(self, user: User) -> None:
        queried_user = User.objects.with_scoreboard_fields().get(id=user.id)

        assert queried_user.current_score == 0

    def test_one_capture(self, user_with_badge: User) -> None:
        location = self._generate_capture(user_with_badge)
        queried_user = User.objects.with_scoreboard_fields().get(id=user_with_badge.id)

        # Score should be exactly the value of that location.
        assert queried_user.current_score == location.difficulty
        assert queried_user.capture_count == 1

    def test_two_captures(self, user_with_badge: User) -> None:
        location_1 = self._generate_capture(user_with_badge)
        location_2 = self._generate_capture(user_with_badge)

        queried_user = User.objects.with_scoreboard_fields().get(id=user_with_badge.id)

        # Score should be the sum of those locations
        assert queried_user.current_score == location_1.difficulty + location_2.difficulty
        assert queried_user.capture_count == 2
