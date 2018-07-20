# Exam Tools
#
# Copyright (C) 2014 - 2018 Oly Exams Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division

from builtins import range
from past.utils import old_div
import json
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from pywebpush import WebPushException

from ipho_core.models import AutoLogin, User, PushSubscription, RandomDrawLog, Delegation
from ipho_core.forms import AccountRequestForm, SendPushForm, RandomDrawForm

DEMO_MODE = getattr(settings, 'DEMO_MODE')
DEMO_SIGN_UP = getattr(settings, 'DEMO_SIGN_UP')
OFFICIAL_DELEGATION = getattr(settings, 'OFFICIAL_DELEGATION')



def any_permission_required(*args):
    """
    A decorator which checks user has any of the given permissions.
    permission required can not be used in its place as that takes only a
    single permission.
    """

    def test_func(user):
        for perm in args:
            if user.has_perm(perm):
                return True
        return False

    return user_passes_test(test_func)


def autologin(request, token):
    if not DEMO_MODE and not request.user.has_perm('ipho_core.is_staff'):
        return HttpResponseForbidden('Only the staff can use autologin.')
    user = authenticate(token=token)
    redirect_to = reverse('home')
    if user:
        login(request, user)
        return redirect(redirect_to)
    else:
        return redirect(settings.LOGIN_URL + '?next={}'.format(redirect_to))


def account_request(request):
    if not DEMO_SIGN_UP and not request.user.has_perm('ipho_core.is_staff'):
        return HttpResponseForbidden('Only the staff can use account-request.')
    form = AccountRequestForm(request.POST or None)
    if form.is_valid():
        form.save()
        selected_user = form.cleaned_data['user']
        ## Redirect authenticate user
        user = authenticate(token=selected_user.autologin.token)
        redirect_to = reverse('home')
        login(request, user)
        return redirect(redirect_to)

    return render(request, 'registration/account_request.html', {'form': form})

@login_required
def service_worker(request):
    if request.method == 'GET':
        return render(request, 'service_worker.js', content_type="application/x-javascript")
    return HttpResponseForbidden('Nothing to see here')

@login_required
def register_push_submission(request):
    if request.method == 'POST' and settings.ENABLE_PUSH:
        data = request.POST.copy()
        del data['csrfmiddlewaretoken']
        newdata = {}
        def get_nd(d, keys):
            for key in keys:
                d = d[key]
            return d

        def set_nd(d, keys, value):
            try:
                d = get_nd(d, keys[:-1])
            except KeyError as e:
                set_nd(d, keys[:-1],{})
                d = get_nd(d, keys[:-1])
            d[keys[-1]] = value

        for k in data:
            val = data[k]
            nk = k.strip('subs')
            klist = []
            i = nk.find(']')
            while i>0:
                klist.append(nk[1:i])
                nk = nk[i+1:]
                i = nk.find(']')
            set_nd(newdata, klist, val)
        if newdata:
            user = request.user

            data = json.dumps(newdata)
            #print(data)
            subs_qset = PushSubscription.objects.get_by_data(data=data)
            #print('------qset-----------------------------------------')
            #print(subs_qset)
            if len(subs_qset) == 0:
                subs = PushSubscription(user=user, data=data)
                subs.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error':'No data'})
    return HttpResponseForbidden('Nothing to see here')

def delete_push_submission(request):
    if request.method == 'POST':
        data = request.POST.copy()
        del data['csrfmiddlewaretoken']
        newdata = {}
        def get_nd(d, keys):
            for key in keys:
                d = d[key]
            return d

        def set_nd(d, keys, value):
            try:
                d = get_nd(d, keys[:-1])
            except KeyError as e:
                set_nd(d, keys[:-1],{})
                d = get_nd(d, keys[:-1])
            d[keys[-1]] = value

        for k in data:
            val = data[k]
            nk = k.strip('subs')
            klist = []
            i = nk.find(']')
            while i>0:
                klist.append(nk[1:i])
                nk = nk[i+1:]
                i = nk.find(']')
            set_nd(newdata, klist, val)
        if newdata:
            data = json.dumps(newdata)
            subs_qset = PushSubscription.objects.get_by_data(data=data)
            print('------qset-----------------------------------------')
            print(subs_qset)
            subs_qset.all().delete()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error':'No data'})
    return HttpResponseForbidden('Nothing to see here')


