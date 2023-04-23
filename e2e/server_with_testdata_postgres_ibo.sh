#!/bin/bash
set -e

python ./ipho_data/postgres_testing_initial_data.py --dataset=ibo2019
python manage.py runserver 0.0.0.0:8000
