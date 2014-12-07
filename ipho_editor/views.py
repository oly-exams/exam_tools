from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse


def index(request):
    return render_to_response('example_exam/index.html',
                              context_instance=RequestContext(request))
def view_exam(request, display_tpl="show"):
    
    base_template = "base_exam.html" if display_tpl == 'show' else "base_ckeditor.html"
    return render_to_response('example_exam/theo_2011_Q1.html', {'base_template': base_template},
                              context_instance=RequestContext(request))
def view(request):
    return view_exam(request, display_tpl="show")
def edit(request):
    return view_exam(request, display_tpl="edit")

def mathquill(request):
    return render_to_response('test_mathquill.html',
                              context_instance=RequestContext(request))

def mathquill_toolbar(request):
    return render_to_response('test_mathquill_toolbar.html',
                              context_instance=RequestContext(request))

