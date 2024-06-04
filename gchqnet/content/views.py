from django.views.generic import TemplateView

from gchqnet.core.mixins import BreadcrumbsMixin


class AboutPage(BreadcrumbsMixin, TemplateView):
    template_name = "pages/content/about.html"
    breadcrumbs = [(None, "About GCHQ.NET")]


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


class ThanksForPlayingPage(BreadcrumbsMixin, TemplateView):
    template_name = "pages/content/thanks-for-playing.html"
    breadcrumbs = [(None, "Thanks For Playing")]


class HoldingPage(TemplateView):
    template_name = "pages/content/holding.html"
