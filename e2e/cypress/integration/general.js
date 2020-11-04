

describe('Basic Functionalities', function() {
    it('Test Index', function() {
        cy.visit('/')
        cy.url().should('contain', 'accounts/login')
    })

    it('Test Login and Logout', function() {
        cy.visit('/')
        cy.url().should('contain', 'accounts/login')
        cy.get('[type="text"]').type('CHE')
        cy.get('[type="password"]').type('1234')
        cy.get('[type="submit"]').click()
        cy.url().should('not.contain', 'accounts/login')
        cy.contains('logout', { matchCase: false }).click()
        cy.url().should('contain', 'accounts/login')
    })

    //Use the login command instead of the ui to log in.
    /*
    it('Another Test', function(){
        cy.login('testdelegation','testpw')

    })
    */
})
