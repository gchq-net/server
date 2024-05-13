from django.apps import apps
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("gchqnet.quest.urls", namespace="quest")),
    path("", include("gchqnet.content.urls", namespace="content")),
    path("admin/", admin.site.urls),
    path("accounts/", include("gchqnet.accounts.urls", namespace="accounts")),
    path("api/", include("gchqnet.core.api", namespace="api")),
]

if apps.is_installed('debug_toolbar'):
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))
