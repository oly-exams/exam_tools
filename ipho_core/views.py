import concurrent.futures
import json
import random

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test,
)
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from past.utils import old_div
from pywebpush import WebPushException

from ipho_core.forms import AccountRequestForm, RandomDrawForm, SendPushForm
from ipho_core.models import Delegation, PushSubscription, RandomDrawLog, User

DEMO_MODE = getattr(settings, "DEMO_MODE")
DEMO_SIGN_UP = getattr(settings, "DEMO_SIGN_UP")
OFFICIAL_DELEGATION = getattr(settings, "OFFICIAL_DELEGATION")
DEFAULT_AUTHENTICATION_BACKEND = getattr(settings, "AUTHENTICATION_BACKENDS")[-1]


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


@permission_required("ipho_core.can_impersonate")
def list_impersonate(request):
    users = sorted(
        [
            user
            for user in User.objects.all()
            if not user.has_perm("ipho_core.can_impersonate")
        ],
        key=lambda user: user.username,
    )
    chunk_size = max(old_div(len(users), 6) + 1, 1)
    grouped_users = [
        users[x : x + chunk_size] for x in range(0, len(users), chunk_size)
    ]
    return render(
        request, "ipho_core/impersonate.html", {"grouped_users": grouped_users}
    )


@permission_required("ipho_core.can_impersonate")
def impersonate(request, pk):
    base_user_id = request.user.id
    user = get_object_or_404(User, id=pk)
    if user.has_perm("ipho_core.can_impersonate"):
        return HttpResponseForbidden("You cannot impersonate this user.")
    login(request, user, backend=DEFAULT_AUTHENTICATION_BACKEND)
    request.session["impersonation_user"] = base_user_id
    request.session.modified = True
    return redirect(reverse("home"))


def impersonate_stop(request):
    user_id = request.session.get("impersonation_user", None)
    if user_id is None:
        return HttpResponseForbidden("No impersonation currently active.")
    login(
        request,
        get_object_or_404(User, id=user_id),
        backend=DEFAULT_AUTHENTICATION_BACKEND,
    )
    return redirect(reverse("home"))


def account_request(request):
    if not DEMO_SIGN_UP and not (
        request.user.has_perm("ipho_core.can_impersonate")
        and request.user.has_perm("ipho_core.is_organizer_admin")
    ):
        return HttpResponseForbidden("Only the staff can use account-request.")
    form = AccountRequestForm(request.POST or None)
    if form.is_valid():
        form.save()
        selected_user = form.cleaned_data["user"]
        redirect_to = reverse("home")
        login(request, selected_user)
        return redirect(redirect_to)

    return render(request, "registration/account_request.html", {"form": form})


@login_required
def service_worker(request):
    if request.method == "GET":
        return render(
            request, "service_worker.js", content_type="application/x-javascript"
        )
    return HttpResponseForbidden("Nothing to see here")


@login_required
def register_push_submission(request):
    if request.method == "POST" and settings.ENABLE_PUSH:
        data = request.POST.copy()
        del data["csrfmiddlewaretoken"]
        newdata = {}

        def get_nd(data, keys):
            for key in keys:
                data = data[key]
            return data

        def set_nd(data, keys, value):
            try:
                data = get_nd(data, keys[:-1])
            except KeyError:
                set_nd(data, keys[:-1], {})
                data = get_nd(data, keys[:-1])
            data[keys[-1]] = value

        for k in data:
            val = data[k]
            newk = k.strip("subs")
            klist = []
            i = newk.find("]")
            while i > 0:
                klist.append(newk[1:i])
                newk = newk[i + 1 :]
                i = newk.find("]")
            set_nd(newdata, klist, val)
        if newdata:
            user = request.user

            data = json.dumps(newdata)
            # print(data)
            subs_qset = PushSubscription.objects.get_by_data(data=data)
            # print('------qset-----------------------------------------')
            # print(subs_qset)
            if len(subs_qset) == 0:
                subs = PushSubscription(user=user, data=data)
                subs.save()
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": "No data"})
    return HttpResponseForbidden("Nothing to see here")


def delete_push_submission(request):
    if request.method == "POST":
        data = request.POST.copy()
        del data["csrfmiddlewaretoken"]
        newdata = {}

        def get_nd(data, keys):
            for key in keys:
                data = data[key]
            return data

        def set_nd(data, keys, value):
            try:
                data = get_nd(data, keys[:-1])
            except KeyError:
                set_nd(data, keys[:-1], {})
                data = get_nd(data, keys[:-1])
            data[keys[-1]] = value

        for k in data:
            val = data[k]
            newk = k.strip("subs")
            klist = []
            i = newk.find("]")
            while i > 0:
                klist.append(newk[1:i])
                newk = newk[i + 1 :]
                i = newk.find("]")
            set_nd(newdata, klist, val)
        if newdata:
            data = json.dumps(newdata)
            subs_qset = PushSubscription.objects.get_by_data(data=data)
            subs_qset.all().delete()
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": "No data"})
    return HttpResponseForbidden("Nothing to see here")


