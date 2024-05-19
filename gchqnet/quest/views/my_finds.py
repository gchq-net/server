from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from gchqnet.core.mixins import BreadcrumbsMixin
from gchqnet.quest.models import CaptureEvent, Location


class MyFindsView(LoginRequiredMixin, BreadcrumbsMixin, TemplateView):
    template_name = "pages/quest/my_finds.html"
    breadcrumbs = [(None, "My Finds")]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        assert self.request.user.is_authenticated
        locations = Location.objects.order_by("difficulty", "display_name")
        captures = self.request.user.capture_events.select_related("location")

        def find_capture(location: Location) -> CaptureEvent | None:
            try:
                return next(capture for capture in captures if capture.location == location)
            except StopIteration:
                return None

        finds = {location: find_capture(location) for location in locations}

        return super().get_context_data(
            finds=finds,
            **kwargs,
        )
