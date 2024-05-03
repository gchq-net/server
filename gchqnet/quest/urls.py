from django.urls import path

from . import views

app_name = "quest"

urlpatterns: list[str] = [
    path("my-finds", views.FindsDashboardView.as_view(), name="dashboard"),
]
