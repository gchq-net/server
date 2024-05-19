from typing import Any

from django.contrib.auth.mixins import AccessMixin
from django.http import HttpRequest, HttpResponse


class AllowedLogisticsAccessMixin(AccessMixin):
    """Verify that the current user is allowed to access logistics."""

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not (request.user.is_authenticated and request.user.is_superuser):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)  # type: ignore[misc]
