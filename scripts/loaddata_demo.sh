#!/bin/sh

set -e

for ll in `ls data/demo/*json`; do
  echo "Loading $ff."
  python manage.py loaddata $ff
done
