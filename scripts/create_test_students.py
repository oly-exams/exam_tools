from __future__ import division
# Exam Tools
#
# Copyright (C) 2014 - 2018 Oly Exams Team
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

from past.utils import old_div
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'

import django
django.setup()

import csv
from ipho_core.models import Delegation, Student


def main(input):
    csv_reader = csv.reader(input)

    all_delegations = Delegation.objects.all()
    for i, row in enumerate(csv_reader):
        delegation = all_delegations[old_div(i, 5)]

        code = '{}-S-{}'.format(delegation.name, i % 5 + 1)
        student = Student(code=code, first_name=row[2], last_name=row[3], delegation=delegation)
        student.save()

        if old_div((i + 1), 5) >= len(all_delegations):
            break


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Convert CSV to Delegation fixture')
    parser.add_argument('file', type=argparse.FileType('rU'), help='Input CSV file')
    args = parser.parse_args()

    main(args.file)