@permission_required("ipho_core.is_organizer_admin")
def send_push(request):
    if not settings.ENABLE_PUSH:
        return HttpResponseForbidden("Push not enabled")
    if request.method == "POST":
        form = SendPushForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["to_all"]:
                ulist = User.objects.all()
            else:
                ulist = form.cleaned_data["users"].all()
            data = {"body": form.cleaned_data["message"]}
            if form.cleaned_data["url"]:
                data["url"] = form.cleaned_data["url"]

            psub_list = []
            for user in ulist:
                psub_list.extend(user.pushsubscription_set.all())

            def send_push_helper(sub):
                try:
                    sub.send(data)
                except WebPushException:
                    # TODO: do some error handling?
                    pass

            # from multiprocessing import Pool
            # func_list = map(send_push, psub_list)
            # with Pool(processes=350) as pool:
            #    res = pool.map_async(work, func_list, 1)
            #    res.get(20)
            if len(psub_list) > 700:
                psub_list = psub_list[:700]
            with concurrent.futures.ThreadPoolExecutor(max_workers=700) as executor:
                executor.map(send_push_helper, psub_list)

        response = HttpResponse(content="", status=303)
        response["Location"] = reverse("send_push")
        return response

    form = SendPushForm()
    return render(request, "ipho_core/send_push.html", {"form": form})


@permission_required("ipho_core.is_organizer_admin")
def random_draw(request):  # pylint: disable=too-many-branches
    if not request.user.is_superuser:
        return HttpResponse("It is not easter yet.")
    if not settings.ENABLE_PUSH:
        return HttpResponseForbidden("Push not enabled")
    if request.method == "POST":
        drawn_delegations = RandomDrawLog.objects.filter(tag="manual").values_list(
            "delegation__pk", flat=True
        )

        off_pk = Delegation.objects.get_by_natural_key(OFFICIAL_DELEGATION).pk
        exclude_delegations = list(drawn_delegations.all())
        exclude_delegations.append(off_pk)
        all_delegations = list(
            Delegation.objects.exclude(pk__in=exclude_delegations).all()
        )
        success = False
        subs_list = []
        sent_n = 0
        while not success:
            sent_n = 0
            if len(all_delegations) == 0:
                return HttpResponse("Easter is over.")
            temp_del = all_delegations[random.randrange(0, len(all_delegations))]
            subs_list = []
            for user in temp_del.members.all():
                subs_list.extend(user.pushsubscription_set.all())
            if len(subs_list) == 0:
                all_delegations.remove(temp_del)
            else:
                drawn_del = temp_del
                msg = "!!!!!! You have Won Chocolate !!!!!!     Please come to the Oly-Exams table to collect your prize."
                if "switzerland" in drawn_del.country.lower():
                    msg = "You have won the privilege of bringing chocolate to the Oly-Exams desk."

                link = reverse("chocobunny")
                data = {"body": msg, "url": link}

                for sub in subs_list:
                    try:
                        sub.send(data)
                        sent_n += 1
                    except WebPushException:
                        pass
                if sent_n == 0:
                    all_delegations.remove(temp_del)
                else:
                    success = True
        RandomDrawLog(delegation=drawn_del, tag="manual").save()

        return HttpResponse(
            f"{drawn_del.country} was drawn as a winner, {sent_n} notifications have been sent"
        )

    form = RandomDrawForm()
    return render(request, "ipho_core/random_draw.html", {"form": form})


@login_required
def chocobunny(request):
    print("Yay, chocolate!")
    delegation = Delegation.objects.filter(members=request.user).first()
    if delegation is None:
        name = request.user.username
        message = "Wait, you're not in a delegation.. how did you get here?"
    else:
        name = delegation.country
        if RandomDrawLog.objects.filter(delegation=delegation).exists():
            draw_logs = RandomDrawLog.objects.filter(delegation=delegation)
            statuses = [s.lower() for s in draw_logs.values_list("status", flat=True)]
            if delegation.country.lower() == "switzerland":
                message = "Bring the cholocate to the OlyExams desk!"
            elif "pending" in statuses:
                message = "Collect your chocolate at the OlyExams desk."
            elif "received" in statuses:
                message = "Wait.. you already collected your chocolate."
            else:
                message = "404...Easter not found, please contact your local Pope."
        else:
            message = "Wait.. you didn't actually win! This incident will be reported!!"
    return render(request, "ipho_core/bunny.html", {"name": name, "message": message})
