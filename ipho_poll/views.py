# Exam Tools
#
# Copyright (C) 2014 - 2023 Oly Exams Team
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
)
from django.urls import reverse
from django.template.context_processors import csrf
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test,
)
from django.views.decorators.csrf import ensure_csrf_cookie
from django.forms import inlineformset_factory, modelform_factory
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Sum, Case, When, IntegerField, F

from crispy_forms.utils import render_crispy_form

from pywebpush import WebPushException


from ipho_core.models import User
from ipho_exam.models import Feedback, Exam

from .models import Voting, VotingChoice, VotingRight, CastedVote, VotingRoom
from .forms import VotingForm, VotingChoiceForm, CastedVoteForm, EndDateForm
from .forms import VotingChoiceFormHelper, CastedVoteFormHelper, CastedVoteBaseFormset

# staff views


@login_required
@permission_required("ipho_core.can_edit_poll")
@ensure_csrf_cookie
def staff_index(request, room_id=None):
    voting_rooms = VotingRoom.objects.for_user(request.user)
    if voting_rooms.exists():
        if room_id is None:
            if voting_rooms.count() == 1:
                return staff_index(request, room_id=voting_rooms.first().pk)
            return render(
                request,
                "ipho_poll/choose-rooms.html",
                {"rooms": voting_rooms.all(), "view_name": "poll:staff-index_room"},
            )
        room = get_object_or_404(voting_rooms, id=room_id)
    else:
        room = None

    return render(
        request,
        "ipho_poll/staff-index.html",
        {
            "rooms": voting_rooms.all(),
            "active_room": room,
            "view_name": "poll:staff-index_room",
        },
    )


@login_required
@permission_required("ipho_core.can_edit_poll")
@ensure_csrf_cookie
def staff_index_partial(request, qtype, room_id=None):
    if room_id is None:
        room = None
    else:
        room = get_object_or_404(VotingRoom.objects.for_user(request.user), pk=room_id)

    votings = Voting.objects.filter(voting_room=room)
    if qtype == "drafted":
        votings_list = votings.is_draft().order_by("pk")
    elif qtype == "open":
        votings_list = votings.is_open().order_by("pk")
    elif qtype == "closed":
        votings_list = votings.is_closed().order_by("pk")
    else:
        raise RuntimeError("No valid qtype")
    choices_list = VotingChoice.objects.all()

    return render(
        request,
        f"ipho_poll/tables/{qtype}_votings.html",
        {
            "votings_list": votings_list,
            "choices_list": choices_list,
            "VOTE_ACCEPTED": Voting.VoteResultMeta.ACCEPTED,
            "VOTE_REJECTED": Voting.VoteResultMeta.REJECTED,
            "VOTE_IMPLEMENTED": Voting.ImplementationMeta.IMPL,
            "VOTE_NOT_IMPLEMENTED": Voting.ImplementationMeta.NOT_IMPL,
            "active_room": room,
        },
    )


@login_required
@permission_required("ipho_core.can_edit_poll")
@ensure_csrf_cookie
def voting_details(request, voting_pk):
    voting = get_object_or_404(Voting, pk=voting_pk)
    choices = voting.votingchoice_set.all()
    voting_rights = VotingRight.objects.all()
    users = (
        User.objects.filter(votingright__in=voting_rights)
        .distinct()
        .order_by("username")
    )
    votes = CastedVote.objects.filter(choice__voting=voting)
    if voting.is_draft():
        status = "draft"
    elif voting.is_open():
        status = "open"
    else:
        status = "closed"
    ncols = 3
    num_users = len(users)
    col_step = max(1, int(old_div(num_users, ncols)))
    cols = [users[i : i + col_step] for i in range(0, num_users, col_step)]

    return render(
        request,
        "ipho_poll/voting.html",
        {
            "voting": voting,
            "choices": choices,
            "voting_rights": voting_rights,
            "cols": cols,
            "votes": votes,
            "status": status,
            "VOTE_ACCEPTED": Voting.VoteResultMeta.ACCEPTED,
            "result_choices": Voting.VoteResultMeta.choices,
            "implementation_choices": Voting.ImplementationMeta.choices,
        },
    )


