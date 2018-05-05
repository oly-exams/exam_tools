#!/bin/bash

INPUT_DIR=$1

echo "# Loading from $INPUT_DIR"


echo "Exams..."
python scripts/export_orig_exams.py

echo "Official translations..."
python scripts/export_trans_exams.py

# echo "Delegation translations"
# python scripts/export_delegation_translations.py

echo "Student seats..."
# python scripts/prod_04_import_student_seating.py "$INPUT_DIR/040_students_seats.csv"
python scripts/set_random_seats.py
python manage.py dumpdata --natural-foreign --natural-primary --indent=2  ipho_exam.place > 040_student_seats.json

echo "Exam Actions..."
python scripts/create_all_examactions.py
python manage.py dumpdata --natural-foreign --natural-primary --indent=2  ipho_exam.examaction > 050_examaction.json

echo "Marking structure..."
python manage.py dumpdata --natural-foreign --natural-primary --indent=2  ipho_marking.markingmeta ipho_marking.marking > 060_marking.json
