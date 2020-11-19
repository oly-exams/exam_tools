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


Cypress.Commands.add('switchExamPhase', (exam_id, phase_id) => {
  // This command is used to switch the exam phase
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
