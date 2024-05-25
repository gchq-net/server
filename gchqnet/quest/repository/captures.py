from __future__ import annotations

from typing import Literal, TypedDict

from django.urls import reverse
from notifications.signals import notify

from gchqnet.accounts.models.badge import Badge
from gchqnet.achievements.repository import award_first_capture, handle_location_capture_for_groups
from gchqnet.hexpansion.models import Hexpansion
from gchqnet.quest.models.captures import CaptureEvent, CaptureLog, RawCaptureEvent
from gchqnet.quest.models.location import Location, LocationDifficulty
from gchqnet.quest.models.scores import ScoreRecord

from .scores import update_score_for_user


class CaptureSuccess(TypedDict):
    result: Literal["success"]
    repeat: bool
    location_name: str
    difficulty: str


class CaptureFailure(TypedDict):
    result: Literal["fail"]
    message: str


def record_attempted_capture(
    badge: Badge,
    hexpansion: Hexpansion,
    *,
    rand: bytes,
    hmac: str,
    app_rev: str,
    fw_rev: str,
) -> CaptureSuccess | CaptureFailure:
    # Firstly, record it regardless.
    raw_event = RawCaptureEvent.objects.create(
        badge=badge,
        hexpansion=hexpansion,
        created_by=badge.user,
        rand=rand,
        hmac=hmac,
        app_rev=app_rev,
        fw_rev=fw_rev,
    )

    try:
        location: Location = hexpansion.location
    except Location.DoesNotExist:
        return CaptureFailure(result="fail", message="Hexpansion not installed")

    # Log that a capture attempt of a location was made.
    CaptureLog.objects.create(
        raw_capture_event=raw_event,
        location=location,
        created_by=badge.user,
    )

    if CaptureEvent.objects.filter(created_by=badge.user, location=location).exists():
        return CaptureSuccess(
            result="success",
            repeat=True,
            location_name=location.display_name,
            difficulty=LocationDifficulty(location.difficulty).label,
        )

    # Mark as captured.
    ce = CaptureEvent.objects.create(raw_capture_event=raw_event, location=location, created_by=badge.user)
    ScoreRecord.objects.create(capture_event=ce, user=badge.user, score=location.difficulty)
    notify.send(
        badge.user,
        recipient=badge.user,
        verb="captured",
        target=location,
        description=f"You have gained {location.difficulty} points.",
        actions=[{"href": reverse("quest:location_detail", args=[location.id]), "title": "View"}],
    )
    award_first_capture(location, badge.user)
    handle_location_capture_for_groups(badge.user, location, update_score=False)
    update_score_for_user(badge.user)
    return CaptureSuccess(
        result="success",
        repeat=False,
        location_name=location.display_name,
        difficulty=LocationDifficulty(location.difficulty).label,
    )
