from django.urls import path
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.views import SpectacularJSONAPIView, SpectacularSwaggerView
from rest_framework import routers

from gchqnet.accounts.api.views import get_token_from_totp, profile
from gchqnet.quest.api.views import GlobalScoreboardAPIView, PrivateScoreboardAPIViewset, my_finds_geojson


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
router.register("scoreboards", PrivateScoreboardAPIViewset, basename="quest_private_scoreboards")

app_name = "api"

urlpatterns = [
    path("users/me/", profile, name="users_me"),
    path("users/me/token/", get_token_from_totp, name="users_totp_token"),
    path("scoreboards/global/", GlobalScoreboardAPIView.as_view(), name="quest_global_scoreboard"),
    path("locations/my-finds/", my_finds_geojson, name="quest_finds_geo"),
    path("openapi.json", SpectacularJSONAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="api:schema"), name="docs"),
] + router.urls
