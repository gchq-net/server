from typing import Any

from django.core.paginator import Paginator
from django.db import models
from django.views.generic import DetailView

from gchqnet.accounts.models import User
from gchqnet.achievements.repository import get_achievements_for_user
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
        finds_qs = CaptureEvent.objects.filter(created_by=self.object).select_related("location").order_by("created_at")

        try:
            page_num = int(self.request.GET.get("page", 1))
        except ValueError:
            page_num = 1

        paginator = Paginator(finds_qs, 20)

        page = paginator.page(page_num)

        if self.request.user.is_authenticated:
            viewer_captures = set(
                self.request.user.capture_events.filter(
                    location__in=page.object_list.values("location_id"),  # type: ignore[attr-defined]
                ).values_list("location_id", flat=True),
            )
            finds = ((obj, obj.location_id in viewer_captures) for obj in page.object_list)
        else:
            finds = ((obj, False) for obj in page.object_list)

        return super().get_context_data(
            active_tab="finds",
            finds=finds,
            page_obj=page,
            **kwargs,
        )


class PlayerAchievementsView(BasePlayerDetailView):
    template_name = "pages/quest/player_detail_achievements.html"

    def get_achievements(self) -> models.QuerySet:
        return get_achievements_for_user(self.object)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        try:
            page_num = int(self.request.GET.get("page", 1))
        except ValueError:
            page_num = 1

        paginator = Paginator(self.get_achievements(), 20)

        return super().get_context_data(
            active_tab="achievements",
            achievement_events=paginator.page(page_num),
            **kwargs,
        )
