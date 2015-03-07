# coding=utf-8
from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.templatetags.static import static


def index(request):
    return render_to_response('ipho_exam/index.html',
                              context_instance=RequestContext(request))


