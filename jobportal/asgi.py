"""ASGI config for the JobPortal project."""

from __future__ import annotations

import logging
import os

from django.core.asgi import get_asgi_application

logger = logging.getLogger(__name__)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobportal.settings.dev")
logger.info("Initializing ASGI application with settings module %s.", os.environ["DJANGO_SETTINGS_MODULE"])
application = get_asgi_application()
