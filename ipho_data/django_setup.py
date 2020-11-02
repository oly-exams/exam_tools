import os
import django

if "DJANGO_SETTINGS_MODULE" not in os.environ:
    os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings_testing"

django.setup()
