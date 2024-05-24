import pytest

from gchqnet.accounts.models import User
from gchqnet.achievements.models import BasicAchievement


@pytest.fixture
def user() -> User:
    user = User.objects.create(
        username="foo-username",
        display_name="foo",
    )
    user.badges.create(mac_address="0A-23-45-67-89-AB", secret="b" * 64)
    return user


@pytest.fixture
def user_2() -> User:
    return User.objects.create(
        username="foo2-username",
        display_name="foo2",
    )


@pytest.fixture
def superuser() -> User:
    user = User.objects.create(
        username="user_with_badge",
        display_name="user_with_badge",
        is_superuser=True,
        email="foo@example.com",
    )
    user.badges.create(mac_address="01-23-45-67-89-AB")
    return user


@pytest.fixture
def internal_achievement() -> BasicAchievement:
    return BasicAchievement.objects.create(
        display_name="foo",
        difficulty=10,
        award_type="internal",
    )


@pytest.fixture
def external_achievement() -> BasicAchievement:
    return BasicAchievement.objects.create(
        display_name="bar",
        difficulty=10,
        award_type="external",
    )
