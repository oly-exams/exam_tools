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

# Django settings for exam_tools project.

import subprocess

# Import the OS module and work out our project's paths
import os

SETTINGS_DIR = os.path.dirname(__file__)

PROJECT_PATH = os.path.join(SETTINGS_DIR, os.pardir)
PROJECT_PATH = os.path.abspath(PROJECT_PATH)

TEMPLATE_PATH = os.path.join(PROJECT_PATH, "templates")
STATIC_PATH = os.path.join(PROJECT_PATH, "static")

EVENT_TEMPLATE_PATH = os.path.join(TEMPLATE_PATH, "events", "demo")

SITE_URL = "http://127.0.0.1:8000"

VERSION = "3.0.0"

try:
    GIT_HEAD_DATE = str(
        subprocess.check_output(
            ["git", "log", "-1", "--date=short", "--pretty=format:%ci"]
        ),
        "utf-8",
    ).strip()
except Exception:  # pylint: disable=broad-except
    GIT_HEAD_DATE = ""
try:
    GIT_HEAD_SHA = "({})".format(
        str(
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]), "utf-8"
        ).strip()
    )
except Exception:  # pylint: disable=broad-except
    GIT_HEAD_SHA = ""

VERSION_DATE = f"{GIT_HEAD_DATE} {GIT_HEAD_SHA}"

OFFICIAL_DELEGATION = "Official"

# Demo mode shows watermark and turns off some functionality
DEMO_MODE = False
# Allow user sign-up for demo
DEMO_SIGN_UP = False

# Adds a watermark to PDFs shown to non-staff
ADD_DELEGATION_WATERMARK = False

# Defines if there is a 'banner' page for the delegation prints
ADD_DELEGATION_PRINT_BANNER = False

# Defines whether a QR code should be printed on the cover sheets
CODE_ON_COVER_SHEET = False

# Defines whether answer sheets are produced
NO_ANSWER_SHEETS = False

# Defines wheter translated answer sheets are possible
ONLY_OFFICIAL_ANSWER_SHEETS = False

# Defines whether a QR code should be printed on the student sheets
# (Answer sheets and Working sheets)
CODE_WITHOUT_QR = False

# Defines whether official marks are shown before submission for moderation
SHOW_OFFICIAL_MARKS_IMMEDIATELY = False

# Defines whether delegations can accept official marks without moderation
ACCEPT_MARKS_BEFORE_MODERATION = False

# Defines whether final marks need to be signed off by a delegation
SIGN_OFF_FINAL_MARKS = False

# Shows the remaining delegations in voting fullscreen view.
VOTING_FULLSCREEN_DISPLAY_REMAINING_USERS = False

