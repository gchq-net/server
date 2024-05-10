from django.urls import path

from . import views

app_name = "content"

urlpatterns = [
    path("about/", views.AboutPage.as_view(), name="about"),
    path("contact/", views.ContactPage.as_view(), name="contact"),
]
