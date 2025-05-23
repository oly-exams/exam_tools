import os

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"
import datetime
import sys

import django

django.setup()

import itertools

from ipho_core.models import *
from ipho_exam import tasks
from ipho_exam.models import *


def main():
    exam = Exam.objects.get(name="Experiment - Marking")
    for delegation in Delegation.objects.exclude(name="Official"):
        for participant in delegation.get_participants(exam):
            all_tasks = []
            participant_languages = ParticipantSubmission.objects.filter(
                exam=exam, participant=participant
            )
            if len(participant_languages) == 0:
                continue
            participant_seat = Place.objects.get(exam=exam, participant=participant)
            questions = exam.question_set.all()
            grouped_questions = {
                k: list(g)
                for k, g in itertools.groupby(questions, key=lambda q: q.position)
            }
            for position, qgroup in list(grouped_questions.items()):
                doc, _ = Document.objects.get_or_create(
                    exam=exam, participant=participant, position=position
                )
                cover_ctx = {
                    "participant": participant,
                    "exam": exam,
                    "question": qgroup[0],
                    "place": participant_seat.name,
                }
                question_task = tasks.participant_exam_document.s(
                    qgroup, participant_languages, cover=cover_ctx, commit=True
                )
                question_task.freeze()
                doc_task, _ = DocumentTask.objects.update_or_create(
                    document=doc, defaults={"task_id": question_task.id}
                )
                question_task.delay()
                print(f"Submitted for {participant.code} #{position}")


if __name__ == "__main__":
    c = eval(input("Do you want to proceed? Yes/No > "))
    if not c in ["y", "yes", "Y", "Yes"]:
        sys.exit()
    main()
