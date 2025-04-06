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

with open(out_file, "w", encoding="utf-8") as out_f:
    out_f.write("username,last_login\n")
    for u in all_users:
        last_login = u.last_login
        if last_login is None:
            last_login_str = ""
        else:
            last_login_str = last_login.isoformat()
        out_f.write(f"{u.username},{last_login_str}\n")
