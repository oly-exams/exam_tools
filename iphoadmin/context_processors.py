from django.conf import settings

def demo_mode(request):
    return {'DEMO_MODE': settings.DEMO_MODE}
