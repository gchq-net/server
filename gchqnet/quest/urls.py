from django.urls import path

from . import views

app_name = "quest"

urlpatterns = [
    path("", views.GlobalScoreboardView.as_view(), name="home"),
]
