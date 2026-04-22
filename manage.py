#!/usr/bin/env python3
"""Django administrative utility."""

from __future__ import annotations

import logging
import os
import sys

logger = logging.getLogger(__name__)


def main() -> None:
    """Run Django administrative commands."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobportal.settings.dev")
    logger.info("Starting manage.py with settings module %s.", os.environ["DJANGO_SETTINGS_MODULE"])
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        logger.error("Django import failed in manage.py: %s", exc)
        raise
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
