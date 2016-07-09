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
    for node in TranslationNode.objects.all():
        language_id = node.language_id
        question_id = node.question_id
        delegation_id = node.language.delegation.name
        
        node_id = '{t}_d{d}_q{q}_l{l}'.format(
            t=timestamp,
            d=delegation_id, 
            q=question_id, 
            l=language_id 
        )
        
        dump_file = os.path.join(
            backup_folder, 
            'translation_dump_' + node_id + '.json'
        )
        export_file = os.path.join(
            backup_folder, 
            'translation_export_' + node_id + '.xml'
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
        if path.startswith('translation')
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
    clean_old_backups(backup_folder, datetime.timedelta(days=1))
    make_backups(backup_folder)
