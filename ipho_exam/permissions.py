from rest_framework import permissions
from django.conf import settings


class HasValidApiKey(permissions.BasePermission):
    message = 'Invalid or missing API Key.'

    def has_permission(self, request, view):
        api_key = request.META.get('HTTP_APIKEY', '')
        for name, key in settings.EXAM_TOOLS_API_KEYS.items():
            if api_key == key:
                return True
        return False


class HasValidApiKeyOrAdmin(permissions.IsAdminUser, HasValidApiKey):
    def has_permission(self, request, view):
        return permissions.IsAdminUser.has_permission(self, request, view) \
            or HasValidApiKey.has_permission(self, request, view)
