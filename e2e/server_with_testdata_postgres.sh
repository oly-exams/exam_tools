#!/bin/bash
set -e

mkdir -p db_data
touch db_data/database.s3db
touch db_data/database-initial.s3db
python ./ipho_data/postgres_testing_initial_data.py
python manage.py runserver 0.0.0.0:8000
