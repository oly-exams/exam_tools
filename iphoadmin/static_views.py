from django.shortcuts import render

def render_page(request, p):
    return render(request, p)
