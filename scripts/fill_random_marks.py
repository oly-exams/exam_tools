import random

from ipho_marking.models import Marking

all_markings = Marking.objects.all()
for marking in all_markings:
    marking.points = random.randint(0, 5)
    marking.save()
