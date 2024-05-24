import os
from pathlib import Path

import sentry_sdk

env = os.environ.copy()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

if "SECRET_KEY" in env:
    SECRET_KEY = env["SECRET_KEY"]

if "ALLOWED_HOSTS" in env:
    ALLOWED_HOSTS = env["ALLOWED_HOSTS"].split(",")

if "CSRF_TRUSTED_ORIGINS" in env:
    CSRF_TRUSTED_ORIGINS = env["CSRF_TRUSTED_ORIGINS"].split(",")

# Application definition
INSTALLED_APPS = [
    "gchqnet.accounts",
    "gchqnet.achievements",
    "gchqnet.content",
    "gchqnet.hexpansion",
    "gchqnet.logistics",
    "gchqnet.quest",
    "crispy_forms",
    "crispy_forms_gds",
    "rest_framework",
    "drf_spectacular",
    "django.contrib.admin",
    "django.contrib.auth",
    "notifications",  # Needs to be after any app that generates notificaiotns
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "gchqnet.core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "gchqnet.core.context_processors.settings_context",
            ],
        },
    },
]

WSGI_APPLICATION = "gchqnet.core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-gb"

TIME_ZONE = "Europe/London"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR.parent / "static"
STATICFILES_DIRS = [
    BASE_DIR / "static",
    BASE_DIR / "static_compiled",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = ["gds"]
CRISPY_TEMPLATE_PACK = "gds"

# Rest Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "gchqnet.accounts.auth.UserTokenAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 20,
}

HIDE_PRIVATE_API_ENDPOINTS = True

SPECTACULAR_SETTINGS = {
    "TITLE": "GCHQ.NET API",
    "DESCRIPTION": "Great Camp Hexpansion Quest API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}


DJANGO_NOTIFICATIONS_CONFIG = {
    "SOFT_DELETE": True,
    "PAGINATE_BY": 10,
    "USE_JSONFIELD": True,
}

# Sentry
SENTRY_SESSION_REPLAY_URI = os.environ.get("SENTRY_SESSION_REPLAY_URI")

if sentry_dsn := os.environ.get("SENTRY_DSN"):
    sentry_environment = os.environ.get("SENTRY_ENVIRONMENT", "development")
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=sentry_environment,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
        # We aren't collecting PII.
        send_default_pii=True,
    )
