# Exam Tools
#
# Copyright (C) 2014 - 2019 Oly Exams Team
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

#!/usr/bin/env python


import pdfkit
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"
import sys

import django

django.setup()
from django.conf import settings

from django.shortcuts import get_object_or_404
from django.http import HttpRequest

from django.urls import reverse
from django.template.loader import render_to_string

from ipho_core.models import Delegation
from ipho_exam.models import Participant, Exam, Question

from django.db.models import Sum, F
from ipho_marking.models import MarkingMeta, Marking
from ipho_marking.forms import ImportForm, PointsForm
from django.forms import modelformset_factory, inlineformset_factory
import decimal


def moderation_detail(question_id, delegation_id, request=HttpRequest()):
    question = get_object_or_404(
        Question,
        id=question_id,
        exam__visibility__gte=Exam.VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT,
        exam__moderation_active=True,
    )
    delegation = get_object_or_404(Delegation, id=delegation_id)
    metas = MarkingMeta.objects.filter(question=question)
    participants = delegation.get_participants(question.exam)

    participant_forms = []
    marking_forms = []
    all_valid = True
    with_errors = False
    for i, participant in enumerate(participants):
        markings_official = Marking.objects.filter(
            participant=participant, marking_meta__in=metas, version="O"
        ).order_by("marking_meta__position")
        markings_delegation = Marking.objects.filter(
            participant=participant, marking_meta__in=metas, version="D"
        ).order_by("marking_meta__position")

        FormSet = modelformset_factory(
            Marking,
            form=PointsForm,
            fields=["points"],
            extra=0,
            can_delete=False,
            can_order=False,
        )
        form = FormSet(
            request.POST or None,
            prefix=f"Stud-{participant.pk}",
            queryset=Marking.objects.filter(
                marking_meta__in=metas, participant=participant, version="F"
            ),
        )
        for j, f in enumerate(form):
            f.fields["points"].widget.attrs["tabindex"] = i * len(metas) + j + 1
            f.fields["points"].widget.attrs["style"] = "width:60px"

        # TODO: accept only submission without None
        all_valid = all_valid and form.is_valid()
        with_errors = with_errors or form.errors

        participant_forms.append(
            (
                participant,
                form,
                markings_official,
                sum(
                    (m.points for m in markings_official if m.points is not None),
                    decimal.Decimal(0),
                ),
                sum(
                    (m.points for m in markings_delegation if m.points is not None),
                    decimal.Decimal(0),
                ),
            )
        )
        marking_forms.append(zip(markings_official, markings_delegation, form))

    if all_valid:
        for _, form, _, _, _ in participant_forms:
            form.save()
        return HttpResponseRedirect(
            reverse(
                "marking:moderation-confirmed",
                kwargs={"question_id": question.pk, "delegation_id": delegation.pk},
            )
        )
    # TODO: display errors
    ctx = {
        "question": question,
        "delegation": delegation,
        "participant_forms": participant_forms,
        "marking_forms": list(zip(metas, zip(*marking_forms))),
        "request": request,
        "max_points_sum": sum(m.max_points for m in metas),
    }
    body = render_to_string(
        "ipho_marking/moderation_detail.html", context=ctx, request=request
    )

    start = body.find("<!-- S")
    intermediate = body.find("sr-only")
    end = body.find('<div class="container', intermediate)

    start2 = body.find("[> /container")
    end2 = start2 + 16

    file = open(f"html/test-{question_id}-{delegation_id}.html", "w")
    file.write(body[:start] + body[end:start2] + body[end2:])
    file.close()
    pdfkit.from_file(
        f"html/test-{question_id}-{delegation_id}.html",
        f"pdf/test-{question_id}-{delegation_id}.pdf",
    )


answer_sheets = Question.objects.filter(
    exam__visibility__gte=Exam.VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT,
    exam__moderation_active=True,
    type=Question.ANSWER,
)
all_delegations = Delegation.objects.all()

for question in answer_sheets:
    for delegation in all_delegations:
        print(question.pk, delegation.pk)
        try:
            moderation_detail(question.pk, delegation.pk)
        except:
            pass
