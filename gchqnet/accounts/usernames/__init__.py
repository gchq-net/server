import random

from .data import ADJECTIVES, NOUNS


def generate_username() -> str:
    from gchqnet.accounts.models import User

    adjective = random.choice(ADJECTIVES)  # noqa: S311
    noun = random.choice(NOUNS)  # noqa: S311

    username = f"{adjective}-{noun}"

    # Check if the username is already in use, it's very unlikely to be so we
    # don't bother properly locking the database
    if User.objects.filter(username=username).exists():
        return generate_username()
    return username
