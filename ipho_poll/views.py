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

import concurrent.futures
from dateutil import tz
from past.utils import old_div

from django.shortcuts import get_object_or_404, render
from django.http import (
    HttpResponseRedirect,
    JsonResponse,
    Http404,
    HttpResponse,
)
from django.urls import reverse
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.forms import inlineformset_factory
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Sum, Case, When, IntegerField, F

from crispy_forms.utils import render_crispy_form

from pywebpush import WebPushException


from ipho_core.models import User
from ipho_exam.models import Feedback, Exam

from .models import Question, Choice, VotingRight, Vote
from .forms import QuestionForm, ChoiceForm, VoteForm, EndDateForm
from .forms import ChoiceFormHelper, VoteFormHelper

# staff views


@login_required
@permission_required("ipho_core.can_manage_poll")
@ensure_csrf_cookie
def staff_index(request):
    return render(request, "ipho_poll/staff-index.html")


@login_required
@permission_required("ipho_core.can_manage_poll")
@ensure_csrf_cookie
def staff_index_partial(request, qtype):
    if qtype == "drafted":
        questions_list = Question.objects.is_draft().order_by("pk")
    elif qtype == "open":
        questions_list = Question.objects.is_open().order_by("pk")
    elif qtype == "closed":
        questions_list = Question.objects.is_closed().order_by("pk")
    else:
        raise RuntimeError("No valid qtype")
    choices_list = Choice.objects.all()

    return render(
        request,
        f"ipho_poll/tables/{qtype}_questions.html",
        {
            "questions_list": questions_list,
            "choices_list": choices_list,
            "VOTE_ACCEPTED": Question.VoteResultMeta.ACCEPTED,
            "VOTE_REJECTED": Question.VoteResultMeta.REJECTED,
            "VOTE_IMPLEMENTED": Question.ImplementationMeta.IMPL,
            "VOTE_NOT_IMPLEMENTED": Question.ImplementationMeta.NOT_IMPL,
        },
    )


@login_required
@permission_required("ipho_core.can_manage_poll")
@ensure_csrf_cookie
def question(request, question_pk):
    que = get_object_or_404(Question, pk=question_pk)
    choices = que.choice_set.all()
    voting_rights = VotingRight.objects.all()
    users = (
        User.objects.filter(votingright__in=voting_rights)
        .distinct()
        .order_by("username")
    )
    votes = Vote.objects.filter(choice__question=que)
    if que.is_draft():
        status = "draft"
    elif que.is_open():
        status = "open"
    else:
        status = "closed"
    ncols = 3
    num_users = len(users)
    col_step = max(1, int(old_div(num_users, ncols)))
    cols = [users[i : i + col_step] for i in range(0, num_users, col_step)]

    return render(
        request,
        "ipho_poll/question.html",
        {
            "question": que,
            "choices": choices,
            "voting_rights": voting_rights,
            "cols": cols,
            "votes": votes,
            "status": status,
            "VOTE_ACCEPTED": Question.VoteResultMeta.ACCEPTED,
            "result_choices": Question.VoteResultMeta.choices,
            "implementation_choices": Question.ImplementationMeta.choices,
        },
    )


@login_required
@permission_required("ipho_core.can_manage_poll")
def staff_set_result(request, question_pk, result):
    que = get_object_or_404(Question, pk=question_pk)
    que.vote_result = result
    que.save()
    return HttpResponseRedirect(reverse("poll:question", args=(que.pk,)))


@login_required
@permission_required("ipho_core.can_manage_poll")
def staff_set_impl(request, question_pk, impl):
    que = get_object_or_404(Question, pk=question_pk)
    que.implementation = impl
    que.save()
    return HttpResponseRedirect(reverse("poll:question", args=(que.pk,)))


