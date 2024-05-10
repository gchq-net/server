from django.urls import path
from drf_spectacular.views import SpectacularJSONAPIView, SpectacularSwaggerView
from rest_framework import routers

from gchqnet.accounts.api.views import profile
from gchqnet.quest.api.views import GlobalScoreboardAPIView, PrivateScoreboardAPIViewset

router = routers.DefaultRouter()
router.register("quest/scoreboards", PrivateScoreboardAPIViewset, basename="quest_private_scoreboards")

app_name = "api"

urlpatterns = [
    path("users/me/", profile, name="users_me"),
    path("quest/scoreboards/global/", GlobalScoreboardAPIView.as_view(), name="quest_global_scoreboard"),
    path("openapi.json", SpectacularJSONAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="api:schema"), name="docs"),
] + router.urls
