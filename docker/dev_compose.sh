#!/bin/sh

# this is identical to compose.sh, but does only include the services
# needed for development, no pre_commit or testing_cypress. Furthermore
# adds overwrite dev.yml.

SCRIPT=$(readlink -f $0)
SCRIPTPATH=$(dirname $SCRIPT)

U_ID="$(id -u)" \
G_ID="$(id -g)" \
docker-compose -p "exam_tools" \
               --project-directory="$SCRIPTPATH" \
               -f "$SCRIPTPATH/django-server/docker-compose.yml" \
               -f "$SCRIPTPATH/celery_worker/docker-compose.yml" \
               -f "$SCRIPTPATH/rabbitmq/docker-compose.yml" \
               -f "$SCRIPTPATH/postgres/docker-compose.yml" \
               -f "$SCRIPTPATH/overwrite/dev.yml" \
               -f "$SCRIPTPATH/overwrite/local_dev_user.yml" \
               $@
