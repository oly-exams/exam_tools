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

from django.db import models
from django.db.models import Q, Count, Sum, Case, When

from ipho_exam.models import *



feedbacks = Feedback.objects.filter(
    question__exam=1
).annotate(
     num_likes=Sum(
         Case(When(like__status='L', then=1),
              output_field=models.IntegerField())
     ),
     num_unlikes=Sum(
         Case(When(like__status='U', then=1),
              output_field=models.IntegerField())
     )
 ).values(
    'num_likes',
    'num_unlikes',
    'pk',
    'question__name',
    'delegation__name',
    'delegation__country',
    'status',
    'part',
    'comment'
 )

print feedbacks
