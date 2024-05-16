import pytest

from gchqnet.accounts.models import User


@pytest.fixture
def user() -> User:
    user = User.objects.create(
        username="foo-username",
        display_name="foo",
    )
    user.badges.create(mac_address="02-23-45-67-89-AB")
    return user


@pytest.fixture
def user_2() -> User:
    user = User.objects.create(
        username="foo2-username",
        display_name="foo2",
    )
    user.badges.create(mac_address="01-23-45-67-89-AB")
    return user


@pytest.fixture
def superuser() -> User:
    user = User.objects.create(
        username="superuser-username",
        display_name="superuser",
        is_superuser=True,
        email="superuser@example.com",
    )
    user.badges.create(mac_address="03-23-45-67-89-AB")
    return user