@login_required
@permission_required("ipho_core.can_edit_poll")
def staff_set_result(request, voting_pk, result):
    voting = get_object_or_404(Voting, pk=voting_pk)
    voting.vote_result = result
    voting.save()
    return HttpResponseRedirect(reverse("poll:voting", args=(voting.pk,)))


@login_required
@permission_required("ipho_core.can_edit_poll")
def staff_set_impl(request, voting_pk, impl):
    voting = get_object_or_404(Voting, pk=voting_pk)
    voting.implementation = impl
    voting.save()
    return HttpResponseRedirect(reverse("poll:voting", args=(voting.pk,)))


@login_required
@permission_required("ipho_core.can_edit_poll")
@ensure_csrf_cookie
def voting_large(request, voting_pk):
    voting = get_object_or_404(Voting, pk=voting_pk)
    choices = voting.votingchoice_set.all()
    if voting.is_draft():
        status = "draft"
    elif voting.is_open():
        status = "open"
    else:
        status = "closed"

    feedbacks = (
        voting.feedbacks.filter(
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
                        When(votingright__castedvote__voting=voting, then=1),
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
                f" ({user.v_count - user.q_count}/{user.v_count})"
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
        "ipho_poll/voting_large.html",
        {
            "voting": voting,
            "choices": choices,
            "status": status,
            "feedbacks": feedbacks,
            "display_remaining_users": display_remaining_users,
            "remaining_users_to_vote": remaining_users_to_vote,
        },
    )


@login_required
@permission_required("ipho_core.can_edit_poll")
@ensure_csrf_cookie
def add_voting(request, room_id=None):
    if not request.headers.get("x-requested-with") == "XMLHttpRequest":
        raise NotImplementedError(
            "TODO: implement small template page for handling without Ajax."
        )
    if room_id is None:
        room = None
    else:
        room = get_object_or_404(VotingRoom.objects.for_user(request.user), pk=room_id)

    VotingChoiceFormset = inlineformset_factory(  # pylint: disable=invalid-name
        Voting,
        VotingChoice,
        form=VotingChoiceForm,
        extra=1,
        can_delete=False,
        min_num=2,
        validate_min=True,
    )
    if request.method == "POST":
        voting_form = VotingForm(request.POST, prefix="voting")
        choice_formset = VotingChoiceFormset(request.POST, prefix="choices")
    else:
        voting_form = VotingForm(None, prefix="voting")
        choice_formset = VotingChoiceFormset(
            None,
            prefix="choices",
            initial=[
                {},
                {},
                {"label": "zzz", "choice_text": "Abstain from this voting."},
            ],
        )
    if voting_form.is_valid() and choice_formset.is_valid():
        new_voting = voting_form.save()
        new_voting.voting_room = room
        new_voting.save()
        for fback in Feedback.objects.filter(vote=new_voting):
            fback.status = "V"  # scheduled for voting
            fback.save()
        choice_formset.instance = new_voting
        choice_list = choice_formset.save(commit=False)
        choice_text_list = []
        for choice in choice_list:
            choice.voting = new_voting
            choice.save()
            choice_text_list.append(choice.choice_text)
        return JsonResponse(
            {
                "success": True,
                "message": "<strong> The voting has successfully been added!</strong>",
                "new_title": new_voting.title,
                "new_voting_pk": new_voting.pk,
                "choice_text_list": choice_text_list,
                "type": "add",
            }
        )

    context = {}
    context.update(csrf(request))
    form_html = render_crispy_form(voting_form, context=context) + render_crispy_form(
        choice_formset, helper=VotingChoiceFormHelper(can_delete=False), context=context
    )
    return JsonResponse(
        {
            "title": "Create new voting",
            "form": form_html,
            "success": False,
        }
    )


@login_required
@permission_required("ipho_core.can_edit_poll")
@ensure_csrf_cookie
def edit_voting(request, voting_pk):
    VotingChoiceFormset = inlineformset_factory(  # pylint: disable=invalid-name
        Voting, VotingChoice, form=VotingChoiceForm, extra=2, can_delete=True
    )
    voting = get_object_or_404(Voting, pk=voting_pk)
    if request.method == "POST":
        voting_form = VotingForm(request.POST, instance=voting, prefix="voting")
        choice_formset = VotingChoiceFormset(
            request.POST, instance=voting, prefix="choices"
        )
    else:
        voting_form = VotingForm(instance=voting, prefix="voting")
        choice_formset = VotingChoiceFormset(instance=voting, prefix="choices")
    if voting_form.is_valid() and choice_formset.is_valid():
        voting = voting_form.save()
        choices = choice_formset.save()
        choice_text_list = []
        for choice in choices:
            choice_text_list.append(choice.choice_text)
        return JsonResponse(
            {
                "success": True,
                "message": "<strong> The voting has successfully been added!</strong>",
                "new_title": voting.title,
                "new_voting_pk": voting.pk,
                "choice_text_list": choice_text_list,
                "type": "edit",
            }
        )

    context = {}
    context.update(csrf(request))
    form_html = render_crispy_form(voting_form, context=context) + render_crispy_form(
        choice_formset, helper=VotingChoiceFormHelper(can_delete=True), context=context
    )
    return JsonResponse(
        {
            "title": "Edit voting",
            "form": form_html,
            "success": False,
        }
    )


@login_required
@permission_required("ipho_core.can_edit_poll")
@ensure_csrf_cookie
def delete_voting(request, voting_pk):
    voting = get_object_or_404(Voting, pk=voting_pk)
    choice_list = VotingChoice.objects.filter(voting=voting)
    # try:
    voting_pk = voting.pk
    voting.delete()
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
            "message": f"<strong>The voting #{voting_pk} has been deleted successfully.</strong>",
        }
    )


