import uuid

from django.db import models


class AchievementDifficulty(models.IntegerChoices):
    EASY = 10
    MEDIUM = 15
    HARD = 20
    INSANE = 30
    IMPOSSIBLE = 50


class Achievement(models.Model):
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)  # noqa: F821

    display_name = models.CharField(
        "Display name",
        help_text="This name is shown to players.",
        max_length=60,
        unique=True,
    )
    hide_display_name = models.BooleanField(
        default=False, help_text="Hide the display name from players until they have achieved it."
    )
    difficulty = models.IntegerField(choices=AchievementDifficulty)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+", null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.display_name


class AchievementEvent(models.Model):
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)  # noqa: F821

    score = models.IntegerField(choices=AchievementDifficulty, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+", null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BasicAchievement(Achievement):
    """
    Basic achievements are assigned via a database entry.

    e.g:
    - 10 points for hacking us (assigned by code)
    - 20 points for sending us a letter (assigned by admin)
    - 20 points because lol
    """

    description = models.TextField(help_text="Description of how the achievement is gained", blank=True)


class BasicAchievementEvent(AchievementEvent):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="basic_achievement_events")
    achievement = models.ForeignKey(BasicAchievement, on_delete=models.CASCADE, related_name="events")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "achievement"], name="user_can_achieve_once")]

    def __str__(self) -> str:
        return f"{self.user} achieved {self.achievement}"
