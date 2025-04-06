import datetime
import hashlib
import mimetypes
import operator
import os
import shutil

import pytz
from crispy_forms.utils import render_crispy_form
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404, HttpResponse, HttpResponseNotModified, JsonResponse
from django.shortcuts import render
from django.utils.cache import patch_response_headers

from ipho_core.models import Delegation
from ipho_download.forms import NewDirectoryForm, NewFileForm

MEDIA_ROOT = getattr(settings, "MEDIA_ROOT")


def file_hash(fname):
    hash_ = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_.update(chunk)
    return hash_.hexdigest()


@login_required
def main(
    request, type, url
):  # pylint: disable=too-many-locals,redefined-builtin,too-many-branches,too-many-statements
    type_ = type
    url = os.path.normpath(url)

    if request.user.has_perm("ipho_core.can_see_boardmeeting"):
        basedir = os.path.join(MEDIA_ROOT, "downloads")
    elif request.user.has_perm("ipho_core.is_delegation_print") and ".." not in url:
        # second check likely not needed since django contracts .. as well
        basedir = os.path.join(MEDIA_ROOT, "downloads", "visible_for_examsite")
    else:
        raise Http404("Insufficient Access!")

    if not os.path.exists(basedir):
        os.makedirs(basedir)
    if not os.path.isdir(basedir):  # a convenient fallback if the dir does not exist
        return render(
            request,
            "ipho_download/main.html",
            {
                "flist": [],
                "cur_path": [],
            },
        )

    path = os.path.join(basedir, url)
    rel_url = os.path.relpath(path, basedir)
    if rel_url[0] == "." and "/" in rel_url:
        raise Http404("File path not valid.")
    if not os.path.exists(path):
        raise Http404("File not found.")

    # Needed to check which folders the user should have access to
    delegation_private_dirs = [
        delegation.name + "_private" for delegation in list(Delegation.objects.all())
    ]
    print([delegation.name for delegation in list(Delegation.objects.all())])
    is_admin = "ipho_core.is_organizer_admin" in request.user.get_all_permissions()
    # Create private folder for delegations if they don't exist yet
    if is_admin:
        for delegation in list(Delegation.objects.all()):
            os.makedirs(
                os.path.join(
                    basedir, "delegations_private_dirs", delegation.name + "_private"
                ),
                exist_ok=True,
            )

    dir_form = NewDirectoryForm()
    file_form = NewFileForm()

    if type_ == "f":
        # Check if user has access to the file
        if any(
            path_subdir in delegation_private_dirs for path_subdir in path.split("/")
        ):
            if (
                not any(
                    path_subdir == str(request.user.username) + "_private"
                    for path_subdir in path.split("/")
                )
                and not is_admin
            ):
                raise Http404("No access to this resource.")

        if os.path.isdir(path):
            # if a directory is requested for download, raise a 404.
            # in the future, we might want to zip of the directory and serve it for download
            raise Http404("File path not valid.")

        etag = file_hash(path)

        if request.META.get("HTTP_IF_NONE_MATCH", "") == etag:
            return HttpResponseNotModified()

        filename = os.path.basename(path)
        content_type, _ = mimetypes.guess_type(path)
        # pylint: disable=consider-using-with
        res = HttpResponse(open(path, "rb"), content_type=content_type)
        res["content-disposition"] = f'inline; filename="{filename}"'
        res["ETag"] = etag
        patch_response_headers(res, cache_timeout=300)
        return res

    flist = []
    if os.path.normpath(path) == os.path.normpath(basedir) and os.path.exists(
        os.path.join(
            basedir, "delegations_private_dirs", str(request.user.username) + "_private"
        )
    ):
        flist.append(
            (
                "folder",
                "d",
                str(request.user.username) + "_private",
                os.path.join(
                    "delegations_private_dirs", str(request.user.username) + "_private"
                ),
                None,
                None,
            )
        )
    for fname in os.listdir(path):
        if fname[0] == "." or (fname == "delegations_private_dirs" and not is_admin):
            continue

        # Check if file or directory should be displayed to the user
        if "delegations_private_dirs" in path:
            if (
                not fname == str(request.user.username) + "_private"
                and not any(
                    path_subdir == str(request.user.username) + "_private"
                    for path_subdir in path.split("/")
                )
                and not is_admin
            ):
                continue

        fullpath = os.path.join(path, fname)
        fpath = os.path.relpath(fullpath, basedir)
        fttype = "f"
        ftype = "file"
        fsize = None
        mtime = None
        if os.path.isdir(fullpath):
            ftype = "folder"
            fttype = "d"
        else:
            fsize = os.path.getsize(fullpath)
            mtime_ts = os.path.getmtime(fullpath)
            mtime = datetime.datetime.fromtimestamp(mtime_ts, tz=pytz.utc)
        flist.append((ftype, fttype, fname, fpath, fsize, mtime))

    flist = sorted(flist, key=operator.itemgetter(2))

    dir_form_html = render_crispy_form(dir_form)
    file_form_html = render_crispy_form(file_form)
    cur_url = ""
    cur_path = [("/", "")]
    cur_split = url.split("/")
    for part in cur_split:
        if part == ".":
            continue
        cur_url += part + "/"
        cur_path.append((part, cur_url))
    return render(
        request,
        "ipho_download/main.html",
        {
            "flist": flist,
            "cur_path": cur_path,
            "dir_form": dir_form_html,
            "file_form": file_form_html,
            "url": url,
        },
    )


