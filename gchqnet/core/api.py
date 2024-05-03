from django.urls import path
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
    path('version/', get_api_version, name='api_get_version'),
    path('users/me/', profile, name='api_users_me'),
]
