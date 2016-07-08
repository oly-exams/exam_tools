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
    ctx = RequestContext(request)
    messages = []
    queue_list = printer.allowed_choices(request.user)
    enable_opts = request.user.has_perm('ipho_core.is_staff')
    success = False
    form = PrintForm(request.POST or None, request.FILES or None, queue_list=queue_list, enable_opts=enable_opts)
    if form.is_valid():
        try:
          opts = {
            'ColourModel': form.cleaned_data['color'],
            'Staple': form.cleaned_data['staple'],
            'Duplex': form.cleaned_data['duplex'],
          }
          status = printer.send2queue(form.cleaned_data['file'], form.cleaned_data['queue'], user=request.user, user_opts=opts)
          messages.append(('alert-success', '<strong>Success</strong> Print job submitted. Please pickup your document at the printing station.'))
          success = True
        except printer.PrinterError as e:
            messages.append(('alert-danger', '<strong>Error</strong> The document was uploaded successfully, but an error occured while communicating with the print server. Please try again or report the problem to the IPhO staff.<br /> Error was: '+e.msg))
        form = PrintForm(queue_list=queue_list)

    form_html = render_crispy_form(form, context=csrf(request))
    if request.is_ajax():
        return JsonResponse({
                'form'     : form_html,
                'messages' : messages,
                'success'  : success,
            })
    else:
        ctx['form'] = form_html
        ctx['messages'] = messages
        return render(request, 'ipho_print/main.html', ctx)
