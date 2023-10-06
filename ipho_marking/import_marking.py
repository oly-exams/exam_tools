import csv
import os.path

import pandas as pd
import numpy as np

from django.db.models import Q

from ipho_marking.models import Marking, MarkingMeta, MarkingAction
from ipho_exam.models import Question


def generate_template(question_id, filehandler):
    """Generates a CSV template

    Args:
        question_id (id): ID of question
        filehandler (file handler): as returned e.g. by open(filename)
            The columns correspond to different students,
            the rows to different parts of the question.
    """
    question = Question.objects.get(id=question_id)
    question_parts = MarkingMeta.objects.filter(question__id=question_id)
    question_parts = [q.name for q in question_parts]
    student_codes = [ppnt.code for ppnt in question.exam.participant_set.all()]
    zeros = len(student_codes) * [""]

    writer = csv.writer(filehandler)
    writer.writerow(["", *student_codes])
    for q in question_parts:
        writer.writerow([q, *zeros])


def import_marking(question_id, file):
    """Imports marking for a question from a CSV file

    Args:
        question_id (int): id of an answer sheet
        file (filename): e.g. CSV file
            The columns correspond to different students,
            the rows to different parts of the question.

    Returns:
        list: list with student codes that answeres this question
    """
    df = pd.read_csv(file, index_col=0)
    df = df.astype(float)  # convert entries to floats

    markings = Marking.objects.filter(
        Q(marking_meta__question__id=question_id) & Q(version="O")
    )
    student_codes = df.columns
    question = Question.objects.get(id=question_id)

    for student_code in student_codes:
        stud_markings = markings.filter(participant__code=student_code)
        for question_part in df.index:
            # do not update if no points have been entered
            if not np.isnan(df[student_code][question_part]):
                marking = stud_markings.filter(marking_meta__name=question_part)
                assert (
                    len(marking) == 1
                ), f"Found {len(marking)} markings for {student_code} {question_part}"
                marking = marking[0]
                marking.points = df[student_code][question_part]
                marking.save()
                print(
                    f"Saved marking for {student_code} {question.name} {question_part}"
                )

    marking_actions = MarkingAction.objects.filter(question__id=question_id)
    for action in marking_actions:
        action.status = 1  # submitted for moderation
        action.save()

    return student_codes
