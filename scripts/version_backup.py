#!/usr/bin/env python

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'
import sys
import datetime

import django
django.setup()

from django.utils import timezone
from django.core import serializers

from ipho_exam.models import *
from ipho_exam import qml

TIMESTP_FORMAT = '%Y%m%d%H%M%S'

def save(objs, stream):
    if type(stream) == str:
        stream = open(stream, 'w')

def get_time():
    return timezone.localtime(timezone.now()).replace(tzinfo=None)

def make_backups(backup_folder):
    timestamp = get_time().strftime(TIMESTP_FORMAT)
    for node in VersionNode.objects.all():
        question_id = node.question_id
        version_id = node.version
        
        node_id = '{t}_q{q}_v{v}'.format(
            t=timestamp,
            q=question_id, 
            v=version_id,
        )
        
        dump_file = os.path.join(
            backup_folder, 
            'version_dump_' + node_id + '.json'
        )
        export_file = os.path.join(
            backup_folder, 
            'version_export_' + node_id + '.xml'
        )
        
        with open(dump_file, 'w') as stream:
            serializers.serialize(
                'json', [node], indent=2,
                use_natural_foreign_keys=True,
                use_natural_primary_keys=True,
                stream=stream
            )
            
        if node.text:
            export = qml.unescape_entities(qml.xml2string(
                qml.make_qml(node).make_xml()
            ))
            with open(export_file, 'w') as f:
                f.write(export.encode('utf8'))
                
def clean_old_backups(backup_folder, timedelta):
    current_time = get_time()
    files = (
        path for path in os.listdir(backup_folder)
        if path.startswith('version')
    )
    for path in files:
        timestamp = path.split('.')[0].split('_')[2]
        creation_time = datetime.datetime.strptime(
            timestamp, 
            TIMESTP_FORMAT
        )
        if (current_time - creation_time) > timedelta:
            os.remove(os.path.join(backup_folder, path))

if __name__ == '__main__':
    backup_folder = sys.argv[1]
    try:
        os.makedirs(backup_folder)
    except OSError:
        pass
    clean_old_backups(backup_folder, datetime.timedelta(hours=4))
    make_backups(backup_folder)
