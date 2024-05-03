from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from random import randint

class FindsDashboardView(LoginRequiredMixin, TemplateView):

    template_name = "pages/quest/finds_dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(
            tiles=[
                {"id": i, "found": randint(0,10)%2==0} for i in range(90)
            ],
            **kwargs,
        )