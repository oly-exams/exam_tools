#!/bin/bash

# turn on bash's job control
set -m

echo "################  Starting server  ##################"
# Start the primary process and put it in the background
python manage.py migrate && python manage.py runserver localhost:8000 &

# Start the helper process http://localhost:8000
npx wait-on http-get://localhost:8000 && npx cypress run $*

kill %1
