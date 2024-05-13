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
        views.LeaderboardDetailSettings.as_view(),
        name="leaderboard_detail_settings",
    ),
    path("my-finds/", views.MyFindsView.as_view(), name="my_finds"),
    path("my-finds/map/", views.MyFindsMapView.as_view(), name="my_finds_map"),
]
