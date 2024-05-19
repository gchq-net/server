from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.core.signing import BadSignature, Signer
from django.db import models
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView

from gchqnet.accounts.models import User
from gchqnet.achievements.models import BasicAchievementEvent
from gchqnet.achievements.repository import award_builtin_basic_achievement
from gchqnet.core.mixins import BreadcrumbsMixin
from gchqnet.quest.forms import LeaderboardCreateForm, LeaderboardInviteAcceptDeclineForm, LeaderboardUpdateForm
from gchqnet.quest.models import Leaderboard
from gchqnet.quest.models.captures import CaptureEvent
from gchqnet.quest.repository import get_private_scoreboard


class LeaderboardListView(LoginRequiredMixin, BreadcrumbsMixin, ListView):
    template_name = "pages/quest/leaderboard_list.html"
    paginate_by = 15
    breadcrumbs = [(None, "My Leaderboards")]

    def get_queryset(self) -> models.QuerySet[Leaderboard]:
        assert self.request.user.is_authenticated
        return self.request.user.leaderboards.order_by("display_name")


class LeaderboardDetailView(LoginRequiredMixin, UserPassesTestMixin, BreadcrumbsMixin, DetailView):
    model = Leaderboard
    template_name = "pages/quest/leaderboard_detail.html"
    breadcrumbs = [(reverse_lazy("quest:leaderboard_list"), "My Leaderboards")]

    def get_breadcrumbs(self) -> list[tuple[str | None, str]]:
        return super().get_breadcrumbs() + [(None, self.object.display_name)]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        try:
            page_num = int(self.request.GET.get("page", 1))
        except ValueError:
            page_num = 1

        qs = get_private_scoreboard(self.object)

        paginator = Paginator(qs, 15)

        return super().get_context_data(
            page_obj=paginator.page(page_num),
            active_tab="scores",
            **kwargs,
        )

    def test_func(self) -> bool:
        return self.get_object().members.filter(id=self.request.user.id).exists()


class LeaderboardDetailActivityView(LoginRequiredMixin, UserPassesTestMixin, BreadcrumbsMixin, DetailView):
    model = Leaderboard
    template_name = "pages/quest/leaderboard_detail_activity.html"
    breadcrumbs = [(reverse_lazy("quest:leaderboard_list"), "My Leaderboards")]

    def get_breadcrumbs(self) -> list[tuple[str | None, str]]:
        return super().get_breadcrumbs() + [(None, self.object.display_name)]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        player_qs = self.object.members.all()

        ce_qs = CaptureEvent.objects.filter(
            created_by__in=player_qs,
        ).annotate(
            player_name=models.F("created_by__display_name"),
            difficulty=models.F("location__difficulty"),
            type=models.Value("capture"),
        )[:20]

        bae_qs = BasicAchievementEvent.objects.filter(
            user__in=player_qs,
        ).annotate(
            player_name=models.F("user__display_name"),
            difficulty=models.F("basic_achievement__difficulty"),
            type=models.Value("basic_achievement"),
        )[:20]

        both = list(ce_qs) + list(bae_qs)

        return super().get_context_data(
            active_tab="activity",
            events=sorted(both, key=lambda x: x.created_at, reverse=True)[:20],
            **kwargs,
        )

    def test_func(self) -> bool:
        return self.get_object().members.filter(id=self.request.user.id).exists()


class LeaderboardDetailSettingsView(LoginRequiredMixin, UserPassesTestMixin, BreadcrumbsMixin, UpdateView):
    model = Leaderboard
    template_name = "pages/quest/leaderboard_detail_settings.html"
    form_class = LeaderboardUpdateForm
    breadcrumbs = [(reverse_lazy("quest:leaderboard_list"), "My Leaderboards")]

    def get_breadcrumbs(self) -> list[tuple[str | None, str]]:
        return super().get_breadcrumbs() + [(None, self.object.display_name)]

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


class LeaderboardCreateView(LoginRequiredMixin, BreadcrumbsMixin, CreateView):
    model = Leaderboard
    template_name = "pages/quest/leaderboard_create.html"
    form_class = LeaderboardCreateForm
    breadcrumbs = [(reverse_lazy("quest:leaderboard_list"), "My Leaderboards"), (None, "Create Leaderboard")]

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        assert self.request.user.is_authenticated

        # Award created or joined a leaderboard
        award_builtin_basic_achievement("193d8853-8000-4261-bdf0-80b73f88e970", self.request.user)

        messages.info(self.request, "Welcome. Increase your social credit score by inviting other humans.")
        return super().form_valid(form)

    def get_success_url(self) -> str:
        assert self.object
        return reverse("quest:leaderboard_detail", args=[self.object.id])


class LeaderboardInviteDetailView(LoginRequiredMixin, BreadcrumbsMixin, FormView):
    template_name = "pages/quest/leaderboard_invite.html"
    form_class = LeaderboardInviteAcceptDeclineForm

    breadcrumbs = [(reverse_lazy("quest:leaderboard_list"), "My Leaderboards")]

    def get_breadcrumbs(self) -> list[tuple[str | None, str]]:
        return super().get_breadcrumbs() + [(None, "Leaderboard Invitation")]

    def dispatch(self, request: HttpRequest, invite_code: str, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        assert request.user.is_authenticated

        signer = Signer()
        try:
            invite = signer.unsign_object(invite_code)
        except BadSignature:
            messages.info(request, "Sorry, that invitation link is not valid.")
            return redirect("quest:home")

        leaderboard = get_object_or_404(Leaderboard, id=invite.get("l"))

        if not leaderboard.enable_invites:
            messages.info(request, "Sorry, that invitation link is no longer valid.")
            return redirect("quest:home")

        inviter = User.objects.get(id=invite.get("u"))

        if leaderboard.members.contains(self.request.user):  # type: ignore[arg-type]
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
            # Award created or joined a leaderboard
            award_builtin_basic_achievement("193d8853-8000-4261-bdf0-80b73f88e970", self.request.user)
            return redirect("quest:leaderboard_detail", leaderboard.id)
        else:
            messages.info(request, "Invitation declined.")
            return redirect("quest:home")
