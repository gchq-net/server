from __future__ import annotations

import uuid
from typing import Any
from uuid import uuid4

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.deconstruct import deconstructible
from django_prometheus.models import ExportModelOperationsMixin


class LocationDifficulty(models.IntegerChoices):
    EASY = 10
    MEDIUM = 15
    HARD = 20
    INSANE = 30
    IMPOSSIBLE = 50


@deconstructible
class UploadToPathAndRename:
    def __call__(self, instance: Any, filename: str) -> str:
        ext = filename.split(".")[-1]
        filename = f"{uuid4().hex}.{ext}"
        # return the whole path to the file
        return f"location_img/{filename}"


class Location(ExportModelOperationsMixin("location"), models.Model):  # type: ignore[misc]
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
    hint = models.CharField(
        "Hint",
        help_text="This name is shown to players to help them find the location.",
        max_length=60,
    )

    # Internal fields
    internal_name = models.CharField(
        "Internal name",
        help_text="This name is shown to admins and should be descriptive.",
        max_length=50,
        blank=True,
    )
    description = models.TextField(help_text="Further description of the location of the installation.", blank=True)
    hexpansion = models.OneToOneField("hexpansion.Hexpansion", on_delete=models.PROTECT, related_name="location")
    install_image = models.ImageField(upload_to=UploadToPathAndRename(), null=True)

    difficulty = models.IntegerField(choices=LocationDifficulty)

    # The creator is assumed to be the user that installed the location.
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("internal_name", "display_name")

    def __str__(self) -> str:
        return self.internal_name or self.display_name


class Coordinates(ExportModelOperationsMixin("coordinates"), models.Model):  # type: ignore[misc]
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    location = models.OneToOneField(Location, on_delete=models.CASCADE, related_name="coordinates")
    lat = models.DecimalField(
        "Latitude", max_digits=16, decimal_places=13, validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    long = models.DecimalField(
        "Longitude", max_digits=16, decimal_places=13, validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"({self.lat},{self.long})"
