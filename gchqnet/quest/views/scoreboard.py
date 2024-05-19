from typing import Any

from django.contrib import messages
from django.views.generic import ListView

from gchqnet.accounts.models import UserQuerySet
from gchqnet.achievements.repository import award_builtin_basic_achievement
from gchqnet.core.mixins import BreadcrumbsMixin
from gchqnet.quest.repository import get_global_scoreboard


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
