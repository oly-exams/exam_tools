#!/bin/sh

python manage.py dumpdata --natural-foreign --natural-primary --indent=2  auth.user ipho_core.autologin > data/demo/010_delegation_users.json
python manage.py dumpdata --natural-foreign --natural-primary --indent=2  ipho_core.delegation > data/demo/011_delegations.json 

