from django.http import HttpResponse, Http404, HttpResponseNotModified, HttpResponseRedirect
from django.core.urlresolvers import reverse

from hashlib import md5

from ipho_exam import pdf, tasks

def compile_tex(request, body, ext_resources=[], filename='question.pdf'):
    etag = md5(body).hexdigest()
    if request.META.get('HTTP_IF_NONE_MATCH', '') == etag:
        return HttpResponseNotModified()

    job = tasks.compile_tex.delay(body, ext_resources, filename, etag)
    return HttpResponseRedirect(reverse('exam:pdf-task', args=[job.id]))
