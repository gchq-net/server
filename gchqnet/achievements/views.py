from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.core.signing import Signer
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView

from gchqnet.core.mixins import BreadcrumbsMixin
from gchqnet.logistics.mixins import AllowedLogisticsAccessMixin

from .models import BasicAchievement, BasicAchievementAwardType

if TYPE_CHECKING:
    from django.db import models


class BasicAchievementListView(AllowedLogisticsAccessMixin, BreadcrumbsMixin, ListView):
    template_name = "pages/achievements/basic_achievements/list.html"
    breadcrumbs = [
        (reverse_lazy("logistics:home"), "Logistics Admin"),
        (None, "Basic Achievements"),
    ]
    paginate_by = 15

    def get_search_query(self) -> str:
        query = self.request.GET.get("search", "")
        return query.strip()

    def get_queryset(self) -> models.QuerySet[BasicAchievement]:
        query = self.get_search_query()
        return BasicAchievement.objects.filter(display_name__icontains=query)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(
            search_query=self.get_search_query(),
            **kwargs,
        )


class BasicAchievementDetailView(AllowedLogisticsAccessMixin, BreadcrumbsMixin, DetailView):
    template_name = "pages/achievements/basic_achievements/detail.html"
    breadcrumbs = [
        (reverse_lazy("logistics:home"), "Logistics Admin"),
        (reverse_lazy("achievements:basic_achievements_list"), "Basic Achievements"),
    ]
    model = BasicAchievement

    def get_breadcrumbs(self) -> list[tuple[str | None, str]]:
        return super().get_breadcrumbs() + [(None, self.object.display_name)]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        if self.object.award_type == BasicAchievementAwardType.EXTERNAL:
            assert self.request.user.is_authenticated
            signer = Signer()
            obj = {
                "ba": str(self.object.id),
                "s": 1,
                "u": self.request.user.id,
            }  # sequence number in case we need to revoke
            achievement_token = signer.sign_object(obj)
            return super().get_context_data(achievement_token=achievement_token, **kwargs)
        return super().get_context_data(**kwargs)
