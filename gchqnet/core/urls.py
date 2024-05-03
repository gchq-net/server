from django.conf import settings
from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path

from gchqnet.core.api import urlpatterns as api_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("gchqnet.accounts.urls", namespace="accounts")),
    path("api/", include(api_urls)),
    path("quest/", include("gchqnet.quest.urls", namespace="quest")),
    path("", lambda r: render(r, "pages/home.html"), name="home"),
]

if settings.DEBUG:
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))
