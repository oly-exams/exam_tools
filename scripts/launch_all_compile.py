from __future__ import print_function

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'
import sys
import datetime

import django
django.setup()

import itertools
from ipho_core.models import *
from ipho_exam.models import *
from ipho_exam import tasks


def main():
  exam = Exam.objects.get(name='Experiment - Marking')
  for delegation in Delegation.objects.exclude(name='Official'):
    for student in delegation.student_set.all():
        all_tasks = []
        student_languages = StudentSubmission.objects.filter(exam=exam, student=student)
        if len(student_languages) == 0: continue
        student_seat = Place.objects.get(exam=exam, student=student)
        questions = exam.question_set.all()
        grouped_questions = {k: list(g) for k,g in itertools.groupby(questions, key=lambda q: q.position) }
        for position, qgroup in grouped_questions.iteritems():
            doc,_ = Document.objects.get_or_create(exam=exam, student=student, position=position)
            cover_ctx = {'student': student, 'exam': exam, 'question': qgroup[0], 'place': student_seat.name}
            question_task = tasks.student_exam_document.s(qgroup, student_languages, cover=cover_ctx, commit=True)
            # question_task = question_utils.compile_stud_exam_question(qgroup, student_languages, cover=cover_ctx, commit=True)
            question_task.freeze()
            doc_task,_ = DocumentTask.objects.update_or_create(document=doc, defaults={'task_id':question_task.id})
            question_task.delay()
            print('Submitted for {} #{}'.format(student.code, position))


if __name__ == '__main__':
  c = raw_input('Do you want to proceed? Yes/No > ')
  if not c in ['y', 'yes', 'Y', 'Yes']:
    sys.exit()
  main()
