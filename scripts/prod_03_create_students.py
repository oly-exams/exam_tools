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

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'exam_tools.settings'

import django
django.setup()

import csv
from ipho_core.models import Delegation, Student


def main(input):
    reader = csv.DictReader(input)
    
    
    for i,row in enumerate(reader):
        try:
            ## Delegation
            delegation = Delegation.objects.get(name=row['delegation'])
            
            student,created = Student.objects.get_or_create(code=row['code'], defaults={
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'delegation': delegation,
            })
            if created: print student, '..', 'created'
            
        except Delegation.DoesNotExist:
            print 'Skip', row['code'], 'because delegation does not exist.'


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Import CSV with users')
    parser.add_argument('file', type=argparse.FileType('rU'), help='Input CSV file')
    args = parser.parse_args()
    
    main(args.file)

