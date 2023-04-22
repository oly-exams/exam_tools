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


import os

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"

import shutil

import django

from ipho_exam.models import *


def get_id(doc):
    ppnt = doc.participant.code
    exam = doc.exam.code
    question = doc.position
    return f"{ppnt}_{exam}_{question}"


def move_doc(doc, dest_folder):
    doc_id = get_id(doc)
    dest_path = os.path.join(dest_folder, doc_id + ".pdf")
    try:
        shutil.copyfile(doc.file.path, dest_path)
        print("exported", doc_id)
    except ValueError:
        print("could not export", doc_id)


if __name__ == "__main__":
    dest_folder = "/srv/exam_tools/backups/submission_pdf_export"
    try:
        os.makedirs(dest_folder)
    except OSError:
        print("could not create destination folder (may already exist)")
    for doc in Document.objects.all():
        move_doc(doc, dest_folder)
