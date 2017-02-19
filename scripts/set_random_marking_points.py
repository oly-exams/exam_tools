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
import sys

root_dir=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
sys.path.insert(0,root_dir)

import django
django.setup()

from ipho_marking.models import Marking, MarkingMeta
import random


def main():
    markings = Marking.objects.all()
    i = 0
    for marking in markings:
        r = random.random()
        marking.points = round(r * marking.marking_meta.max_points, 1)
        marking.save()
        if i%100 == 1:
            print "markings changed:", i
        i += 1

if __name__ == '__main__':
    print main()
