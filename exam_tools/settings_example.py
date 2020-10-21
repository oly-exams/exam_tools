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
from .settings_common import *

# Printing paths for sanity's sake
print("Settings directory:", SETTINGS_DIR, file=sys.stderr)
print("Project root:", PROJECT_PATH, file=sys.stderr)
print("Templates:", TEMPLATE_PATH, file=sys.stderr)
print("Static:", STATIC_PATH, file=sys.stderr)

DEBUG = True
# TEMPLATE_DEBUG = DEBUG
NO_ANSWER_SHEETS = False
ONLY_OFFICIAL_ANSWER_SHEETS = False
VOTING_FULLSCREEN_DISPLAY_REMAINING_USERS = False

AUTO_TRANSLATE = True
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

GOOGLE_TRANSLATE_SERVICE_ACCOUNT_KEY = r"""{}"""

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