@permission_required('ipho_core.is_staff')
def send_push(request):
    if not settings.ENABLE_PUSH:
        return HttpResponseForbidden('Push not enabled')
    if request.method == 'POST':
        form = SendPushForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['to_all']:
                ulist = User.objects.all()
            else:
                ulist = form.cleaned_data['users'].all()
            data = {'body': form.cleaned_data['message']}
            if form.cleaned_data['url']:
                data['url'] = form.cleaned_data['url']

            psub_list = []
            import concurrent.futures
            for user in User.objects.all():
                psub_list.extend(user.pushsubscription_set.all())
            def send_push(sub):
                try:
                    sub.send(data)
                except WebPushException as ex:
                    #TODO: do some error handling?
                    pass
            #from multiprocessing import Pool
            #func_list = map(send_push, psub_list)
            #with Pool(processes=350) as pool:
            #    res = pool.map_async(work, func_list, 1)
            #    res.get(20)
            if len(psub_list) > 700:
                psub_list = psub_list[:700]
            with concurrent.futures.ThreadPoolExecutor(max_workers=700) as executor:
                executor.map(send_push, psub_list)

        response = HttpResponse(content="", status=303)
        response["Location"] = reverse('send_push')
        return response

    else:
        form = SendPushForm()
    return render(request, 'ipho_core/send_push.html', {'form':form})

@permission_required('ipho_core.is_staff')
def random_draw(request):
    if not request.user.is_superuser:
        return HttpResponse('It is not easter yet.')
    if request.method == 'POST':
        import random
        drawn_delegations = RandomDrawLog.objects.values_list('delegation__pk', flat=True)
        off_pk = Delegation.objects.get_by_natural_key(OFFICIAL_DELEGATION).pk
        exclude_delegations = list(drawn_delegations.all())
        exclude_delegations.append(off_pk)
        all_delegations = list(Delegation.objects.exclude(pk__in=exclude_delegations).all())
        drawn_del = None
        while not drawn_del:
            if len(all_delegations) == 0:
                return HttpResponse('Easter is over.')
            temp_del = all_delegations[random.randrange(0, len(all_delegations))]
            subs_list = []
            for u in temp_del.members.all():
                subs_list.extend(u.pushsubscription_set.all())
            if len(subs_list) == 0:
                all_delegations.remove(temp_del)
            else:
                drawn_del = temp_del
        RandomDrawLog(delegation = drawn_del).save()
        if 'switzerland' in draw_del.country.lower():
            msg = 'You have won the privilege of bringing chocolate to the Oly-Exams desk.'
        else:
            msg = '!!!!!! You have Won Chocolate !!!!!!     Please come to the Oly-Exams table to collect your prize.'
        link = ''# TODO: reverse('')
        data = {'body':msg, 'url':link}
        for s in subs_list:
            s.send(data)

        return HttpResponse('{} was drawn as a winner, {} notifications have been sent'.format(drawn_del.country, len(subs_list)))
    else:
        form = RandomDrawForm()
    return render(request, 'ipho_core/random_draw.html', {'form':form})


@permission_required('ipho_core.is_staff')
@permission_required('ipho_core.can_impersonate')
def list_impersonate(request):
    users = User.objects.exclude(delegation__isnull=True).exclude(autologin__isnull=True).order_by('username')
    chunk_size = max(old_div(len(users), 6) + 1, 1)
    grouped_users = [users[x:x + chunk_size] for x in range(0, len(users), chunk_size)]
    return render(request, 'ipho_core/impersonate.html', {'grouped_users': grouped_users})
