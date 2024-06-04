from typing import Any

from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import render
from django.views import View

from gchqnet.accounts.models.user import User
from gchqnet.quest.models.captures import CaptureEvent, CaptureLog
from gchqnet.quest.models.leaderboard import Leaderboard
from gchqnet.quest.models.location import Location

from .scoreboard import GlobalScoreboardView


class HomepageView(View):
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        if settings.GAME_MODE == "post":
            context = {
                "player_count": User.objects.count(),
                "hexpansion_count": Location.objects.count(),
                "capture_count": CaptureEvent.objects.count(),
                "capture_log_count": CaptureLog.objects.count(),
                "leaderboard_count": Leaderboard.objects.count(),
            }
            return render(request, "pages/quest/thanks-for-playing.html", context)

        view = GlobalScoreboardView.as_view(is_root_page=True)
        return view(request, *args, **kwargs)
