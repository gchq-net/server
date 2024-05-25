import os

import dj_database_url

from .base import *  # noqa

# Explicitly disable debug in production
DEBUG = False

# Read db info from DATABASE_URL
DATABASES["default"] = dj_database_url.config(  # type: ignore  # noqa: F405
    conn_max_age=600,
    conn_health_checks=True,
)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
    }
}

HIDE_PRIVATE_API_ENDPOINTS = os.environ.get("GCHQNET_HIDE_PRIVATE_API_ENDPOINTS", "true").lower() == "true"

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

USE_X_FORWARDED_HOST = True

PUBLIC_MODE = os.environ.get("PUBLIC_MODE", False)