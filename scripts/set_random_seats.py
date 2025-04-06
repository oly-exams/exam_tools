import os

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"

import django

django.setup()

import random

from ipho_exam.models import Exam, Participant, Place


def main():
    exams = Exam.objects.all()
    print("\nFor which exam you want to generate random seats.")
    exams_ix = []
    for i, exam in enumerate(exams):
        print(f"[{i + 1}] {exam.name}")
    ix = int(eval(input("Select index > ")))
    if ix <= 0 or ix > len(exams):
        print("Index is invalid.")
        return
    exam = exams[ix - 1]
    Place.objects.filter(exam=exam).delete()

    for participant in Participant.objects.all():
        seat = "{}-{}{}".format(
            random.choice(["M", "N"]),
            random.choice(["A", "B", "C", "D", "E", "F"]),
            random.randint(100, 400),
        )
        Place.objects.get_or_create(participant=participant, exam=exam, name=seat)


if __name__ == "__main__":
    main()
