from .base import *  # noqa

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "local"  # noqa: S105

ALLOWED_HOSTS = ["*"]

DEBUG = True

# Debug Toolbar
try:
    import debug_toolbar  # noqa
    INSTALLED_APPS.insert(0, "debug_toolbar")  # noqa: F405
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
    INTERNAL_IPS = [
        "127.0.0.1",
        "::1",
    ]
except ImportError:
    pass

# Template Debugging
TEMPLATES[0]["OPTIONS"]["debug"] = True  # noqa

# Import settings from local.py if it exists.
try:
    from .local import *  # noqa: F403
except ImportError:
    pass
