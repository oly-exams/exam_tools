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

#!/usr/bin/env python


import os

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"
import shutil
import sys

sys.path.append(".")

import django

django.setup()
from django.conf import settings
from django.db.models import F

from ipho_exam.models import Document, Exam, ExamAction

# BASE_PATH = "/srv/exam_tools/backups/submission_pdf_export/"
BASE_PATH = "downloads/participant_pdf/"  # inside media folder


def get_filename(doc):
    ppnt = doc.participant.code
    exam = doc.participant.exam.code
    question = doc.position

    if doc.participant.exam.flags & doc.participant.exam.FLAG_SQUASHED:
        return f"{ppnt}_{exam}"
    else:
        return f"{ppnt}_{exam}{question}"


def move_doc(doc):
    filename = get_filename(doc)
    dest_path = os.path.join(settings.DOCUMENT_PATH, BASE_PATH, filename + ".pdf")

    try:
        shutil.copyfile(doc.file.path, dest_path)
        print("exported", filename)
    except ValueError:
        print("could not export", filename)


def generate_all(exam_names=("Theory", "Experiment")):
    try:
        os.makedirs(os.path.join(settings.DOCUMENT_PATH, BASE_PATH), exist_ok=True)
    except OSError:
        print("could not create destination folder")

    exams = Exam.objects.filter(name__in=exam_names)

    if not exams:
        print(f"ERROR: no exams corresponding to {exam_names}.")
        return

    submitted_docs = Document.objects.filter(
        participant__exam__in=exams,
        participant__exam__delegation_status__action=ExamAction.TRANSLATION,
        participant__exam__delegation_status__delegation=F("participant__delegation"),
        participant__exam__delegation_status__status=ExamAction.SUBMITTED,
    ).distinct()

    for doc in submitted_docs:
        move_doc(doc)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_all(exam_names=sys.argv[1:])
    else:
        generate_all()
