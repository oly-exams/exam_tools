from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.core import serializers
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import ensure_csrf_cookie
from crispy_forms.utils import render_crispy_form
from django.forms.formsets import formset_factory
from django.template import RequestContext



from .models import Question, Choice, Vote

from .forms import QuestionForm, ChoiceForm, VoteForm
from .forms import ChoiceFormHelper


#staff views

@login_required
@permission_required('iphoperm.is_staff')
@ensure_csrf_cookie
def staffIndex(request):
    drafted_questions_list = Question.objects.filter(status = 0)
    live_questions_list = Question.objects.filter(status = 1)
    closed_questions_list = Question.objects.filter(status = 2)
    choices_list = Choice.objects.all()

    return render(request, 'ipho_poll/staffIndex.html',
            {
                'drafted_questions_list'    : drafted_questions_list,
                'live_questions_list'       : live_questions_list,
                'closed_questions_list'     : closed_questions_list,
                'choices_list'              : choices_list,
            }
        )



@login_required
@permission_required('iphoperm.is_staff')
@ensure_csrf_cookie
def addQuestion(request):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    ChoiceFormset = formset_factory(ChoiceForm, extra=2)
    if request.method == 'POST':
        questionForm = QuestionForm(request.POST, prefix='question')
        choiceFormset = ChoiceFormset(request.POST, prefix='choices')
    else:
        questionForm = QuestionForm(None, prefix='question')
        choiceFormset = ChoiceFormset(None, prefix='choices')
    if questionForm.is_valid() and choiceFormset.is_valid():
        new_question = questionForm.save()
        choice_text_list = []
        for choiceForm in choiceFormset:
            new_choice = choiceForm.save(commit=False)
            new_choice.question = new_question
            new_choice.save()
            choice_text_list.append(new_choice.choice_text)
        return JsonResponse({
                    'success'           : True,
                    'message'           : '<strong> The voting has successfully been added!</strong>',
                    'new_question_text' : new_question.question_text,
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
@permission_required('iphoperm.is_staff')
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







#delegation views


@login_required
@permission_required('iphoperm.is_leader')
@ensure_csrf_cookie
def delegationIndex(request):
    live_questions_list = Question.objects.filter(status = 1)
    choices_list = Choice.objects.all()
    form_html = render_crispy_form(VoteForm())
    return render(request, 'ipho_poll/delegationIndex.html',
                {
                    'live_questions_list'       : live_questions_list,
                    'choices_list'              : choices_list,
                    'form'                      : form_html,
                }
            )


@login_required
@permission_required('iphoperm.is_leader')
@ensure_csrf_cookie
def addVote(request):
    if request.method == 'POST':
        voteForm = VoteForm(request.POST)
        if voteForm.is_valid():
            vote = voteForm.save(submit=False)
            #hier koennte ein test fuer die anzahl votes kommen
            return JsonResponse({
                        'message'   : 'Thanks, your vote has been saved.'
            })
