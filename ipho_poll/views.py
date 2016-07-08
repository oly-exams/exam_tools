from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, JsonResponse, Http404, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.core import serializers
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import ensure_csrf_cookie
from crispy_forms.utils import render_crispy_form
from django.forms import formset_factory, inlineformset_factory
from django.template import RequestContext
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Q, Count, Sum, Case, When, IntegerField, F, Max



from ipho_core.models import User

from .models import Question, Choice, VotingRight, Vote
from ipho_exam.models import Feedback

from .forms import QuestionForm, ChoiceForm, VoteForm, EndDateForm
from .forms import ChoiceFormHelper, VoteFormHelper


#staff views

@login_required
@permission_required('ipho_core.is_staff')
@ensure_csrf_cookie
def staffIndex(request):
    return render(request, 'ipho_poll/staffIndex.html')

@login_required
@permission_required('ipho_core.is_staff')
@ensure_csrf_cookie
def staffIndexPartial(request, qtype):
    if qtype == 'drafted':
        questions_list = Question.objects.is_draft()
    elif qtype == 'open':
        questions_list = Question.objects.is_open()
    elif qtype == 'closed':
        questions_list = Question.objects.is_closed()
    else:
        raise RuntimeError('No valid qtype')
    choices_list = Choice.objects.all()

    return render(request, 'ipho_poll/tables/{}_questions.html'.format(qtype),
            {
                'questions_list'            : questions_list,
                'choices_list'              : choices_list,
                'VOTE_ACCEPTED'             : Question.VOTE_RESULT_META.ACCEPTED,
                'VOTE_REJECTED'             : Question.VOTE_RESULT_META.REJECTED,
                'VOTE_IMPLEMENTED'          : Question.IMPLEMENTATION_META.IMPL,
                'VOTE_NOT_IMPLEMENTED'      : Question.IMPLEMENTATION_META.NOT_IMPL,
            }
        )


@login_required
@permission_required('ipho_core.is_staff')
@ensure_csrf_cookie
def question(request, question_pk):
    question = get_object_or_404(Question, pk=question_pk)
    choices = question.choice_set.all()
    voting_rights = VotingRight.objects.all()
    users = User.objects.filter(votingright = voting_rights).distinct().order_by('username')
    votes = Vote.objects.filter(choice__question=question)
    if question.is_draft():
        status = 'draft'
    elif question.is_open():
        status = 'open'
    else:
        status = 'closed'
    ncols = 3
    num_users = len(users)
    col_step = max(1, int(num_users/ncols))
    cols = [users[i:i+col_step] for i in xrange(0, num_users, col_step)]


    return render(request, 'ipho_poll/question.html',
            {
                'question'      : question,
                'choices'       : choices,
                'voting_rights' : voting_rights,
                'cols'          : cols,
                'votes'         : votes,
                'status'        : status,
                'VOTE_ACCEPTED' : Question.VOTE_RESULT_META.ACCEPTED,
                'result_choices' : Question.VOTE_RESULT_META.choices,
                'implementation_choices': Question.IMPLEMENTATION_META.choices,
            }
    )

@login_required
@permission_required('ipho_core.is_staff')
def staff_setResult(request, question_pk, result):
    question = get_object_or_404(Question, pk=question_pk)
    question.vote_result = result
    question.save()
    return HttpResponseRedirect(reverse('poll:question', args=(question.pk,)))

@login_required
@permission_required('ipho_core.is_staff')
def staff_setImpl(request, question_pk, impl):
    question = get_object_or_404(Question, pk=question_pk)
    question.implementation = impl
    question.save()
    return HttpResponseRedirect(reverse('poll:question', args=(question.pk,)))


