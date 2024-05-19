import uuid

from django.db import models


class AchievementDifficulty(models.IntegerChoices):
    EASY = 10
    MEDIUM = 15
    HARD = 20
    INSANE = 30
    IMPOSSIBLE = 50


class BasicAchievement(models.Model):
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    display_name = models.CharField(
        "Display name", help_text="This name is shown to players who have the achievement.", max_length=30, unique=True
    )
    difficulty = models.IntegerField(choices=AchievementDifficulty)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+", null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("display_name",)

    def __str__(self) -> str:
        return self.display_name


class BasicAchievementEvent(models.Model):
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
