from __future__ import annotations

from collections.abc import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import resolve


class PublicAccessMiddleware:
    EXCLUDED_PATHS: set[tuple[str | None, str]] = {
        ("content", "holding"),
        (None, "logout"),
        (None, "prometheus-django-metrics"),
    }

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:  # noqa: F821
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if (not (settings.PUBLIC_MODE or request.user.is_authenticated)) and self._request_is_affected(request):
            return redirect("content:holding")

        response = self.get_response(request)
        return response

    def _request_is_affected(self, request: HttpRequest) -> bool:
        path_info = resolve(request.path_info)

        if path_info.app_name in {"admin", "api"}:
            return False

        # Django Debug Toolbar
        if settings.DEBUG and path_info.app_name == "djdt":  # pragma: nocover
            return False

        path = (path_info.app_name or None, path_info.url_name)
        return path not in self.EXCLUDED_PATHS