@login_required
@permission_required('ipho_core.is_staff')
@ensure_csrf_cookie
def question_large(request, question_pk):
    question = get_object_or_404(Question, pk=question_pk)
    choices = question.choice_set.all()
    if question.is_draft():
        status = 'draft'
    elif question.is_open():
        status = 'open'
    else:
        status = 'closed'

    feedbacks = question.feedbacks.all().annotate(
         num_likes=Sum(
             Case(When(like__status='L', then=1),
                  output_field=IntegerField(),
                  default=0)
         ),
         num_unlikes=Sum(
             Case(When(like__status='U', then=1),
                  output_field=IntegerField(),
                  default=0)
         )
    ).values(
        'num_likes',
        'num_unlikes',
        'pk',
        'question__name',
        'delegation__name',
        'delegation__country',
        'status',
        'timestamp',
        'part',
        'comment'
    )

    return render(request, 'ipho_poll/question_large.html',
            {
                'question'      : question,
                'choices'       : choices,
                'status'        : status,
                'feedbacks'     : feedbacks,
            }
    )


@login_required
@permission_required('ipho_core.is_staff')
@ensure_csrf_cookie
def addQuestion(request):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    ChoiceFormset = inlineformset_factory(Question, Choice, form=ChoiceForm, extra=0, can_delete=False, min_num=2, validate_min=True)
    if request.method == 'POST':
        questionForm = QuestionForm(request.POST, prefix='question')
        choiceFormset = ChoiceFormset(request.POST, prefix='choices')
    else:
        questionForm = QuestionForm(None, prefix='question')
        choiceFormset = ChoiceFormset(None, prefix='choices')
    if questionForm.is_valid() and choiceFormset.is_valid():
        new_question = questionForm.save()
        for fb in Feedback.objects.filter(vote=new_question):
            fb.status = 'V' # scheduled for voting
            fb.save()
        choiceFormset.instance = new_question
        choice_list = choiceFormset.save(commit=False)
        choice_text_list = []
        for choice in choice_list:
            choice.question = new_question
            choice.save()
            choice_text_list.append(choice.choice_text)
        return JsonResponse({
                    'success'           : True,
                    'message'           : '<strong> The voting has successfully been added!</strong>',
                    'new_title' : new_question.title,
                    'new_question_pk'   : new_question.pk,
                    'choice_text_list'  : choice_text_list,
                    'type'              : 'add',
                })
    else:
        context = {}
        context.update(csrf(request))
        form_html = (
                    render_crispy_form(questionForm, context=context) +
                    render_crispy_form(
                                        choiceFormset,
                                        helper=ChoiceFormHelper,
                                        context=context
                                        )
                    )
        return JsonResponse({
                    'title'         : 'Create new voting',
                    'form'          : form_html,
                    'success'       : False,
                })


@login_required
@permission_required('ipho_core.is_staff')
@ensure_csrf_cookie
def editQuestion(request, question_pk):
    ChoiceFormset = inlineformset_factory(Question, Choice, form=ChoiceForm, extra=2, can_delete=True)
    question = get_object_or_404(Question, pk=question_pk)
    if request.method == 'POST':
        questionForm = QuestionForm(request.POST, instance=question, prefix='question')
        choiceFormset = ChoiceFormset(request.POST, instance=question, prefix='choices')
    else:
        questionForm = QuestionForm(instance=question, prefix='question')
        choiceFormset = ChoiceFormset(instance=question, prefix='choices')
    if questionForm.is_valid() and choiceFormset.is_valid():
        question = questionForm.save()
        choices = choiceFormset.save()
        choice_text_list = []
        for choice in choices:
            choice_text_list.append(choice.choice_text)
        return JsonResponse({
                    'success'           : True,
                    'message'           : '<strong> The voting has successfully been added!</strong>',
                    'new_title' : question.title,
                    'new_question_pk'   : question.pk,
                    'choice_text_list'  : choice_text_list,
                    'type'              : 'edit',
                })
    else:
        context = {}
        context.update(csrf(request))
        form_html = (
                    render_crispy_form(questionForm, context=context) +
                    render_crispy_form(
                                        choiceFormset,
                                        helper=ChoiceFormHelper,
                                        context=context
                                        )
                    )
        return JsonResponse({
                    'title'         : 'Edit voting',
                    'form'          : form_html,
                    'success'       : False,
                })


