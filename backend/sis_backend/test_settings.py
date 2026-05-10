from .settings import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Disable WhiteNoise for tests if needed, or just keep it
MIDDLEWARE = [m for m in MIDDLEWARE if "WhiteNoiseMiddleware" not in m]  # noqa: F405
