# Exam Tools
#
# Copyright (C) 2014 - 2021 Oly Exams Team
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

import os
import operator
import mimetypes
import hashlib
import datetime
import shutil
import pytz
from crispy_forms.utils import render_crispy_form

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseNotModified, Http404, JsonResponse
from django.conf import settings
from django.utils.cache import patch_response_headers

from ipho_download.forms import NewDirectoryForm, NewFileForm


MEDIA_ROOT = getattr(settings, "MEDIA_ROOT")


def file_hash(fname):
    hash_ = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_.update(chunk)
    return hash_.hexdigest()


@login_required
@permission_required("ipho_core.can_see_boardmeeting")
def main(request, type, url):  # pylint: disable=too-many-locals,redefined-builtin
    type_ = type
    url = os.path.normpath(url)

    basedir = os.path.join(MEDIA_ROOT, "downloads")
    path = os.path.join(basedir, url)
    rel_url = os.path.relpath(path, basedir)
    if rel_url[0] == "." and "/" in rel_url:
        raise Http404("File path not valid.")
    if not os.path.exists(path):
        raise Http404("File not found.")

    dir_form = NewDirectoryForm()
    file_form = NewFileForm()

    if type_ == "f":
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
    for fname in os.listdir(path):
        if fname[0] == ".":
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
