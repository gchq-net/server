import pytest

from gchqnet.accounts.models.user import User
from gchqnet.hexpansion.factories import HexpansionFactory
from gchqnet.quest.factories import LocationFactory
from gchqnet.quest.models import CaptureEvent, CaptureLog, RawCaptureEvent
from gchqnet.quest.models.location import LocationDifficulty
from gchqnet.quest.repository import record_attempted_capture


@pytest.mark.django_db
class TestRecordAttemptedCapture:
    def test_happy_path(self, user: User) -> None:
        # Arrange
        location = LocationFactory(created_by=user)
        badge = user.badges.first()

        # Act
        result = record_attempted_capture(
            badge,
            location.hexpansion,
            rand=1234567890,
            hmac="a" * 64,
            app_rev="0.0.0",
            fw_rev="0.0.0",
            wifi_bssid="00-00-00-00-00-00",
            wifi_channel=7,
            wifi_rssi=0,
        )

        # Assert
        assert result == {
            "result": "success",
            "repeat": False,
            "location_name": location.display_name,
            "difficulty": LocationDifficulty(location.difficulty).label,
        }

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
        _ = record_attempted_capture(
            badge,
            location.hexpansion,
            rand=1234567890,
            hmac="a" * 64,
            app_rev="0.0.0",
            fw_rev="0.0.0",
            wifi_bssid="00-00-00-00-00-00",
            wifi_channel=7,
            wifi_rssi=0,
        )
        result = record_attempted_capture(
            badge,
            location.hexpansion,
            rand=1234567890,
            hmac="a" * 64,
            app_rev="0.0.0",
            fw_rev="0.0.0",
            wifi_bssid="00-00-00-00-00-00",
            wifi_channel=7,
            wifi_rssi=0,
        )

        # Assert
        assert result == {
            "result": "success",
            "repeat": True,
            "location_name": location.display_name,
            "difficulty": LocationDifficulty(location.difficulty).label,
        }

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
        result = record_attempted_capture(
            badge,
            hexpansion,
            rand=1234567890,
            hmac="a" * 64,
            app_rev="0.0.0",
            fw_rev="0.0.0",
            wifi_bssid="00-00-00-00-00-00",
            wifi_channel=7,
            wifi_rssi=0,
        )

        # Assert
        assert result == {"result": "fail", "message": "Hexpansion not installed"}

        rce_count = RawCaptureEvent.objects.filter(badge=badge, hexpansion=hexpansion).count()
        assert rce_count == 1
