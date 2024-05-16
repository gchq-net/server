from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models
from django.db.models.functions import DenseRank

from gchqnet.accounts.models import User

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from gchqnet.accounts.models import User, UserQuerySet
    from gchqnet.quest.models.leaderboard import Leaderboard


def _annotate_scoreboard_query(qs: UserQuerySet | QuerySet[User]) -> UserQuerySet:
    qs = qs.only("id", "username", "display_name")
    qs = qs.annotate(
        capture_count=models.Count("capture_events"),
        current_score=models.functions.Coalesce(
            models.Sum("capture_events__location__difficulty"),
            models.Value(0),
        ),
        rank=models.Window(expression=DenseRank(), order_by=models.F("current_score").desc()),
    )
    qs = qs.order_by("rank", "capture_count", "display_name")
    return qs  # type: ignore[return-value]


def get_global_scoreboard(*, search_query: str = "") -> UserQuerySet:
    # Only display users who are not administrators.
    qs = User.objects.filter(is_superuser=False)
    qs = _annotate_scoreboard_query(qs)

    if search_query:
        # Construct a CTE expression manually as the Django ORM does not support them
        # Hack for case-insensitivity that works across both SQLite and PostgreSQL
        qs = User.objects.raw(
            f"SELECT * FROM ({qs.query}) as u0 WHERE Lower(display_name) LIKE Lower(%s)",  # noqa: S608
            [f"%{search_query}%"],
        )

    return qs


def get_private_scoreboard(leaderboard: Leaderboard) -> UserQuerySet:
    qs = leaderboard.members.all()
    qs = _annotate_scoreboard_query(qs)
    return qs
