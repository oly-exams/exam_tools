#!/bin/bash

npx wait-on http-get://localhost:8000 && cypress run --headless -b firefox --spec "cypress/integration/ibo_data/*.js"
