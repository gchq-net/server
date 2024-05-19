from typing import Literal
from uuid import UUID

from gchqnet.accounts.models.user import User
from gchqnet.quest.models.scores import ScoreRecord
from gchqnet.quest.repository.scores import update_score_for_user

from .models import BasicAchievement

AchievementAwardResult = Literal["success", "failure", "already_obtained"]


def award_builtin_basic_achievement(
    achievement_id: UUID | str,
    user: User,
) -> AchievementAwardResult:
    try:
        achievement = BasicAchievement.objects.get(id=achievement_id)
    except BasicAchievement.DoesNotExist:
        return "failure"

    # Create or get the event, if it already exists
    bae, created = achievement.events.get_or_create(
        user=user,
        defaults={
            "created_by": user,
        },
    )

    if created:
        ScoreRecord.objects.create(
            basic_achievement_event=bae,
            user=user,
            score=achievement.difficulty,
        )
        update_score_for_user(user)
        return "success"
    else:
        return "already_obtained"
