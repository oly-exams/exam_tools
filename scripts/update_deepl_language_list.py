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


# Imports the Deepl client library
import deepl
import sys
import os


raw_cred = sys.argv[1]
# Instantiates a client
translate_client = deepl.Translator(raw_cred)
lan_list_source = {l.code for l in translate_client.get_source_languages()}
lan_list_target = {l.code for l in translate_client.get_target_languages()}
with open(
    os.path.join(os.path.dirname(__file__), "../exam_tools/settings.py"), "a"
) as f:
    f.write("DEEPL_SOURCE_LANGUAGES = " + repr(lan_list_source) + "\n")
    f.write("DEEPL_TARGET_LANGUAGES = " + repr(lan_list_target) + "\n")
