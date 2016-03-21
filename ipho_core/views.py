from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse

from ipho_core.models import AutoLogin, User

def autologin(request, token):
    user = authenticate(token=token)
    redirect_to = reverse('home')
    if user:
        login(request, user)
        return redirect(redirect_to)
    else:
        return redirect(settings.LOGIN_URL+'?next={}'.format(redirect_to))
