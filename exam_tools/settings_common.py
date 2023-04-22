# Exam Tools
#
# Copyright (C) 2014 - 2021 Oly Exams Team
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

# pylint: disable = consider-using-f-string

SETTINGS_DIR = os.path.dirname(__file__)

PROJECT_PATH = os.path.join(SETTINGS_DIR, os.pardir)
PROJECT_PATH = os.path.abspath(PROJECT_PATH)

TEMPLATE_PATH = os.path.join(PROJECT_PATH, "templates")
STATIC_PATH = os.path.join(PROJECT_PATH, "static")
DOCUMENT_PATH = os.path.join(PROJECT_PATH, "media")
LOCALE_PATHS = [os.path.join(PROJECT_PATH, "locale")]

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

# Determines whether the unoffical banner on top of every web page displayed
OFFICIALLY_SUPPORTED = False

# record users logging in and out
# (will produce these entries, via exam-tools logger info)
# CHE User 172.20.0.1 successfully logged in at 12/08/2020 08:44:41
# CHE User 172.20.0.1 successfully logged out at 12/08/2020 08:44:47
RECORD_USER_LOGIN_LOGOUT_IPS = True

# Show a summary of the exam control phases on the home page
CONTROL_SHOW_PHASES_ON_HOME = True

# Adds a watermark to PDFs shown to non-staff
ADD_DELEGATION_WATERMARK = True

# Defines if there is a 'banner' page showing the name of the delegation for the official prints
# to facilitate sorting the printed pages
ADD_DELEGATION_PRINT_BANNER = True

# Defines whether a QR code should be printed on the cover sheets
CODE_ON_COVER_SHEET = False

# Defines whether answer sheets are produced
NO_ANSWER_SHEETS = False

# Defines wheter translated answer sheets are possible
ONLY_OFFICIAL_ANSWER_SHEETS = False

# Defines whether the QR code should *not* be printed on the student sheets
# (Answer sheets and Working sheets)
# ```CODE_WITHOUT_QR = True``` means: do not print QR codes on any sheets
# ```CODE_WITHOUT_QR = False```means: print QR codes on Answer and Working sheets
CODE_WITHOUT_QR = False

# Defines whether delegations can accept official marks without moderation
ACCEPT_MARKS_BEFORE_MODERATION = True

# Defines whether final marks need to be signed off by a delegation
SIGN_OFF_FINAL_MARKS = False

# Defines wheter negative marks are allowed
ALLOW_NEGATIVE_MARKS = False

# Shows the remaining delegations in voting fullscreen view.
VOTING_FULLSCREEN_DISPLAY_REMAINING_USERS = False

# Activates autotranslate
AUTO_TRANSLATE = False
# The API-key for google translate
GOOGLE_TRANSLATE_SERVICE_ACCOUNT_KEY = r"""{}"""
# The API-key for deepl
DEEPL_API_KEY = ""
# DeepL and google translate use different codes for the languages
# This dictionary maps the AUTO_TRANSLATE_LANGUAGES to the DeepL nomenclature
# These languages are also preferrably translated with DeepL
DEEPL_SOURCE_LANGUAGES = {
    "DE",
    "EN",
    "FR",
    "IT",
    "JA",
    "ES",
    "NL",
    "PL",
    "PT",
    "RU",
    "ZH",
}

DEEPL_TARGET_LANGUAGES = {
    "DE",
    "EN-GB",
    "EN-US",
    "FR",
    "IT",
    "JA",
    "ES",
    "NL",
    "PL",
    "PT-PT",
    "PT-BR",
    "RU",
    "ZH",
}

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
    {"language": "zh-CN", "name": "Chinese (Simplified)"},
    {"language": "zh-TW", "name": "Chinese (Traditional)"},
    {"language": "co", "name": "Corsican"},
    {"language": "hr", "name": "Croatian"},
    {"language": "cs", "name": "Czech"},
    {"language": "da", "name": "Danish"},
    {"language": "nl", "name": "Dutch"},
    {"language": "en-GB", "name": "English (British)"},
    {"language": "en-US", "name": "English (American)"},
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
    {"language": "rw", "name": "Kinyarwanda"},
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
    {"language": "or", "name": "Odia (Oriya)"},
    {"language": "ps", "name": "Pashto"},
    {"language": "fa", "name": "Persian"},
    {"language": "pl", "name": "Polish"},
    {"language": "pt-PT", "name": "Portuguese"},
    {"language": "pt-BR", "name": "Portuguese (Brazilian)"},
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
    {"language": "tt", "name": "Tatar"},
    {"language": "te", "name": "Telugu"},
    {"language": "th", "name": "Thai"},
    {"language": "tr", "name": "Turkish"},
    {"language": "tk", "name": "Turkmen"},
    {"language": "uk", "name": "Ukrainian"},
    {"language": "ur", "name": "Urdu"},
    {"language": "ug", "name": "Uyghur"},
    {"language": "uz", "name": "Uzbek"},
    {"language": "vi", "name": "Vietnamese"},
    {"language": "cy", "name": "Welsh"},
    {"language": "xh", "name": "Xhosa"},
    {"language": "yi", "name": "Yiddish"},
    {"language": "yo", "name": "Yoruba"},
    {"language": "zu", "name": "Zulu"},
    {"language": "he", "name": "Hebrew"},
]

