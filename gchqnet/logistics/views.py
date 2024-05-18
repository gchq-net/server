from django.views.generic import ListView, TemplateView

from gchqnet.logistics.models import PlannedLocation

from .mixins import AllowedLogisticsAccessMixin


class LogisticsHomeView(AllowedLogisticsAccessMixin, TemplateView):
    template_name = "pages/logistics/home.html"


class PlannedLocationsListView(AllowedLogisticsAccessMixin, ListView):
    template_name = "pages/logistics/planned_locations/list.html"
    paginate_by = 15
    model = PlannedLocation
