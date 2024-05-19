from typing import Any

from django.core.paginator import Paginator
from django.views.generic import DetailView

from gchqnet.accounts.models import User
from gchqnet.core.mixins import BreadcrumbsMixin
from gchqnet.quest.models.captures import CaptureEvent


class BasePlayerDetailView(BreadcrumbsMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    breadcrumbs = [(None, "Players")]

    def get_breadcrumbs(self) -> list[tuple[str | None, str]]:
        return super().get_breadcrumbs() + [(None, self.object.display_name)]


class PlayerFindsView(BasePlayerDetailView):
    template_name = "pages/quest/player_detail_finds.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        finds = CaptureEvent.objects.filter(created_by=self.object).select_related("location").order_by("created_at")

        try:
            page_num = int(self.request.GET.get("page", 1))
        except ValueError:
            page_num = 1

        paginator = Paginator(finds, 20)

        return super().get_context_data(
            active_tab="finds",
            finds=paginator.page(page_num),
            **kwargs,
        )


class PlayerAchievementsView(BasePlayerDetailView):
    template_name = "pages/quest/player_detail_achievements.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(
            active_tab="achievements",
            **kwargs,
        )