# A map from Language.style -> auto translate languages
STYLES_TO_AUTO_TRANSLATE_MAPPING = {
    "irish": "ga",
    "montenegrin": "",
    "telugu": "te",
    "tajik": "tg",
    "amharic": "am",
    "romanian": "ro",
    "filipino": "tl",
    "serbian": "sr",
    "icelandic": "is",
    "tamil": "ta",
    "czech": "cs",
    "malayalam": "ml",
    "danish": "da",
    "german": "de",
    "persian": "fa",
    "dutch": "nl",
    "welsh": "cy",
    "asturian": "",
    "kurdish": "ku",
    "kyrgyz": "ky",
    "interlingua": "",
    "arabic": "ar",
    "afrikaans": "af",
    "portuguese": "pt",
    "ukrainian": "uk",
    "thai": "th",
    "occitan": "",
    "macedonian": "mk",
    "kannada": "kn",
    "cantonese": "",
    "turkish": "tr",
    "southern sotho": "",
    "hebrew": "iw",
    "urdu": "ur",
    "english": "en",
    "slovak": "sk",
    "malaysian": "ms",
    "latvian": "lv",
    "georgian": "ka",
    "lao": "lo",
    "bosnian": "bs",
    "armenian": "hy",
    "magyar": "hu",
    "finnish": "fi",
    "khmer": "km",
    "chinese": "zh-CN",
    "spanish": "es",
    "romansh": "",
    "norwegian nynorsk": "no",
    "russian": "ru",
    "mandarin": "",
    "tsonga": "",
    "luxembourgish": "lb",
    "polish": "pl",
    "latin": "la",
    "coptic": "",
    "divehi": "",
    "breton": "",
    "tibetan": "",
    "basque": "eu",
    "croatian": "hr",
    "norwegian bokmål": "no",
    "bulgarian": "bg",
    "hungarian": "hu",
    "indonesian": "id",
    "lithuanian": "lt",
    "burmese": "my",
    "swedish": "sv",
    "turkmen": "tk",
    "greek": "el",
    "nepali": "ne",
    "bengali": "bn",
    "sinhalese": "",
    "albanian": "sq",
    "galician": "gl",
    "uzbek": "uz",
    "azerbaijani": "az",
    "mongolian": "mn",
    "belarusian": "be",
    "southern ndebele": "",
    "friulian": "",
    "catalan": "ca",
    "estonian": "et",
    "kazakh": "kk",
    "tswana": "",
    "italian": "it",
    "syriac": "",
    "sanskrit": "",
    "slovenian": "sl",
    "zulu": "zu",
    "marathi": "mr",
    "venda": "",
    "vietnamese": "vi",
    "french": "fr",
    "chinese_tc": "zh-TW",
    "korean": "ko",
    "japanese": "ja",
    "esperanto": "eo",
    "piedmontese": "",
    "northern sotho": "",
    "scottish": "",
    "hindi": "hi",
    "xhosa": "xh",
    "malay": "ms",
}

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
    #   'required_perm': 'ipho_core.can_print_boardmeeting_site',
    # },
    # 'technopark.printer-2': {
    #   'name': 'Technopark 2',
    #   'host': '',
    #   'queue': 'printer-2',
    #   'auth_token': '',
    #   'opts': {'Duplex': 'None', 'ColourModel': 'Greyscale', 'Staple': '1PLU'},
    #   'required_perm': 'ipho_core.can_print_boardmeeting_site',
    # },
    # 'irchel.printer-1': {
    #   'name': 'Irchel 1',
    #   'host': '',
    #   'queue': 'printer-1',
    #   'auth_token': '',
    #   'opts': {'Duplex': 'None', 'ColourModel': 'Colour', 'Staple': '1PLU'},
    #   'required_perm': 'ipho_core.can_print_exam_site',
    # },
    # 'irchel.printer-2': {
    #   'name': 'Irchel 2',
    #   'host': '',
    #   'queue': 'printer-2',
    #   'auth_token': '',
    #   'opts': {'Duplex': 'None', 'ColourModel': 'Colour', 'Staple': '1PLU'},
    #   'required_perm': 'ipho_core.can_print_exam_site',
    # },
    # 'irchel.printer-3': {
    #   'name': 'Irchel 3',
    #   'host': '',
    #   'queue': 'printer-3',
    #   'auth_token': '',
    #   'opts': {'Duplex': 'None', 'ColourModel': 'Colour', 'Staple': '1PLU'},
    #   'required_perm': 'ipho_core.can_print_exam_site',
    # },
    "generic.printer-1": {
        "name": "Generic printer",
        "host": "",
        "queue": "printer-1",
        "auth_token": "",
        "opts": {"Duplex": "None", "ColourModel": "Colour", "Staple": "1PLU"},
        "required_perm": "ipho_core.can_print_exam_site",
    },
}

EXAM_TOOLS_API_KEYS = {
    "PDF Worker": "KeyChangeMe",
    "Scan Worker": "KeyChangeMe",
}

# Random draw
RANDOM_DRAW_ON_SUBMISSION = False

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
MEDIA_ROOT = DOCUMENT_PATH

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ""

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = "collected_static"

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = "/static/"

# Additional locations of static files
BOWER_STATIC_PATH = os.getenv(
    "BOWER_STATIC_PATH", os.path.join(PROJECT_PATH, "bower", "static")
)
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    STATIC_PATH,
    BOWER_STATIC_PATH,
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
    "drf_spectacular",
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
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
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
        "exam_tools": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
        "exam_tools": {
            "handlers": ["exam_tools"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LANGUAGES = [("en-PH", "Physics"), ("en-CH", "Chemistry")]
LANGUAGE_CODE = "en-PH"
