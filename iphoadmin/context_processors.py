from django.conf import settings

def demo_mode(request):
    return {'DEMO_MODE': settings.DEMO_MODE}

def version(request):
    return {'VERSION': settings.VERSION, 'VERSION_DATE': settings.VERSION_DATE}
