from typing import Any

from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import render
from django.views import View

from .scoreboard import GlobalScoreboardView


class HomepageView(View):
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        if settings.GAME_MODE == "post":
            return render(request, "pages/quest/thanks-for-playing.html")

        view = GlobalScoreboardView.as_view(is_root_page=True)
        return view(request, *args, **kwargs)
