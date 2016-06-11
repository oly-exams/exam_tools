from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseNotModified
from django.conf import settings

import os
import mimetypes
from hashlib import md5

MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')

@login_required
def main(request, type, url):
    url = os.path.normpath(url)

    basedir = os.path.join(MEDIA_ROOT,'downloads')
    path = os.path.join(basedir,url)

    if type == 'f':
        etag = md5(path).hexdigest()

        if request.META.get('HTTP_IF_NONE_MATCH', '') == etag:
            return HttpResponseNotModified()

        filename = os.path.basename(path)
        content_type,encoding = mimetypes.guess_type(path)
        res = HttpResponse(open(path), content_type=content_type)
        res['content-disposition'] = 'inline; filename="{}"'.format(filename)
        res['ETag'] = etag
        return res

    flist = []
    for f in os.listdir(path):
        if f[0] == '.': continue
        fullpath = os.path.join(path,f)
        fpath = os.path.relpath(fullpath, basedir)
        tt = 'f'
        t = 'file'
        if os.path.isdir(fullpath):
            t = 'folder'
            tt = 'd'
        flist.append((t, tt, f, fpath))

    rel_url = os.path.relpath(path, basedir)
    cur_url = ''
    cur_path = [('/', '')]
    cur_split = url.split('/')
    for p in cur_split:
        if p == '.': continue
        cur_url += p+'/'
        cur_path.append((p, cur_url))
    return render(request, 'ipho_download/main.html', {
        'flist': flist,
        'cur_path': cur_path,
    })
