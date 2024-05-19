from django.urls import path

from . import views

app_name = "quest"

urlpatterns = [
    path("", views.GlobalScoreboardView.as_view(), name="home"),
    path("leaderboards/", views.LeaderboardListView.as_view(), name="leaderboard_list"),
    path("leaderboards/create/", views.LeaderboardCreateView.as_view(), name="leaderboard_create"),
    path(
        "leaderboards/invite/<str:invite_code>/", views.LeaderboardInviteDetailView.as_view(), name="leaderboard_invite"
    ),
    path("leaderboards/<uuid:pk>/", views.LeaderboardDetailView.as_view(), name="leaderboard_detail"),
    path(
        "leaderboards/<uuid:pk>/settings/",
        views.LeaderboardDetailSettingsView.as_view(),
        name="leaderboard_detail_settings",
    ),
    path("locations/<uuid:pk>/", views.LocationDetailView.as_view(), name="location_detail"),
    path("profile/", views.PlayerFindsView.as_view(), name="profile", kwargs={"current_user": True}),
    path(
        "profile/achievements/",
        views.PlayerAchievementsView.as_view(),
        name="profile_achievements",
        kwargs={"current_user": True},
    ),
    path("profile/map/", views.MyProfileMapView.as_view(), name="profile_map"),
    path(
        "players/<str:username>/", views.PlayerFindsView.as_view(), name="player_detail", kwargs={"current_user": False}
    ),
    path(
        "players/<str:username>/achievements/",
        views.PlayerAchievementsView.as_view(),
        name="player_achievements",
        kwargs={"current_user": False},
    ),
]