@login_required
@permission_required("ipho_core.can_edit_poll")
@ensure_csrf_cookie
def set_end_date(request, voting_pk):
    voting = get_object_or_404(Voting, pk=voting_pk)
    end_date_form = EndDateForm(request.POST or None, instance=voting)
    if end_date_form.is_valid():
        tzuser = tz.tzoffset(None, end_date_form.cleaned_data["utc_offset"] * 60)
        end_date = end_date_form.cleaned_data["end_date"]
        end_date = end_date.replace(tzinfo=None)
        end_date = end_date.replace(tzinfo=tzuser)
        voting = end_date_form.save(commit=False)
        voting.end_date = timezone.localtime(end_date)
        voting.save()
        choice_text_list = []
        for choice in VotingChoice.objects.filter(voting=voting):
            choice_text_list.append(choice.choice_text)

        if settings.ENABLE_PUSH:
            # send push messages
            room_txt = ""
            if voting.voting_room is not None:
                room_txt = f" in room {voting.voting_room.name}"
            data = {
                "body": f"A voting has just opened{room_txt}, click here to go to the voting page",
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
                "new_title": voting.title,
                "new_voting_pk": voting.pk,
                "choice_text_list": choice_text_list,
            }
        )

    if not voting.is_closed():
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
@permission_required("ipho_core.can_edit_poll")
@ensure_csrf_cookie
def remove_end_date(request, voting_pk):
    voting = get_object_or_404(Voting, pk=voting_pk)
    if not voting.is_open():
        raise Http404("Action not allowed")

    voting.end_date = None
    voting.save()
    if voting.voting_room is not None:
        return HttpResponseRedirect(
            reverse("poll:staff-index_room", kwargs={"room_id": voting.voting_room.id})
        )
    return HttpResponseRedirect(reverse("poll:staff-index"))


@login_required
@permission_required("ipho_core.can_edit_poll")
@ensure_csrf_cookie
def close_voting(request, voting_pk):
    voting = get_object_or_404(Voting, pk=voting_pk)
    if not voting.is_open():
        raise Http404("Action not allowed")

    voting.end_date = timezone.now()
    voting.save()
    if voting.voting_room is not None:
        return HttpResponseRedirect(
            reverse("poll:staff-index_room", kwargs={"room_id": voting.voting_room.id})
        )
    return HttpResponseRedirect(reverse("poll:staff-index"))


@user_passes_test(lambda u: u.is_superuser)
@ensure_csrf_cookie
def edit_room(request, room_id):
    # pylint: disable=invalid-name
    room = get_object_or_404(VotingRoom.objects.for_user(request.user), pk=room_id)
    VotingRoomForm = modelform_factory(VotingRoom, fields=["name", "visibility"])
    form = VotingRoomForm(request.POST or None, instance=room)
    if form.is_valid():
        form.save()
        return JsonResponse(
            {
                "success": True,
                "message": "<strong> Saved</strong>",
            }
        )

    context = {}
    context.update(csrf(request))
    form_html = render_crispy_form(form, context=context)
    return JsonResponse(
        {
            "success": False,
            "title": "Edit Room",
            "form": form_html,
        }
    )


