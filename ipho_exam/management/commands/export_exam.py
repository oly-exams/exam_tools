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

from django.core.management.base import BaseCommand, CommandError
from django.core import serializers

from ipho_exam.models import Exam, Question, VersionNode


class Command(BaseCommand):
    help = 'Export the exam that matches the name'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, help='Search term in Exam name.')
        parser.add_argument('--format', default='json', dest='format',
            help='Specifies the output serialization format for fixtures.')
        parser.add_argument('--indent', default=2, dest='indent', type=int,
            help='Specifies the indent level to use when pretty-printing output.')
        parser.add_argument('-o', '--output', default=None, dest='output',
            help='Specifies file to which the output is written.')

    def handle(self, *args, **options):
        name = options['name']
        format = options.get('format')
        indent = options.get('indent')
        output = options.get('output')
        
        objs = []
        objs += list(Exam.objects.filter(name__contains=name))
        objs += list(Question.objects.filter(exam__name__contains=name))
        objs += list(VersionNode.objects.filter(question__exam__name__contains=name))
        
        self.stdout.ending = None
        stream = open(output, 'w') if output else None
        try:
            serializers.serialize(format, objs, indent=indent,
                    use_natural_foreign_keys=True,
                    use_natural_primary_keys=True,
                    stream=stream or self.stdout)
        finally:
            if stream:
                stream.close()
