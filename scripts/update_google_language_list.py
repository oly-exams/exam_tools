# Exam Tools
#
# Copyright (C) 2014 - 2023 Oly Exams Team
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


# Imports the Google Cloud client library
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
import json
import sys
import os

raw_cred = sys.argv[1]
str_cred = eval(raw_cred)
# Instantiates a client
json_cred = json.loads(str_cred)
translate_client = translate.Client(
    credentials=service_account.Credentials.from_service_account_info(json_cred)
)
lan_list = json.dumps(translate_client.get_languages())
with open(
    os.path.join(os.path.dirname(__file__), "../exam_tools/settings.py"), "a"
) as f:
    f.write("AUTO_TRANSLATE_LANGUAGES = " + lan_list + "\n")
