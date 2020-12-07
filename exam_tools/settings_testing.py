# Exam Tools
#
# Copyright (C) 2014 - 2019 Oly Exams Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# pylint: disable=unused-wildcard-import

import sys

# Django settings for exam_tools project.
from .settings_only_sqlite import *

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


ADMINS = ()

ALLOWED_HOSTS = []
MANAGERS = ADMINS
