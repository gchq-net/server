from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import RedirectURLMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, resolve_url
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, TemplateView, UpdateView

from gchqnet.accounts.mixins import LoginPageMixin

from .forms import (
    BadgeLoginChallengeForm,
    BadgeLoginUsernameForm,
    CredentialsLoginForm,
    ProfileUpdateForm,
)
from .models import User

if TYPE_CHECKING:
    from django.db.models import QuerySet


class MyProfileView(LoginRequiredMixin, UpdateView):
    template_name = "pages/accounts/profile.html"
    model = User
    form_class = ProfileUpdateForm
    success_url = reverse_lazy("accounts:profile")

    # @method_decorator(sensitive_post_parameters())
    # @method_decorator(csrf_protect)
    # @method_decorator(login_required)
    # def dispatch(self, *args, **kwargs):
    #    return super().dispatch(*args, **kwargs)

    def get_object(self, queryset: QuerySet[User] | None = None) -> User:
        assert self.request.user.is_authenticated
        return self.request.user

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form: ProfileUpdateForm) -> HttpResponse:
        messages.success(self.request, "Updated profile successfully.")
        form.save()
        # Cycle sessions if password has changed
        update_session_auth_hash(self.request, form.user)
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


class BadgeLoginLandingView(LoginPageMixin, TemplateView):
    template_name = "pages/accounts/login_badge_landing.html"


class BadgeLoginUsernamePromptView(LoginPageMixin, FormView):
    template_name = "pages/accounts/login_badge_username.html"
    form_class = BadgeLoginUsernameForm
    success_url = reverse_lazy("accounts:login_badge_challenge")

    def form_valid(self, form: BadgeLoginUsernameForm) -> HttpResponse:
        self.request.session["badge_login__user_id"] = form.cleaned_data["account_name"].id
        resp = super().form_valid(form)
        if next_q := self.request.GET.get("next"):
            resp["Location"] += f"?next={next_q}"
        return resp


class BadgeLoginChallengePromptView(LoginPageMixin, RedirectURLMixin, FormView):
    template_name = "pages/accounts/login_badge_challenge.html"
    form_class = BadgeLoginChallengeForm

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if "badge_login__user_id" not in request.session:
            return redirect("accounts:login_badge")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()

        # We might see a 500 here sometimes, but that's okay.
        user_id = self.request.session.get("badge_login__user_id", -1)
        kwargs["user"] = User.objects.get(id=user_id, is_active=True)
        return kwargs

    def form_valid(self, form: BadgeLoginChallengeForm) -> HttpResponse:
        del self.request.session["badge_login__user_id"]
        if form.user.is_superuser:
            messages.info(self.request, "Please login with a password for security purposes.")
            return redirect("accounts:login_credentials")
        else:
            auth_login(self.request, form.user)
            return super().form_valid(form)

    def get_default_redirect_url(self) -> str:
        """Return the default redirect URL."""
        if self.next_page:
            return resolve_url(self.next_page)
        else:
            return resolve_url(settings.LOGIN_REDIRECT_URL)
