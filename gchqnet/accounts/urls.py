from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginLandingView.as_view(), name="login"),
    path("login/badge/", views.BadgeLoginView.as_view(), name="login_badge"),
    path("login/credentials/", views.CredentialsLoginView.as_view(), name="login_credentials"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", views.ProfileUpdateView.as_view(), name="profile"),
]
