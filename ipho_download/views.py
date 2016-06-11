from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
import os

@login_required
def main(request, type, url):
    url = url.replace('//', '/')

    path = '/'+url

    if type == 'f':
        return HttpResponse(open(path))

    flist = []
    for f in os.listdir(path):
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
