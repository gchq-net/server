import uuid

from django.db import models
from django.utils.crypto import get_random_string
from django_prometheus.models import ExportModelOperationsMixin


class AchievementDifficulty(models.IntegerChoices):
    EASY = 10
    MEDIUM = 15
    HARD = 20
    INSANE = 30
    IMPOSSIBLE = 50


class BasicAchievementAwardType(models.TextChoices):
    INTERNAL = "internal"  # i.e within this codebase
    EXTERNAL = "external"  # i.e by another GCHQ.NET system
    MANUAL = "manual"  # i.e within the web interface by an admin
    CLAIM = "claim"  # i.e claim with a hidden flag


def generate_claim_code() -> str:
    return get_random_string(20)


class BasicAchievement(ExportModelOperationsMixin("basic_achievement"), models.Model):  # type: ignore[misc]
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    display_name = models.CharField(
        "Display name", help_text="This name is shown to players who have the achievement.", max_length=30, unique=True
    )
    description = models.CharField(max_length=250, blank=True)
    difficulty = models.IntegerField(choices=AchievementDifficulty)
    award_type = models.CharField(max_length=8, choices=BasicAchievementAwardType)
    claim_code = models.CharField(max_length=50, default=generate_claim_code, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+", null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("display_name",)

    def __str__(self) -> str:
        return self.display_name


class BasicAchievementEvent(ExportModelOperationsMixin("basic_achievement_event"), models.Model):  # type: ignore[misc]
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    basic_achievement = models.ForeignKey(BasicAchievement, on_delete=models.PROTECT, related_name="events")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="basic_achievement_events")

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("created_at",)
        constraints = [
            models.UniqueConstraint(fields=["basic_achievement", "user"], name="one_event_per_user_per_achievement"),
        ]

    def __str__(self) -> str:
        return f"{self.user} achieved {self.basic_achievement}"


class FirstToCaptureAchievementEvent(ExportModelOperationsMixin("first_capture_achievement"), models.Model):  # type: ignore[misc]
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    location = models.OneToOneField(
        "quest.Location",
        on_delete=models.CASCADE,
        related_name="first_capture_event",
    )
    user = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="first_capture_events")

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self) -> str:
        return f"{self.user} was first to capture {self.location}"


class LocationGroup(ExportModelOperationsMixin("location_group"), models.Model):  # type: ignore[misc]
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    display_name = models.CharField(
        "Display name",
        max_length=30,
        unique=True,
    )
    difficulty = models.IntegerField(choices=AchievementDifficulty)
    locations = models.ManyToManyField("quest.Location", related_name="groups")

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("display_name",)

    def __str__(self) -> str:
        return self.display_name


class LocationGroupAchievementEvent(ExportModelOperationsMixin("location_group_achievement_event"), models.Model):  # type: ignore[misc]
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    location_group = models.ForeignKey(
        "achievements.LocationGroup",
        on_delete=models.CASCADE,
        related_name="events",
    )
    user = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT, related_name="location_group_achievement_events"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("created_at",)
        constraints = [
            models.UniqueConstraint(fields=["location_group", "user"], name="one_event_per_user_per_location_group"),
        ]

    def __str__(self) -> str:
        return f"{self.user} completed group {self.display_name}"
