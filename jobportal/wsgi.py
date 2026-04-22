"""WSGI config for the JobPortal project."""

from __future__ import annotations

import logging
import os

from django.core.wsgi import get_wsgi_application


logger = logging.getLogger(__name__)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobportal.settings.dev")
logger.info("Initializing WSGI application with settings module %s.", os.environ["DJANGO_SETTINGS_MODULE"])
application = get_wsgi_application()

