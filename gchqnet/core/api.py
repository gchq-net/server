from django.urls import path
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.views import SpectacularJSONAPIView, SpectacularSwaggerView
from rest_framework import routers

from gchqnet.accounts.api.views import get_auth_token, profile
from gchqnet.hexpansion.api.views import HexpansionViewset
from gchqnet.logistics.api.views import PlannedLocationViewset
from gchqnet.quest.api.views import (
    BadgeAPIViewset,
    GlobalScoreboardAPIView,
    LocationViewset,
    PrivateScoreboardAPIViewset,
)


class MyAuthenticationScheme(OpenApiAuthenticationExtension):  # type: ignore[no-untyped-call]
    target_class = "gchqnet.accounts.auth.UserTokenAuthentication"
    name = "API Token"  # name used in the schema

    def get_security_definition(self, auto_schema):  # type: ignore  # noqa
        return {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "A user API token with required prefix Token",
        }


router = routers.SimpleRouter()
router.register("badge", BadgeAPIViewset, basename="badge")
router.register("hexpansions", HexpansionViewset, basename="hexpansions")
router.register("scoreboards", PrivateScoreboardAPIViewset, basename="quest_private_scoreboards")
router.register("planned-locations", PlannedLocationViewset, basename="planned_locations")
router.register("locations", LocationViewset, basename="locations")

app_name = "api"

urlpatterns = [
    path("users/me/", profile, name="users_me"),
    path("auth/token/", get_auth_token, name="auth_user_token"),
    path("scoreboards/global/", GlobalScoreboardAPIView.as_view(), name="quest_global_scoreboard"),
    path("openapi.json", SpectacularJSONAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="api:schema"), name="docs"),
] + router.urls
