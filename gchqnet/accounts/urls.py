from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("logout", LogoutView.as_view(), name="logout"),
    path("profile", views.ProfileUpdateView.as_view(), name="profile"),
]
