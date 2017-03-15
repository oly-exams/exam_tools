#!/bin/bash

INPUT_DIR=$1


echo "Initialize 'users' and 'delegations'"
scripts/initialize_00x_01x_02x.sh "$INPUT_DIR"

echo "Export 'exams' and initialize 'seats' and 'examaction'"
scripts/initialize_03x_04x_05x.sh "$INPUT_DIR"
