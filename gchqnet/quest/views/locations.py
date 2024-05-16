from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from gchqnet.quest.models.location import Location


class LocationDetailView(LoginRequiredMixin, DetailView):
    model = Location
    template_name = "pages/quest/location_detail.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        assert self.request.user.is_authenticated
        capture_event = self.request.user.capture_events.filter(location=self.object).first()
        recent_captures = self.object.capture_events.select_related("created_by").order_by("created_at")[:10]
        return super().get_context_data(capture_event=capture_event, recent_captures=recent_captures, **kwargs)
