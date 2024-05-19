from typing import Any

from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView

from gchqnet.accounts.models import User
from gchqnet.achievements.repository import get_achievements_for_user
from gchqnet.core.mixins import BreadcrumbsMixin
from gchqnet.quest.models.captures import CaptureEvent


class BasePlayerDetailView(BreadcrumbsMixin, AccessMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    breadcrumbs = []

    def dispatch(self, request: HttpRequest, *args: Any, current_user: bool, **kwargs: Any) -> HttpResponse:
        if self.request.user.is_anonymous and current_user:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)  # type: ignore[return-value]

    def get_object(self, queryset: models.QuerySet[Any] | None = None) -> models.Model:
        if self.kwargs['current_user']:
            assert self.request.user.is_authenticated
            return self.request.user
        return super().get_object(queryset)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(
            current_user=self.kwargs['current_user'],
            **kwargs,
        )

    def get_breadcrumbs(self) -> list[tuple[str | None, str]]:
        if self.kwargs['current_user']:
            return super().get_breadcrumbs() + [(None, "My Profile")]
        return super().get_breadcrumbs() + [(None, "Players"), (None, self.object.display_name)]


class PlayerFindsView(BasePlayerDetailView):
    template_name = "pages/quest/player_detail_finds.html"

    def dispatch(self, request: HttpRequest, *args: Any, current_user: bool, **kwargs: Any) -> HttpResponse:
        if not current_user and self.get_object() == request.user:
            return redirect('quest:profile')
        return super().dispatch(request, *args, current_user=current_user, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        finds_qs = CaptureEvent.objects.filter(created_by=self.object).select_related("location").order_by("created_at")

        try:
            page_num = int(self.request.GET.get("page", 1))
        except ValueError:
            page_num = 1

        paginator = Paginator(finds_qs, 20)

        page = paginator.page(page_num)

        if self.request.user.is_authenticated:
            viewer_captures = set(
                self.request.user.capture_events.filter(
                    location__in=page.object_list.values("location_id"),  # type: ignore[attr-defined]
                ).values_list("location_id", flat=True),
            )
            finds = ((obj, obj.location_id in viewer_captures) for obj in page.object_list)
        else:
            finds = ((obj, False) for obj in page.object_list)

        return super().get_context_data(
            active_tab="finds",
            finds=finds,
            page_obj=page,
            **kwargs,
        )


class PlayerAchievementsView(BasePlayerDetailView):
    template_name = "pages/quest/player_detail_achievements.html"

    def dispatch(self, request: HttpRequest, *args: Any, current_user: bool, **kwargs: Any) -> HttpResponse:
        if not current_user and self.get_object() == request.user:
            return redirect('quest:profile_achievements')
        return super().dispatch(request, *args, current_user=current_user, **kwargs)


    def get_achievements(self) -> models.QuerySet:
        return get_achievements_for_user(self.object)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        try:
            page_num = int(self.request.GET.get("page", 1))
        except ValueError:
            page_num = 1

        paginator = Paginator(self.get_achievements(), 20)

        return super().get_context_data(
            active_tab="achievements",
            achievement_events=paginator.page(page_num),
            **kwargs,
        )


class MyProfileMapView(LoginRequiredMixin, BreadcrumbsMixin, TemplateView):
    template_name = "pages/quest/profile_map.html"
    breadcrumbs = [(reverse_lazy('quest:profile'), "My Profile"), (None, "Map")]
