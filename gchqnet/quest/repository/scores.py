from django.db import models

from gchqnet.accounts.models import User, UserQuerySet
from gchqnet.quest.models.scores import ScoreRecord, UserScore


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
