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
from gchqnet.core.mixins import BreadcrumbsMixin

from .forms import (
    BadgeLoginChallengeForm,
    BadgeLoginUsernameForm,
    BaseProfileUpdateForm,
    CredentialsLoginForm,
    PasswordProfileUpdateForm,
    TOTPProfileUpdateForm,
)
from .models import User

if TYPE_CHECKING:  # pragma: nocover
    from django.db.models import QuerySet


class MyProfileView(LoginRequiredMixin, BreadcrumbsMixin, UpdateView):
    template_name = "pages/accounts/profile.html"
    model = User
    form_class = PasswordProfileUpdateForm
    success_url = reverse_lazy("accounts:profile")
    breadcrumbs = [(None, "My Profile")]

    def get_form_class(self) -> type[BaseProfileUpdateForm]:
        if self.object.password and self.object.has_usable_password():
            return PasswordProfileUpdateForm
        else:
            return TOTPProfileUpdateForm

    def get_object(self, queryset: QuerySet[User] | None = None) -> User:
        assert self.request.user.is_authenticated
        return self.request.user

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.object
        return kwargs

    def form_valid(self, form: BaseProfileUpdateForm) -> HttpResponse:
        self.object = form.save()

        if form.cleaned_data.get("new_password2"):
            messages.success(self.request, "Your password has been changed.")
            # Cycle sessions if password has changed
            update_session_auth_hash(self.request, self.object)
        else:
            messages.success(self.request, "Updated profile successfully.")

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        assert self.request.user.is_authenticated
        return super().get_context_data(
            badges=self.request.user.badges.all(),
            **kwargs,
        )


class LoginLandingView(LoginPageMixin, BreadcrumbsMixin, TemplateView):
    template_name = "pages/accounts/login_landing.html"
    breadcrumbs = [(None, "Login to GCHQ.NET")]


class CredentialsLoginView(LoginPageMixin, BreadcrumbsMixin, DjangoLoginView):
    template_name = "pages/accounts/login_credentials.html"
    form_class = CredentialsLoginForm
    breadcrumbs = [(reverse_lazy("accounts:login"), "Login to GCHQ.NET"), (None, "Login using your password")]


class BadgeLoginLandingView(LoginPageMixin, BreadcrumbsMixin, TemplateView):
    template_name = "pages/accounts/login_badge_landing.html"
    breadcrumbs = [(reverse_lazy("accounts:login"), "Login to GCHQ.NET"), (None, "Login using your badge")]


class BadgeLoginUsernamePromptView(LoginPageMixin, BreadcrumbsMixin, FormView):
    template_name = "pages/accounts/login_badge_username.html"
    form_class = BadgeLoginUsernameForm
    success_url = reverse_lazy("accounts:login_badge_challenge")
    breadcrumbs = [(reverse_lazy("accounts:login"), "Login to GCHQ.NET"), (None, "Login using your badge")]

    def form_valid(self, form: BadgeLoginUsernameForm) -> HttpResponse:
        self.request.session["badge_login__user_id"] = form.cleaned_data["account_name"].id
        resp = super().form_valid(form)
        if next_q := self.request.GET.get("next"):
            resp["Location"] += f"?next={next_q}"
        return resp


class BadgeLoginChallengePromptView(LoginPageMixin, RedirectURLMixin, BreadcrumbsMixin, FormView):
    template_name = "pages/accounts/login_badge_challenge.html"
    form_class = BadgeLoginChallengeForm
    breadcrumbs = [(reverse_lazy("accounts:login"), "Login to GCHQ.NET"), (None, "Login using your badge")]

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
