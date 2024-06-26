from __future__ import annotations

import uuid

from django.core.validators import RegexValidator
from django.db import models
from django_prometheus.models import ExportModelOperationsMixin

from .location import Location


class RawCaptureEvent(ExportModelOperationsMixin("raw_capture_event"), models.Model):  # type: ignore[misc]
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    badge = models.ForeignKey("accounts.Badge", on_delete=models.PROTECT, related_name="raw_capture_events")
    hexpansion = models.ForeignKey("hexpansion.Hexpansion", on_delete=models.PROTECT, related_name="raw_capture_events")

    rand = models.BinaryField(max_length=32)
    hmac = models.CharField(
        max_length=64,
        validators=[
            RegexValidator("^[0-9a-f]{64}$", "The HMAC does not appear to be in the correct format."),
        ],
    )
    app_rev = models.CharField(verbose_name="App Revision", max_length=20)
    fw_rev = models.CharField(verbose_name="Firmware Revision", max_length=20)

    # The created_by field here should not be relied upon for scorekeeping.
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Raw capture of {self.hexpansion} by {self.badge} at {self.created_at}"


class CaptureLog(ExportModelOperationsMixin("capture_log"), models.Model):  # type: ignore[misc]
    """
    A log of a RawCaptureEvent being mapped to a real location.

    Unlike CaptureEvents, these can be duplicated. There is no unique constraint.

    Do not use for scoring. This is just a log of hexpansion -> location mapping at raw capture time.
    """

    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    raw_capture_event = models.OneToOneField(RawCaptureEvent, on_delete=models.PROTECT, related_name="capture_log")
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="capture_logs",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.raw_capture_event.badge.user} attempted capture of {self.location} at {self.created_at}"


class CaptureEvent(ExportModelOperationsMixin("capture_event"), models.Model):  # type: ignore[misc]
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    raw_capture_event = models.OneToOneField(RawCaptureEvent, on_delete=models.PROTECT, related_name="capture_event")
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="capture_events",
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
