from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models

from gchqnet.quest.models.scores import ScoreRecord, UserScore

if TYPE_CHECKING:
    from gchqnet.accounts.models import User, UserQuerySet


def get_current_score_for_user(user: User) -> int:
    try:
        return user.user_score.current_score
    except UserScore.DoesNotExist:
        return 0


def annotate_current_score_for_user_queryset(
    qs: models.QuerySet[User] | UserQuerySet,
) -> models.QuerySet[User] | UserQuerySet:
    return qs.select_related("user_score").annotate(
        current_score=models.functions.Coalesce(models.F("user_score__current_score"), models.Value(0)),
    )


def _calculate_current_score_for_user(user: User) -> int:
    res = ScoreRecord.objects.filter(user=user).aggregate(models.Sum("score"))

    # Note: if no score_record rows, then res['score__sum'] is None
    return res.get("score__sum") or 0


def update_score_for_user(user: User) -> None:
    UserScore.objects.update_or_create(
        user=user,
        defaults={"current_score": _calculate_current_score_for_user(user)},
        create_defaults={"current_score": _calculate_current_score_for_user(user)},
    )


def grade_for_score(score: int) -> str:
    grades = {
        0: "Just observing",
        1: "Warming up",
        50: "Hexpansion collector",
        100: "Running around site",
        400: "Missing talks",
        800: "Badge destroyer",
    }
    for score_threshold, description in reversed(grades.items()):
        if score >= score_threshold:
            return description
    return grades[0]
