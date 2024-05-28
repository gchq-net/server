import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_prometheus.models import ExportModelOperationsMixin

from gchqnet.quest.models.location import LocationDifficulty


class PlannedLocation(ExportModelOperationsMixin("planned_location"), models.Model):  # type: ignore[misc]
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.CharField(
        "Display name",
        help_text="This name is shown to players who have captured the location.",
        max_length=30,
        blank=True,
    )
    hint = models.CharField(
        "Hint",
        help_text="This name is shown to players to help them find the location.",
        max_length=60,
        blank=True,
    )

    # Internal fields
    internal_name = models.CharField(
        "Internal name",
        help_text="This name is shown to admins and should be descriptive.",
        max_length=50,
        unique=True,
    )
    description = models.TextField(
        help_text="Further description of the planned location of the installation.", blank=True
    )
    difficulty = models.IntegerField(choices=LocationDifficulty, blank=True, null=True)

    # Location
    lat = models.DecimalField(
        "Latitude",
        max_digits=16,
        decimal_places=13,
        blank=True,
        null=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    long = models.DecimalField(
        "Longitude",
        max_digits=16,
        decimal_places=13,
        blank=True,
        null=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+", null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("internal_name",)

    def __str__(self) -> str:
        return self.internal_name

    def is_ready_to_deploy(self) -> bool:
        return bool(self.display_name and self.hint and self.difficulty and self.description and self.lat and self.long)