@permission_required("ipho_core.is_organizer_admin")
def remove(request, url):
    url = os.path.normpath(url)

    basedir = os.path.join(MEDIA_ROOT, "downloads")
    path = os.path.join(basedir, url)
    rel_url = os.path.relpath(path, basedir)
    if rel_url[0] == "." and "/" in rel_url:
        return JsonResponse({"error": "Something went wrong!"})
    if not os.path.exists(path):
        return JsonResponse({"error": "Parent directory missing!"})

    if os.path.samefile(path, basedir):
        return JsonResponse({"error": "Cannot remove base directory!"})
    if not os.path.realpath(path).startswith(os.path.realpath(basedir)):
        return JsonResponse({"error": "Cannot remove path outside base directory!"})
    if os.path.isfile(path):
        os.remove(path)
    elif request.user.is_superuser:
        shutil.rmtree(path)
    else:
        return JsonResponse({"error": "Only superusers can remove directories!"})
    return JsonResponse({"success": True})


@permission_required("ipho_core.is_organizer_admin")
def add_new_file(request, url):
    url = os.path.normpath(url)

    basedir = os.path.join(MEDIA_ROOT, "downloads")
    path = os.path.join(basedir, url)
    rel_url = os.path.relpath(path, basedir)
    if rel_url[0] == "." and "/" in rel_url:
        return JsonResponse({"error": "Something went wrong!"})
    if not os.path.exists(path):
        return JsonResponse({"error": "Parent directory missing!"})

    file_form = NewFileForm(request.POST or None, request.FILES or None)
    if file_form.is_valid():
        file = request.FILES["file"]
        with open(os.path.join(path, file.name), "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return JsonResponse({"success": True})
    return JsonResponse({"form": render_crispy_form(file_form)})


@permission_required("ipho_core.is_organizer_admin")
def add_new_directory(request, url):
    url = os.path.normpath(url)

    basedir = os.path.join(MEDIA_ROOT, "downloads")
    path = os.path.join(basedir, url)
    rel_url = os.path.relpath(path, basedir)
    if rel_url[0] == "." and "/" in rel_url:
        return JsonResponse({"error": "Something went wrong!"})
    if not os.path.exists(path):
        return JsonResponse({"error": "Parent directory missing!"})

    if not os.path.isdir(path):
        return JsonResponse({"error": "Cannot add directory to file!"})

    dir_form = NewDirectoryForm(request.POST or None)
    if dir_form.is_valid():
        os.makedirs(os.path.join(path, dir_form.data["directory"]), exist_ok=True)
        return JsonResponse({"success": True})
    return JsonResponse({"form": render_crispy_form(dir_form)})