@login_required
@permission_required('ipho_core.is_staff')
@ensure_csrf_cookie
def deleteQuestion(request, question_pk):
    question = get_object_or_404(Question, pk=question_pk)
    choice_list = Choice.objects.filter(question=question)
    # try:
    question.delete()
    for choice in choice_list:
        choice.delete()
    # except Exception:
    #     return JsonResponse({
    #                 'success'   : False,
    #                 'message'   : Exception.message,
    #     })
    #

    return JsonResponse({
                'success'   : True,
                'message'   : "<strong>The voting #" + question_pk + " has been deleted successfully.</strong>"
                })



@login_required
@permission_required('ipho_core.is_staff')
@ensure_csrf_cookie
def setEndDate(request, question_pk):
    question = get_object_or_404(Question, pk=question_pk)
    endDateForm = EndDateForm(request.POST or None, instance=question)
    if endDateForm.is_valid():
        question = endDateForm.save()
        choice_text_list = []
        for choice in Choice.objects.filter(question=question):
            choice_text_list.append(choice.choice_text)
        return JsonResponse({
                        'success'           : True,
                        'message'           : '<strong> The voting is now open!</strong>',
                        'new_title' : question.title,
                        'new_question_pk'   : question.pk,
                        'choice_text_list'  : choice_text_list,
        })
    else:
        if not question.is_closed():
            context = {}
            context.update(csrf(request))
            form_html = render_crispy_form(endDateForm, context=context)
            return JsonResponse({
                        'success'           : False,
                        'title'             : 'Open Vote',
                        'form'              : form_html,
                        'modal_body_text'   : "Select the deadline for the voting.",
            })
        else:
            raise Http404("Action not allowed")

@login_required
@permission_required('ipho_core.is_staff')
@ensure_csrf_cookie
def removeEndDate(request, question_pk):
    question = get_object_or_404(Question, pk=question_pk)
    if not question.is_open():
        raise Http404("Action not allowed")
    else:
        question.end_date = None
        question.save()
        return HttpResponseRedirect(reverse('poll:staffIndex'))











#delegation views


@login_required
@ensure_csrf_cookie
def voterIndex(request):
    user = request.user
    if len(user.votingright_set.all()) <= 0:
        raise PermissionDenied
    unvoted_questions_list = Question.objects.not_voted_upon_by(user)
    formset_html_dict = {}
    just_voted = ()
    for question in unvoted_questions_list:
        # gather voting_rights that could still be used
        voting_rights = user.votingright_set.exclude(vote__question=question)
        VoteFormsetFactory = inlineformset_factory(Question, Vote, form=VoteForm, extra = len(voting_rights), can_delete = False)
        postReqest = None
        if request.POST is not None and 'q{}-TOTAL_FORMS'.format(question.pk) in request.POST:
            postReqest = request.POST
        voteFormset = VoteFormsetFactory(postReqest, prefix='q{}'.format(question.pk), instance = question, queryset=Vote.objects.filter(voting_right__user=user), initial=[{'voting_right': vt} for vt in voting_rights])
        for voteForm in voteFormset:
            voteForm.fields['choice'].queryset = question.choice_set.all()
        if voteFormset.is_valid():
            if timezone.now() < question.end_date:
                voteFormset.save()
            just_voted += (question.pk,)
            return HttpResponseRedirect(reverse('poll:voted'))


        else:
            formset_html_dict[question.pk] = render_crispy_form(voteFormset, helper=VoteFormHelper)

        question.feedbacks_list = question.feedbacks.all().annotate(
             num_likes=Sum(
                 Case(When(like__status='L', then=1),
                      output_field=IntegerField(),
                      default=0)
             ),
             num_unlikes=Sum(
                 Case(When(like__status='U', then=1),
                      output_field=IntegerField(),
                      default=0)
             )
        ).values(
            'num_likes',
            'num_unlikes',
            'pk',
            'question__name',
            'delegation__name',
            'delegation__country',
            'status',
            'timestamp',
            'part',
            'comment'
        )
    unvoted_questions_list = filter(lambda q: q.pk not in just_voted, unvoted_questions_list)
    return render(request, 'ipho_poll/voterIndex.html',
                {
                    'unvoted_questions_list'    : unvoted_questions_list,
                    'formset_list'              : formset_html_dict,
                }
            )

def voted(request):
    return render(request, 'ipho_poll/voted.html')