# Activates autotranslate
AUTO_TRANSLATE = True
# The API-key for google translate
GOOGLE_TRANSLATE_SERVICE_ACCOUNT_KEY = r"""{}"""
# A list of languages for auto translate
AUTO_TRANSLATE_LANGUAGES = [
    {"language": "af", "name": "Afrikaans"},
    {"language": "sq", "name": "Albanian"},
    {"language": "am", "name": "Amharic"},
    {"language": "ar", "name": "Arabic"},
    {"language": "hy", "name": "Armenian"},
    {"language": "az", "name": "Azerbaijani"},
    {"language": "eu", "name": "Basque"},
    {"language": "be", "name": "Belarusian"},
    {"language": "bn", "name": "Bengali"},
    {"language": "bs", "name": "Bosnian"},
    {"language": "bg", "name": "Bulgarian"},
    {"language": "ca", "name": "Catalan"},
    {"language": "ceb", "name": "Cebuano"},
    {"language": "ny", "name": "Chichewa"},
    {"language": "zh", "name": "Chinese (Simplified)"},
    {"language": "zh-TW", "name": "Chinese (Traditional)"},
    {"language": "co", "name": "Corsican"},
    {"language": "hr", "name": "Croatian"},
    {"language": "cs", "name": "Czech"},
    {"language": "da", "name": "Danish"},
    {"language": "nl", "name": "Dutch"},
    {"language": "en", "name": "English"},
    {"language": "eo", "name": "Esperanto"},
    {"language": "et", "name": "Estonian"},
    {"language": "tl", "name": "Filipino"},
    {"language": "fi", "name": "Finnish"},
    {"language": "fr", "name": "French"},
    {"language": "fy", "name": "Frisian"},
    {"language": "gl", "name": "Galician"},
    {"language": "ka", "name": "Georgian"},
    {"language": "de", "name": "German"},
    {"language": "el", "name": "Greek"},
    {"language": "gu", "name": "Gujarati"},
    {"language": "ht", "name": "Haitian Creole"},
    {"language": "ha", "name": "Hausa"},
    {"language": "haw", "name": "Hawaiian"},
    {"language": "iw", "name": "Hebrew"},
    {"language": "hi", "name": "Hindi"},
    {"language": "hmn", "name": "Hmong"},
    {"language": "hu", "name": "Hungarian"},
    {"language": "is", "name": "Icelandic"},
    {"language": "ig", "name": "Igbo"},
    {"language": "id", "name": "Indonesian"},
    {"language": "ga", "name": "Irish"},
    {"language": "it", "name": "Italian"},
    {"language": "ja", "name": "Japanese"},
    {"language": "jw", "name": "Javanese"},
    {"language": "kn", "name": "Kannada"},
    {"language": "kk", "name": "Kazakh"},
    {"language": "km", "name": "Khmer"},
    {"language": "ko", "name": "Korean"},
    {"language": "ku", "name": "Kurdish (Kurmanji)"},
    {"language": "ky", "name": "Kyrgyz"},
    {"language": "lo", "name": "Lao"},
    {"language": "la", "name": "Latin"},
    {"language": "lv", "name": "Latvian"},
    {"language": "lt", "name": "Lithuanian"},
    {"language": "lb", "name": "Luxembourgish"},
    {"language": "mk", "name": "Macedonian"},
    {"language": "mg", "name": "Malagasy"},
    {"language": "ms", "name": "Malay"},
    {"language": "ml", "name": "Malayalam"},
    {"language": "mt", "name": "Maltese"},
    {"language": "mi", "name": "Maori"},
    {"language": "mr", "name": "Marathi"},
    {"language": "mn", "name": "Mongolian"},
    {"language": "my", "name": "Myanmar (Burmese)"},
    {"language": "ne", "name": "Nepali"},
    {"language": "no", "name": "Norwegian"},
    {"language": "ps", "name": "Pashto"},
    {"language": "fa", "name": "Persian"},
    {"language": "pl", "name": "Polish"},
    {"language": "pt", "name": "Portuguese"},
    {"language": "pa", "name": "Punjabi"},
    {"language": "ro", "name": "Romanian"},
    {"language": "ru", "name": "Russian"},
    {"language": "sm", "name": "Samoan"},
    {"language": "gd", "name": "Scots Gaelic"},
    {"language": "sr", "name": "Serbian"},
    {"language": "st", "name": "Sesotho"},
    {"language": "sn", "name": "Shona"},
    {"language": "sd", "name": "Sindhi"},
    {"language": "si", "name": "Sinhala"},
    {"language": "sk", "name": "Slovak"},
    {"language": "sl", "name": "Slovenian"},
    {"language": "so", "name": "Somali"},
    {"language": "es", "name": "Spanish"},
    {"language": "su", "name": "Sundanese"},
    {"language": "sw", "name": "Swahili"},
    {"language": "sv", "name": "Swedish"},
    {"language": "tg", "name": "Tajik"},
    {"language": "ta", "name": "Tamil"},
    {"language": "te", "name": "Telugu"},
    {"language": "th", "name": "Thai"},
    {"language": "tr", "name": "Turkish"},
    {"language": "uk", "name": "Ukrainian"},
    {"language": "ur", "name": "Urdu"},
    {"language": "uz", "name": "Uzbek"},
    {"language": "vi", "name": "Vietnamese"},
    {"language": "cy", "name": "Welsh"},
    {"language": "xh", "name": "Xhosa"},
    {"language": "yi", "name": "Yiddish"},
    {"language": "yo", "name": "Yoruba"},
    {"language": "zu", "name": "Zulu"},
]

# Url of documentation
DOCS_URL = "/docs"

# Path to tex binaries and Inkscape binary
try:
    TEXBIN = os.path.dirname(
        str(subprocess.check_output(["which", "xelatex"]), "utf-8").strip()
    )
except Exception:  # pylint: disable=broad-except
    TEXBIN = "/opt/texbin"
INKSCAPE_BIN = "inkscape"

# Celery SETTINGS_DIR
CELERY_ACCEPT_CONTENT = ["pickle", "json", "msgpack", "yaml"]
CELERY_TASK_SERIALIZER = "pickle"
CELERY_RESULT_SERIALIZER = "pickle"
CELERY_RESULT_BACKEND = "django-db"
CELERY_TASK_TIME_LIMIT = (
    15 * 60
)  # task execution time limit in seconds before the workers are killed using SIGKILL

