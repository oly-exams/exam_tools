

function download_test_file(filename, prefix) {
    // Wait for pdf to compile
    cy.get(".download-item").contains(filename).should('have.attr', 'href')
        .then((href) => {
            // Send request
            cy.request({
                url: href,
                encoding: 'ascii',
            })
            .then((response) => {
                // Write file to disk and compare
                cy.writeFile('cypress/test_files/'+ prefix + filename, response.body, 'ascii');
                cy.exec('diff cypress/test_files/' + prefix + filename + ' cypress/fixtures/test_files/' + filename);
            })
    })
}


describe('Downloads', function() {
    // Here we are only checking whether the bulk-print page loads without error
    // There are more tests in pdf_compilation/, checking different pdf related things.

    before(() => {
        // runs once before all tests in the block
        //cy.beforeAllDBInit()
    })

    beforeEach(() => {
        // this runs prior to every test
        //cy.beforeEachDBInit()
    })

    beforeEach(() => {
        cy.server()
        cy.route("POST", "/downloads/add_directory/**").as("addDirectory");
        cy.route("POST", "/downloads/add_file/**").as("addFile");
        cy.route("POST", "/downloads/remove/**").as("Remove");
    })


    it('Test Visibility', function() {
        cy.login('admin','1234')
        cy.visit('downloads/')

        cy.get('#upload-file-button')
        cy.get('#add-folder-button')
        cy.get('.remove-button').should('not.exist')
        cy.logout()
        cy.login("ARM", "1234")
        cy.visit('downloads/')
        cy.get('#upload-file-button').should('not.exist')
        cy.get('#add-folder-button').should('not.exist')
        cy.get('.remove-button').should('not.exist')
    })

    it('Test Add folder', function(){
        cy.login('admin','1234')
        cy.visit('downloads/')
        cy.get('#add-folder-button').click()
        cy.wait(1000)
        cy.get('#new-directory-modal').should('be.visible')
        cy.get('#new-directory-modal #id_directory').type("new-folder")
        cy.wait(500)
        cy.get("#new-directory-modal #new-directory-modal-submit").click()
        cy.wait("@addDirectory")
        cy.visit('downloads/')
        cy.get(".download-item").contains("new-folder")
        cy.get('.remove-button').should('not.exist')

        cy.logout()
        cy.login("ARM", "1234")
        cy.visit('downloads/')
        cy.get(".download-item").contains("new-folder")
        cy.get('.remove-button').should('not.exist')
    })

    it('Test Add/Remove File', function(){
        cy.login('admin','1234')
        cy.visit('downloads/')
        cy.get('#upload-file-button').click()
        cy.wait(1000)
        cy.get('#new-file-modal').should('be.visible')
        const filename = 'download_test.txt';
        const filepath = 'test_files/' + filename;

        cy.get('#new-file-modal #id_file').attachFile({ filePath:filepath, mimeType: 'text/plain' , encoding:"binary"})
        cy.wait(500)
        cy.get("#new-file-modal #new-file-modal-submit").click()
        cy.wait("@addFile")
        cy.visit('downloads/')
        cy.get(".download-item").contains(filename)
        download_test_file(filename, 'admin_')

        cy.logout()
        cy.login("ARM", "1234")
        cy.visit('downloads/')
        cy.get(".download-item").contains(filename)
        cy.get('.remove-button').should('not.exist')
        download_test_file(filename, 'ARM_')

        cy.logout()
        cy.login('admin','1234')
        cy.visit('downloads/')
        cy.get(".download-item").contains(filename).parent().parent().find("button.remove-button").click()
        cy.get('#remove-modal').should('be.visible')
        cy.get("#remove-modal").find("button").contains("Remove").click()
        cy.wait("@Remove")
        cy.visit('downloads/')
        cy.get(".download-item").contains(filename).should('not.exist')
        cy.get('.remove-button').should('not.exist')

        cy.logout()
        cy.login("ARM", "1234")
        cy.visit('downloads/')
        cy.get(".download-item").contains(filename).should('not.exist')
        cy.get('.remove-button').should('not.exist')
    })

})
