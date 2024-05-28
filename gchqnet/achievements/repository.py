from __future__ import annotations

from typing import TYPE_CHECKING, Literal
from uuid import UUID

from django.db import models
from django.urls import reverse
from django_prometheus.conf import NAMESPACE
from notifications.signals import notify
from prometheus_client import Counter

from gchqnet.accounts.models.user import User
from gchqnet.quest.models.location import Location
from gchqnet.quest.models.scores import ScoreRecord
from gchqnet.quest.repository.scores import update_score_for_user

from .models import BasicAchievement, FirstToCaptureAchievementEvent, LocationGroup, LocationGroupAchievementEvent

if TYPE_CHECKING:
    from django.contrib.auth.models import AnonymousUser

AchievementAwardResult = Literal["success", "failure", "already_obtained"]


basic_achievement_awards = Counter(
    "gchqnet_achievement_awards_total",
    "Number of basic achievements awarded.",
    ["id", "display_name", "award_type", "difficulty", "username"],
    namespace=NAMESPACE,
)

location_group_awards = Counter(
    "gchqnet_location_group_completions_total",
    "Number of location groups completed.",
    ["id", "display_name", "difficulty", "username"],
    namespace=NAMESPACE,
)


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
        basic_achievement_awards.labels(
            achievement_id, achievement.display_name, achievement.award_type, achievement.difficulty, user.username
        ).inc()
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

    # First Captures
    first_captures = user.first_capture_events.select_related("location")
    first_captures = first_captures.annotate(difficulty=models.F("location__difficulty"))
    if viewer == user:
        first_captures = first_captures.annotate(
            display_name=models.functions.Concat(models.Value("First to capture "), models.F("location__display_name"))
        )
    else:
        first_captures = first_captures.annotate(display_name=models.Value("First to capture a location"))

    first_captures = first_captures.order_by().values("display_name", "difficulty", "created_at")  # type: ignore[misc]

    # Location Groups
    lgae = (
        user.location_group_achievement_events.select_related("location_group")
        .annotate(
            display_name=models.F("location_group__display_name"),
            difficulty=models.F("location_group__difficulty"),
        )
        .order_by()
        .values("display_name", "difficulty", "created_at")
    )

    return bae.union(first_captures, lgae).order_by("-created_at")


def has_user_captured_group(user: User, location_group: LocationGroup) -> bool:
    location_ids_for_group = location_group.locations.values("id")
    of_which_found = user.capture_events.filter(location__in=location_ids_for_group).count()
    return bool(location_ids_for_group.count()) and (of_which_found == location_ids_for_group.count())


def handle_location_capture_for_groups(user: User, location: Location, *, update_score: bool = False) -> None:
    for group in location.groups.all():
        if has_user_captured_group(user, group):
            obj, created = LocationGroupAchievementEvent.objects.get_or_create(
                location_group=group,
                user=user,
                defaults={"created_by": user},
            )
            if created:
                location_group_awards.labels(group.id, group.display_name, group.difficulty, user.username).inc()
                ScoreRecord.objects.create(
                    location_group_achievement_event=obj,
                    user=user,
                    score=group.difficulty,
                )
                notify.send(
                    user,
                    recipient=user,
                    verb="captured all locations in",
                    target=group,
                    description="You have received a group capture bonus.",
                    actions=[{"href": reverse("achievements:location_group_detail", args=[group.id]), "title": "View"}],
                )
    if update_score:
        update_score_for_user(user)
