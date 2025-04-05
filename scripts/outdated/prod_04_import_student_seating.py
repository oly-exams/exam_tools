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
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

import django

django.setup()

import csv

from ipho_exam.models import Exam, Participant, Place


def main(input):
    reader = csv.DictReader(input)
    assert "individual_id" in reader.fieldnames

    header = reader.fieldnames.copy()
    header.remove("individual_id")
    print(header)
    exams = [Exam.objects.get(name=n) for n in header]
    # theory = Exam.objects.get(name='Theory')
    # experiment = Exam.objects.get(name='Experiment')
    for i, row in enumerate(reader):
        try:
            for f, ex in zip(header, exams):
                participant = Participant.objects.get(
                    code=row["individual_id"], exam=ex
                )
                Place.objects.get_or_create(participant=participant, name=row[f])

            # Place.objects.get_or_create(participant=participant, exam=theory, name=row['seat_theory'])
            # Place.objects.get_or_create(participant=participant, exam=experiment, name=row['seat_experiment'])

            print(row["individual_id"], ".....", "imported.")
        except Participant.DoesNotExist:
            print("Skip", row["individual_id"], "because participant does not exist.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import CSV with users seating info")
    parser.add_argument(
        "file",
        type=argparse.FileType("rU", encoding="utf-8-sig"),
        help="Input CSV file",
    )
    args = parser.parse_args()

    main(args.file)
