#!/bin/bash

INPUT_DIR=$1

echo "# Loading from $INPUT_DIR"


echo "Permissions..."
python manage.py dumpdata --natural-foreign --natural-primary --indent=2  auth.permission > 000_django_permissions.json

echo "Groups..."
python manage.py dumpdata --natural-foreign --natural-primary --indent=2  auth.group > 001_groups.json

echo "Admin users..."
python scripts/prod_01_other_users.py --dumpdata "$INPUT_DIR/010_users_admin.csv" > 010_admins.json

echo "Other users..."
python scripts/prod_01_other_users.py --dumpdata "$INPUT_DIR/011_users_others.csv" > 011_others.json

echo "Delegations..."
python scripts/prod_02_create_delegations.py --dumpdata "$INPUT_DIR/020_delegations.csv" > 020_delegations.json

echo "Students..."
python scripts/prod_03_create_students.py "$INPUT_DIR/021_students.csv"
python manage.py dumpdata --natural-foreign --natural-primary --indent=2  ipho_core.student > 021_students.json

echo "Delegations examsite..."
python scripts/prod_02b_create_delegations_examsite_team.py --dumpdata "$INPUT_DIR/022_delegations_examsite.csv" > 022_delegations_examsite.json
