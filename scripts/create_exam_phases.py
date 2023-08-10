# Exam Tools
#
# Copyright (C) 2014 - 2023 Oly Exams Team
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
sys.path.append(".")

import django

django.setup()

import json

from ipho_exam.models import Exam
from ipho_control.models import ExamPhase


def log(*args):
    sys.stderr.write(" ".join([str(a) for a in args]) + "\n")


def create_exam_phase(exam, force_update, name, position, exam_settings, **kwargs):
    default_kwargs = {
        "description": f"Description Phase {name} of {exam}",
        "public_description": f"Public description Phase {name} of {exam}",
        "before_switching": f"Before switching Phase {name} of {exam}",
        "available_to_organizers": True,
        "available_question_settings": [],
        "checks_warning": [],
        "checks_error": [],
        "exam": exam,
        "name": name,
        "position": position,
        "exam_settings": exam_settings,
    }
    default_kwargs.update(kwargs)

    phase, created = ExamPhase.objects.get_or_create(exam_id=exam.pk, position=position)
    if created or force_update:
        phase.save()
        ExamPhase.objects.filter(pk=phase.pk).update(**default_kwargs)
    phase = ExamPhase.objects.get(exam_id=exam.pk, position=position)
    if created:
        log(phase, "..", "created")
    elif force_update:
        log(phase, "..", "updated")
    else:
        log(phase, "..", "skipped")

    return phase


def create_exam_phases_for_exam(exam, phases_kwargs, force):

    phases = []
    for kwargs in phases_kwargs:
        phase = create_exam_phase(exam=exam, force_update=force, **kwargs)
        phases.append(phase)
    return phases


def main(exam_names, all_exams, file, force=False):

    with file as f:
        phases_kwargs = json.load(f)

    if all_exams:
        exams = Exam.objects.all()
    else:
        exams = Exam.objects.filter(name__in=exam_names).all()

    if exams.count() == 0:
        log("No exams found, possible exam names are:")
        for exm in Exam.objects.all():
            log(exm.name)
    log(exams.count(), "exams found:")
    for exam in exams:
        log(exam)

    for exam in exams:
        create_exam_phases_for_exam(exam, phases_kwargs, force)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Add Exam Phases")

    parser.add_argument("file", type=argparse.FileType("rU"), help="Input JSON file")
    parser.add_argument(
        "--exams",
        nargs="+",
        help="Exams for which phases should be imported (example --enable Theory Experiment)",
    )
    parser.add_argument(
        "--all-exams",
        help="Import phases for all exams",
        action="store_true",
    )
    parser.add_argument(
        "--force",
        help="Overwrite phases already in db",
        action="store_true",
    )

    args = parser.parse_args()

    main(args.exams, args.all_exams, args.file, args.force)
