#!/bin/sh

# 2020 Oct: this is a convenience bash script to prevent users from having
# to specify all partial docker-compose.yml files with -f.
# docker-compose file v3 does not yet support a convenient way to
# fuse partial files together. (v2 had extends, but that is not in v3)
# use this command in any place you would use docker-compose.
# The name was choosen to be easily tab-completed, not colliding with
# the docker folder
SCRIPT=$(readlink -f $0)
SCRIPTPATH=$(dirname $SCRIPT)

docker-compose -p "exam_tools" \
               --project-directory="$SCRIPTPATH" \
               --env-file="$SCRIPTPATH/env/dev.yml" \
               -f "$SCRIPTPATH/django_server/docker-compose.yml" \
               -f "$SCRIPTPATH/celery_worker/docker-compose.yml" \
               -f "$SCRIPTPATH/rabbitmq/docker-compose.yml" \
               -f "$SCRIPTPATH/postgres/docker-compose.yml" \
               -f "$SCRIPTPATH/docker-compose.dev.yml" \
               $@
