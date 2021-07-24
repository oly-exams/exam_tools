# Exam Tools
#
# Copyright (C) 2014 - 2021 Oly Exams Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, sys


os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"

import django

django.setup()

import json

from ipho_exam.models import Exam
from ipho_control.models import ExamPhase


def log(*args):
    sys.stderr.write(" ".join([str(a) for a in args]) + "\n")


fields_to_export = [
    "name",
    "position",
    "exam_settings",
    "description",
    "public_description",
    "before_switching",
    "available_to_organizers",
    "available_question_settings",
    "checks_warning",
    "checks_error",
]


def export_exam_phase(phase, fields=fields_to_export):

    return {k: getattr(phase, k) for k in fields}


def export_exam_phases_for_exam(exam):
    phases = ExamPhase.objects.filter(exam=exam).order_by("position").all()
    data = [export_exam_phase(phase) for phase in phases]
    json.dump(data, sys.stdout, indent=2)


def main(exam_name):

    exam = Exam.objects.filter(name=exam_name)
    if not exam.exists():
        log(f"Exam {exam_name} not found, possible exam names are:")
        for exm in Exam.objects.all():
            log(exm.name)
    else:
        export_exam_phases_for_exam(exam.first())


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Add Exam Phases")

    parser.add_argument(
        "exam",
        help="Exams for which phases should be imported (example --enable Theory Experiment)",
    )

    args = parser.parse_args()

    main(args.exam)
