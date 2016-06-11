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
    url = url.replace('//', '/')

    path = os.path.join(os.path.join(MEDIA_ROOT,'downloads'),url)

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
        fpath = os.path.join(path,f)
        tt = 'f'
        t = 'file'
        if os.path.isdir(fpath):
            t = 'folder'
            tt = 'd'
        flist.append((t, tt, f, fpath))

    cur_url = ''
    cur_path = []
    for p in url.split('/'):
        cur_url += '/'+p
        cur_path.append((p, cur_url))
    return render(request, 'ipho_download/main.html', {
        'flist': flist,
        'cur_path': cur_path,
    })
