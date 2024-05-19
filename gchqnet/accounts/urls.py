from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("accounts/login/", views.LoginLandingView.as_view(), name="login"),
    path("accounts/login/badge/", views.BadgeLoginLandingView.as_view(), name="login_badge"),
    path(
        "accounts/login/badge/step-1/",
        views.BadgeLoginUsernamePromptView.as_view(),
        name="login_badge_username",
    ),
    path(
        "accounts/login/badge/step-2/",
        views.BadgeLoginChallengePromptView.as_view(),
        name="login_badge_challenge",
    ),
    path(
        "accounts/login/credentials/",
        views.CredentialsLoginView.as_view(),
        name="login_credentials",
    ),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("profile/settings/", views.AccountSettingsView.as_view(), name="settings"),
]
