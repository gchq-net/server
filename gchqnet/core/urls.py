from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("gchqnet.quest.urls", namespace="quest")),
    path("", include("gchqnet.content.urls", namespace="content")),
    path("admin/", admin.site.urls),
    path("accounts/", include("gchqnet.accounts.urls", namespace="accounts")),
    path("api/", include("gchqnet.core.api", namespace="api")),
]

if settings.DEBUG:
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))
