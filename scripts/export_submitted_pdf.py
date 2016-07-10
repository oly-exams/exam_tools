import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'

import shutil

import django

from ipho_exam.models import *

def get_id(doc):
    stud = doc.student.code
    exam = doc.exam.code
    question = doc.position
    return '{}_{}_{}'.format(stud, exam, question)

def move_doc(doc, dest_folder):
    doc_id = get_id(doc)
    dest_path = os.path.join(dest_folder, doc_id + '.pdf')
    try:
        shutil.copyfile(doc.file.path, dest_path)
        print 'exported', doc_id
    except ValueError:
        print 'could not export', doc_id
    
if __name__ == '__main__':
    dest_folder = '/srv/exam_tools/backups/submission_pdf_export'
    try:
        os.makedirs(dest_folder)
    except OSError:
        print 'could not create destination folder (may already exist)'
    for doc in Document.objects.all():
        move_doc(doc, dest_folder)
