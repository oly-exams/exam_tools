// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })

import 'cypress-file-upload';

Cypress.Commands.add('login', (username, password) => {
    // This command is used to log into the page.
    cy.clearCookies()
    return cy.request({
      url: 'accounts/login/',
      method: 'GET'
    }).then(() => {

      cy.getCookie('sessionid').should('not.exist')
      cy.getCookie('csrftoken').its('value').then((token) => {
        var oldToken = token;
        cy.request({
          url: 'accounts/login/',
          method: 'POST',
          form: true,
          followRedirect: false, // no need to retrieve the page after login
          body: {
            username: username,
            password: password,
            csrfmiddlewaretoken: token
          }
        }).then(() => {

          cy.getCookie('sessionid').should('exist')
          return cy.getCookie('csrftoken').its('value')

        })
      })
    })

  })

  Cypress.Commands.add('logout', () => {
    // This command is used to logout.
    cy.clearCookies()
    cy.wait(1000)
    return
  })

  Cypress.Commands.add(
    "shouldHaveTrimmedText",
    { prevSubject: true },
    (subject, equalTo) => {
        expect(subject.text().trim()).to.eq(equalTo);
        return subject;
    },
);

Cypress.Commands.add("typeCKeditor", (element, content) => {
  cy.window()
    .then(win => {
      win.CKEDITOR.instances[element].setData(content);
    });
});

Cypress.Commands.add("readCKeditor", (element) => {
  cy.window()
    .then(win => {
      return win.CKEDITOR.instances[element].getData();
    });
});


Cypress.Commands.add('switchExamPhase', (id_arr) => {
  // This command is used to switch the exam phase
  var exam_id = id_arr[0];
  var phase_id = id_arr[1];
  return cy.request({
    url: 'control/cockpit/switch-phase/' + exam_id + '/' + phase_id,
    method: 'GET'
  }).then(() => {
    cy.getCookie('csrftoken').its('value').then((token) => {
      var oldToken = token;
      cy.request({
        url: 'control/cockpit/switch-phase/' + exam_id + '/' + phase_id,
        method: 'POST',
        form: true,
        followRedirect: false,
        body: {
          csrfmiddlewaretoken: token
        }
      })
    })
  })

})

Cypress.Commands.add('getExamPhaseByName', (exam_name, phase_name) => {
  // This command returns the pks of Exam and ExamPhase with given names
  if (exam_name == "Theory") {
    var base_pk = 0
    var exam_pk = 1
  } else {
    throw "Exam name " + exam_name + " not found in lookup. You might need to add it to getExamPhaseByName."
  }

  var phase_pk_lookup = {
    "Hidden": 1,
    "Preparation (Editing)": 2,
    "Preparation (Translating)": 3,
    "Discussion": 4,
    "Discussion (Translation)": 5,
    "Translation": 6,
    "Printing": 7,
    "Scanning": 8,
    "Organizer Marking": 9,
    "Delegation Marking": 10,
    "Delegation Marking (Submit only)": 11,
    "Moderation": 12,
    "Final": 13,
  }

  if (!phase_pk_lookup.hasOwnProperty(phase_name)) {
    throw "Phase name " + phase_name + " not found in lookup. You might need to add it to getExamPhaseByName."
  }
  var id_arr = [exam_pk, (phase_pk_lookup[phase_name] + base_pk)];
  return id_arr
});
