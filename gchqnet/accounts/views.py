from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from .forms import ProfileUpdateForm
from .models import User

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.forms import BaseModelForm


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
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
