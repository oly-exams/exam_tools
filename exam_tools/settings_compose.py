# Django settings for exam_tools project.

# pylint: disable=unused-wildcard-import


# pylint: disable=unreachable
raise NotImplementedError(
    "have not fixed RABBITMQ env change, not sure if this file is needed"
)

from .settings_common import *

EVENT_TEMPLATE_PATH = os.path.join(TEMPLATE_PATH, "events", "apho2019")

DEBUG = True
# TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
    ("Michele Dolfi", "michele.dolfi@gmail.com"),
)

MANAGERS = ADMINS

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOST"],
        "PORT": 5432,
    }
}

CELERY_BROKER_URL = f'amqp://{os.environ["RABBITMQ_USER"]}:{os.environ["RABBITMQ_PASSWORD"]}@{os.environ["RABBITMQ_HOST"]}:5672/'

SITE_URL = "http://django-server:8000"
ALLOWED_HOSTS += (
    "django-server",
    "localhost",
)


# Make this unique, and don't share it with anybody.
SECRET_KEY = "^t-a=sbo_05wq!*(x4mpv7kw&u_n=5js$lwadn_yx(bzx*fzjw"
