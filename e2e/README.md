# Testing with Cypress

Cypress is an end-to-end testing framework. It starts a browser in headless mode, executes a series of commands and assertions (e.g. click here, check this value, load that page, etc.) in that browser and generates a report at the end.

This document should help you start writing tests and explain some of the specific challenges when testing this repository. For more details, a general introduction and much more, please refer to the [Cypress docs](https://docs.cypress.io/).

## Folder structure
### i.e. where are the tests?
The structure is as follows (where I left out files unimportant to our discussion):
```
e2e
 |-- cypress.json
 `-- cypress
      |-- integration
      |    |-- batch1
      |    |    |-- some_test.js
      |    |    |-- another_test.js
      |    |    .   ...
      |    |-- batch2
      |    .   ...
      |-- reports
      |    |-- some_test_report.xml
      |    |-- another_test_report.xml
      |    .   ...
      |-- screenshots
      |
      `-- support
           |-- commands.js
           `-- index.js
```
 We will shortly go through all files/directories:
 1. `cypress.json` is the configuration file for Cypress. Please refer to the Cypress docs for more information.
 2. `integration` contains the tests, they are split into multiple batches. Each batch will run in a separate CI job, to speed up testing. If you add a new batch, make sure to also add the corresponding CI configuration in `.gitlab/ci/test.yml`
 3. `integration/batch_/some_test.js` is one test file. I will go into a bit more detail in the following section.
 4. `reports` and `screenshots` contain test reports and screenshots, respectively. Note that the latter are only taken when an error occurs.
 5. `support` contains two important files, `commands.js` and `index.js`. The former contains custom commands, the latter contains the `before` and `after` hooks.

## General Setup of a test

We will look at a simple example from `integration/batch1/general.js`
```js
describe('Basic Functionalities', function() {
    it('Test Index', function() {
        cy.visit('/')
        cy.url().should('contain', 'accounts/login')
    })

    it('Another Test', function() {
        ...
    })
})
```

The `describe(...)` function is used to group a number of tests (i.e. all tests in this file). It sets a name (`Basic Functionalities` in this example) for this group.

Single tests are encapsulated in `it(<name>, function(){ <test_code> })`.

The actual test code are then just Cypress commands. For example:
* `cy.visit(<url>)` visits the given url
* `cy.get("#some_id").should('contain', "Some text")` gets the DOM element with id `some_id` and checks whether it contains `some text`.

Check the Cypress docs [here](https://docs.cypress.io/guides/getting-started/writing-your-first-test.html) and [here](https://docs.cypress.io/guides/references/best-practices.html) for an overview and best practices.

## Hooks
To prepare the initial dataset, Cypress uses the `before` and `beforeEach` hooks defined in `support/index.js`. The `before` hook runs once before all tests (watch out when using the test runner, see [here](https://docs.cypress.io/guides/core-concepts/writing-and-organizing-tests.html#Hooks)). The `beforeEach` hook runs once before each test (each `it()`).

## Specific challenges and solutions, custom commands
### Selecting elements
Cypress uses `.css` selectors to select elements e.g. `cy.get("#some-id")`. The easiest way to select an element is obviously by using the id. Feel free to add ids in the HTML templates, if they help you write better tests. Just make sure they are unique and choose sensible names.

The Cypress test runner (`cypress open`) also provides a nice gui which yields a selector for a given element.


### Custom commands
There are some custom commands defined in `support/commands.js`. Noteworthy are:
* `cy.login(username, password)` Use this command to log a user in. This is faster than using the UI, as it directly sends the corresponding requests.

* `cy.logout()` The same for the logout.

* `shouldHaveTrimmedText(text)` This is similar to the Cypress command `should('have.text', text)`, but it first trims whitespaces from the HTML text.

* `typeCKeditor(element, text)` and `readCKeditor(element)` are used to type and read CKeditor fields. `element` is the name of the specific editor, as assigned by CKeditor. See `transate.js` for examples.

* `switchExamPhase(exam_id, phase_id)` similar to the login, using this command is much faster than using the UI. `exam_id` and `phase_id` are the pk's of the respective models. Note that you need to be logged in as admin for this command to work.

## Timeouts
Most Cypress commands have built in timeouts. Sometimes they are not sufficient, however. As the wait times mostly depend on the speed of the machine, timeouts can occur only in the CI jobs or only locally and they might not occur consistently.

Note: Timeouts also occur when a test should fail, e.g. when Cypress looks for a DOM element that is not there, it timeout looking for that element.

After checking (e.g. with the Cypress test runner), that the test should succeed (e.g. that the DOM element is really there), you can add additional waiting time using `cy.wait(<time in ms>)`.
If the problematic content is loaded with Ajax (e.g. the content of some modal), use the solution below.

## Waiting for Ajax responses
We use many Ajax calls to dynamically load content, e.g. for modals. If an Ajax response takes a long time, this will lead to a timeout in Cypress. One could use `cy.wait()`, but there is a nicer solution: [Routing](https://docs.cypress.io/api/commands/wait.html#Wait-for-a-specific-XHR-to-respond).

In our case this looks like (example from `feedbacks.js`):

```js
describe('Feedback', function() {

    beforeEach(() => {
        cy.server()
        cy.route("GET", "/exam/feedbacks/list/**").as("getFeedbackTable");
    })

    it('Test Loaded Feedback', function(){
        cy.login("ARM", "1234")
        //check feedback overview page
        //This will trigger the Ajax call.
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")
        ......
    })
```

The elements are:
* The `beforeEach` hook which runs before each test in the `describe` (As it is only defined in this scope, hooks in `index.js` will run before each test in every `describe`).
* `cy.server()` starting a Cypress server to interfere requests.
* `cy.route("<MODE>","<url pattern>").as("<name>")` which collects all requests to the given url pattern under `name`.
* `cy.wait("@<name>")` will then wait for the next request to this route. You can use this multiple times, Cypress will automatically keep track of the number of requests.
