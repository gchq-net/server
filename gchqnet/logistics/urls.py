from django.urls import path

from . import views

app_name = "logistics"

urlpatterns = [
    path("", views.LogisticsHomeView.as_view(), name="home"),
]
