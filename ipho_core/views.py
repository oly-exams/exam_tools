from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse

from ipho_core.models import AutoLogin, User

DEMO_MODE = getattr(settings, 'DEMO_MODE')

def autologin(request, token):
    if not DEMO_MODE and not request.user.has_perm('ipho_core.is_staff'):
        return HttpResponseForbidden('Only the staff can use autologin.')
    user = authenticate(token=token)
    redirect_to = reverse('home')
    if user:
        login(request, user)
        return redirect(redirect_to)
    else:
        return redirect(settings.LOGIN_URL+'?next={}'.format(redirect_to))

@permission_required('ipho_core.is_staff')
def list_impersonate(request):
    users = User.objects.exclude(delegation__isnull=True).exclude(autologin__isnull=True).order_by('username')
    chunk_size = max(len(users) / 6 + 1, 1)
    grouped_users = [users[x:x+chunk_size] for x in xrange(0, len(users), chunk_size)]
    return render(request, 'ipho_core/impersonate.html', {'grouped_users' : grouped_users})
