#!/bin/bash

npx wait-on http-get://localhost:8000 && cypress run --headless -b chrome --spec "cypress/integration/$1/*.js"
