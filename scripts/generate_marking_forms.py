#!/usr/bin/env python


import os

import pdfkit

os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings"
import sys

import django

django.setup()
import decimal

from django.conf import settings
from django.db.models import F, Sum
from django.forms import inlineformset_factory, modelformset_factory
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse

from ipho_core.models import Delegation
from ipho_exam.models import Exam, Participant, Question
from ipho_marking.forms import ImportForm, PointsForm
from ipho_marking.models import Marking, MarkingMeta


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
        )
        markings_delegation = Marking.objects.filter(
            participant=participant, marking_meta__in=metas, version="D"
        )

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
