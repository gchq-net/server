from django.urls import path
from drf_spectacular.views import SpectacularJSONAPIView, SpectacularSwaggerView
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from gchqnet.accounts.api.views import profile


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def get_api_version(request: Request) -> Response:
    """Get the API version."""
    return Response({"version": "1.0.0"})


urlpatterns = [
    path("version/", get_api_version, name="api_get_version"),
    path("users/me/", profile, name="api_users_me"),
    path("openapi.json", SpectacularJSONAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="api-docs"),
]
