from typing import Any

from django.contrib import messages
from django.db import models
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from gchqnet.core.mixins import BreadcrumbsMixin
from gchqnet.logistics.forms import PlannedLocationCreateForm, PlannedLocationDeleteForm, PlannedLocationEditForm
from gchqnet.logistics.models import PlannedLocation

from .mixins import AllowedLogisticsAccessMixin


class LogisticsHomeView(AllowedLogisticsAccessMixin, BreadcrumbsMixin, TemplateView):
    template_name = "pages/logistics/home.html"
    breadcrumbs = [(None, "Logistics Admin")]


class PlannedLocationsListView(AllowedLogisticsAccessMixin, BreadcrumbsMixin, ListView):
    template_name = "pages/logistics/planned_locations/list.html"
    paginate_by = 15
    breadcrumbs = [(reverse_lazy("logistics:home"), "Logistics Admin"), (None, "Planned Locations")]

    def get_search_query(self) -> str:
        query = self.request.GET.get("search", "")
        return query.strip()

    def get_queryset(self) -> models.QuerySet[PlannedLocation]:
        query = self.get_search_query()
        return PlannedLocation.objects.filter(
            models.Q(display_name__icontains=query)
            | models.Q(internal_name__icontains=query)
            | models.Q(hint__icontains=query)
            | models.Q(description__icontains=query)
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(
            search_query=self.get_search_query(),
            **kwargs,
        )


class PlannedLocationCreateView(AllowedLogisticsAccessMixin, BreadcrumbsMixin, CreateView):
    template_name = "pages/logistics/planned_locations/create.html"
    model = PlannedLocation
    form_class = PlannedLocationCreateForm
    breadcrumbs = [
        (reverse_lazy("logistics:home"), "Logistics Admin"),
        (reverse_lazy("logistics:planned_list"), "Planned Locations"),
        (None, "Create Planned Location"),
    ]

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form: PlannedLocationCreateForm) -> HttpResponse:
        messages.info(self.request, "Successfully created.")
        return super().form_valid(form)

    def get_success_url(self) -> str:
        assert self.object
        return reverse("logistics:planned_edit", args=[self.object.id])


class PlannedLocationEditView(AllowedLogisticsAccessMixin, BreadcrumbsMixin, UpdateView):
    template_name = "pages/logistics/planned_locations/edit.html"
    model = PlannedLocation
    form_class = PlannedLocationEditForm
    breadcrumbs = [
        (reverse_lazy("logistics:home"), "Logistics Admin"),
        (reverse_lazy("logistics:planned_list"), "Planned Locations"),
    ]

    def get_breadcrumbs(self) -> list[tuple[str | None, str]]:
        return super().get_breadcrumbs() + [(None, self.object.internal_name)]

    def get_success_url(self) -> str:
        return reverse("logistics:planned_edit", args=[self.object.id])


class PlannedLocationDeleteView(AllowedLogisticsAccessMixin, BreadcrumbsMixin, DeleteView):  # type: ignore[misc]
    template_name = "pages/logistics/planned_locations/delete.html"
    model = PlannedLocation
    form_class = PlannedLocationDeleteForm

    breadcrumbs = [
        (reverse_lazy("logistics:home"), "Logistics Admin"),
        (reverse_lazy("logistics:planned_list"), "Planned Locations"),
    ]

    def get_breadcrumbs(self) -> list[tuple[str | None, str]]:
        return super().get_breadcrumbs() + [
            (reverse_lazy("logistics:planned_edit", args=[self.object.id]), self.object.internal_name),
            (None, "Delete"),
        ]

    def form_valid(self, form: PlannedLocationDeleteForm) -> HttpResponse:
        messages.info(self.request, "Successfully deleted.")
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse("logistics:planned_list")
