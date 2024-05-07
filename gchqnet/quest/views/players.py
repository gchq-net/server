from typing import Any

from django.views.generic import DetailView

from gchqnet.accounts.models import User
from gchqnet.quest.models.captures import CaptureEvent


class PlayerDetailView(DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = "pages/quest/player_detail.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        finds = CaptureEvent.objects.filter(created_by=self.object).select_related("location")

        return super().get_context_data(
            finds=finds,
            **kwargs,
        )
