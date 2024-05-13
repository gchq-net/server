from .base import *  # noqa

# Explicitly disable debug in production
DEBUG = False

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
