from __future__ import annotations

from typing import Literal, TypedDict
from uuid import UUID

from gchqnet.accounts.models.badge import Badge
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
    rand: int,
    hmac: str,
    app_rev: str,
    fw_rev: str,
    wifi_bssid: str,
    wifi_channel: int,
    wifi_rssi: int,
) -> CaptureSuccess | CaptureFailure:
    # Firstly, record it regardless.
    raw_event = RawCaptureEvent.objects.create(
        badge=badge,
        hexpansion=hexpansion,
        created_by=badge.user,
        rand=UUID(int=rand),
        hmac=hmac,
        app_rev=app_rev,
        fw_rev=fw_rev,
        wifi_bssid=wifi_bssid,
        wifi_channel=wifi_channel,
        wifi_rssi=wifi_rssi,
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
    update_score_for_user(badge.user)
    return CaptureSuccess(
        result="success",
        repeat=False,
        location_name=location.display_name,
        difficulty=LocationDifficulty(location.difficulty).label,
    )
