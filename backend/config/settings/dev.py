import os

import dj_database_url

from .base import *  # noqa: F401, F403

DEBUG = os.environ.get("DEBUG", "1").lower() in ("1", "true", "yes")
ALLOWED_HOSTS = ["*"]

# Override DATABASES with dj_database_url if DATABASE_URL is set
if os.environ.get("DATABASE_URL"):
    DATABASES = {"default": dj_database_url.config(conn_max_age=600)}
