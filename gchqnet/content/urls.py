from django.conf import settings
from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "content"

urlpatterns = [
    path("about/", views.AboutPage.as_view(), name="about"),
    path("play/", views.PlayPage.as_view(), name="play"),
    path("contact/", views.ContactPage.as_view(), name="contact"),
]

if settings.DEBUG:
    urlpatterns += [
        path("400/", TemplateView.as_view(template_name="400.html")),
        path("403/", TemplateView.as_view(template_name="403.html")),
        path("404/", TemplateView.as_view(template_name="404.html")),
        path("500/", TemplateView.as_view(template_name="500.html")),
    ]
