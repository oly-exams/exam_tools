
// Set this to false to disable pdf_checking
// (e.g. to recreate pdfs after changes to the inital data)
const check_pdf = false
//
//
function download_test_pdf(ppnt_id, doc_pos, id_prefix="preview", file_prefix="final_submission_") {
    // Wait for pdf to compile
    cy.get('#'+id_prefix+'-'+String(ppnt_id)+'-'+String(doc_pos)+' i.fa',  { timeout: 60000 }).should('not.have.class', 'fa-spinner').then(($i)=>{
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
                var filename_end = '__participant-'+String(ppnt_id)+'__position-'+String(doc_pos)+'.pdf';
                var filename = file_prefix + id_prefix + filename_end;
                var filename_fixture = "final_submission" + filename_end;
                cy.writeFile('cypress/pdfs/'+filename, response.body, 'binary');
                if(check_pdf){
                    cy.exec('comparepdf --compare=appearance cypress/pdfs/' + filename + ' cypress/fixtures/pdfs/' + filename_fixture);
                }
            })
        })
    })
}


describe('General', function() {

    beforeEach(() => {
        cy.server()
        cy.route("GET", /exam\/pdf-task\/[^\/]*/).as("getPDFPendingPage");
        cy.route("GET", "/exam/submission/submitted/scan/exam/**").as("getUploadModal");
        cy.route("POST", "/exam/submission/submitted/scan/exam/**").as("postUploadModal");
    })

    // Note that the usual beforeEach hook does not reset the postgres database.
    // So this test will change the state of the following ones. However they shouldn't interfere.
    it("Test pdf Compilation", function() {
        cy.login("admin", 1234)
        cy.visit('/exam/pdf/question/1/lang/1/v1').then(()=>{
            cy.wait("@getPDFPendingPage")
        })

        cy.url().then((url) => {
            // Switch page and Wait for  30 seconds to ensure compilation
            // We need to wait manually because otherwise firefox would open the pdf reader, triggering a cross site request
            cy.visit("/chocobunny")
            cy.wait(45000)
            // visit page again and confirm contenttype
            cy.request({
                url: url,
                encoding: 'binary',
            })
            .then((response) => {
              cy.writeFile('cypress/pdfs/ibo1.pdf', response.body, 'binary')
              if(check_pdf){
                cy.exec("comparepdf --compare=appearance cypress/pdfs/general_instruction_v1.pdf cypress/fixtures/pdfs/general_instruction_v1.pdf")
              }
            })
        })
    })

})
