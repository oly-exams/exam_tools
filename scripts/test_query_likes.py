import os

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

import django

django.setup()

from django.db import models
from django.db.models import Case, Count, Q, Sum, When

from ipho_exam.models import *

feedbacks = (
    Feedback.objects.filter(question__exam=1)
    .annotate(
        num_likes=Sum(
            Case(When(like__status="L", then=1), output_field=models.IntegerField())
        ),
        num_unlikes=Sum(
            Case(When(like__status="U", then=1), output_field=models.IntegerField())
        ),
    )
    .values(
        "num_likes",
        "num_unlikes",
        "pk",
        "question__name",
        "delegation__name",
        "delegation__country",
        "status",
        "part",
        "comment",
    )
)

print(feedbacks)
