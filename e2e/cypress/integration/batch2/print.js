
describe('Print', function() {
    // Here we are only checking whether the bulk-print page loads without error
    // There are more tests in pdf_compilation/, checking different pdf related things.

    before(() => {
        // runs once before all tests in the block
        cy.beforeAllDBInit()
    })

    beforeEach(() => {
        // this runs prior to every test
        cy.beforeEachDBInit()
    })

    it('Test Bulk Print load', function() {
        cy.login('print','1234')
        cy.visit('exam/admin/bulk-print')
        cy.get("h1").should('contain', "Bulk print / scan status")
    })

})
