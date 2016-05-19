
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
