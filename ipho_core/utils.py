__all__ = ("is_ajax",)


def is_ajax(request):
    """
    Utility to replace the deprecated Django is_ajax.
    """
    return request.headers.get("x-requested-with") == "XMLHttpRequest"
