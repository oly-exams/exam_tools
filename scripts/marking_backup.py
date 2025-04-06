#!/usr/bin/env python

import os

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"
import datetime
import sys

import django

django.setup()

from django.core import serializers
from django.utils import timezone

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
