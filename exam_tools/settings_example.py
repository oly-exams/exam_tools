# pylint: disable=unused-wildcard-import

import sys

# Django settings for exam_tools project.
from .settings_common import *

# Printing paths for sanity's sake
print("Settings directory:", SETTINGS_DIR, file=sys.stderr)
print("Project root:", PROJECT_PATH, file=sys.stderr)
print("Templates:", TEMPLATE_PATH, file=sys.stderr)
print("Static:", STATIC_PATH, file=sys.stderr)

DEBUG = True

# GOOGLE_TRANSLATE_SERVICE_ACCOUNT_KEY = r"""{}"""

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
    ("Michele Dolfi", "michele.dolfi@gmail.com"),
)


MANAGERS = ADMINS

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        "NAME": "ipho.db",  # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        "USER": "",
        "PASSWORD": "",
        "HOST": "",  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        "PORT": "",  # Set to empty string for default.
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = "^t-a=sbo_05wq!*(x4mpv7kw&u_n=5js$lwadn_yx(bzx*fzjw"
