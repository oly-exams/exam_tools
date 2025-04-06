# pylint: disable=unused-wildcard-import

import sys

# Django settings for exam_tools project.
from .settings_a_dev import *

# Printing paths for sanity's sake
print("Settings directory:", SETTINGS_DIR, file=sys.stderr)
print("Project root:", PROJECT_PATH, file=sys.stderr)
print("Templates:", TEMPLATE_PATH, file=sys.stderr)
print("Staticfiles Dirs:", STATICFILES_DIRS, file=sys.stderr)

DEBUG = True
# TEMPLATE_DEBUG = DEBUG

TEST_RUNNER = "xmlrunner.extra.djangotestrunner.XMLTestRunner"
TEST_OUTPUT_DIR = "unittest_reports"
TEST_OUTPUT_FILE_NAME = "results.xml"
TEST_OUTPUT_VERBOSE = 2

CONTROL_SHOW_PHASES_ON_HOME = True
ACCEPT_MARKS_BEFORE_MODERATION = True
SIGN_OFF_FINAL_MARKS = True
ADD_DELEGATION_WATERMARK = False
INCLUDE_COVER = True

ADMINS = ()
MANAGERS = ADMINS

SITE_URL = "http://django-server:8000"
ALLOWED_HOSTS += (
    "django-server",
    "localhost",
)
