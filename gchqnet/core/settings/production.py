import dj_database_url

from .base import *  # noqa

# Explicitly disable debug in production
DEBUG = False

# Read db info from DATABASE_URL
DATABASES['default'] = dj_database_url.config(  # noqa: F405
    conn_max_age=600,
    conn_health_checks=True,
)

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

USE_X_FORWARDED_HOST = True
