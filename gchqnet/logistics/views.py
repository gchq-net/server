from typing import Any

from django.db import models
from django.urls import reverse
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from gchqnet.logistics.forms import PlannedLocationCreateForm, PlannedLocationEditForm
from gchqnet.logistics.models import PlannedLocation

from .mixins import AllowedLogisticsAccessMixin


class LogisticsHomeView(AllowedLogisticsAccessMixin, TemplateView):
    template_name = "pages/logistics/home.html"


class PlannedLocationsListView(AllowedLogisticsAccessMixin, ListView):
    template_name = "pages/logistics/planned_locations/list.html"
    paginate_by = 15

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


class PlannedLocationCreateView(AllowedLogisticsAccessMixin, CreateView):
    template_name = "pages/logistics/planned_locations/create.html"
    model = PlannedLocation
    form_class = PlannedLocationCreateForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self) -> str:
        assert self.object
        return reverse("logistics:planned_edit", args=[self.object.id])


class PlannedLocationEditView(AllowedLogisticsAccessMixin, UpdateView):
    template_name = "pages/logistics/planned_locations/edit.html"
    model = PlannedLocation
    form_class = PlannedLocationEditForm

    def get_success_url(self) -> str:
        return reverse("logistics:planned_edit", args=[self.object.id])
