from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.core.urlresolvers import reverse
from django.core import serializers
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import ensure_csrf_cookie
from crispy_forms.utils import render_crispy_form
from django.forms import formset_factory, inlineformset_factory
from django.template import RequestContext



from .models import Question, Choice, Vote

from .forms import QuestionForm, ChoiceForm, VoteForm, EndDateForm
from .forms import ChoiceFormHelper


#staff views

@login_required
@permission_required('iphoperm.is_staff')
@ensure_csrf_cookie
def staffIndex(request):
    drafted_questions_list = Question.objects.is_draft()
    open_questions_list = Question.objects.is_open()
    closed_questions_list = Question.objects.is_closed()
    choices_list = Choice.objects.all()

    return render(request, 'ipho_poll/staffIndex.html',
            {
                'drafted_questions_list'    : drafted_questions_list,
                'open_questions_list'       : open_questions_list,
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
    ChoiceFormset = inlineformset_factory(Question, Choice, form=ChoiceForm, extra=0, can_delete=False, min_num=2, validate_min=True)
    if request.method == 'POST':
        questionForm = QuestionForm(request.POST, prefix='question')
        choiceFormset = ChoiceFormset(request.POST, prefix='choices')
    else:
        questionForm = QuestionForm(None, prefix='question')
        choiceFormset = ChoiceFormset(None, prefix='choices')
    if questionForm.is_valid() and choiceFormset.is_valid():
        new_question = questionForm.save()
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
                    'new_question_text' : question.question_text,
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



@login_required
@permission_required('iphoperm.is_staff')
@ensure_csrf_cookie
def setEndDate(request, question_pk):
    question = get_object_or_404(Question, pk=question_pk)
    if request.method == 'POST':
        endDateForm = EndDateForm(request.POST, instance=question)
    else:
        endDateForm = EndDateForm(instance=question)
    if endDateForm.is_valid():
        question = endDateForm.save()
        choice_text_list = []
        for choice in Choice.objects.filter(question=question):
            choice_text_list.append(choice.choice_text)
        return JsonResponse({
                        'success'           : True,
                        'message'           : '<strong> The voting is now open!</strong>',
                        'new_question_text' : question.question_text,
                        'new_question_pk'   : question.pk,
                        'choice_text_list'  : choice_text_list,
        })
    else:
        if not question.is_closed():
            context = {}
            context.update(csrf(request))
            form_html = render_crispy_form(endDateForm, context=context)
            return JsonResponse({
                        'title'             : 'Open Vote',
                        'form'              : form_html,
                        'modal_body_text'   : "Select the deadline for the voting.",
            })
        else:
            raise Http404("Action not allowed")




#delegation views


@login_required
@permission_required('iphoperm.is_leader')
@ensure_csrf_cookie
def delegationIndex(request):
    open_questions_list = Question.objects.is_open()
    choices_list = Choice.objects.all()
    # form_html_list = []
    # for question in open_questions_list:
    #      form_html_list.append(render_crispy_form(VoteForm(instance=question))
    return render(request, 'ipho_poll/delegationIndex.html',
                {
                    'open_questions_list'       : open_questions_list,
                    'choices_list'              : choices_list,
                    # 'form_list'               : form_html_list,
                }
            )


@login_required
@permission_required('iphoperm.is_leader')
@ensure_csrf_cookie
def addVote(request):
    if request.method == 'POST':
        voteForm = VoteForm(request.POST)
    else:
        voteForm = VoteForm()

    if voteForm.is_valid():
        vote = voteForm.save(submit=False)
        #hier koennte ein test fuer die anzahl votes kommen
        return JsonResponse({
                    'message'   : 'Thanks, your vote has been saved.'
        })
