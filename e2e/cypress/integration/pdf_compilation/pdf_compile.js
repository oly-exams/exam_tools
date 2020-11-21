
// Set this to false to disable pdf_checking
// (e.g. to recreate pdfs after changes to the inital data)
const check_pdf = true
//
//
function download_test_pdf(stud_id, doc_pos, id_prefix="preview", file_prefix="final_submission_") {
    // Wait for pdf to compile
    cy.get('#'+id_prefix+'-'+String(stud_id)+'-'+String(doc_pos)+' i.fa',  { timeout: 60000 }).should('not.have.class', 'fa-spinner').then(($i)=>{
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
                var filename_end = '__student-'+String(stud_id)+'__position-'+String(doc_pos)+'.pdf';
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
            cy.wait(45000)
            // visit page again and confirm contenttype
            cy.request({
                url: url,
                encoding: 'binary',
            })
            .then((response) => {
              cy.writeFile('cypress/pdfs/general_instruction_v1.pdf', response.body, 'binary')
              if(check_pdf){
                cy.exec("comparepdf --compare=appearance cypress/pdfs/general_instruction_v1.pdf cypress/fixtures/pdfs/general_instruction_v1.pdf")
              }
            })
        })
    })

    it("Test Final submission", function() {
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

        download_test_pdf(6, 0)
        download_test_pdf(6, 1)
        download_test_pdf(6, 2)
        download_test_pdf(7, 0)
        download_test_pdf(7, 1)
        download_test_pdf(7, 2)

        // Checkbox alert should now be visible
        cy.get("form div.alert-warning").should('contain', "I understand that this is the final submission")
        cy.get('form div.alert-warning input[type="checkbox"]')
        // Try to submit without checking
        cy.get('button[type="submit"]').should('contain', "Submit").click()
        // alert should now be alert-danger
        cy.get("form div.alert-danger").should('contain', "You have to agree on the final submission before continuing.")
        cy.get('form div.alert-danger input[type="checkbox"]').check()
        cy.get('button[type="submit"]').should('contain', "Submit").click()

        cy.url().should('contain', '/exam/submission/1/submitted')

        // Check bulk-print scan
        cy.logout()
        cy.login("admin", "1234")

        cy.visit("/exam/admin/bulk-print")

        // Compare files in bulk-print
        var id_prefix = "exam-doc"
        var file_prefix = ""
        download_test_pdf(6, 0, id_prefix, file_prefix)
        download_test_pdf(6, 1, id_prefix, file_prefix)
        download_test_pdf(6, 2, id_prefix, file_prefix)
        download_test_pdf(7, 0, id_prefix, file_prefix)
        download_test_pdf(7, 1, id_prefix, file_prefix)
        download_test_pdf(7, 2, id_prefix, file_prefix)
    })

    // Note that this test depends on the state of the previous one
    // (namely on the documents being created)
    it("Test Manual File Upload", function(){
        cy.login('admin', '1234')
        cy.visit('/exam/admin/scan/upload')

        cy.get('#id_question').select("Two Problems in Mechanics - Answer Sheet [#1 in Theory]")
        cy.get('#id_student').select("AUS-S-1")

        // Attaching the corresponding fixture to scan. This enables us to use download_test_pdf again
        const filepath = 'pdfs/final_submission__student-6__position-1.pdf';
        cy.get('#id_file').attachFile({ filePath:filepath, mimeType: 'application/pdf' , encoding:"binary"})
        cy.get('#submit-id-submit').click()

        // Check file in bulk-print
        cy.visit("/exam/admin/bulk-print")
        var id_prefix = "processed_scan"
        download_test_pdf(6, 1, id_prefix, "")
        // Set status
        cy.get('a[href="/exam/admin/scan-status/2/S"]').click()
        cy.getExamPhaseByName('Theory', "Delegation Marking").then(cy.switchExamPhase)

        // Check delegation scan view
        cy.logout()
        cy.login('AUS', '1234')
        cy.visit('/marking/')
        var id_prefix = "processed_scan"
        download_test_pdf(6, 1, id_prefix, "delegation_view_")
    })

})
