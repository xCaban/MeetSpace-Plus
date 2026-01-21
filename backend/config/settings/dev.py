import os

import dj_database_url

from .base import *  # noqa: F401, F403

DEBUG = os.environ.get("DEBUG", "1").lower() in ("1", "true", "yes")
ALLOWED_HOSTS = ["*"]

# Override DATABASES with dj_database_url if DATABASE_URL is set
if os.environ.get("DATABASE_URL"):
    DATABASES = {"default": dj_database_url.config(conn_max_age=600)}

# CORS - Development settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
