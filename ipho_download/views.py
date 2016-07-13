from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseNotModified, Http404
from django.conf import settings

import os
from unicodedata import normalize
import mimetypes
from hashlib import md5

MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')

@login_required
def main(request, type, url):
    url = os.path.normpath(url)

    basedir = os.path.join(MEDIA_ROOT,'downloads')
    path = os.path.join(basedir,url).encode('utf8')
    rel_url = os.path.relpath(path, basedir)
    if rel_url[0] == '.' and '/' in rel_url:
        raise Http404('File path not valid.')
    if not os.path.exists(path):
        raise Http404('File not found.')

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
        fullpath = os.path.join(path, f.decode('utf8')).encode('utf8')
        fpath = os.path.relpath(fullpath, basedir)
        tt = 'f'
        t = 'file'
        fsize = None
        if os.path.isdir(fullpath):
            t = 'folder'
            tt = 'd'
        else:
            fsize = os.path.getsize(fullpath)
        flist.append((t, tt, f, fpath, fsize))

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
