#!/bin/sh

python manage.py dumpdata --natural-foreign --natural-primary --indent=2  contenttypes > data/demo/000_django_contenttype.json
python manage.py dumpdata --natural-foreign --natural-primary --indent=2  auth.permission > data/demo/000_django_permissions.json
