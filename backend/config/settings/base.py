"""Shared Django settings for LIMP API."""

from datetime import timedelta
from pathlib import Path

import environ
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = BASE_DIR.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
)

_env_file = BASE_DIR / ".env"
if not _env_file.exists():
    _env_file = REPO_ROOT / ".env"
environ.Env.read_env(_env_file)

SECRET_KEY = env(
    "SECRET_KEY",
    default="dev-insecure-key-min-50-chars-please-replace-in-dotenv-xxxxxxxxxxxxxxxx",
)
DEBUG = env("DEBUG", default=False)

_hosts = env.list("ALLOWED_HOSTS", default=[])
ALLOWED_HOSTS = _hosts if _hosts else (["*"] if DEBUG else [])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "apps.core",
    "apps.users",
    "apps.geography",
    "apps.land",
    "apps.legal",
    "apps.revenue",
    "apps.tasks",
    "apps.documents",
    "apps.audit",
    "apps.telemetry",
    "rest_framework_simplejwt.token_blacklist",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.audit.middleware.AuditMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-in"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.User"

# ---------------------------------------------------------------------------
# Security headers (defence-in-depth — production.py tightens further)
# ---------------------------------------------------------------------------
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

_cors = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOWED_ORIGINS = [o for o in _cors if o]
CORS_ALLOW_CREDENTIALS = True

_csrf = env.list("CSRF_TRUSTED_ORIGINS", default=[])
CSRF_TRUSTED_ORIGINS = [o for o in _csrf if o]


_redis_url = env("REDIS_URL", default="redis://127.0.0.1:6379/0")
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": _redis_url,
        "OPTIONS": {"socket_connect_timeout": 5},
    }
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "apps.users.keycloak.KeycloakJWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_RENDERER_CLASSES": ("apps.core.renderers.EnvelopeJSONRenderer",),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "EXCEPTION_HANDLER": "apps.core.handlers.custom_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {"anon": "100/min", "user": "1000/min"},
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=env.int("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", default=10)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=env.int("JWT_REFRESH_TOKEN_LIFETIME_DAYS", default=7)
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "TOKEN_OBTAIN_SERIALIZER": "apps.users.serializers.LimpTokenObtainPairSerializer",
    "JTI_CLAIM": "jti",
    "USER_ID_CLAIM": "user_id",
    "USER_ID_FIELD": "id",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "LIMP API",
    "DESCRIPTION": "Land Intelligence Management Platform",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default=_redis_url)
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default=_redis_url)
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)
CELERY_TIMEZONE = TIME_ZONE


CELERY_BEAT_SCHEDULE = {
    "celery-heartbeat": {
        "task": "apps.core.tasks.celery_heartbeat",
        "schedule": crontab(minute="*/15"),
    },
}


# --- Event pipeline (optional; empty in local dev / CI) ---
KAFKA_BOOTSTRAP_SERVERS = env("KAFKA_BOOTSTRAP_SERVERS", default="")
KAFKA_AUDIT_TOPIC = env("KAFKA_AUDIT_TOPIC", default="limp.audit")
CASSANDRA_HOSTS = env("CASSANDRA_HOSTS", default="")
CASSANDRA_KEYSPACE = env("CASSANDRA_KEYSPACE", default="limp")


# --- Keycloak OIDC (optional; empty = disabled, SimpleJWT only) ---
KEYCLOAK_SERVER_URL = env("KEYCLOAK_SERVER_URL", default="")
KEYCLOAK_REALM = env("KEYCLOAK_REALM", default="limp")
KEYCLOAK_CLIENT_ID = env("KEYCLOAK_CLIENT_ID", default="limp-api")
