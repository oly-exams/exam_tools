from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse


def main(request):
    
    return render_to_response('main.html', {'allreps': []},
                              context_instance=RequestContext(request))

