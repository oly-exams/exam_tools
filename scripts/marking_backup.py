#!/usr/bin/env python

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

import os

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"
import sys
import datetime

import django

django.setup()

from django.utils import timezone
from django.core import serializers

from ipho_marking.models import Marking

TIMESTP_FORMAT = "%Y%m%d%H%M%S"
PREFIX = "marking"


def save(objs, stream):
    if type(stream) == str:
        stream = open(stream, "w")


def get_time():
    return timezone.localtime(timezone.now()).replace(tzinfo=None)


def make_backups(backup_folder):
    timestamp = get_time().strftime(TIMESTP_FORMAT)
    node_id = timestamp
    dump_file = os.path.join(backup_folder, PREFIX + "_dump_" + node_id + ".json")
    with open(dump_file, "w") as stream:
        serializers.serialize(
            "json",
            Marking.objects.all(),
            indent=2,
            use_natural_foreign_keys=True,
            use_natural_primary_keys=True,
            stream=stream,
        )


def clean_old_backups(backup_folder, timedelta):
    current_time = get_time()
    files = (path for path in os.listdir(backup_folder) if path.startswith(PREFIX))
    for path in files:
        timestamp = path.split(".")[0].split("_")[2]
        creation_time = datetime.datetime.strptime(timestamp, TIMESTP_FORMAT)
        if (current_time - creation_time) > timedelta:
            os.remove(os.path.join(backup_folder, path))


if __name__ == "__main__":
    backup_folder = sys.argv[1]
    try:
        os.makedirs(backup_folder)
    except OSError:
        pass
    make_backups(backup_folder)
    clean_old_backups(backup_folder, datetime.timedelta(hours=4))
