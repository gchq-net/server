import uuid

from django.db import models
from django_prometheus.models import ExportModelOperationsMixin


class ScoreRecord(ExportModelOperationsMixin("score_record"), models.Model):  # type: ignore[misc]
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    capture_event = models.OneToOneField(
        "quest.CaptureEvent", on_delete=models.CASCADE, related_name="score_record", null=True
    )
    basic_achievement_event = models.OneToOneField(
        "achievements.BasicAchievementEvent", on_delete=models.CASCADE, related_name="score_record", null=True
    )
    first_capture_event = models.OneToOneField(
        "achievements.FirstToCaptureAchievementEvent", on_delete=models.CASCADE, related_name="score_record", null=True
    )
    location_group_achievement_event = models.OneToOneField(
        "achievements.LocationGroupAchievementEvent", on_delete=models.CASCADE, related_name="score_record", null=True
    )
    score = models.IntegerField()
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="score_records")

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(capture_event__isnull=False)
                | models.Q(basic_achievement_event__isnull=False)
                | models.Q(first_capture_event__isnull=False)
                | models.Q(location_group_achievement_event__isnull=False),
                name="ensure_linked_event",
            )
        ]

    def __str__(self) -> str:
        return "Score Record"


class UserScore(ExportModelOperationsMixin("user_score"), models.Model):  # type: ignore[misc]
    """The current score of the user, dynamically updated."""

    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="user_score")
    current_score = models.IntegerField()

    def __str__(self) -> str:
        return f"Current score for {self.user} is {self.current_score}"
