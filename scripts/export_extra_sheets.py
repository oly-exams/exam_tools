#!/usr/bin/env python
#
# Author:  Dominik Gresch <greschd@gmx.ch>

import os
import sys
import csv

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"

import django

django.setup()
from django.db.models import Q

from ipho_exam.models import Document


def get_extra_sheets_count(exam_name, output_file):
    docs = Document.objects.filter(
        ~Q(position=0), ~Q(extra_num_pages=0), exam__name=exam_name
    ).order_by("participant", "position")
    res = [(d.participant, d.position, d.extra_num_pages) for d in docs]
    with open(output_file, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["participant_code", "question_number", "extra_num_pages"])
        writer.writerows(res)


if __name__ == "__main__":
    exam_name = sys.argv[1]
    try:
        output_file = sys.argv[2]
    except IndexError:
        output_file = f"extra_sheets_{exam_name}.csv"
    get_extra_sheets_count(exam_name, output_file=output_file)
