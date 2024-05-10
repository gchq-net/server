from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularJSONAPIView, SpectacularSwaggerView

from gchqnet.core.api import urlpatterns as api_urls

urlpatterns = [
    path("", include("gchqnet.quest.urls", namespace="quest")),
    path("", include("gchqnet.content.urls", namespace="content")),
    path("admin/", admin.site.urls),
    path("accounts/", include("gchqnet.accounts.urls", namespace="accounts")),
    path("api/", include(api_urls)),
    path("api/openapi.json", SpectacularJSONAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="api-docs"),
]

if settings.DEBUG:
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))
