from typing import Any

from django.views.generic import TemplateView

from gchqnet.accounts.models.user import User


class AboutPage(TemplateView):
    template_name = "pages/content/about.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        admin_count = User.objects.filter(is_superuser=True).count()
        return super().get_context_data(admin_count=admin_count, **kwargs)


class ContactPage(TemplateView):
    template_name = "pages/content/contact.html"
    extra_context = {"dect_number": "4247", "fax_number": "4248 (TBC)"}


class PlayPage(TemplateView):
    template_name = "pages/content/play.html"
