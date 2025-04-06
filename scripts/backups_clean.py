import datetime
import logging
import os

logger = logging.getLogger("exam_tools.backups")

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"

import django

django.setup()

from dbbackup import utils
from dbbackup.storage import Storage


def clean_old_backups():
    storage = Storage()
    keep_delta = datetime.timedelta(hours=13)
    files = storage.list_backups()
    now = datetime.datetime.now()
    files = sorted(files, key=utils.filename_to_date, reverse=True)
    files_to_delete = [
        fi for fi in files if (now - utils.filename_to_date(fi)) > keep_delta
    ]
    logger.info(
        "Deleting %s files on %s. keep_delta=%s",
        len(files_to_delete),
        len(files),
        keep_delta,
    )
    for filename in files_to_delete:
        logger.info("Removing %s", filename)
        storage.delete_file(filename)


if __name__ == "__main__":
    clean_old_backups()
