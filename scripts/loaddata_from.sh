#!/bin/sh

set -e

ls "$1"/*json | while read ff
do
  echo "Loading $ff."
  python manage.py loaddata "$ff"
done
