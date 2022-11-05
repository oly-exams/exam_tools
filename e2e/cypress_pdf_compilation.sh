#!/bin/bash

npx wait-on http-get://localhost:8000 && cypress run --headless -b firefox --spec "cypress/integration/pdf_compilation/*.js"
