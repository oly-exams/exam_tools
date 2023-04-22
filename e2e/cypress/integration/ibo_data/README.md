Note:
This batch is used to test pdf compilation of the ibo2019 data. It runs using a postgres db and with different test data.

The tests in this section will need firefox to run properly. Hence you need to run the tests using:
```bash
cypress run --spec "cypress/integration/ibo_data/ibo_data.js" -b firefox --headless
```
