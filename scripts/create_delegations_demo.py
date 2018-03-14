# Exam Tools
#
# Copyright (C) 2014 - 2017 Oly Exams Team
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

from __future__ import print_function

from builtins import str
from builtins import range
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'

import django
django.setup()

import csv
from ipho_core.models import Delegation, Student


def main(input):
    reader = csv.DictReader(input)

    for i, row in enumerate(reader):
        delegation = Delegation(name=row['Country code'], country=row['Country name'])
        nk = delegation.natural_key()
        try:
            current_delegation = Delegation.objects.get_by_natural_key(*nk)
            print(row['Country code'], '...', 'already present. Skip.')
            continue
        except Delegation.DoesNotExist:
            pass
        delegation.save()

        for j in range(5):
            code = '{}-S-{}'.format(delegation.name, j + 1)
            student = Student(code=code, first_name='Student', last_name=str(j + 1), delegation=delegation)
            student.save()

        print(row['Country code'], '...', 'imported.')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Import CSV to Delegation model and create demo students')
    parser.add_argument('file', type=argparse.FileType('rU'), help='Input CSV file')
    args = parser.parse_args()

    main(args.file)
