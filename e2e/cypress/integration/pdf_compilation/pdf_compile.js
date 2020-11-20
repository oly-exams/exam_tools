
// Set this to false to disable pdf_checking
// (e.g. to recreate pdfs after changes to the inital data)
const check_pdf = true
//
//

function test_final_pdf(stud_id, doc_pos) {
    // Wait for pdf to compile
    cy.get('#preview-'+String(stud_id)+'-'+String(doc_pos)+' i.fa',  { timeout: 60000 }).should('not.have.class', 'fa-spinner').then(($i)=>{
        // Check icon again
        cy.wrap($i).should('have.class', 'fa-file-pdf-o')
        // Get Href
        cy.wrap($i).parent().should('have.attr', 'href')
        .then((href) => {
            // Send request
            cy.request({
                url: href,
                encoding: 'binary',
            })
            .then((response) => {
                // Write file to disk and compare
                cy.writeFile('cypress/pdfs/preview-'+String(stud_id)+'-'+String(doc_pos)+'.pdf', response.body, 'binary')
                if(check_pdf){
                    cy.exec('comparepdf --compare=appearance cypress/pdfs/preview-'+String(stud_id)+'-'+String(doc_pos)+'.pdf cypress/fixtures/pdfs/preview-'+String(stud_id)+'-'+String(doc_pos)+'.pdf')
                }
            })
        })
    })
}


describe('General', function() {

    beforeEach(() => {
        cy.server()
        cy.route("GET", /exam\/pdf-task\/[^\/]*/).as("getPDFPendingPage");
    })

    // Note that the usual beforeEach hook does not reset the postgres database.
    // So this test will change the state of the following ones. However they shouldn't interfere.
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
              if(check_pdf){
                cy.exec("comparepdf --compare=appearance cypress/pdfs/general_instr_v1.pdf cypress/fixtures/pdfs/general_instr_v1.pdf")
              }
            })
        })
    })

    it.only("Test Final submission", function() {
        cy.login("AUS", 1234)

        cy.visit("/exam/submission/1/assign")

        //choose languages
        cy.get("#stud-6-languages-val-1").check()
        cy.get("#stud-6-languages-val-2").check()
        cy.get("#stud-6-answer_language-val-2").check()

        cy.get("#stud-7-languages-val-1").check()
        cy.get("#stud-7-answer_language-val-1").check()

        cy.get('button[type="submit"]').should('contain', "Next").click()

        cy.url().should('contain', "/exam/submission/1/confirm")

        // We can only test the final submission for now, as there are missing images in the test data.
        test_final_pdf(6, 0)
        test_final_pdf(6, 1)
        test_final_pdf(6, 2)
        test_final_pdf(7, 0)
        test_final_pdf(7, 1)
        test_final_pdf(7, 2)
    })
})
