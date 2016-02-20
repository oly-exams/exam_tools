from django.conf import settings

def ipho_context(request):
    return {
        'DEMO_MODE': settings.DEMO_MODE,
        'VERSION': settings.VERSION,
        'VERSION_DATE': settings.VERSION_DATE,
        'DOCS_URL': settings.DOCS_URL,
    }
