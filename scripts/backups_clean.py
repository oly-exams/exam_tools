
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'

import django
django.setup()

from django.conf import settings
import datetime

from dbbackup import settings as dbbackup_settings
from dbbackup import utils
from dbbackup.storage.base import BaseStorage, StorageError

import logging
logger = logging.getLogger('exam_tools.backups')

def clean_old_backups():
    storage = BaseStorage.storage_factory()
    keep_days = 4
    files = storage.list_backups()
    now = datetime.datetime.now()
    files = sorted(files, key=utils.filename_to_date, reverse=True)
    files_to_delete = [fi for fi in files if (now - utils.filename_to_date(fi)).days > keep_days]
    logger.info('Deleting {} files on {}. keep_days={}'.format( len(files_to_delete), len(files), keep_days))
    for filename in files_to_delete:
        logging.info('Removing ' +filename)
        storage.delete_file(filename)

if __name__ == '__main__':
    clean_old_backups()    

