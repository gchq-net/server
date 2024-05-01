from typing import Any

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views import View


class PublicUsersOnlyMixin(View):
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in.")
            return redirect("home")

        return super().dispatch(request, *args, **kwargs)  # type: ignore[return-value]
