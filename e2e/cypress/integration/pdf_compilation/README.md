Note:
This batch is used to test pdf compilation and file downloads. It runs using a postgres db and with different test data.

The tests in this section will need firefox to run properly. Hence you need to run the tests using:
```bash
cypress run --spec "cypress/integration/pdf_compilation/pdf_compile.js" -b firefox --headless
```
