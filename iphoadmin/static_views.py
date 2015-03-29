from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def render_page(request, p):
    return render(request, p)
