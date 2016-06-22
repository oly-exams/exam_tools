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
        q = qml.QMLquestion(node.text)
        question_points(q)
        node.text = qml.xml2string(q.make_xml())
        node.save()

    for node in TranslationNode.objects.all():
        if not '<question' in node.text: continue
        q = qml.QMLquestion(node.text)
        question_points(q)
        node.text = qml.xml2string(q.make_xml())
        node.save()


if __name__ == '__main__':
    main()

