#!/bin/bash

# turn on bash's job control
set -m

echo "################  Starting server  ##################"
# Start the primary process and put it in the background
cp ipho-backup.db ipho.db || true
cp ipho.db ipho-backup.db

# Start the helper process http://localhost:8000
npx wait-on http-get://localhost:8000 && npx cypress run $*
