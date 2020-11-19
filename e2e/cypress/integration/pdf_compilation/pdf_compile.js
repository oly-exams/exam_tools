

describe('General', function() {

    beforeEach(() => {
        cy.server()
        cy.route("GET", /exam\/pdf-task\/[^\/]*/).as("getPDFPendingPage");
    })

    // Note that the usual beforeEach hook does not reset the postgres database, so we are only using one test.
    it("Test pdf Compilation", function() {
        cy.login("admin", 1234)
        cy.visit('/exam/pdf/question/1/lang/1/v2').then(()=>{
            cy.wait("@getPDFPendingPage")
        })

        cy.url().then((url) => {
            // Switch page and Wait for  30 seconds to ensure compilation
            // We need to wait manually because otherwise firefox would open the pdf reader, triggering a cross site request
            cy.visit("")
            cy.wait(30000)
            // visit page again and confirm contenttype
            cy.request({
                url: url,
                encoding: 'binary',
            })
            .then((response) => {
              cy.writeFile('cypress/pdfs/general_instr_v1.pdf', response.body, 'binary')
              cy.exec("comparepdf --compare=appearance cypress/pdfs/general_instr_v1.pdf cypress/fixtures/general_instr_v1.pdf")
            })
        })
    })
})