# Printing system
PRINTER_QUEUES = {
    # 'technopark.printer-1': {
    #   'name': 'Technopark 1',
    #   'host': '',
    #   'queue': 'printer-1',
    #   'auth_token': '',
    #   'opts': {'Duplex': 'None', 'ColourModel': 'Greyscale', 'Staple': '1PLU'},
    #   'required_perm': 'ipho_core.print_technopark',
    # },
    # 'technopark.printer-2': {
    #   'name': 'Technopark 2',
    #   'host': '',
    #   'queue': 'printer-2',
    #   'auth_token': '',
    #   'opts': {'Duplex': 'None', 'ColourModel': 'Greyscale', 'Staple': '1PLU'},
    #   'required_perm': 'ipho_core.print_technopark',
    # },
    # 'irchel.printer-1': {
    #   'name': 'Irchel 1',
    #   'host': '',
    #   'queue': 'printer-1',
    #   'auth_token': '',
    #   'opts': {'Duplex': 'None', 'ColourModel': 'Colour', 'Staple': '1PLU'},
    #   'required_perm': 'ipho_core.print_irchel',
    # },
    # 'irchel.printer-2': {
    #   'name': 'Irchel 2',
    #   'host': '',
    #   'queue': 'printer-2',
    #   'auth_token': '',
    #   'opts': {'Duplex': 'None', 'ColourModel': 'Colour', 'Staple': '1PLU'},
    #   'required_perm': 'ipho_core.print_irchel',
    # },
    # 'irchel.printer-3': {
    #   'name': 'Irchel 3',
    #   'host': '',
    #   'queue': 'printer-3',
    #   'auth_token': '',
    #   'opts': {'Duplex': 'None', 'ColourModel': 'Colour', 'Staple': '1PLU'},
    #   'required_perm': 'ipho_core.print_irchel',
    # },
    "generic.printer-1": {
        "name": "Generic printer",
        "host": "",
        "queue": "printer-1",
        "auth_token": "",
        "opts": {"Duplex": "None", "ColourModel": "Colour", "Staple": "1PLU"},
        "required_perm": "ipho_core.print_irchel",
    },
}

EXAM_TOOLS_API_KEYS = {
    "PDF Worker": "KeyChangeMe",
    "Scan Worker": "KeyChangeMe",
}

# Random draw
RANDOM_DRAW_ON_SUBMISSION = True

# Push Notifications
ENABLE_PUSH = False
PUSH_PUBLIC_KEY = ""
PUSH_PRIVATE_KEY = ""

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

TEST_RUNNER = "django.test.runner.DiscoverRunner"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = "Europe/Zurich"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ""

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ""

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ""

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = "/static/"

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    STATIC_PATH,
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            TEMPLATE_PATH,
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "exam_tools.context_processors.ipho_context",
            ],
        },
    },
]

MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "ipho_exam.middleware.IphoExamExceptionsMiddleware",
)

AUTHENTICATION_BACKENDS = (
    "ipho_core.backends.TokenLoginBackend",
    "django.contrib.auth.backends.ModelBackend",
)

ROOT_URLCONF = "exam_tools.urls"

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "exam_tools.wsgi.application"

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    #'django.contrib.sites',
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Uncomment the next line to enable the admin:
    "django.contrib.admin",
    # Uncomment the next line to enable admin documentation:
    "django.contrib.admindocs",
    "django.contrib.humanize",
    "crispy_forms",
    "django_ace",
    "django_celery_results",
    "rest_framework",
    "rest_framework_swagger",
    "polymorphic",
    "ipho_core",
    "ipho_control",
    "ipho_exam",
    "ipho_poll",
    "ipho_marking",
    "ipho_download",
    "ipho_print",
    # 'django_extensions', # Some useful utils, e.g. graph models
)

CRISPY_TEMPLATE_PACK = "bootstrap3"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAdminUser",
        "ipho_exam.permissions.HasValidApiKey",
    ],
    "PAGE_SIZE": 10,
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
}

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Api Token": {
            "type": "apiKey",
            "name": "APIKEY",
            "in": "header",
        }
    },
    "DOC_EXPANSION": "list",
    "VALIDATOR_URL": None,
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "default": {"format": "[%(asctime)s - %(name)s] - %(levelname)s - %(message)s"},
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
        },
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[%(server_time)s] %(message)s",
        },
    },
    "handlers": {
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
    },
    "loggers": {
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        }
    },
}
