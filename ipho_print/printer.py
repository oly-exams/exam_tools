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

# pylint: disable = consider-using-f-string


import os
import json
import types
from copy import deepcopy

import urllib.request
import urllib.parse
import urllib.error

from future import standard_library

standard_library.install_aliases()

import requests
from django.conf import settings

from ipho_exam.models import Delegation

SUCCESS = 0
FAILED = 1
PRINTER_QUEUES = getattr(settings, "PRINTER_QUEUES")


class PrinterError(RuntimeError):
    def __init__(self, msg):
        self.msg = msg
        super().__init__("Print error: " + self.msg)


def allowed_choices(user):
    return [
        (k, q["name"])
        for k, q in sorted(PRINTER_QUEUES.items())
        if user.has_perm(q["required_perm"])
    ]


def allowed_opts(queue):
    return PRINTER_QUEUES[queue]["opts"]


def default_opts():
    try:
        opts = getattr(settings, "PRINTER_DEFAULT_GLOBAL_OPTS")
    except AttributeError:
        opts = {"Duplex": "None", "ColourModel": "Gray", "Staple": "None"}
    return opts


def delegation_opts():
    try:
        opts = getattr(settings, "PRINTER_DELEGATION_OPTS")
    except AttributeError:
        opts = {"Duplex": "DuplexNoTumble", "ColourModel": "Gray", "Staple": "None"}
    return opts


def send2queue(
    file, queue, user=None, user_opts=types.MappingProxyType({}), title=None
):
    url = "http://{host}/print/{queue}".format(**PRINTER_QUEUES[queue])
    files = {
        "file": (
            urllib.parse.quote(os.path.basename(file.name)),
            file,
            "application/pdf",
        )
    }
    headers = {
        "Authorization": "IPhOToken {auth_token}".format(**PRINTER_QUEUES[queue])
    }
    data = {}
    if user is not None:
        data["user"] = user.username
    opts = deepcopy(default_opts())
    opts.update(user_opts)
    al_opts = allowed_opts(queue)
    if getattr(settings, "ADD_DELEGATION_PRINT_BANNER", False) and (
        user.has_perm("ipho_core.is_delegation")
        and user
        not in Delegation.objects.get_by_natural_key(
            settings.OFFICIAL_DELEGATION
        ).members.all()
    ):
        title = f"DELEGATION: {user.username}"
        add_banner_page = True
    else:
        if title is None:
            title = "IPhO Print"
        add_banner_page = False
    for k in al_opts:
        if opts.get(k) not in ["None", "Gray"] and opts.get(k) != al_opts[k]:
            opts[k] = al_opts[k]
    data["opts"] = json.dumps(opts)
    data["title"] = json.dumps(title)
    data["add_banner_page"] = json.dumps(add_banner_page)
    req = requests.post(url, files=files, headers=headers, data=data, timeout=30)
    if req.status_code == 200:
        return SUCCESS

    error_msg = req.json()["message"]
    raise PrinterError(error_msg)
