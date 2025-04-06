# syntax=docker/dockerfile:1

ARG DOCKER_PYTHON_IMAGE=python:3.11-slim-bookworm
ARG DOCKER_NGINX_IMAGE=nginx:1.19
ARG DJANGO_SETTINGS_NAME=settings_b_dev

FROM $DOCKER_PYTHON_IMAGE AS wheelhouse-builder-base

ENV DEBIAN_FRONTEND noninteractive

RUN --mount=type=cache,sharing=locked,target=/var/cache/apt \
    apt-get update && apt-get install -y \
    build-essential \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/home/container/.cache/pip \
    python -m pip wheel uwsgi==2.0.22 --wheel-dir=/wheelhouse

FROM wheelhouse-builder-base AS wheelhouse-builder

COPY requirements.txt /requirements.txt

RUN --mount=type=cache,target=/home/container/.cache/pip \
    python -m pip wheel -r requirements.txt --wheel-dir=/wheelhouse

FROM wheelhouse-builder-base AS wheelhouse-builder-dev

COPY requirements_dev.txt /requirements_dev.txt

RUN --mount=type=cache,target=/home/container/.cache/pip \
    python -m pip wheel -r requirements_dev.txt --wheel-dir=/wheelhouse

FROM wheelhouse-builder-base AS wheelhouse-builder-test

COPY requirements_test.txt /requirements_test.txt

RUN --mount=type=cache,target=/home/container/.cache/pip \
    python -m pip wheel -r requirements_test.txt --wheel-dir=/wheelhouse

FROM $DOCKER_PYTHON_IMAGE AS python-base

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 1

# create non-root-user
RUN addgroup --gid 5000 container
RUN useradd --create-home --uid 5000 --gid 5000 --shell /bin/bash container
ENV PATH=$PATH:/home/container/.local/bin

FROM python-base AS django-server-nosrc

RUN --mount=type=cache,sharing=locked,target=/var/cache/apt \
    apt-get update && apt-get install -y \
    git \
    npm \
    patch \
    pandoc \
    nodejs \
    gettext \
    inkscape \
    imagemagick \
    postgresql-client \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

RUN npm install -g bower && npm cache clean --force

USER container
WORKDIR /home/container

# we need to write as container to these folder
COPY --chown=5000:5000 ./bower ./bower
RUN cd bower && bower install && bower cache clean && rm -rf static_bower
ENV BOWER_STATIC_PATH /home/container/bower/static

RUN mkdir -m777 /home/container/logs

RUN --mount=type=bind,target=/tmp/wheelhouse,from=wheelhouse-builder,source=/wheelhouse \
    python3 -m pip install --no-index --user /tmp/wheelhouse/*.whl

WORKDIR /home/container/workdir

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM django-server-nosrc AS django-server-dbg

USER root

# Disable git ownership checks: these may cause git to fail if the git
# directory is not owned by the current user.
#
# This scenario doesn't apply here, because the entire FS is under our
# control, but may belong to a different user based on where it's created from.
#
# See https://github.com/git/git/commit/8959555cee7ec045958f9b6dd62e541affb7e7d9
# for the rationale behind the ownership check.
RUN git config --system --add safe.directory '/home/container/workdir'

USER container

RUN python -m pip install debugpy

EXPOSE 5678

CMD ["python", "-m", "debugpy", "--listen", "localhost:5678", "manage.py", "runserver", "0.0.0.0:8000"]

FROM django-server-nosrc AS pre-commit

RUN --mount=type=bind,target=/tmp/wheelhouse,from=wheelhouse-builder-dev,source=/wheelhouse \
    python3 -m pip install --no-index --user /tmp/wheelhouse/*.whl

COPY --chown=5000:5000 .pre-commit-config.yaml .

RUN git init && pre-commit install-hooks

COPY --chown=5000:5000 . .

CMD ["pre-commit", "run", "--all-files"]

FROM django-server-nosrc AS pytest

RUN --mount=type=bind,target=/tmp/wheelhouse,from=wheelhouse-builder-test,source=/wheelhouse \
    python3 -m pip install --no-index --user /tmp/wheelhouse/*.whl

COPY --chown=5000:5000 . .

CMD ["pytest"]

FROM django-server-nosrc AS django-server

COPY --chown=5000:5000 . .

EXPOSE 8001

CMD /bin/sh -c "python docker/wait_for/wait_for_postgres_60.py && python manage.py migrate && uwsgi --ini uwsgi.ini  --socket :8001"

FROM django-server AS static-provider

# Need to use 'settings_testing', since secrets are not yet available
RUN DJANGO_SETTINGS_MODULE=exam_tools.settings_testing python manage.py compilemessages
RUN DJANGO_SETTINGS_MODULE=exam_tools.settings_testing python manage.py collectstatic

FROM $DOCKER_NGINX_IMAGE AS nginx-with-static

COPY --from=static-provider /home/container/workdir/collected_static /collected_static

ARG NGINX_TEMPLATE_NAME=dev

COPY docker/nginx/${NGINX_TEMPLATE_NAME}.conf.template /etc/nginx/templates/default.conf.template
COPY docker/wait_for/wait-for-it.sh /wait-for-it.sh


FROM python-base AS celery-worker-nosrc

RUN --mount=type=cache,sharing=locked,target=/var/cache/apt \
    apt-get update && apt-get install -y \
    inkscape imagemagick \
    locales \
    texlive-full \
    --no-install-recommends && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --chmod=644 static/noto/*tf /usr/local/share/fonts/
RUN dpkg-reconfigure fontconfig-config

# Set the locale
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

USER container
WORKDIR /home/container

# The celery worker thinks it is being run as root when the UID / GID
# does not match a user that is configured on the system. Since we
# need to run with the UID / GID of the host when developing on Linux,
# we need to set this environment variable to make celery ignore the
# error.
# Note that celery should *not_* be run as root.
ENV C_FORCE_ROOT=1

RUN mkdir -m777 /home/container/logs

RUN --mount=type=bind,target=/tmp/wheelhouse,from=wheelhouse-builder,source=/wheelhouse \
    python3 -m pip install --no-index --user /tmp/wheelhouse/*.whl

WORKDIR /home/container/workdir

ARG DJANGO_SETTINGS_NAME
ENV DJANGO_SETTINGS_MODULE=exam_tools.${DJANGO_SETTINGS_NAME}

CMD /bin/sh -c "docker/wait_for/wait-for-it.sh -t 90 $RABBITMQ_HOST:$RABBITMQ_PORT && celery -A exam_tools worker -E --concurrency=$CELERY_WORKER -O fair"

FROM celery-worker-nosrc AS celery-worker

COPY --chown=5000:5000 . .
