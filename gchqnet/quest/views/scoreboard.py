from typing import Any

from django.contrib import messages
from django.views.generic import ListView

from gchqnet.accounts.models import UserQuerySet
from gchqnet.quest.repository import get_global_scoreboard


class GlobalScoreboardView(ListView):
    template_name = "pages/home.html"
    paginate_by = 15
    ordering = ("rank",)

    def get_search_query(self) -> str | None:
        if query := self.request.GET.get("search", ""):
            if "'" in query:
                # TODO: Add achievement for attempting to hack us
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
