from __future__ import annotations

from typing import TYPE_CHECKING, Literal
from uuid import UUID

from django.db import models
from django.urls import reverse
from notifications.signals import notify

from gchqnet.accounts.models.user import User
from gchqnet.quest.models.location import Location
from gchqnet.quest.models.scores import ScoreRecord
from gchqnet.quest.repository.scores import update_score_for_user

from .models import BasicAchievement, FirstToCaptureAchievementEvent

if TYPE_CHECKING:
    from django.contrib.auth.models import AnonymousUser

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
        current_score = update_score_for_user(user)
        notify.send(
            user,
            recipient=user,
            verb="achieved",
            target=achievement,
            description=f"You have gained {achievement.difficulty} points and now have a score of {current_score}.",
        )
        return "success"
    else:
        return "already_obtained"


def award_first_capture(location: Location, user: User, *, update_score: bool = False) -> AchievementAwardResult:
    obj, created = FirstToCaptureAchievementEvent.objects.get_or_create(
        location=location,
        defaults={"user": user, "created_by": user},
    )
    if created:
        ScoreRecord.objects.create(
            first_capture_event=obj,
            user=user,
            score=location.difficulty,
        )
        notify.send(
            user,
            recipient=user,
            verb="was the first to capture",
            target=obj.location,
            description="You have received a first capture bonus.",
            actions=[{"href": reverse("quest:location_detail", args=[location.id]), "title": "View"}],
        )
        if update_score:
            update_score_for_user(user)
    return "success" if created else "failure"


def get_achievements_for_user(user: User, viewer: User | AnonymousUser) -> models.QuerySet:
    bae = (
        user.basic_achievement_events.select_related("basic_achievement")
        .annotate(
            display_name=models.F("basic_achievement__display_name"),
            difficulty=models.F("basic_achievement__difficulty"),
        )
        .order_by()
        .values("display_name", "difficulty", "created_at")
    )

    first_captures = user.first_capture_events.select_related("location")
    first_captures = first_captures.annotate(difficulty=models.F("location__difficulty"))
    if viewer == user:
        first_captures = first_captures.annotate(
            display_name=models.functions.Concat(models.Value("First to capture "), models.F("location__display_name"))
        )
    else:
        first_captures = first_captures.annotate(display_name=models.Value("First to capture a location"))

    first_captures = first_captures.order_by().values("display_name", "difficulty", "created_at")  # type: ignore[assignment]

    return bae.union(first_captures).order_by("-created_at")
