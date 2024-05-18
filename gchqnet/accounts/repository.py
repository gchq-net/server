from typing import Literal, TypedDict

from django.utils.crypto import constant_time_compare

from gchqnet.accounts.models import Badge, User
from gchqnet.accounts.usernames import generate_username


class BadgeCredentialsSuccessfulResult(TypedDict):
    result: Literal["success"]
    badge: Badge
    user: User
    new_user: bool


class BadgeCredentialsFailResult(TypedDict):
    result: Literal["failure"]


def _handle_unknown_badge(
    mac_address: str,
    badge_secret: str,
) -> tuple[Badge, User]:
    username = generate_username()
    user = User.objects.create(
        username=username,
        display_name=username,
    )
    badge = user.badges.create(mac_address=mac_address, secret=badge_secret)

    return badge, user


def check_badge_credentials(
    mac_address: str,
    badge_secret: str,
) -> BadgeCredentialsSuccessfulResult | BadgeCredentialsFailResult:
    try:
        badge = Badge.objects.select_related("user").get(
            mac_address=mac_address,
        )

        # If the badge secret is blank, set it.
        # This might be used if badges are hard reset.
        if not badge.secret:
            badge.secret = badge_secret
            badge.save()

        if not constant_time_compare(badge_secret, badge.secret):
            return BadgeCredentialsFailResult(result="failure")

        return BadgeCredentialsSuccessfulResult(
            result="success",
            badge=badge,
            user=badge.user,
            new_user=False,
        )
    except Badge.DoesNotExist:
        badge, user = _handle_unknown_badge(mac_address, badge_secret)
        return BadgeCredentialsSuccessfulResult(
            result="success",
            badge=badge,
            user=user,
            new_user=True,
        )
