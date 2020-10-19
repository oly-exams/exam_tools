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

from __future__ import unicode_literals, absolute_import

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseNotModified, Http404
from django.conf import settings
from django.utils.cache import patch_response_headers

import os
import operator
from unicodedata import normalize
import mimetypes
import hashlib
import datetime
import pytz

MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')


def hash(fname):
    h = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


@login_required
@permission_required('ipho_core.can_see_boardmeeting')
def main(request, type, url):
    url = os.path.normpath(url)

    basedir = os.path.join(MEDIA_ROOT, 'downloads')
    path = os.path.join(basedir, url)
    rel_url = os.path.relpath(path, basedir)
    if rel_url[0] == '.' and '/' in rel_url:
        raise Http404('File path not valid.')
    if not os.path.exists(path):
        raise Http404('File not found.')

    if type == 'f':
        if os.path.isdir(path):
            # if a directory is requested for download, raise a 404.
            # in the future, we might want to zip of the directory and serve it for download
            raise Http404('File path not valid.')

        etag = hash(path)

        if request.META.get('HTTP_IF_NONE_MATCH', '') == etag:
            return HttpResponseNotModified()

        filename = os.path.basename(path)
        content_type, encoding = mimetypes.guess_type(path)
        res = HttpResponse(open(path, 'rb'), content_type=content_type)
        res['content-disposition'] = 'inline; filename="{}"'.format(filename)
        res['ETag'] = etag
        patch_response_headers(res, cache_timeout=300)
        return res

    flist = []
    for f in os.listdir(path):
        if f[0] == '.': continue
        fullpath = os.path.join(path, f)
        fpath = os.path.relpath(fullpath, basedir)
        tt = 'f'
        t = 'file'
        fsize = None
        mtime = None
        if os.path.isdir(fullpath):
            t = 'folder'
            tt = 'd'
        else:
            fsize = os.path.getsize(fullpath)
            mtime_ts = os.path.getmtime(fullpath)
            mtime = datetime.datetime.fromtimestamp(mtime_ts, tz=pytz.utc)
        flist.append((t, tt, f, fpath, fsize, mtime))

    flist = sorted(flist, key=operator.itemgetter(2))

    cur_url = ''
    cur_path = [('/', '')]
    cur_split = url.split('/')
    for p in cur_split:
        if p == '.': continue
        cur_url += p + '/'
        cur_path.append((p, cur_url))
    return render(request, 'ipho_download/main.html', {
        'flist': flist,
        'cur_path': cur_path,
    })
