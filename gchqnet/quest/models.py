import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class LocationDifficulty(models.IntegerChoices):
    EASY = 10
    MEDIUM = 15
    HARD = 20
    INSANE = 30
    IMPOSSIBLE = 50


class Location(models.Model):
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.CharField(
        "Display name",
        help_text="This name is shown to players who have captured the location.",
        max_length=30,
        unique=True,
        error_messages={
            "unique": "Another location already has that display name",
        },
    )
    internal_name = models.CharField(
        "Internal name",
        help_text="This name is shown to admins and should be descriptive.",
        max_length=50,
        blank=True,
    )
    description = models.TextField(help_text="Further description of the location of the installation.", blank=True)

    difficulty = models.IntegerField(choices=LocationDifficulty)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("internal_name", "display_name")

    def __str__(self) -> str:
        return self.internal_name or self.display_name


class Coordinates(models.Model):
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    location = models.OneToOneField(Location, on_delete=models.CASCADE, related_name="coordinates")
    lat = models.DecimalField(
        "Latitude", max_digits=8, decimal_places=3, validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    long = models.DecimalField(
        "Longitude", max_digits=8, decimal_places=3, validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"({self.lat},{self.long})"


class LocationInstallation(models.Model):
    """If present, indicates that this location has been installed."""

    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    location = models.OneToOneField(Location, on_delete=models.CASCADE, related_name="installation")
    hexpansion = models.OneToOneField("hexpansion.Hexpansion", on_delete=models.PROTECT, related_name="installation")

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Installed by {self.created_by} at {self.created_at}"


class RawCaptureEvent(models.Model):
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    badge = models.ForeignKey("accounts.Badge", on_delete=models.PROTECT, related_name="raw_capture_events")
    hexpansion = models.ForeignKey("hexpansion.Hexpansion", on_delete=models.PROTECT, related_name="raw_capture_events")

    # The created_by field here should not be relied upon for scorekeeping.
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Raw capture of {self.hexpansion} by {self.badge} at {self.created_at}"


class CaptureEvent(models.Model):
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    raw_capture_event = models.OneToOneField(RawCaptureEvent, on_delete=models.PROTECT, related_name="capture_event")
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="capture_events",
        limit_choices_to={"installation__isnull": False},
    )

    # The created_by field here should not be relied upon for auditing scorekeeping.
    # However, to make queries easier when generating the scoreboard, we assume that a CaptureEvent
    # is created by the User that owns the badge. We cannot enforce this at the db level.
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="capture_events")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["created_by", "location"], name="one_capture_per_user"),
        ]

    def __str__(self) -> str:
        return f"{self.raw_capture_event.badge.user} captured {self.location} at {self.created_at}"
