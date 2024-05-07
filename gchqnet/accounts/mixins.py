from typing import Any

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic.base import ContextMixin, View


class LoginPageMixin(ContextMixin, View):
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in.")
            return redirect("quest:home")

        return super().dispatch(request, *args, **kwargs)  # type: ignore[return-value]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        if next_q := self.request.GET.get("next"):
            query_string = f"?next={next_q}"
        else:
            query_string = ""
        return super().get_context_data(
            query_string=query_string,
            **kwargs,
        )
