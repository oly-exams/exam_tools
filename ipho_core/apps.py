from django.apps import AppConfig

# solution from https://stackoverflow.com/questions/43300305/django-rest-auth-user-logged-in-signal
class IphoCoreConfig(AppConfig):
    name = "ipho_core"

    def ready(self):
        # pylint: disable=import-outside-toplevel, unused-import
        import ipho_core.signals
