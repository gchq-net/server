from typing import Any

from django.views.generic import TemplateView

from gchqnet.accounts.models.user import User
from gchqnet.core.mixins import BreadcrumbsMixin


class AboutPage(BreadcrumbsMixin, TemplateView):
    template_name = "pages/content/about.html"
    breadcrumbs = [(None, "About GCHQ.NET")]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        admin_count = User.objects.filter(is_superuser=True).count()
        return super().get_context_data(admin_count=admin_count, **kwargs)


class ContactPage(BreadcrumbsMixin, TemplateView):
    template_name = "pages/content/contact.html"
    breadcrumbs = [(None, "Contact Us")]
    extra_context = {"dect_number": "4247", "fax_number": "2999"}


class PlayPage(BreadcrumbsMixin, TemplateView):
    template_name = "pages/content/play.html"
    breadcrumbs = [(None, "How to Play")]


class PlatformsPage(BreadcrumbsMixin, TemplateView):
    template_name = "pages/content/platforms.html"
    breadcrumbs = [(None, "Our Platforms")]


class HoldingPage(TemplateView):
    template_name = "pages/content/holding.html"
