from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def render_page(request, p, **kwargs):  # pylint: disable=invalid-name
    return render(request, p, **kwargs)
