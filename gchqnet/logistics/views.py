from typing import Any

from django.contrib import messages
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, FormView, ListView, TemplateView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from gchqnet.core.mixins import BreadcrumbsMixin
from gchqnet.logistics.forms import (
    LocationEditForm,
    PlannedLocationCreateForm,
    PlannedLocationDeleteForm,
    PlannedLocationDeployForm,
    PlannedLocationEditForm,
)
from gchqnet.logistics.models import PlannedLocation
from gchqnet.quest.models.location import Coordinates, Location

from .mixins import AllowedLogisticsAccessMixin


class LogisticsHomeView(AllowedLogisticsAccessMixin, BreadcrumbsMixin, TemplateView):
    template_name = "pages/logistics/home.html"
    breadcrumbs = [(None, "Logistics Admin")]


class LocationsListView(AllowedLogisticsAccessMixin, BreadcrumbsMixin, ListView):
    template_name = "pages/logistics/locations/list.html"
    paginate_by = 15
    breadcrumbs = [(reverse_lazy("logistics:home"), "Logistics Admin"), (None, "Locations")]

    def get_search_query(self) -> str:
        query = self.request.GET.get("search", "")
        return query.strip()

    def get_queryset(self) -> models.QuerySet[Location]:
        query = self.get_search_query()
        return Location.objects.filter(
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


class LocationEditView(AllowedLogisticsAccessMixin, BreadcrumbsMixin, UpdateView):
    model = Location
    form_class = LocationEditForm
    template_name = "pages/logistics/locations/edit.html"
    breadcrumbs = [
        (reverse_lazy("logistics:home"), "Logistics Admin"),
        (reverse_lazy("logistics:locations_list"), "Locations"),
    ]

    def get_breadcrumbs(self) -> list[tuple[str | None, str]]:
        return super().get_breadcrumbs() + [(None, self.object.display_name)]

    def get_success_url(self) -> str:
        return reverse("logistics:locations_edit", args=[self.object.id])

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        if self.object.coordinates:
            kwargs["lat"] = self.object.coordinates.lat
            kwargs["long"] = self.object.coordinates.long
        return kwargs

    def form_valid(self, form: LocationEditForm) -> HttpResponse:
        if (
            self.object.coordinates
            and (lat := form.cleaned_data.get("lat"))
            and (long := form.cleaned_data.get("long", None))
        ):
            self.object.coordinates.lat = lat
            self.object.coordinates.long = long
            self.object.coordinates.save()
        return super().form_valid(form)


class LocationMapView(AllowedLogisticsAccessMixin, BreadcrumbsMixin, TemplateView):
    template_name = "pages/logistics/locations/map.html"

    breadcrumbs = [
        (reverse_lazy("logistics:home"), "Logistics Admin"),
        (reverse_lazy("logistics:locations_list"), "Locations"),
        (None, "Locations Map"),
    ]


class PlannedLocationsListView(AllowedLogisticsAccessMixin, BreadcrumbsMixin, ListView):
    template_name = "pages/logistics/planned_locations/list.html"
    paginate_by = 15
    breadcrumbs = [(reverse_lazy("logistics:home"), "Logistics Admin"), (None, "Planned Locations")]

    def get_search_query(self) -> str:
        query = self.request.GET.get("search", "")
        return query.strip()

    def get_queryset(self) -> models.QuerySet[PlannedLocation]:
        query = self.get_search_query()
        return PlannedLocation.objects.filter(is_installed=False).filter(
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
    form_class = PlannedLocationEditForm
    breadcrumbs = [
        (reverse_lazy("logistics:home"), "Logistics Admin"),
        (reverse_lazy("logistics:planned_list"), "Planned Locations"),
    ]

    def get_queryset(self) -> models.QuerySet[PlannedLocation]:
        return PlannedLocation.objects.filter(is_installed=False)

    def get_breadcrumbs(self) -> list[tuple[str | None, str]]:
        return super().get_breadcrumbs() + [(None, self.object.internal_name)]

    def get_success_url(self) -> str:
        return reverse("logistics:planned_edit", args=[self.object.id])


class PlannedLocationDeployView(AllowedLogisticsAccessMixin, BreadcrumbsMixin, SingleObjectMixin, FormView):
    template_name = "pages/logistics/planned_locations/deploy.html"
    form_class = PlannedLocationDeployForm
    breadcrumbs = [
        (reverse_lazy("logistics:home"), "Logistics Admin"),
        (reverse_lazy("logistics:planned_list"), "Planned Locations"),
    ]

    def get_queryset(self) -> models.QuerySet[PlannedLocation]:
        return PlannedLocation.objects.filter(is_installed=False)

    def get_initial(self) -> dict[str, Any]:
        planned = self.get_object()
        return {
            "lat": planned.lat,
            "long": planned.long,
        }

    def get_breadcrumbs(self) -> list[tuple[str | None, str]]:
        planned = self.get_object()
        return super().get_breadcrumbs() + [(None, planned.internal_name), (None, "Deploy")]

    def form_valid(self, form: PlannedLocationDeployForm) -> HttpResponse:
        assert self.request.user.is_authenticated

        location = Location()
        location.display_name = self.object.display_name
        location.internal_name = self.object.internal_name
        location.hint = self.object.hint
        location.description = self.object.description
        location.difficulty = self.object.difficulty
        location.hexpansion = form.cleaned_data["hexpansion"]
        location.install_image = form.cleaned_data["image"]
        location.created_by = self.request.user
        location.save()

        Coordinates.objects.create(
            location=location,
            lat=form.cleaned_data["lat"],
            long=form.cleaned_data["long"],
            created_by=self.request.user,
        )
        self.object.is_installed = True
        self.object.save(update_fields=["is_installed"])
        messages.success(self.request, f"Successfully deployed {location.display_name}")
        return redirect("logistics:planned_list")

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        if not self.object.is_ready_to_deploy():
            messages.warning(request, "Please fill out all details before deploying.")
            return redirect("logistics:planned_edit", self.object.id)
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        self.object = self.get_object()
        if not self.object.is_ready_to_deploy():
            messages.warning(request, "Please fill out all details before deploying.")
            return redirect("logistics:planned_edit", self.object.id)

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class PlannedLocationDeleteView(AllowedLogisticsAccessMixin, BreadcrumbsMixin, DeleteView):  # type: ignore[misc]
    template_name = "pages/logistics/planned_locations/delete.html"
    model = PlannedLocation
    form_class = PlannedLocationDeleteForm

    breadcrumbs = [
        (reverse_lazy("logistics:home"), "Logistics Admin"),
        (reverse_lazy("logistics:planned_list"), "Planned Locations"),
    ]

    def get_queryset(self) -> models.QuerySet[PlannedLocation]:
        return PlannedLocation.objects.filter(is_installed=False)

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


class PlannedLocationMapView(AllowedLogisticsAccessMixin, BreadcrumbsMixin, TemplateView):
    template_name = "pages/logistics/planned_locations/map.html"

    breadcrumbs = [
        (reverse_lazy("logistics:home"), "Logistics Admin"),
        (reverse_lazy("logistics:planned_list"), "Planned Locations"),
        (None, "Planning Map"),
    ]
