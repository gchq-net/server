from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginLandingView.as_view(), name="login"),
    path("login/badge/", views.BadgeLoginLandingView.as_view(), name="login_badge"),
    path(
        "login/badge/step-1/",
        views.BadgeLoginUsernamePromptView.as_view(),
        name="login_badge_username",
    ),
    path(
        "login/badge/step-2/",
        views.BadgeLoginChallengePromptView.as_view(),
        name="login_badge_challenge",
    ),
    path(
        "login/credentials/",
        views.CredentialsLoginView.as_view(),
        name="login_credentials",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", views.MyProfileView.as_view(), name="profile")
]
