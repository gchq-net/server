from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from gchqnet.core.mixins import BreadcrumbsMixin
from gchqnet.quest.models.captures import CaptureEvent
from gchqnet.quest.models.location import Location


class LocationDetailView(LoginRequiredMixin, BreadcrumbsMixin, DetailView):
    model = Location
    template_name = "pages/quest/location_detail.html"
    breadcrumbs = [(None, "Locations")]

    def get_capture_event(self) -> CaptureEvent | None:
        assert self.request.user.is_authenticated
        return self.request.user.capture_events.filter(location=self.object).first()

    def get_breadcrumbs(self) -> list[tuple[str | None, str]]:
        if self.get_capture_event():
            display_name = self.object.display_name
        else:
            display_name = "???"

        return super().get_breadcrumbs() + [(None, display_name)]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        recent_captures = self.object.capture_events.select_related("created_by").order_by("created_at")[:10]
        return super().get_context_data(
            capture_event=self.get_capture_event(),
            recent_captures=recent_captures,
            **kwargs,
        )
