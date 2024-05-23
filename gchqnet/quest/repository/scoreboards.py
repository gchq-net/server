from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from django.db import models
from django.db.models.functions import DenseRank

from gchqnet.accounts.models import User, UserQuerySet
from gchqnet.achievements.models import BasicAchievementEvent, FirstToCaptureAchievementEvent
from gchqnet.quest.models.captures import CaptureEvent

from .scores import annotate_current_score_for_user_queryset

if TYPE_CHECKING:  # pragma: nocover
    from django.contrib.auth.models import AnonymousUser
    from django.db.models import QuerySet

    from gchqnet.accounts.models import User, UserQuerySet
    from gchqnet.quest.models.leaderboard import Leaderboard


def _annotate_scoreboard_query(qs: UserQuerySet | QuerySet[User]) -> UserQuerySet:
    qs = qs.only("id", "username", "display_name")
    qs = annotate_current_score_for_user_queryset(qs)
    qs = qs.annotate(
        capture_count=models.Count("capture_events"),
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


def get_recent_events_for_users(
    users: QuerySet[User], *, current_user: User | AnonymousUser, max_num: int = 20
) -> tuple[QuerySet, set[UUID]]:
    ce_qs = (
        CaptureEvent.objects.select_related("location")
        .filter(
            created_by__in=users,
        )
        .annotate(
            player_username=models.F("created_by__username"),
            player_name=models.F("created_by__display_name"),
            difficulty=models.F("location__difficulty"),
            type=models.Value("capture"),
        )[:max_num]
    )

    bae_qs = BasicAchievementEvent.objects.filter(
        user__in=users,
    ).annotate(
        player_username=models.F("user__username"),
        player_name=models.F("user__display_name"),
        difficulty=models.F("basic_achievement__difficulty"),
        type=models.Value("basic_achievement"),
    )[:max_num]

    fcae_qs = FirstToCaptureAchievementEvent.objects.filter(
        user__in=users,
    ).annotate(
        player_username=models.F("user__username"),
        player_name=models.F("user__display_name"),
        difficulty=models.F("location__difficulty"),
        type=models.Value("first_capture"),
    )[:max_num]

    both = list(ce_qs) + list(bae_qs) + list(fcae_qs)

    if current_user.is_authenticated:
        user_found_locations = set(
            CaptureEvent.objects.filter(
                location_id__in=[ce.location_id for ce in ce_qs] + [fcae.location_id for fcae in fcae_qs],
                created_by=current_user,
            ).values_list("location_id", flat=True)
        )
    else:
        user_found_locations = set()

    events = sorted(both, key=lambda x: x.created_at, reverse=True)[:max_num]

    return events, user_found_locations  # type: ignore[return-value]
