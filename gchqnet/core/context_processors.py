from django.conf import settings
from django.http import HttpRequest


def settings_context(request: HttpRequest) -> dict[str, str]:
    return {
        "SENTRY_SESSION_REPLAY_URI": getattr(settings, "SENTRY_SESSION_REPLAY_URI"),
    }
