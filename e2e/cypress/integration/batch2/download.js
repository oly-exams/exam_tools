
describe('Downloads', function() {
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

    beforeEach(() => {
        cy.server()
        cy.route("POST", "/downloads/add_directory/**").as("addDirectory");
    })


    it('Test Visibility', function() {
        cy.login('admin','1234')
        cy.visit('downloads')

        cy.get('#upload-file-button')
        cy.get('#add-folder-button')
        cy.logout()
        cy.login("ARM", "1234")
        cy.get('#upload-file-button').should('not.exist')
        cy.get('#add-folder-button').should('not.exist')
    })

    it('Test Add folder', function(){
        cy.login('admin','1234')
        cy.visit('downloads')
        cy.get('#add-folder-button').click()
        cy.wait(1000)
        cy.get('#new-directory-modal').should('be.visible')
        cy.get('#new-directory-modal #id_directory').type("new-folder")
        cy.wait(500)
        cy.get("#new-directory-modal #new-directory-modal-submit").click()
        cy.wait("@addDirectory")
        cy.visit('downloads')
        cy.get(".download-item").find("new-folder")
        cy.logout()
        cy.login("ARM", "1234")
        cy.visit('downloads')
        cy.get(".download-item").find("new-folder")
    })

})
