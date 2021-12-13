
// Set this to false to disable pdf_checking
// (e.g. to recreate pdfs after changes to the inital data)
const check_pdf = true
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
        cy.login("AUS-Leader", 1234)

        cy.visit("/exam/submission/1/assign")

        //choose languages
        cy.get("#ppnt-6-languages-val-1").check()
        cy.get("#ppnt-6-languages-val-2").check()
        cy.get("#ppnt-6-answer_language-val-2").check()

        cy.get("#ppnt-7-languages-val-1").check()
        cy.get("#ppnt-7-answer_language-val-1").check()

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
        cy.login("print", "1234")

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
    it("Test Admin Manual File Upload", function(){
        cy.login('print', '1234')
        cy.visit('/exam/admin/scan/upload')

        cy.get('#id_question').select("Two Problems in Mechanics - Answer Sheet [#1 in Theory]")
        cy.get('#id_participant').select("AUS-S-1 (Theory)")

        // Attaching the corresponding fixture to scan. This enables us to use download_test_pdf again
        const filepath = 'pdfs/final_submission__participant-6__position-1.pdf';
        cy.get('#id_file').attachFile({ filePath:filepath, mimeType: 'application/pdf' , encoding:"binary"})
        cy.get('#submit-id-submit').click()

        // Check file in bulk-print
        cy.visit("/exam/admin/bulk-print")
        var id_prefix = "processed_scan"
        download_test_pdf(6, 1, id_prefix, "")
        // Set status
        cy.get('a[href="/exam/admin/scan-status/2/S"]').click()

        cy.logout()
        cy.login('admin', '1234')
        cy.getExamPhaseByName('Theory', "Delegation Marking").then(cy.switchExamPhase)

        // Check delegation scan view
        cy.logout()
        cy.login("AUS-Leader", '1234')
        cy.visit('/marking/')
        var id_prefix = "processed_scan"
        download_test_pdf(6, 1, id_prefix, "delegation_view_")
    })

    // Note that this test depends on the state of the previous one
    // (namely on the documents being created)
    it("Test Examsite User", function(){
        cy.logout()
        cy.login('admin', '1234')
        cy.getExamPhaseByName('Theory', "Translation").then(cy.switchExamPhase)

        // Test an examsite user without submissions
        cy.logout()
        cy.login('ARM-Supervisor', '1234')
        cy.visit('/exam/submission/submitted')
        //Table should be empty
        cy.get('#submission-table tbody').children().should('have.length', 0)

        // Test an examsite user with submissions
        cy.logout()
        cy.login('AUS-Supervisor', '1234')
        cy.visit('/exam/submission/submitted')
        //Table should be empty
        cy.get('#submission-table tbody').children().should('have.length', 0)

        cy.logout()
        cy.login('admin', '1234')
        cy.getExamPhaseByName('Theory', "Printing").then(cy.switchExamPhase)

        // Test an examsite user without submissions
        cy.logout()
        cy.login('ARM-Supervisor', '1234')
        cy.visit('/exam/submission/submitted')
        //Table should be empty
        cy.get('#submission-table tbody').children().should('have.length', 0)

        // Test an examsite user with submissions
        cy.logout()
        cy.login('AUS-Supervisor', '1234')
        cy.visit('/exam/submission/submitted')
        //Table should now have 3 entries
        cy.get('#submission-table tbody').children().should('have.length', 6)

        var id_prefix = "submission-1"
        download_test_pdf(6, 0, id_prefix, "")
        download_test_pdf(6, 1, id_prefix, "")
        download_test_pdf(6, 2, id_prefix, "")

        cy.get('#upload-1-6-2').click()
        cy.wait('@getUploadModal')
        cy.get('#upload-modal').should('be.visible').and('contain', "The organizers have not yet opened or already closed the scan upload, uploads are not possible.")

        cy.logout()
        cy.login('admin', '1234')
        cy.getExamPhaseByName('Theory', "Scanning").then(cy.switchExamPhase)

        // Test an examsite user with submissions
        cy.logout()
        cy.login('AUS-Supervisor', '1234')
        cy.visit('/exam/submission/submitted')
        //Table should now have 3 entries
        cy.get('#submission-table tbody').children().should('have.length', 6)

        var id_prefix = "submission-1"
        download_test_pdf(6, 0, id_prefix, "")
        download_test_pdf(6, 1, id_prefix, "")
        download_test_pdf(6, 2, id_prefix, "")

        // Check uploaded scans
        var scan_prefix = "scan-1"
        download_test_pdf(6, 1, scan_prefix, "")

        cy.get('#upload-1-6-2').click()
        cy.wait('@getUploadModal')

        const filepath = 'pdfs/final_submission__participant-6__position-2.pdf';
        cy.get('#id_file').attachFile({ filePath:filepath, mimeType: 'application/pdf' , encoding:"binary"})
        cy.get('#upload-modal button[type="submit"]').click()
        cy.wait('@postUploadModal')

        cy.visit('/exam/submission/submitted')
        // Check uploaded scan
        download_test_pdf(6, 2, scan_prefix, "")

        // change exam phase
        cy.logout()
        cy.login('admin', '1234')
        cy.getExamPhaseByName('Theory', "Delegation Marking").then(cy.switchExamPhase)

        // Check delegation scan view
        cy.logout()
        cy.login("AUS-Leader", '1234')
        cy.visit('/marking/')
        var id_prefix = "processed_scan"
        download_test_pdf(6, 2, id_prefix, "delegation_view_")
    })

    it("Test Marker Scan View", function(){
        cy.logout()
        cy.login('admin', '1234')
        cy.getExamPhaseByName('Theory', "Organizer Marking").then(cy.switchExamPhase)

        // Test one marking view and try to download the scan
        cy.logout()
        cy.login('marker', '1234')
        cy.visit('/marking/official/question/3/delegation/2')
        var id_prefix = "scan"
        download_test_pdf(6, 1, id_prefix, "marking_")

        cy.logout()
        cy.login('admin', '1234')
        cy.getExamPhaseByName('Theory', "Moderation").then(cy.switchExamPhase)

        // Test one moderation view and try to download the scan
        cy.logout()
        cy.login('marker', '1234')
        cy.visit('/marking/moderate/question/3/delegation/2')
        var id_prefix = "scan"
        download_test_pdf(6, 1, id_prefix, "moderation_")
    })
})
