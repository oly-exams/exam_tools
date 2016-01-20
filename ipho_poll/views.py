from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import ensure_csrf_cookie
from crispy_forms.utils import render_crispy_form

from .models import Question, Choice, Vote

from .forms import QuestionForm

#admin views

@login_required
@permission_required('iphoperm.is_staff')
@ensure_csrf_cookie
def adminIndex(request):
    drafted_questions_list = Question.objects.filter(status = 0)
    live_questions_list = Question.objects.filter(status = 1)
    closed_questions_list = Question.objects.filter(status = 2)


    return render(request, 'ipho_poll/adminIndex.html',
            {
                'drafted_questions_list'    : drafted_questions_list,
                'live_questions_list'       : live_questions_list,
                'closed_questions_list'     : closed_questions_list,
            }
        )



@login_required
@permission_required('iphoperm.is_staff')
@ensure_csrf_cookie
def addQuestion(request):
    if not request.is_ajax:
        raise Exception('TODO: implement small template page for handling without Ajax.')
    questionForm = QuestionForm(request.POST or None)
    if questionForm.is_valid():
        new_question = questionForm.save()
        return JsonResponse({
                    'success' : True,
                    'message' : 'The question has successfully been added.',
                })
    else:
        form_html = render_crispy_form(questionForm)
        return JsonResponse({
                    'title' : 'Create New Question',
                    'form' : form_html,
                    'success' : False,
                    'message' : 'The question could not be added.',
                })








#delegation views


@login_required
@permission_required('iphoperm.is_leader')
@ensure_csrf_cookie
def delegationIndex(request):
    live_questions_list = Question.objects.filter(status = 1)


















#class IndexView(generic.ListView):
#    template_name = 'polls/index.html'
#    context_object_name = 'latest_question_list'
#
#    def get_queryset(self):
#        """
#        Return the last five published questions (not including those set to be
#        published in the future and those with no choices).
#        """
#        return Question.objects.filter(
#               choice__gte=1, pub_date__lte=timezone.now()
#        ).distinct().order_by('-pub_date')[0:5]
#
#
#class DetailView(generic.DetailView):
#    model = Question
#    template_name = 'polls/detail.html'
#    def get_queryset(self):
#        """
#        Excludes any questions that aren't published yet.
#        Excludes any questions with no choices.
#        """
#        return Question.objects.filter(
#            choice__gte=1, pub_date__lte=timezone.now()
#        ).distinct()
#
#
#class ResultsView(generic.DetailView):
#    model = Question
#    template_name = 'polls/results.html'
#    def get_queryset(self):
#        """
#        Excludes any questions that aren't published yet.
#        """
#        return Question.objects.filter(pub_date__lte=timezone.now())
#
#
#def vote(request, question_id):
#    p = get_object_or_404(Question, pk=question_id)
#    try:
#        selected_choice = p.choice_set.get(pk=request.POST['choice'])
#    except (KeyError, Choice.DoesNotExist):
#        #Redisplay the question voting form
#        return render(request, 'polls/detail.html', {'question': p, 'error_message': "You didn't select a choice.",
#        })
#    else:
#        selected_choice.votes += 1
#        selected_choice.save()
#        #Always return an HttpResponse after succesfully dealing with POST data. This prevents data from being posted twice if a user hits the Back button.
#        return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))
