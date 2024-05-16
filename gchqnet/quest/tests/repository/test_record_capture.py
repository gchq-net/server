import pytest

from gchqnet.accounts.models.user import User
from gchqnet.hexpansion.factories import HexpansionFactory
from gchqnet.quest.factories import LocationFactory
from gchqnet.quest.models import CaptureEvent, CaptureLog, RawCaptureEvent
from gchqnet.quest.repository import record_attempted_capture


@pytest.mark.django_db
class TestRecordAttemptedCapture:
    def test_happy_path(self, user: User) -> None:
        # Arrange
        location = LocationFactory(created_by=user)
        badge = user.badges.first()

        # Act
        result = record_attempted_capture(badge, location.hexpansion)

        # Assert
        assert result == {"result": "success", "message": "Successfully captured"}

        rce = RawCaptureEvent.objects.get(badge=badge, hexpansion=location.hexpansion)
        assert rce.created_by == user

        log = CaptureLog.objects.get(created_by=user, location=location)
        assert log.raw_capture_event == rce

        event = CaptureEvent.objects.get(created_by=user, location=location)
        assert event.raw_capture_event == rce

    def test_multiple_captures(self, user: User) -> None:
        # Arrange
        location = LocationFactory(created_by=user)
        badge = user.badges.first()

        # Act
        _ = record_attempted_capture(badge, location.hexpansion)
        result = record_attempted_capture(badge, location.hexpansion)

        # Assert
        assert result == {"result": "repeat", "message": "You have captured this before."}

        rce_count = RawCaptureEvent.objects.filter(badge=badge, hexpansion=location.hexpansion).count()
        assert rce_count == 2

        log_count = CaptureLog.objects.filter(created_by=user, location=location).count()
        assert log_count == 2

        event_count = CaptureEvent.objects.filter(created_by=user, location=location).count()
        assert event_count == 1

    def test_unlinked_hexpansion(self, user: User) -> None:
        # Arrange
        hexpansion = HexpansionFactory(created_by=user)
        badge = user.badges.first()

        # Act
        result = record_attempted_capture(badge, hexpansion)

        # Assert
        assert result == {"result": "error", "message": "Unable to find that hexpansion"}

        rce_count = RawCaptureEvent.objects.filter(badge=badge, hexpansion=hexpansion).count()
        assert rce_count == 1
