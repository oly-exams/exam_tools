
describe('Print', function() {
    // At the moment we are only checking whether the bulk-print page loads without error

    it('Test Bulk Print load', function() {
        cy.login('print','1234')
        cy.visit('exam/admin/bulk-print')
        cy.get("h1").should('contain', "Bulk print / scan status")
    })

})
