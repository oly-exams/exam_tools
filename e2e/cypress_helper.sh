#!/bin/bash

# turn on bash's job control
set -m

echo "################  Starting server  ##################"
# Start the helper process http://localhost:8000
npx wait-on http-get://localhost:8000
cp ../ipho-backup.db ../ipho.db || true #if we run testing_cypress multiple times
cp ../ipho.db ../ipho-backup.db
npx cypress run $*
