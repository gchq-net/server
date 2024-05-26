from .dev import *  # noqa

HEXPANSION_ROOT_KEY = bytearray.fromhex("a" * 64)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
}
