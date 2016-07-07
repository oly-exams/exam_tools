#!/bin/sh

set -e

for ff in `ls "$1/*json"`; do
  echo "Loading $ff."
  python manage.py loaddata "$ff"
done
