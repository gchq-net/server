from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView

from gchqnet.achievements.repository import award_builtin_basic_achievement
from gchqnet.core.mixins import BreadcrumbsMixin
from gchqnet.quest.repository import get_global_scoreboard, get_recent_events_for_users

if TYPE_CHECKING:
    from gchqnet.accounts.models import UserQuerySet


class GlobalScoreboardView(BreadcrumbsMixin, ListView):
    template_name = "pages/home.html"
    paginate_by = 15
    ordering = ("rank",)
    breadcrumbs = [(None, "Global Leaderboard")]

    def get_search_query(self) -> str:
        if query := self.request.GET.get("search", ""):
            if "'" in query:
                # Award achievement for hacking us
                if self.request.user.is_authenticated:
                    award_builtin_basic_achievement("f42b1ff0-f559-47d0-b6ec-b092169ccf9e", self.request.user)
                messages.info(self.request, 'ERROR:  syntax error at or near "%"LINE 1: %\';')
            return query.strip()
        return query

    def get_queryset(self) -> UserQuerySet:
        return get_global_scoreboard(search_query=self.get_search_query())

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(
            search_query=self.request.GET.get("search", ""),
            **kwargs,
        )


class GlobalRecentActivityView(BreadcrumbsMixin, TemplateView):
    template_name = "pages/quest/recent_activity.html"
    breadcrumbs = [(reverse_lazy("quest:home"), "Global Leaderboard"), (None, "Recent Activity")]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        from gchqnet.accounts.models import User

        player_qs = User.objects.all()

        events, user_found_locations = get_recent_events_for_users(player_qs, current_user=self.request.user)

        return super().get_context_data(
            events=events,
            user_found_locations=user_found_locations,
            **kwargs,
        )
