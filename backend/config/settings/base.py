import os
from datetime import time as _time
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me-in-production")

DEBUG = os.environ.get("DEBUG", "0").lower() in ("1", "true", "yes")

ALLOWED_HOSTS: list[str] = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "accounts",
    "rooms",
    "reservations",
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

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pl-pl"
TIME_ZONE = "Europe/Warsaw"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Database: Postgres via DATABASE_URL or SQLite fallback
_db_url = os.environ.get("DATABASE_URL")
if _db_url:
    if _db_url.startswith("postgres://"):
        _db_url = "postgresql://" + _db_url[10:]
    _r = urlparse(_db_url)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": (_r.path or "/").lstrip("/") or "postgres",
            "USER": _r.username or "",
            "PASSWORD": _r.password or "",
            "HOST": _r.hostname or "localhost",
            "PORT": str(_r.port or 5432),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# DRF
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}

# JWT (djangorestframework-simplejwt); override via .env: JWT_ACCESS_TOKEN_LIFETIME_MINUTES, JWT_REFRESH_TOKEN_LIFETIME_DAYS
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.environ.get("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", "15"))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.environ.get("JWT_REFRESH_TOKEN_LIFETIME_DAYS", "7"))
    ),
}

# drf-spectacular: /api/schema/ (JSON: ?format=json), /api/docs/ (Swagger UI)
SPECTACULAR_SETTINGS = {
    "TITLE": "MeetSpace Plus API",
    "DESCRIPTION": "API systemu rezerwacji sal konferencyjnych MeetSpace Plus. Uwierzytelnianie JWT (SPA), role admin/user, rezerwacje z holdem 15 min i asynchronicznym wygaszaniem.",
    "VERSION": "1.0.0",
}

# Rezerwacje: godziny robocze (parametryzowalne w create_reservation)
RESERVATION_WORK_START = _time(8, 0)
RESERVATION_WORK_END = _time(18, 0)
RESERVATION_HOLD_MINUTES = 15

# Celery
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ALWAYS_EAGER = os.environ.get("CELERY_TASK_ALWAYS_EAGER", "0").lower() in (
    "1",
    "true",
    "yes",
)

# Celery Beat: reconcile_pending co 5 min (sprzątanie starych pending)
CELERY_BEAT_SCHEDULE = {
    "reconcile-pending": {
        "task": "reservations.tasks.reconcile_pending",
        "schedule": 300.0,  # sekundy
    },
}

# Retry: per-task (bind=True, max_retries, default_retry_delay) w tasks.
#
# Dead-Letter (DLX) w RabbitMQ – jak skonfigurować (bez nadmiarowej konfiguracji):
# 1) Utwórz exchange DLX: rabbitmqadmin declare exchange name=dlx type=direct
# 2) Kolejkę DLQ z argumentami: x-dead-letter-exchange=dlx, x-message-ttl=86400000
#    (opcjonalnie x-dead-letter-routing-key=celery dla przekierowania)
# 3) W RabbitMQ: Policies lub przy deklaracji kolejki Celery ustaw dead_letter_exchange.
#    Dla Celery: task_queues w settings / CELERY_TASK_QUEUES z arguments
#    {"x-dead-letter-exchange": "dlx"} – w zależności od wersji.
# 4) Zbinduj DLQ do exchange dlx (routing key = nazwa kolejki źródłowej lub ogólna).
# Niezrealizowane wiadomości (reject, TTL, max-length) trafią do DLQ.
