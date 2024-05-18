from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

from gchqnet.accounts.models.badge import Badge
from gchqnet.hexpansion.models import Hexpansion
from gchqnet.quest.models.captures import CaptureEvent, CaptureLog, RawCaptureEvent
from gchqnet.quest.models.location import Location
from gchqnet.quest.models.scores import ScoreRecord

if TYPE_CHECKING:  # pragma: nocover
    pass


class CaptureResult(TypedDict):
    result: Literal["success", "error", "repeat"]
    message: str


def record_attempted_capture(badge: Badge, hexpansion: Hexpansion) -> CaptureResult:
    # Firstly, record it regardless.
    raw_event = RawCaptureEvent.objects.create(badge=badge, hexpansion=hexpansion, created_by=badge.user)

    try:
        location = hexpansion.location
    except Location.DoesNotExist:
        return CaptureResult(result="error", message="Unable to find that hexpansion")

    # Log that a capture attempt of a location was made.
    CaptureLog.objects.create(raw_capture_event=raw_event, location=location, created_by=badge.user)

    if CaptureEvent.objects.filter(created_by=badge.user, location=location).exists():
        return CaptureResult(result="repeat", message="You have captured this before.")

    # Mark as captured.
    ce = CaptureEvent.objects.create(raw_capture_event=raw_event, location=location, created_by=badge.user)
    ScoreRecord.objects.create(capture_event=ce, user=badge.user, score=location.difficulty)
    return CaptureResult(result="success", message="Successfully captured")
