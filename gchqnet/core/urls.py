import notifications.urls
from django.apps import apps
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("gchqnet.accounts.urls", namespace="accounts")),
    path("", include("gchqnet.achievements.urls", namespace="achievements")),
    path("", include("gchqnet.content.urls", namespace="content")),
    path("", include("gchqnet.quest.urls", namespace="quest")),
    path("", include("django_prometheus.urls")),
    path("admin/", admin.site.urls),
    path("api/", include("gchqnet.core.api", namespace="api")),
    path("logistics/", include("gchqnet.logistics.urls", namespace="logistics")),
    path("notifications/", include(notifications.urls, namespace="notifications")),
]

if apps.is_installed("debug_toolbar"):
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))
