from typing import Any

from django.contrib import messages
from django.views.generic import ListView

from gchqnet.accounts.models import User, UserQuerySet


class GlobalScoreboardView(ListView):
    template_name = "pages/home.html"
    paginate_by = 15

    def get_search_query(self) -> str | None:
        if query := self.request.GET.get("search", ""):
            if "'" in query:
                # TODO: Add achievement for attempting to hack us
                messages.info(self.request, 'ERROR:  syntax error at or near "%"LINE 1: %\';')
            return query.strip()
        return query

    def get_queryset(self) -> UserQuerySet:
        # Only display users who are not administrators.
        qs = User.objects.filter(is_superuser=False)
        qs = qs.only("id", "display_name")
        qs = qs.with_scoreboard_fields().order_by("rank", "capture_count", "display_name")

        if search_query := self.get_search_query():
            # Construct a CTE expression manually as the Django ORM does not support them
            # Hack for case-insensitivity that works across both SQLite and PostgreSQL
            qs = User.objects.raw(
                f"SELECT * FROM ({qs.query}) as u0 WHERE Lower(display_name) LIKE Lower(%s)",  # noqa: S608
                [f"%{search_query}%"],
            )

        return qs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(
            search_query=self.request.GET.get("search", ""),
            **kwargs,
        )
