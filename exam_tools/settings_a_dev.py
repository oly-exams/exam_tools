# pylint: disable=unused-wildcard-import
import os
from pathlib import Path
from .settings_common import *

TMP_ENV = dict()
TMP_ENV.update(os.environ)

for key in ["POSTGRES_USER", "POSTGRES_PASSWORD", "RABBITMQ_USER", "RABBITMQ_PASSWORD"]:
    if key + "_FILE" in TMP_ENV:
        with Path(TMP_ENV[key + "_FILE"]).open("r") as f:
            TMP_ENV[key] = f.readline().strip()

DATABASES = dict()
DATABASES["default"] = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": "postgres",
    "USER": TMP_ENV["POSTGRES_USER"],
    "PASSWORD": TMP_ENV["POSTGRES_PASSWORD"],
    "HOST": TMP_ENV["POSTGRES_HOST"],
    "PORT": TMP_ENV["POSTGRES_PORT"],
}

CELERY_BROKER_URL = "amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/".format_map(
    TMP_ENV
)
CELERY_ACCEPT_CONTENT = ["pickle", "json", "msgpack", "yaml"]
CELERY_TASK_SERIALIZER = "pickle"
CELERY_RESULT_SERIALIZER = "pickle"
CELERY_RESULT_BACKEND = "django-db"
CELERY_TASK_TIME_LIMIT = 15 * 60
CELERY_WORKER = os.environ["CELERY_WORKER"]

del TMP_ENV

# Make this unique, and don't share it with anybody.
SECRET_KEY = "^t-a=sbo_05wq!*(x4mpv7kw&u_n=5js$lwadn_yx(bzx*fzjw"
DEBUG = True

SITE_URL = "http://django-server:8000"
ALLOWED_HOSTS += (
    "django-server",
    "localhost",
)

ADD_DELEGATION_WATERMARK = True
RECORD_USER_LOGIN_LOGOUT_IPS = True

LOGGING["handlers"]["logfile"] = {
    "class": "logging.handlers.WatchedFileHandler",
    "filename": "exam_tools-django.log",
}

LOGGING["loggers"].update(
    {
        "exam_tools": {
            "handlers": ["logfile"],
            "level": "INFO",
            "propagate": False,
        }
    }
)
