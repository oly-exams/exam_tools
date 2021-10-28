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
import datetime
import logging

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
