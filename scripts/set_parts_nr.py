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
from ipho_exam.models import TranslationNode, VersionNode
from ipho_exam import qml

def question_points(root, part_num=-1, subq_num=0):
    part_code = lambda num: chr(65+num)
    for obj in root.children:
        if isinstance(obj, qml.QMLpart):
            part_num += 1
            subq_num = 0
            if not 'Part' in obj.data:
                obj.data = 'Part {}: '.format(part_code(part_num)) + obj.data
        if isinstance(obj, qml.QMLsubquestion):
            subq_num += 1
            obj.attributes['part_nr'] = part_code(part_num)
            obj.attributes['question_nr'] = str(subq_num)
        part_num, subq_num = question_points(obj, part_num, subq_num)
    return part_num, subq_num


def main():
    for node in VersionNode.objects.all():
        if not '<question' in node.text: continue
        q = qml.make_qml(node)
        question_points(q)
        node.text = qml.xml2string(q.make_xml())
        node.save()

    for node in TranslationNode.objects.all():
        if not '<question' in node.text: continue
        q = qml.make_qml(node)
        question_points(q)
        node.text = qml.xml2string(q.make_xml())
        node.save()


if __name__ == '__main__':
    main()
