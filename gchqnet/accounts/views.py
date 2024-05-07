from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView

from gchqnet.accounts.mixins import LoginPageMixin

from .forms import CredentialsLoginForm, ProfileUpdateForm
from .models import User

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.forms import BaseModelForm


class MyProfileView(LoginRequiredMixin, UpdateView):
    template_name = "pages/accounts/profile.html"
    model = User
    form_class = ProfileUpdateForm
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset: QuerySet[User] | None = None) -> User:
        assert self.request.user.is_authenticated
        return self.request.user

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, "Updated profile successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        assert self.request.user.is_authenticated
        return super().get_context_data(
            badges=self.request.user.badges.all(),
            **kwargs,
        )


class LoginLandingView(LoginPageMixin, TemplateView):
    template_name = "pages/accounts/login_landing.html"


class CredentialsLoginView(LoginPageMixin, DjangoLoginView):
    template_name = "pages/accounts/login_credentials.html"
    form_class = CredentialsLoginForm


class BadgeLoginView(LoginPageMixin, TemplateView):
    template_name = "pages/accounts/login_badge.html"
