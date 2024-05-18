from django.views.generic import TemplateView

from .mixins import AllowedLogisticsAccessMixin


class LogisticsHomeView(AllowedLogisticsAccessMixin, TemplateView):
    template_name = "pages/logistics/home.html"
