"""Konfiguracja pytest i fixtury współdzielone."""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
os.environ.setdefault("CELERY_TASK_ALWAYS_EAGER", "1")
