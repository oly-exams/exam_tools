import os
import django

if "DJANGO_SETTINGS_MODULE" not in os.environ:
    print("\033[1;31mNote: you are using exam_tools.settings_testing\033[0m")
    os.environ["DJANGO_SETTINGS_MODULE"] = "exam_tools.settings_testing"
    print(
        "\033[1;31muse DJANGO_SETTINGS_MODULE=X or execute from inside the docker container\033[0m"
    )

django.setup()
