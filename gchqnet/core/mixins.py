from typing import Any

from django.urls import reverse
from django.views.generic.base import ContextMixin


class BreadcrumbsMixin(ContextMixin):
    breadcrumbs: list[tuple[str, str]] = []

    def get_breadcrumbs(self) -> list[tuple[str, str]]:
        """Returns a list of tuples (url, display)."""
        return [(reverse("quest:home"), "GCHQ.NET")] + self.breadcrumbs

    def get_context_data(self, **kwargs: dict[str, Any]) -> dict[str, Any]:
        return super().get_context_data(
            breadcrumbs=self.get_breadcrumbs(),
            **kwargs,
        )
