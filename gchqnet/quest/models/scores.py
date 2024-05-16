import uuid

from django.db import models


class ScoreRecord(models.Model):
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    capture_event = models.OneToOneField("quest.CaptureEvent", on_delete=models.CASCADE, related_name="score_record")
    score = models.IntegerField()
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="score_records")

    def __str__(self) -> str:
        return "Score Record"
