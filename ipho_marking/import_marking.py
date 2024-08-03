import csv
import os.path

import numpy as np
import pandas as pd
from django.db.models import Q
from ipho_exam.models import Question
from ipho_marking.models import Marking, MarkingAction, MarkingMeta


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
    student_codes = [ppnt.code for ppnt in question.exam.participant_set.all()]
    zeros = len(student_codes) * [""]

    writer = csv.writer(filehandler)
    writer.writerow(["", "Min. Points", "Max. Points", *student_codes])
    for q in question_parts:
        writer.writerow([q.name, q.min_points, q.max_points, *zeros])


def import_marking(question_id, file):
    """Imports marking for a question from a CSV file

    Args:
        question_id (int): id of an answer sheet
        file (filename): e.g. CSV file
            The columns correspond to different students,
            the rows to different parts of the question.

    Returns:
        list: list with student codes that answers this question
    """
    # Needed to ensure indices are string and e.g. 1.1 and 1.10 are not mixed up
    df = pd.read_csv(file, dtype=str)
    df = df.set_index(df.columns[0])

    markings = Marking.objects.filter(
        Q(marking_meta__question__id=question_id) & Q(version="O")
    )
    student_codes = df.columns.values[2:]
    for student_code in student_codes:
        stud_markings = markings.filter(participant__code=student_code)
        for question_part in df.index:
            try:
                awarded_points = float(df[student_code][question_part])
            except ValueError as e:
                raise ValueError(f"Value error for {student_code} {question_part}: {e}")
            # do not update if no points have been entered
            if not np.isnan(awarded_points) and not df[student_code][question_part] == "":
                marking = stud_markings.filter(marking_meta__name=question_part)
                print(marking.__dict__)
                assert (
                    len(marking) == 1
                ), f"Found {len(marking)} markings for {student_code} {question_part}"
                marking = marking[0]
                assert (
                    awarded_points >= float(marking.marking_meta.min_points) and
                    awarded_points <= float(marking.marking_meta.max_points)
                ), f"Points {awarded_points} not in range {marking.marking_meta.min_points}, {marking.marking_meta.max_points} for {student_code} {question_part}"
                marking = marking
                marking.points = awarded_points
                marking.save()

    return student_codes
