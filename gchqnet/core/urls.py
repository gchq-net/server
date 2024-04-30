from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("gchqnet.accounts.urls", namespace="accounts")),
    path("", lambda r: render(r, "pages/home.html")),
]
