from typing import Any

from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView

from gchqnet.core.mixins import BreadcrumbsMixin
from gchqnet.quest.models.captures import CaptureEvent
from gchqnet.quest.models.location import Location


class LocationDetailView(BreadcrumbsMixin, DetailView):
    model = Location
    template_name = "pages/quest/location_detail.html"

    def get_capture_event(self) -> CaptureEvent | None:
        if self.request.user.is_authenticated:
            return self.request.user.capture_events.filter(location=self.object).first()
        else:
            return None

    def get_breadcrumbs(self) -> list[tuple[str | None, str]]:
        if self.get_capture_event():
            display_name = self.object.display_name
        else:
            display_name = "???"

        if self.request.user.is_authenticated:
            crumbs = [(reverse_lazy("quest:profile"), "My Profile"), (None, display_name)]
        else:
            crumbs = [(None, "Locations"), (None, display_name)]

        return super().get_breadcrumbs() + crumbs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        recent_captures = self.object.capture_events.select_related("created_by").order_by("created_at")[:10]
        return super().get_context_data(
            capture_event=self.get_capture_event(),
            recent_captures=recent_captures,
            **kwargs,
        )


class MapView(BreadcrumbsMixin, TemplateView):
    template_name = "pages/quest/map.html"

    def get_breadcrumbs(self) -> list[tuple[str | None, str]]:
        if self.request.user.is_authenticated:
            return super().get_breadcrumbs() + [(reverse_lazy("quest:profile"), "My Profile"), (None, "Map")]
        else:
            return super().get_breadcrumbs() + [(None, "Locations"), (None, "Map")]
