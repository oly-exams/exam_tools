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

import os
import sys

if len(sys.argv) != 2:
    print("Usage: python <script_file> <output_file>")

out_file = sys.argv[1]

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exam_tools.settings")
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

import django

django.setup()

from ipho_core.models import User

all_users = list(User.objects.all())

with open(out_file, 'w', encoding='utf-8') as out_f:
    out_f.write("username,last_login\n")
    for u in all_users:
        last_login = u.last_login
        if last_login is None:
            last_login_str = ''
        else:
            last_login_str = last_login.isoformat()
        out_f.write(f"{u.username},{last_login_str}\n")
