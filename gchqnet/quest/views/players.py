from typing import Any

from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView

from gchqnet.accounts.models import User
from gchqnet.achievements.repository import get_achievements_for_user
from gchqnet.core.mixins import BreadcrumbsMixin
from gchqnet.quest.models.captures import CaptureEvent
from gchqnet.quest.models.location import Location
from gchqnet.quest.repository.scoreboards import get_recent_events_for_users


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
        if self.kwargs["current_user"]:
            assert self.request.user.is_authenticated
            return self.request.user
        return super().get_object(queryset)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        find_count = self.object.get_capture_count()

        return super().get_context_data(
            current_user=self.kwargs["current_user"],
            find_count=find_count,
            to_find_count=Location.objects.count() - find_count,
            **kwargs,
        )

    def get_breadcrumbs(self) -> list[tuple[str | None, str]]:
        if self.kwargs["current_user"]:
            return super().get_breadcrumbs() + [(None, "My Profile")]
        return super().get_breadcrumbs() + [(None, "Players"), (None, self.object.display_name)]


class PlayerFindsView(BasePlayerDetailView):
    template_name = "pages/quest/player_detail_finds.html"

    def dispatch(self, request: HttpRequest, *args: Any, current_user: bool, **kwargs: Any) -> HttpResponse:
        if not current_user and self.get_object() == request.user:
            return redirect("quest:profile")
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
            return redirect("quest:profile_achievements")
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


class PlayerRecentActivityView(BasePlayerDetailView):
    template_name = "pages/quest/player_detail_activity.html"

    def dispatch(self, request: HttpRequest, *args: Any, current_user: bool, **kwargs: Any) -> HttpResponse:
        if not current_user and self.get_object() == request.user:
            return redirect("quest:profile_activity")
        return super().dispatch(request, *args, current_user=current_user, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        events, user_found_locations = get_recent_events_for_users(
            User.objects.filter(id=self.object.id), current_user=self.request.user
        )

        return super().get_context_data(
            active_tab="activity",
            events=events,
            user_found_locations=user_found_locations,
            **kwargs,
        )


class MyProfileUnfoundLocationsView(LoginRequiredMixin, BreadcrumbsMixin, DetailView):
    template_name = "pages/quest/player_detail_to_find.html"
    breadcrumbs = [(reverse_lazy("quest:profile"), "My Profile")]

    def get_object(self) -> User:  # type: ignore[override]
        assert self.request.user.is_authenticated
        return self.request.user

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        found_locations = self.object.capture_events.values("location")
        locations_to_find = Location.objects.exclude(id__in=found_locations)

        try:
            page_num = int(self.request.GET.get("page", 1))
        except ValueError:
            page_num = 1

        paginator = Paginator(locations_to_find, 20)
        page = paginator.page(page_num)

        return super().get_context_data(
            active_tab="to_find",
            current_user=True,
            find_count=Location.objects.count() - paginator.count,
            to_find_count=paginator.count,
            locations=page,
            **kwargs,
        )
