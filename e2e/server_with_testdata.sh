#!/bin/bash
set -e

python ./ipho_data/cypress_initial_data.py
python manage.py runserver 0.0.0.0:8000
