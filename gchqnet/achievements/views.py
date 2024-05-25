from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.core.signing import Signer
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView

from gchqnet.core.mixins import BreadcrumbsMixin
from gchqnet.logistics.mixins import AllowedLogisticsAccessMixin
from gchqnet.quest.models.captures import CaptureEvent

from .models import BasicAchievement, BasicAchievementAwardType, LocationGroup

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


class LocationGroupDetailView(BreadcrumbsMixin, DetailView):
    template_name = "pages/achievements/location_group_detail.html"
    breadcrumbs = [
        (None, "Locations"),
        (None, "Groups"),
    ]
    model = LocationGroup

    def get_breadcrumbs(self) -> list[tuple[str | None, str]]:
        return super().get_breadcrumbs() + [(None, self.object.display_name)]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        locations = self.object.locations.order_by("id").values("id", "display_name", "difficulty")

        if self.request.user.is_authenticated:
            user_found_locations = set(
                self.request.user.capture_events.filter(
                    location__in=[lo["id"] for lo in locations],
                ).values_list("location_id", flat=True)
            )
        else:
            user_found_locations = set()

        location_count = len(locations)
        user_found_all = location_count == len(user_found_locations)

        recent_captures = (
            CaptureEvent.objects.filter(location__in=self.object.locations.all())
            .select_related("created_by")
            .order_by("-created_at")[:10]
        )

        return super().get_context_data(
            locations=locations,
            location_count=location_count,
            user_found_all=user_found_all,
            user_found_locations=user_found_locations,
            recent_captures=recent_captures,
            **kwargs,
        )
