#!/usr/bin/env python

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'

import django
django.setup()
from django.conf import settings

from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from django.template import RequestContext

from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from crispy_forms.utils import render_crispy_form
from django.template.loader import render_to_string

from django.conf import settings
from ipho_core.models import Delegation, Student
from ipho_exam.models import Exam, Question, VersionNode, TranslationNode, PDFNode, Language, Figure, Feedback, StudentSubmission, ExamAction
from ipho_marking.models import Marking, MarkingMeta
from ipho_exam import qml, tex, pdf, qquery, fonts, iphocode

OFFICIAL_LANGUAGE = 1
OFFICIAL_DELEGATION = getattr(settings, 'OFFICIAL_DELEGATION')



def compile_all():
    for delegation in Delegation.objects.exclude(name='IPhO'):
        students = Student.objects.filter(delegation=delegation).values('id', 'pk', 'code', 'first_name', 'last_name')
        vid = 'F'
        points_per_student = []
        for student in students:
            stud_exam_points_list = Marking.objects.filter(
                version=vid, student=student['id']
            ).values(
                'marking_meta__question__exam'
            ).annotate(
                exam_points=Sum('points')
            ).values(
                'exam_points'
            ).order_by(
                'marking_meta__question__exam'
            )
            total = sum([ st_points['exam_points'] for st_points in stud_exam_points_list if st_points['exam_points'] is not None ])
            points_per_student.append( (student, stud_exam_points_list, total) )

        exams = MarkingMeta.objects.filter(question__exam__hidden=False).values(
            'question__exam'
        ).annotate(
            exam_points=Sum('max_points')
        ).values(
            'question__exam__code',
            'question__position',
            'question__exam__name',
            'exam_points'
        ).order_by(
            'question__exam',
        ).distinct()


        results = u''
        results += u'\\begin{tabular}'
        for i, ex in enumerate(exams):
            if i != 0:
                results += u' & '
            results += u'{}-{} (max {})'.format(ex['question__exam__code'], ex['question__position'])
        results += u' \\'
        for (student, stud_exam_points_list, total) in points_per_student:
            results += u'{} & '.format(student.code)
            for p in stud_exam_points_list:
                results += u'{} & '.format(p['exam_points'])
            results += u'{} \\'.format(total)
        results += u'\\end{tabular}'

        context = {
                    'polyglossia' : 'english',
                    'polyglossia_options' : '',
                    'font'        : fonts.ipho['notosans'],
                    'extraheader' : '',
                    'delegation'    : delegation,
                    'results'    : results,
                  }
        body = render_to_string('ipho_marking/tex/exam_points.tex', RequestContext(HttpRequest(), context)).encode("utf-8")
        print 'Compile...'
        try:
            question_pdf = pdf.compile_tex(body, ext_resources)

            filename = u'FINALPOINTS-{}.pdf'.format(delagtion.name)
            with open(filename.encode('utf8'), 'wb') as fp:
                fp.write(question_pdf)
            print filename, 'DONE'


if __name__ == '__main__':
    compile_all()
