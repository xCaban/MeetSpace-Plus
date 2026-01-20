import os

from .base import *  # noqa: F401, F403

DEBUG = os.environ.get("DEBUG", "1").lower() in ("1", "true", "yes")
ALLOWED_HOSTS = ["*"]
