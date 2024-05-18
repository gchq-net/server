import uuid

from django.db import models


class ScoreRecord(models.Model):
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    capture_event = models.OneToOneField("quest.CaptureEvent", on_delete=models.CASCADE, related_name="score_record")
    score = models.IntegerField()
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="score_records")

    def __str__(self) -> str:
        return "Score Record"


class UserScore(models.Model):
    """The current score of the user, dynamically updated."""

    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="user_score")
    current_score = models.IntegerField()

    def __str__(self) -> str:
        return f"Current score for {self.user} is {self.current_score}"