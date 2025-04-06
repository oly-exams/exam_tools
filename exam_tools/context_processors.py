import os

from django.conf import settings


def ipho_context(request):
    favicons_path = "favicons"
    default_favicon_path = os.path.join(favicons_path, "default")
    favicon_path = default_favicon_path
    if any("secret" in hostname for hostname in settings.ALLOWED_HOSTS):
        favicon_path = os.path.join(favicons_path, "secret")
    if any(
        partial_name in hostname
        for hostname in settings.ALLOWED_HOSTS
        for partial_name in ["dev", "test"]
    ):
        favicon_path = os.path.join(favicons_path, "dev")
    return {
        "DEMO_MODE": settings.DEMO_MODE,
        "DEMO_SIGN_UP": settings.DEMO_SIGN_UP,
        "VERSION_DATE": settings.VERSION_DATE,
        "DOCS_URL": settings.DOCS_URL,
        "STATIC_PATH": settings.STATIC_PATH,
        "DEBUG": getattr(settings, "DEBUG", False),
        "OFFICIALLY_SUPPORTED": settings.OFFICIALLY_SUPPORTED,
        "FAVICON_PATH": favicon_path,
        "SUPPORT_CONTACT": settings.SUPPORT_CONTACT,
    }
