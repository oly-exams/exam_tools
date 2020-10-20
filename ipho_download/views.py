# Exam Tools
#
# Copyright (C) 2014 - 2019 Oly Exams Team
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
import pytz

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseNotModified, Http404
from django.conf import settings
from django.utils.cache import patch_response_headers


MEDIA_ROOT = getattr(settings, "MEDIA_ROOT")


def file_hash(fname):
    hash_ = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_.update(chunk)
    return hash_.hexdigest()


@login_required
@permission_required("ipho_core.can_see_boardmeeting")
def main(request, type_, url):  # pylint: disable=too-many-locals
    url = os.path.normpath(url)

    basedir = os.path.join(MEDIA_ROOT, "downloads")
    path = os.path.join(basedir, url)
    rel_url = os.path.relpath(path, basedir)
    if rel_url[0] == "." and "/" in rel_url:
        raise Http404("File path not valid.")
    if not os.path.exists(path):
        raise Http404("File not found.")

    if type_ == "f":
        if os.path.isdir(path):
            # if a directory is requested for download, raise a 404.
            # in the future, we might want to zip of the directory and serve it for download
            raise Http404("File path not valid.")

        etag = file_hash(path)

        if request.META.get("HTTP_IF_NONE_MATCH", "") == etag:
            return HttpResponseNotModified()

        filename = os.path.basename(path)
        content_type, encoding = mimetypes.guess_type(
            path
        )  # pylint: disable=unused-variable
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
        },
    )
