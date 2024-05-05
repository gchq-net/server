import pytest

from gchqnet.accounts.models import User


@pytest.fixture
def user() -> User:
    return User.objects.create(
        username="foo-username",
        display_name="foo",
    )


@pytest.fixture
def user_2() -> User:
    return User.objects.create(
        username="foo2-username",
        display_name="foo2",
    )


@pytest.fixture
def user_with_badge() -> User:
    user = User.objects.create(
        username="user_with_badge",
        display_name="user_with_badge",
    )
    user.badges.create(mac_address="01-23-45-67-89-AB")
    return user
