from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.core.signing import BadSignature, Signer
from django.db import models
from django.forms import BaseModelForm
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, FormView, ListView, TemplateView, UpdateView

from gchqnet.accounts.models import User, UserQuerySet
from gchqnet.quest.forms import LeaderboardCreateForm, LeaderboardInviteAcceptDeclineForm, LeaderboardUpdateForm
from gchqnet.quest.models import CaptureEvent, Leaderboard, Location


class GlobalScoreboardView(ListView):
    template_name = "pages/home.html"
    paginate_by = 15

    def get_search_query(self) -> str | None:
        if query := self.request.GET.get("search", ""):
            if "'" in query:
                # TODO: Add achievement for attempting to hack us
                messages.info(self.request, 'ERROR:  syntax error at or near "%"LINE 1: %\';')
            return query.strip()
        return query

    def get_queryset(self) -> UserQuerySet:
        # Only display users who are not administrators.
        qs = User.objects.filter(is_superuser=False)
        qs = qs.only("id", "display_name")
        qs = qs.with_scoreboard_fields().order_by("rank", "capture_count", "display_name")

        if search_query := self.get_search_query():
            # Construct a CTE expression manually as the Django ORM does not support them
            # Hack for case-insensitivity that works across both SQLite and PostgreSQL
            qs = User.objects.raw(
                f"SELECT * FROM ({qs.query}) as u0 WHERE Lower(display_name) LIKE Lower(%s)",  # noqa: S608
                [f"%{search_query}%"],
            )

        return qs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(
            search_query=self.request.GET.get("search", ""),
            **kwargs,
        )


class LeaderboardListView(LoginRequiredMixin, ListView):
    template_name = "pages/quest/leaderboard_list.html"
    paginate_by = 15

    def get_queryset(self) -> models.QuerySet[Leaderboard]:
        assert self.request.user.is_authenticated
        return self.request.user.leaderboards.all()


class LeaderboardDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Leaderboard
    template_name = "pages/quest/leaderboard_detail.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        try:
            page_num = int(self.request.GET.get("page", 1))
        except ValueError:
            page_num = 1

        qs = self.object.members.only("id", "display_name")
        qs = qs.with_scoreboard_fields().order_by("rank", "display_name")

        paginator = Paginator(qs, 15)

        return super().get_context_data(
            page_obj=paginator.page(page_num),
            active_tab="scores",
            **kwargs,
        )

    def test_func(self) -> bool:
        return self.get_object().members.filter(id=self.request.user.id).exists()


class LeaderboardDetailSettings(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Leaderboard
    template_name = "pages/quest/leaderboard_detail_settings.html"
    form_class = LeaderboardUpdateForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        signer = Signer()
        invite_code = signer.sign_object({"l": str(self.object.id), "u": self.request.user.id})
        return super().get_context_data(
            active_tab="settings",
            invite_link=self.request.build_absolute_uri(reverse("quest:leaderboard_invite", args=[invite_code])),
            **kwargs,
        )

    def test_func(self) -> bool:
        return self.get_object().owner == self.request.user

    def get_success_url(self) -> str:
        return reverse_lazy("quest:leaderboard_detail_settings", args=[self.object.id])


class LeaderboardCreateView(LoginRequiredMixin, CreateView):
    model = Leaderboard
    template_name = "pages/quest/leaderboard_create.html"
    form_class = LeaderboardCreateForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        messages.info(self.request, "Welcome. Increase your social credit score by inviting other humans.")
        return super().form_valid(form)

    def get_success_url(self) -> str:
        assert self.object
        return reverse("quest:leaderboard_detail", args=[self.object.id])


class LeaderboardInviteDetailView(LoginRequiredMixin, FormView):
    template_name = "pages/quest/leaderboard_invite.html"
    form_class = LeaderboardInviteAcceptDeclineForm

    def dispatch(self, request: HttpRequest, invite_code: str, *args: Any, **kwargs: Any) -> HttpResponse:
        assert self.request.user.is_authenticated
        signer = Signer()
        try:
            invite = signer.unsign_object(invite_code)
        except BadSignature:
            raise Http404() from None

        leaderboard = get_object_or_404(Leaderboard, id=invite.get("l"))
        inviter = User.objects.get(id=invite.get("u"))

        if leaderboard.members.contains(self.request.user):
            messages.info(request, "You are already a member of this leaderboard.")
            return redirect("quest:leaderboard_detail", leaderboard.pk)

        return super().dispatch(request, *args, leaderboard=leaderboard, inviter=inviter, **kwargs)  # type: ignore[return-value]

    def get(
        self,
        request: HttpRequest,
        *args: Any,
        leaderboard: Leaderboard,
        inviter: User,
        **kwargs: Any,
    ) -> HttpResponse:
        """Handle GET requests: instantiate a blank version of the form."""
        return self.render_to_response(self.get_context_data(leaderboard=leaderboard, inviter=inviter))

    def get_form_kwargs(self) -> dict[str, Any]:
        return {"post_url": self.request.path}

    def post(
        self,
        request: HttpRequest,
        *args: Any,
        leaderboard: Leaderboard,
        inviter: User,
        **kwargs: Any,
    ) -> HttpResponse:
        assert self.request.user.is_authenticated
        accepted = request.GET.get("accept", "true").lower() == "true"

        if accepted:
            leaderboard.members.add(self.request.user)
            leaderboard.save()
            return redirect("quest:leaderboard_detail", leaderboard.id)
        else:
            messages.info(request, "Invitation declined.")
            return redirect("quest:home")


class MyFindsView(LoginRequiredMixin, TemplateView):
    template_name = "pages/quest/my_finds.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        assert self.request.user.is_authenticated
        locations = Location.objects.all()
        captures = self.request.user.capture_events.select_related("location")

        def find_capture(location: Location) -> CaptureEvent | None:
            try:
                return next(capture for capture in captures if capture.location == location)
            except StopIteration:
                return None

        finds = {location: find_capture(location) for location in locations}

        return super().get_context_data(
            finds=finds,
            **kwargs,
        )