@login_required
@permission_required("ipho_core.can_manage_poll")
@ensure_csrf_cookie
def question_large(request, question_pk):
    que = get_object_or_404(Question, pk=question_pk)
    choices = que.choice_set.all()
    if que.is_draft():
        status = "draft"
    elif que.is_open():
        status = "open"
    else:
        status = "closed"

    feedbacks = (
        que.feedbacks.filter(
            question__exam__visibility__gte=Exam.VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT_AND_BOARDMEETING
        )
        .all()
        .annotate(
            num_likes=Sum(
                Case(
                    When(like__status="L", then=1),
                    output_field=IntegerField(),
                    default=0,
                )
            ),
            num_unlikes=Sum(
                Case(
                    When(like__status="U", then=1),
                    output_field=IntegerField(),
                    default=0,
                )
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
            "timestamp",
            "part",
            "comment",
        )
    )

    display_remaining_users = getattr(
        settings, "VOTING_FULLSCREEN_DISPLAY_REMAINING_USERS", False
    )
    if display_remaining_users:
        users = (
            User.objects.filter(delegation__isnull=False)
            .annotate(v_count=Count("votingright", distinct=True))
            .annotate(
                q_count=Sum(
                    Case(
                        When(votingright__vote__question=que, then=1),
                        output_field=IntegerField(),
                        default=0,
                    )
                )
            )
            .exclude(q_count=F("v_count"))
        )
        usernames = sorted(
            user.username
            + (
                " ({}/{})".format(user.v_count - user.q_count, user.v_count)
                if user.q_count != 0
                else ""
            )
            for user in users
        )
        columns = 6
        if usernames:
            usernames.extend((None,) * (columns - len(usernames) % columns))
        remaining_users_to_vote = [
            usernames[i * columns : (i + 1) * columns]
            for i in range(len(usernames) // columns)
        ]
    else:
        remaining_users_to_vote = []

    return render(
        request,
        "ipho_poll/question_large.html",
        {
            "question": que,
            "choices": choices,
            "status": status,
            "feedbacks": feedbacks,
            "display_remaining_users": display_remaining_users,
            "remaining_users_to_vote": remaining_users_to_vote,
        },
    )


@login_required
@permission_required("ipho_core.can_manage_poll")
@ensure_csrf_cookie
def add_question(request):
    if not request.is_ajax:
        raise Exception(
            "TODO: implement small template page for handling without Ajax."
        )
    ChoiceFormset = inlineformset_factory(  # pylint: disable=invalid-name
        Question,
        Choice,
        form=ChoiceForm,
        extra=1,
        can_delete=False,
        min_num=2,
        validate_min=True,
    )
    if request.method == "POST":
        question_form = QuestionForm(request.POST, prefix="question")
        choice_formset = ChoiceFormset(request.POST, prefix="choices")
    else:
        question_form = QuestionForm(None, prefix="question")
        choice_formset = ChoiceFormset(
            None,
            prefix="choices",
            initial=[
                {},
                {},
                {"label": "zzz", "choice_text": "Abstain from this voting."},
            ],
        )
    if question_form.is_valid() and choice_formset.is_valid():
        new_question = question_form.save()
        for fback in Feedback.objects.filter(vote=new_question):
            fback.status = "V"  # scheduled for voting
            fback.save()
        choice_formset.instance = new_question
        choice_list = choice_formset.save(commit=False)
        choice_text_list = []
        for choice in choice_list:
            choice.question = new_question
            choice.save()
            choice_text_list.append(choice.choice_text)
        return JsonResponse(
            {
                "success": True,
                "message": "<strong> The voting has successfully been added!</strong>",
                "new_title": new_question.title,
                "new_question_pk": new_question.pk,
                "choice_text_list": choice_text_list,
                "type": "add",
            }
        )

    context = {}
    context.update(csrf(request))
    form_html = render_crispy_form(question_form, context=context) + render_crispy_form(
        choice_formset, helper=ChoiceFormHelper(can_delete=False), context=context
    )
    return JsonResponse(
        {
            "title": "Create new voting",
            "form": form_html,
            "success": False,
        }
    )


@login_required
@permission_required("ipho_core.can_manage_poll")
@ensure_csrf_cookie
def edit_question(request, question_pk):
    ChoiceFormset = inlineformset_factory(  # pylint: disable=invalid-name
        Question, Choice, form=ChoiceForm, extra=2, can_delete=True
    )
    que = get_object_or_404(Question, pk=question_pk)
    if request.method == "POST":
        question_form = QuestionForm(request.POST, instance=que, prefix="question")
        choice_formset = ChoiceFormset(request.POST, instance=que, prefix="choices")
    else:
        question_form = QuestionForm(instance=que, prefix="question")
        choice_formset = ChoiceFormset(instance=que, prefix="choices")
    if question_form.is_valid() and choice_formset.is_valid():
        que = question_form.save()
        choices = choice_formset.save()
        choice_text_list = []
        for choice in choices:
            choice_text_list.append(choice.choice_text)
        return JsonResponse(
            {
                "success": True,
                "message": "<strong> The voting has successfully been added!</strong>",
                "new_title": que.title,
                "new_question_pk": que.pk,
                "choice_text_list": choice_text_list,
                "type": "edit",
            }
        )

    context = {}
    context.update(csrf(request))
    form_html = render_crispy_form(question_form, context=context) + render_crispy_form(
        choice_formset, helper=ChoiceFormHelper(can_delete=True), context=context
    )
    return JsonResponse(
        {
            "title": "Edit voting",
            "form": form_html,
            "success": False,
        }
    )


@login_required
@permission_required("ipho_core.can_manage_poll")
@ensure_csrf_cookie
def delete_question(request, question_pk):
    que = get_object_or_404(Question, pk=question_pk)
    choice_list = Choice.objects.filter(question=que)
    # try:
    que.delete()
    for choice in choice_list:
        choice.delete()
    # except Exception:
    #     return JsonResponse({
    #                 'success'   : False,
    #                 'message'   : Exception.message,
    #     })
    #

    return JsonResponse(
        {
            "success": True,
            "message": "<strong>The voting #"
            + question_pk
            + " has been deleted successfully.</strong>",
        }
    )


@login_required
@permission_required("ipho_core.can_manage_poll")
@ensure_csrf_cookie
def set_end_date(request, question_pk):
    que = get_object_or_404(Question, pk=question_pk)
    end_date_form = EndDateForm(request.POST or None, instance=que)
    if end_date_form.is_valid():
        tzuser = tz.tzoffset(None, end_date_form.cleaned_data["utc_offset"] * 60)
        end_date = end_date_form.cleaned_data["end_date"]
        end_date = end_date.replace(tzinfo=None)
        end_date = end_date.replace(tzinfo=tzuser)
        que = end_date_form.save(commit=False)
        que.end_date = timezone.localtime(end_date)
        que.save()
        choice_text_list = []
        for choice in Choice.objects.filter(question=que):
            choice_text_list.append(choice.choice_text)

        if settings.ENABLE_PUSH:
            # send push messages
            data = {
                "body": "A voting has just opened, click here to go to the voting page",
                "url": reverse("poll:voter-index"),
                "reload_client": True,
            }
            psub_list = []

            for user in User.objects.all():
                if len(user.votingright_set.all()) > 0:
                    psub_list.extend(user.pushsubscription_set.all())

            def send_push(sub):
                try:
                    sub.send(data)
                except WebPushException:
                    # TODO: do some error handling?
                    pass

            # from multiprocessing import Pool
            # func_list = map(send_push, psub_list)
            # with Pool(processes=350) as pool:
            #    res = pool.map_async(work, func_list, 1)
            #    res.get(20)
            if len(psub_list) > 700:
                psub_list = psub_list[:700]
            with concurrent.futures.ThreadPoolExecutor(max_workers=700) as executor:
                executor.map(send_push, psub_list)
        return JsonResponse(
            {
                "success": True,
                "message": "<strong> The voting is now open!</strong>",
                "new_title": que.title,
                "new_question_pk": que.pk,
                "choice_text_list": choice_text_list,
            }
        )

    if not que.is_closed():
        context = {}
        context.update(csrf(request))
        form_html = render_crispy_form(end_date_form, context=context)
        return JsonResponse(
            {
                "success": False,
                "title": "Open Vote",
                "form": form_html,
                "modal_body_text": '<p>Select the deadline for the voting.</p><span id="deadline-buttons"></span>',
            }
        )

    raise Http404("Action not allowed")


@login_required
@permission_required("ipho_core.can_manage_poll")
@ensure_csrf_cookie
def remove_end_date(request, question_pk):
    que = get_object_or_404(Question, pk=question_pk)
    if not que.is_open():
        raise Http404("Action not allowed")

    que.end_date = None
    que.save()
    return HttpResponseRedirect(reverse("poll:staff-index"))


@login_required
@permission_required("ipho_core.can_manage_poll")
@ensure_csrf_cookie
def close_question(request, question_pk):
    que = get_object_or_404(Question, pk=question_pk)
    if not que.is_open():
        raise Http404("Action not allowed")

    que.end_date = timezone.now()
    que.save()
    return HttpResponseRedirect(reverse("poll:staff-index"))


# delegation views


@login_required
@ensure_csrf_cookie
def voter_index(request, err_id=None):
    user = request.user
    if len(user.votingright_set.all()) <= 0:
        raise PermissionDenied
    unvoted_questions_list = Question.objects.not_voted_upon_by(user)
    formset_html_dict = {}
    just_voted = ()
    for que in unvoted_questions_list:
        # gather voting_rights that could still be used
        voting_rights = user.votingright_set.exclude(vote__question=que).order_by(
            "name"
        )
        VoteFormsetFactory = inlineformset_factory(  # pylint: disable=invalid-name
            Question, Vote, form=VoteForm, extra=len(voting_rights), can_delete=False
        )
        post_request = None
        if request.POST is not None and f"q{que.pk}-TOTAL_FORMS" in request.POST:
            post_request = request.POST
        VoteFormset = VoteFormsetFactory(  # pylint: disable=invalid-name
            post_request,
            prefix=f"q{que.pk}",
            instance=que,
            queryset=Vote.objects.none(),  # .filter(voting_right__user=user),
            initial=[{"voting_right": vt} for vt in voting_rights],
        )
        for vote_form in VoteFormset:
            vote_form.fields["choice"].queryset = que.choice_set.all()
        if VoteFormset.is_valid():
            if timezone.now() < que.end_date:
                VoteFormset.save()
            just_voted += (que.pk,)
            return HttpResponseRedirect(reverse("poll:voted"))

        if request.method == "POST":
            response = HttpResponse(content="", status=303)
            err_id = 42
            response["Location"] = reverse("poll:voter-index_err", args=(42,))
            return response

        formset_html_dict[que.pk] = render_crispy_form(
            VoteFormset, helper=VoteFormHelper
        )

        que.feedbacks_list = (
            que.feedbacks.filter(
                question__exam__visibility__gte=Exam.VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT_AND_BOARDMEETING
            )
            .all()
            .annotate(
                num_likes=Sum(
                    Case(
                        When(like__status="L", then=1),
                        output_field=IntegerField(),
                        default=0,
                    )
                ),
                num_unlikes=Sum(
                    Case(
                        When(like__status="U", then=1),
                        output_field=IntegerField(),
                        default=0,
                    )
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
                "timestamp",
                "part",
                "comment",
            )
        )
    unvoted_questions_list = [
        q for q in unvoted_questions_list if q.pk not in just_voted
    ]
    if err_id == "42":
        err_msg = "Vote could not be saved (did you try to override a vote ?), please try again."
    else:
        err_msg = None
    return render(
        request,
        "ipho_poll/voter-index.html",
        {
            "unvoted_questions_list": unvoted_questions_list,
            "formset_list": formset_html_dict,
            "err": err_msg,
        },
    )


def voted(request):
    return render(request, "ipho_poll/voted.html")
