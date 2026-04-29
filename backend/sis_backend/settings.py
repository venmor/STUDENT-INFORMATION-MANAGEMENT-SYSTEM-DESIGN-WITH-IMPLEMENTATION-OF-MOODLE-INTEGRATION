import os
import json
from pathlib import Path
from datetime import timedelta


BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


def env_int(name: str, default: int = 0) -> int:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return int(value)


def env_json(name: str, default=None):
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return json.loads(value)


SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = env_bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", default="127.0.0.1,localhost")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework_simplejwt.token_blacklist",
    "rest_framework",
    "apps.accounts",
    "apps.academics",
    "apps.students",
    "apps.integration",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.accounts.middleware.APIAccessControlMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "sis_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "sis_backend.wsgi.application"
ASGI_APPLICATION = "sis_backend.asgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ["MYSQL_DATABASE"],
        "USER": os.environ["MYSQL_USER"],
        "PASSWORD": os.environ["MYSQL_PASSWORD"],
        "HOST": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "PORT": int(os.getenv("MYSQL_PORT", "3306")),
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {
        "NAME": "apps.accounts.validators.ComplexityPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]


LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Lusaka"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

MOODLE_BASE_URL = os.getenv("MOODLE_BASE_URL", "").strip().rstrip("/")
MOODLE_WS_TOKEN = os.getenv("MOODLE_WS_TOKEN", "").strip()
MOODLE_DEFAULT_USERNAME = os.getenv("MOODLE_USERNAME", "admin").strip() or "admin"
MOODLE_DEFAULT_CATEGORY_ID = env_int("MOODLE_DEFAULT_CATEGORY_ID", default=0)
MOODLE_STUDENT_ROLE_ID = env_int("MOODLE_STUDENT_ROLE_ID", default=0)
MOODLE_EDITING_TEACHER_ROLE_ID = env_int("MOODLE_EDITING_TEACHER_ROLE_ID", default=0)
MOODLE_INSTITUTION = os.getenv("MOODLE_INSTITUTION", "Student Information System").strip() or "Student Information System"
MOODLE_GRADE_SOURCE = os.getenv("MOODLE_GRADE_SOURCE", "modern_sis").strip() or "modern_sis"
MOODLE_SYNC_TIMEOUT = env_int("MOODLE_SYNC_TIMEOUT", default=10)

LTI_PLATFORM_ISSUER_ALLOWLIST = env_list(
    "LTI_PLATFORM_ISSUER_ALLOWLIST",
    default=os.getenv("LTI_TOOL_ISSUER", "").strip(),
)
LTI_CLIENT_ID = os.getenv("LTI_CLIENT_ID", "").strip()
LTI_DEPLOYMENT_ID = os.getenv("LTI_DEPLOYMENT_ID", "").strip()
LTI_PRIVATE_KEY = os.getenv("LTI_PRIVATE_KEY", "")
LTI_PRIVATE_KEY_FILE = os.getenv("LTI_PRIVATE_KEY_FILE", "").strip()
LTI_PUBLIC_KEY = os.getenv("LTI_PUBLIC_KEY", "")
LTI_PUBLIC_KEY_FILE = os.getenv("LTI_PUBLIC_KEY_FILE", "").strip()
LTI_KEY_ID = os.getenv("LTI_KEY_ID", "modern-sis-lti-key").strip() or "modern-sis-lti-key"
LTI_PLATFORM_AUTH_LOGIN_URL = os.getenv("LTI_PLATFORM_AUTH_LOGIN_URL", "").strip()
LTI_PLATFORM_AUTH_TOKEN_URL = os.getenv("LTI_PLATFORM_AUTH_TOKEN_URL", "").strip()
LTI_PLATFORM_JWKS_URL = os.getenv("LTI_PLATFORM_JWKS_URL", "").strip()
LTI_PLATFORM_JWKS_JSON = env_json("LTI_PLATFORM_JWKS_JSON", default={})
LTI_PLATFORM_PUBLIC_KEY = os.getenv("LTI_PLATFORM_PUBLIC_KEY", "")
LTI_PLATFORM_PUBLIC_KEY_FILE = os.getenv("LTI_PLATFORM_PUBLIC_KEY_FILE", "").strip()
LTI_PLATFORM_JWKS_TIMEOUT = env_int("LTI_PLATFORM_JWKS_TIMEOUT", default=10)
LTI_LAUNCH_SUCCESS_REDIRECT_BASE = os.getenv("LTI_LAUNCH_SUCCESS_REDIRECT_BASE", "").strip().rstrip("/")
LTI_STATE_TTL_SECONDS = env_int("LTI_STATE_TTL_SECONDS", default=600)
LTI_SESSION_TTL_SECONDS = env_int("LTI_SESSION_TTL_SECONDS", default=3600)
LTI_SESSION_COOKIE_NAME = os.getenv("LTI_SESSION_COOKIE_NAME", "sis_lti_session").strip() or "sis_lti_session"
LTI_SESSION_COOKIE_SECURE = env_bool("LTI_SESSION_COOKIE_SECURE", default=False)
LTI_SESSION_COOKIE_SAMESITE = os.getenv("LTI_SESSION_COOKIE_SAMESITE", "Lax").strip() or "Lax"
