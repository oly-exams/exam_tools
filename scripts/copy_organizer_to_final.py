"""Copy all markings from organizer to final. 

This is useful for exams without moderation.
"""
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"
import shutil
import sys

sys.path.append(".")

import django

django.setup()
from django.conf import settings
from django.db.models import Q

from ipho_exam.models import Question
from ipho_marking.models import Marking

exams = Exam.objects.filter(name__in=names)
for exam in exams[0]:
    markings = Marking.objects.filter(marking_meta__question__id=exam.id)
    markings_organizer = markings.filter(version="O")
    for m in markings_organizer[0]:
        marking_final = markings.filter(
            Q(participant__id=m.participant.id)
            & Q(marking_meta__id=m.marking_meta.id)
            & Q(version="F")
        )
        assert len(marking_final) == 1
        m_final = marking_final[0]
        m_final.points = m.points
        m_final.save()
