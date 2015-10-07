from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required

from ipho_poll.models import Question, Choice, Vote
# What about staff ask Michele again





@login_required
@permission('iphoperm.is_staff')
def AdminOverview():
    drafted_questions_list = Question.objects.filter(status = 0)
    live_questions_list = Question.objects.filter(status = 1)
    closed_questions_list = Question.objects.filter(status = 2) 
    pass


@login_required
@permission('iphoperm.is_leader')
def DelegationOverwiev():
    live_questions_list = Question.objects.filter(status = 1)
    pass


















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
