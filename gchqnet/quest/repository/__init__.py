from __future__ import annotations

from typing import TYPE_CHECKING

from .cache import CachedScoreboardQuerySet

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from gchqnet.accounts.models import User, UserQuerySet
    from gchqnet.quest.models.leaderboard import Leaderboard


def _annotate_scoreboard_query(qs: UserQuerySet | QuerySet[User]) -> UserQuerySet:
    qs = qs.only("id", "username", "display_name")
    qs = qs.with_scoreboard_fields()  # type: ignore[attr-defined]
    qs = qs.order_by("rank", "capture_count", "display_name")
    return qs  # type: ignore[return-value]


def get_global_scoreboard(*, search_query: str | None = None) -> CachedScoreboardQuerySet:
    from gchqnet.accounts.models.user import User

    # Only display users who are not administrators.
    qs = User.objects.filter(is_superuser=False)
    qs = _annotate_scoreboard_query(qs)

    qsi = CachedScoreboardQuerySet(qs, "global")

    if search_query:
        qsi = qsi.filter(display_name__ilike=search_query)

    return qsi


def get_private_scoreboard(leaderboard: Leaderboard) -> CachedScoreboardQuerySet:
    qs = leaderboard.members.all()
    qs = _annotate_scoreboard_query(qs)
    return CachedScoreboardQuerySet(qs, str(leaderboard.id))
