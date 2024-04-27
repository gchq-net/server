import pytest

from gchqnet.accounts.models import User


@pytest.fixture
def user() -> User:
    return User.objects.create(
        username="foo",
        display_name="foo",
    )


@pytest.fixture
def user_2() -> User:
    return User.objects.create(
        username="foo2",
        display_name="foo2",
    )
