from django.urls import path

from . import views

app_name = "achievements"

urlpatterns = [
    path("logistics/basic-achievements/", views.BasicAchievementListView.as_view(), name="basic_achievements_list"),
    path(
        "logistics/basic-achievements/create/",
        views.BasicAchievementCreateView.as_view(),
        name="basic_achievements_create",
    ),
    path(
        "logistics/basic-achievements/<uuid:pk>/",
        views.BasicAchievementDetailView.as_view(),
        name="basic_achievements_detail",
    ),
    path("locations/groups/<uuid:pk>/", views.LocationGroupDetailView.as_view(), name="location_group_detail"),
    path("claim/<str:claim_code>/", views.BasicAchivementClaimView.as_view(), name="basic_achievement_claim"),
]