# delegation views


@login_required
@ensure_csrf_cookie
def voter_index(
    request, err_id=None, room_id=None
):  # pylint: disable=too-many-branches, too-many-locals
    voting_rooms = VotingRoom.objects.for_user(request.user)
    if voting_rooms.exists():
        if room_id is None:
            if voting_rooms.count() == 1:
                return voter_index(request, err_id, room_id=voting_rooms.first().pk)
            return render(
                request,
                "ipho_poll/choose-rooms.html",
                {"rooms": voting_rooms.all(), "view_name": "poll:voter-index_room"},
            )
        room = get_object_or_404(voting_rooms, id=room_id)
    else:
        room = None

    user = request.user
    if len(user.votingright_set.all()) <= 0:
        raise PermissionDenied
    votings = Voting.objects.filter(voting_room=room)
    unvoted_votings_list = votings.not_voted_upon_by(user)
    formset_html_dict = {}
    feedback_dict = {}
    just_voted = []
    errors = []
    err_msg = None
    for voting in unvoted_votings_list:
        # gather voting_rights that could still be used
        voting_rights = user.votingright_set.exclude(
            castedvote__voting=voting
        ).order_by("name")
        CastedVoteFormsetFactory = (  # pylint: disable=invalid-name
            inlineformset_factory(
                Voting,
                CastedVote,
                form=CastedVoteForm,
                formset=CastedVoteBaseFormset,
                extra=len(voting_rights),
                can_delete=False,
            )
        )
        post_for_this_voting = None
        this_voting_submitted = False
        if request.POST is not None and f"q{voting.pk}-TOTAL_FORMS" in request.POST:
            post_for_this_voting = request.POST
            this_voting_submitted = True

        CastedVoteFormset = CastedVoteFormsetFactory(  # pylint: disable=invalid-name
            post_for_this_voting,
            prefix=f"q{voting.pk}",
            instance=voting,
            queryset=CastedVote.objects.none(),  # .filter(voting_right__user=user),
            initial=[{"voting_right": vt} for vt in voting_rights],
        )
        for vote_form in CastedVoteFormset:
            vote_form.fields[
                "choice"
            ].queryset = voting.votingchoice_set.all().order_by("pk")

        if this_voting_submitted:
            if CastedVoteFormset.is_valid():
                CastedVoteFormset.save()
                just_voted.append(voting.pk)
            else:
                errors.append(voting.pk)
        formset_html_dict[voting.pk] = render_crispy_form(
            CastedVoteFormset, helper=CastedVoteFormHelper
        )

        feedbacks_list = (
            voting.feedbacks.filter(
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

        feedback_dict[voting.pk] = feedbacks_list
    if just_voted and not errors:
        if room:
            return HttpResponseRedirect(
                reverse("poll:voted_room", kwargs={"room_id": room.pk})
            )
        return HttpResponseRedirect(reverse("poll:voted"))

    # If there is a request.POST but no valid question, show an error message
    if (not just_voted) and (not errors) and request.POST:
        err_msg = "No vote saved. The corresponding voting is already closed or all votes of your delegation have been cast."

    unvoted_open_votings_list = votings.is_open().not_voted_upon_by(user)

    # If an error occured but the voting is not accessible anymore (i.e. closed), show an error message
    if err_msg is None and unvoted_open_votings_list.filter(
        pk__in=errors
    ).count() < len(errors):
        err_msg = "No vote saved. The corresponding voting is already closed or all votes of your delegation have been cast."

    return render(
        request,
        "ipho_poll/voter-index.html",
        {
            "unvoted_votings_list": unvoted_open_votings_list,
            "formset_list": formset_html_dict,
            "feedback_dict": feedback_dict,
            "err": err_msg,
            "rooms": voting_rooms.all(),
            "active_room": room,
            "voting_rights_count": user.votingright_set.count(),
        },
    )


def voted(request, room_id=None):
    return render(request, "ipho_poll/voted.html", {"room_id": room_id})
