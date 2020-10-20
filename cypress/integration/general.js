

describe('Page Load', function() {
    it('Test Login Page', function() {
        cy.visit('/')
        cy.url().should('contain', 'accounts/login')
    })
})