import pytest

from gchqnet.accounts.models.user import User
from gchqnet.achievements.models import LocationGroup
from gchqnet.achievements.repository import has_user_captured_group
from gchqnet.quest.factories import LocationFactory
from gchqnet.quest.repository.captures import record_attempted_capture


@pytest.mark.django_db
class TestHasUserCapturedGroup:
    def test_no_locations_in_group(self, user: User, location_group: LocationGroup) -> None:
        res = has_user_captured_group(user, location_group)
        assert res is False

    def test_one_location_in_group__no_capture(self, user: User, location_group: LocationGroup) -> None:
        location = LocationFactory(created_by=user)
        location_group.locations.add(location)

        res = has_user_captured_group(user, location_group)
        assert res is False

    def test_one_location_in_group__one_capture(self, user: User, location_group: LocationGroup) -> None:
        location = LocationFactory(created_by=user)
        location_group.locations.add(location)

        record_attempted_capture(
            user.badges.first(), location.hexpansion, rand=b"1", hmac="a" * 64, app_rev="1", fw_rev="1"
        )

        res = has_user_captured_group(user, location_group)
        assert res is True

    def test_two_locations_in_group__one_capture(self, user: User, location_group: LocationGroup) -> None:
        location = LocationFactory(created_by=user)
        location2 = LocationFactory(created_by=user)
        location_group.locations.set([location, location2])
        record_attempted_capture(
            user.badges.first(), location.hexpansion, rand=b"1", hmac="a" * 64, app_rev="1", fw_rev="1"
        )

        res = has_user_captured_group(user, location_group)
        assert res is False

    def test_two_locations_in_group__two_captures(self, user: User, location_group: LocationGroup) -> None:
        location = LocationFactory(created_by=user)
        location2 = LocationFactory(created_by=user)
        location_group.locations.set([location, location2])
        record_attempted_capture(
            user.badges.first(), location.hexpansion, rand=b"1", hmac="a" * 64, app_rev="1", fw_rev="1"
        )
        record_attempted_capture(
            user.badges.first(), location2.hexpansion, rand=b"1", hmac="a" * 64, app_rev="1", fw_rev="1"
        )

        res = has_user_captured_group(user, location_group)
        assert res is True
