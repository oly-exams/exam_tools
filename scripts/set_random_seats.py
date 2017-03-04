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

from ipho_core.models import Student
from ipho_exam.models import Place, Exam

import random

def main():
    Place.objects.all().delete()
    
    exams = Exam.objects.all()
    for student in Student.objects.all():
        for exam in exams:
            seat = '{}-{}{}'.format(
                random.choice(['M', 'N']),
                random.choice(['A', 'B', 'C', 'D', 'E', 'F']),
                random.randint(100, 400),
            )
            Place.objects.get_or_create(student=student, exam=exam, name=seat)


if __name__ == '__main__':
    main()
