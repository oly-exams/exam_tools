from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotModified, JsonResponse, Http404, HttpResponseForbidden
from django.template import RequestContext
from django.core.context_processors import csrf
from crispy_forms.utils import render_crispy_form
from django.conf import settings

from .forms import PrintForm

import printer

PRINTER_QUEUES = getattr(settings, 'PRINTER_QUEUES')


@login_required
def main(request):
    # TODO: check permissions and select printers accordingly
    ctx = RequestContext(request)
    messages = []
    form = PrintForm(request.POST or None, request.FILES or None, queue_list=['irchel-1', 'irchel-2'])
    if form.is_valid():
        #txt = request.FILES['file'].read()
        status = printer.send2queue(request.FILES['file'], form.cleaned_data['queue'], user=request.user)
        if status == printer.SUCCESS:
            messages.append(('alert-success', '<strong>Success</strong> Print job submitted. Please pickup your document at the printing station.'))
        else:
            messages.append(('alert-danger', '<strong>Error</strong> The document was uploaded successfully, but an error occured while communicating with the print server. Please try again or report the problem to the IPhO staff.'))
            
        form = PrintForm(queue_list=['irchel-1', 'irchel-2'])

    form_html = render_crispy_form(form, context=csrf(request))
    if request.is_ajax():
        return JsonResponse({
                'form'     : form_html,
                'messages' : messages,
            })
    else:
        ctx['form'] = form_html
        ctx['messages'] = messages
        return render(request, 'ipho_print/main.html', ctx)
