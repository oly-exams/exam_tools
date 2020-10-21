

describe('Test Basic Functionalities', function() {
    it('Test Index', function() {
        cy.visit('/')
        cy.url().should('contain', 'accounts/login')
    })

    it('Test Login Page', function() {
        cy.visit('/')
        cy.url().should('contain', 'accounts/login')
        // TODO: add credentials
        /*
        cy.get('[type="text"]').type('testdelegation')
        cy.get('[type="password"]').type('testpw')
        cy.get('[type="submit"]').click()
        cy.url().should('not.contain', 'accounts/login')
        */
    })

    //Use the login command instead of the ui to log in.
    /*
    it('Another Test', function(){
        cy.login('testdelegation','testpw')
        
    })
    */
})