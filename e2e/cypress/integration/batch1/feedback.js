

describe('Feedback', function() {

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
        cy.route("GET", "/exam/feedbacks/partial/**").as("getFeedbackPartial");
        cy.route("POST", "/exam/feedbacks/partial/**").as("addFeedback");
        cy.route("GET", "/exam/feedbacks/list/**").as("getFeedbackTable");
        cy.route("GET", "/exam/feedbacks/add/**").as("getCommentModal");
    })

    it('Test Loaded Feedback', function(){
        cy.login("ARM", "1234")

        //check feedback overview page
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(2)').contains('Submitted')
        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(3)').contains('Armenia')
        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(4)').contains('Two Problems in Mechanics')
        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(5)').contains('A.1')
        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(7)').contains("Armenia Lorem ipsum")

        cy.get('#feedback-tbody-1 > :nth-child(2) > :nth-child(3)').contains('Australia')
        cy.get('#feedback-tbody-1 > :nth-child(2) > :nth-child(7)').contains("Australia Lorem ipsum")

        cy.get('#feedback-tbody-1 > :nth-child(3) > :nth-child(3)').contains('Austria')
        cy.get('#feedback-tbody-1 > :nth-child(3) > :nth-child(7)').contains("Austria Lorem ipsum")

        cy.get('#feedback-tbody-1 > :nth-child(4) > :nth-child(3)').contains('Switzerland')
        cy.get('#feedback-tbody-1 > :nth-child(4) > :nth-child(7)').contains("Switzerland Lorem ipsum")

        //check exam view site
        cy.visit("exam/view/1/question/2")

        cy.get("#q0_ti1").contains("5")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal").should("be.visible")
        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(1) > :nth-child(3)").contains("Armenia")
        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(1) > :nth-child(4)").contains("Armenia Lorem ipsum")

        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(2) > :nth-child(3)").contains("Australia")
        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(2) > :nth-child(4)").contains("Australia Lorem ipsum")

        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(3) > :nth-child(3)").contains("Austria")
        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(3) > :nth-child(4)").contains("Austria Lorem ipsum")

        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(4) > :nth-child(3)").contains("Switzerland")
        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(4) > :nth-child(4)").contains("Switzerland Lorem ipsum")

    })

    it('Test Visibility', function(){
        cy.login("admin", "1234")
        // Preparation Phase (neither exam nor feedbacks are visible to delegations)
        cy.getExamPhaseByName('Theory', "Preparation (Editing)").then(cy.switchExamPhase)
        //admin
        cy.request({ url:"exam/feedbacks/list/1", failOnStatusCode: false}).its("status").should('eq', 404)
        cy.visit("exam/view/1/question/2")
        cy.get('[data-target="#feedback-modal"]').should('not.exist')
        cy.logout()
        //delegation
        cy.login("ARM","1234")
        cy.request({ url:"exam/feedbacks/list/1", failOnStatusCode: false}).its("status").should('eq', 404)
        cy.request({ url:"exam/view/1/question/2", failOnStatusCode: false}).its("status").should('eq', 404)

        cy.logout()

        cy.login("admin", "1234")
        // Discussion (exam.feedback = Exam.FEEDBACK_CAN_BE_OPENED)
        cy.getExamPhaseByName('Theory', "Discussion").then(cy.switchExamPhase)
        //admin
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get("#feedback-tbody-1").should('contain', "Armenia")
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").contains("5")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal").should("be.visible")
        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(1) > :nth-child(3)").contains("Armenia")
        cy.logout()
        //delegation
        cy.login("ARM","1234")
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get("#feedback-tbody-1").should('contain', "Armenia")
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").contains("5")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal").should("be.visible")
        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(1) > :nth-child(3)").contains("Armenia")
        cy.logout()

        cy.login("admin", "1234")
        // Translation (where exam.feedback = Exam.FEEDBACK_READONLY)
        cy.getExamPhaseByName('Theory', "Translation").then(cy.switchExamPhase)
        //admin
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get("#feedback-tbody-1").should('contain', "Armenia")
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").contains("5")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal").should("be.visible")
        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(1) > :nth-child(3)").contains("Armenia")
        cy.logout()
        //delegation
        cy.login("ARM","1234")
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get("#feedback-tbody-1").should('contain', "Armenia")
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").contains("5")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal").should("be.visible")
        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(1) > :nth-child(3)").contains("Armenia")
        cy.logout()

        cy.login("admin", "1234")
        // Printing (feedback invisible, exam visible)
        cy.getExamPhaseByName('Theory', "Printing").then(cy.switchExamPhase)
        //admin
        cy.request({ url:"exam/feedbacks/list/1", failOnStatusCode: false}).its("status").should('eq', 404)
        cy.visit("exam/view/1/question/2")
        cy.get('[data-target="#feedback-modal"]').should('not.exist')
        cy.logout()
        //delegation
        cy.login("ARM","1234")
        cy.request({ url:"exam/feedbacks/list/1", failOnStatusCode: false}).its("status").should('eq', 404)
        cy.visit("exam/view/1/question/2")
        cy.get('[data-target="#feedback-modal"]').should('not.exist')

    })

    it('Test Add Feedback', function() {
        cy.login("ARM",'1234')
        //Feedbacks are closed on default. No user should be able to add feedback
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_pa1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal").should("be.visible")
        cy.get("#feedback-modal #id_comment").should("not.exist")
        cy.get("#feedback-modal #modal-form-submit").should("not.exist")

        cy.logout()
        cy.login('admin', '1234')
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_pa1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal").should("be.visible")
        cy.get("#feedback-modal #id_comment").should("not.exist")
        cy.get("#feedback-modal #modal-form-submit").should("not.exist")

        // open feedbacks for question
        cy.visit("control/cockpit")
        cy.get("#id_question_set-1-feedback_status").select("Open")
        cy.get("#submit-id-submit").click()
        //Admin should still not be able to add feedback
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_pa1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal").should("be.visible")
        cy.get("#feedback-modal #id_comment").should("not.exist")
        cy.get("#feedback-modal #modal-form-submit").should("not.exist")

        cy.logout()
        cy.login("ARM", '1234')
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_pa1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal").should("be.visible")
        //Add feedback
        //preventing a bug where cypress doesn't fill the form
        cy.wait(1500)
        cy.get("#feedback-modal #id_comment").type("Some Feedback ARM")
        cy.wait(500)
        cy.get("#feedback-modal #modal-form-submit").click()
        cy.wait("@addFeedback")

        cy.get("#feedback-modal").should("be.visible")
        cy.get("#feedback-modal").contains("Some Feedback ARM")
        //check feedback on feedback list
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")
        cy.get('#feedback-tbody-1 > :nth-child(6) > :nth-child(2)').contains('Submitted')
        cy.get('#feedback-tbody-1 > :nth-child(6) > :nth-child(3)').contains('Armenia')
        cy.get('#feedback-tbody-1 > :nth-child(6) > :nth-child(4)').contains('Two Problems in Mechanics')
        cy.get('#feedback-tbody-1 > :nth-child(6) > :nth-child(5)').contains('Introduction')
        cy.get('#feedback-tbody-1 > :nth-child(6) > :nth-child(7)').contains("Some Feedback ARM")

        // Close(org_comment) feedbacks for question
        cy.logout()
        cy.login('admin', '1234')
        cy.visit("control/cockpit")
        cy.get("#id_question_set-1-feedback_status").select("Closed, Organizer can still comment.")
        cy.get("#submit-id-submit").click()
        //Admin should still not be able to add feedback
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_pa1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal").should("be.visible")
        cy.get("#feedback-modal #id_comment").should("not.exist")
        cy.get("#feedback-modal #modal-form-submit").should("not.exist")
        //Delegation should not be able to add feedback
        cy.logout()
        cy.login("ARM", '1234')
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_pa1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal").should("be.visible")
        cy.get("#feedback-modal #id_comment").should("not.exist")
        cy.get("#feedback-modal #modal-form-submit").should("not.exist")

        // Switch phase
        // Translation (exam.feedback = Exam.FEEDBACK_READONLY)
        cy.logout()
        cy.login('admin','1234')
        cy.getExamPhaseByName('Theory', "Translation").then(cy.switchExamPhase)
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_pa1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal").should("be.visible")
        cy.get("#feedback-modal #id_comment").should("not.exist")
        cy.get("#feedback-modal #modal-form-submit").should("not.exist")

        cy.logout()
        cy.login("ARM", '1234')
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_pa1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal").should("be.visible")
        cy.get("#feedback-modal #id_comment").should("not.exist")
        cy.get("#feedback-modal #modal-form-submit").should("not.exist")
    })

    it('Test Organizer Comment', function(){
        cy.login("ARM",'1234')
        //Feedbacks are closed on default. No user should be able to add comments
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1').should('not.contain', "Add comment")
        cy.get('#feedback-tbody-1 .add-comment-button').should('not.exist')

        cy.logout()
        cy.login('admin', '1234')
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1').should('not.contain', "Add comment")
        cy.get('#feedback-tbody-1 .add-comment-button').should('not.exist')

        // open feedbacks for question
        cy.visit("control/cockpit")
        cy.get("#id_question_set-1-feedback_status").select("Open")
        cy.get("#submit-id-submit").click()

        //Add Comment
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 #add-comment-1').click()
        cy.wait("@getCommentModal")

        cy.get('#feedback-modal').should('be.visible')
        cy.wait(500)
        cy.get('#feedback-modal #id_comment').type('Some comment')
        cy.get('#feedback-modal [type="submit"]').click()
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(7)').contains("Some comment")
        //Update Comment
        cy.get('#feedback-tbody-1 #add-comment-1').click()
        cy.wait("@getCommentModal")

        cy.get('#feedback-modal').should('be.visible')
        cy.get('#feedback-modal #id_comment').should('have.value', 'Some comment')
        cy.wait(500)
        cy.get('#feedback-modal #id_comment').clear().type('Another comment')
        cy.get('#feedback-modal [type="submit"]').click()
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(7)').contains("Another comment")
        //Check on exam view
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal").should("be.visible")
        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(1) > :nth-child(4)").contains("Another comment")

        //Delegations should never be able to add comments
        cy.logout()
        cy.login("ARM",'1234')
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1').should('not.contain', "Add comment")
        cy.get('#feedback-tbody-1 .add-comment-button').should('not.exist')

        // close (org_comment) feedbacks for question
        cy.logout()
        cy.login('admin', '1234')
        cy.visit("control/cockpit")
        cy.get("#id_question_set-1-feedback_status").select("Open")
        cy.get("#submit-id-submit").click()

        //Add Comment
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 #add-comment-1').click()
        cy.wait("@getCommentModal")

        cy.get('#feedback-modal').should('be.visible')
        cy.wait(500)
        cy.get('#feedback-modal #id_comment').clear().type('Some comment2')
        cy.get('#feedback-modal [type="submit"]').click()
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(7)').contains("Some comment2")
        //Update Comment
        cy.get('#feedback-tbody-1 #add-comment-1').click()
        cy.wait("@getCommentModal")

        cy.get('#feedback-modal').should('be.visible')
        cy.get('#feedback-modal #id_comment').should('have.value', 'Some comment2')
        cy.wait(500)
        cy.get('#feedback-modal #id_comment').clear().type('Another comment2')
        cy.get('#feedback-modal [type="submit"]').click()
        cy.wait("@getFeedbackTable")
        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(7)').contains("Another comment2")
        //Check on exam view
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal").should("be.visible")
        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(1) > :nth-child(4)").contains("Another comment2")

        //Delegations should never be able to add comments
        cy.logout()
        cy.login("ARM",'1234')
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1').should('not.contain', "Add comment")
        cy.get('#feedback-tbody-1 .add-comment-button').should('not.exist')

        // Switch phase
        // Translation (exam.feedback = Exam.FEEDBACK_READONLY)
        cy.logout()
        cy.login('admin','1234')
        cy.getExamPhaseByName('Theory', "Translation").then(cy.switchExamPhase)
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1').should('not.contain', "Add comment")
        cy.get('#feedback-tbody-1 .add-comment-button').should('not.exist')

        cy.logout()
        cy.login("ARM", '1234')
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1').should('not.contain', "Add comment")
        cy.get('#feedback-tbody-1 .add-comment-button').should('not.exist')

    })

    it('Test Status', function(){
        cy.login("ARM",'1234')
        //Feedbacks are closed on default. No user should be able to edit the status
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        // Check if table has loaded (as we are checking for non-existence later)
        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(3)').contains('Armenia')
        cy.get('#feedback-tbody-1 button.dropdown-toggle').should('not.exist')
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")
        //Check if modal content has been loaded.
        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(1) > :nth-child(3)").contains("Armenia")
        cy.get("#feedback-modal #feedback-tbody-1 button.dropdown-toggle").should('not.exist')

        cy.logout()
        cy.login('admin', '1234')
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(3)').contains('Armenia')
        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(3)').contains('Armenia')
        cy.get('#feedback-tbody-1 button.dropdown-toggle').should('not.exist')
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(1) > :nth-child(3)").contains("Armenia")
        cy.get("#feedback-modal #feedback-tbody-1 button.dropdown-toggle").should('not.exist')

        // open feedbacks for question
        cy.visit("control/cockpit")
        cy.get("#id_question_set-1-feedback_status").select("Open")
        cy.get("#submit-id-submit").click()

        //Delegations should not be able to change the status, independent of the settings
        cy.logout()
        cy.login("ARM",'1234')
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(3)').contains('Armenia')
        cy.get('#feedback-tbody-1 button.dropdown-toggle').should('not.exist')
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(1) > :nth-child(3)").contains("Armenia")
        cy.get("#feedback-modal #feedback-tbody-1 button.dropdown-toggle").should('not.exist')

        //Organizers should be able to edit statuses
        cy.logout()
        cy.login('admin', '1234')
        //Change status on feedback list.
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(3)').contains('Armenia')
        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(2) button').should('not.contain', 'Implemented')
        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(2) button.dropdown-toggle').click()
        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(2)').contains("Implemented").click()
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(2) button').should('contain', 'Implemented').and('not.contain', 'Submitted')
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(1) > :nth-child(3)").contains("Armenia")
        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(1) > :nth-child(2) button").should('contain', 'Implemented').and('not.contain', 'Submitted')
        //Change status in exam view
        cy.get('#feedback-tbody-1 > :nth-child(2) > :nth-child(2) button').should('not.contain', 'Scheduled for voting')
        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(2) > :nth-child(2) button.dropdown-toggle").click()
        cy.get('#feedback-modal #feedback-tbody-1 > :nth-child(2) > :nth-child(2)').contains("Scheduled for voting").click()
        cy.wait("@getFeedbackPartial")

        cy.get('#feedback-modal #feedback-tbody-1 > :nth-child(2) > :nth-child(2) button').should('contain', 'Scheduled for voting').and('not.contain', 'Submitted')
        //Check in feedback list
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(3)').contains('Armenia')
        cy.get('#feedback-tbody-1 > :nth-child(2) > :nth-child(2) button').should('contain', 'Scheduled for voting').and('not.contain', 'Submitted')

        // close (org_comment) feedbacks for question
        cy.visit("control/cockpit")
        cy.get("#id_question_set-1-feedback_status").select("Closed, Organizer can still comment.")
        cy.get("#submit-id-submit").click()

        //Admins should still be able to edit statuses
        //Change status on feedback list.
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(3)').contains('Armenia')
        cy.get('#feedback-tbody-1 > :nth-child(3) > :nth-child(2) button').should('not.contain', 'Settled after voting')
        cy.get('#feedback-tbody-1 > :nth-child(3) > :nth-child(2) button.dropdown-toggle').click()
        cy.get('#feedback-tbody-1 > :nth-child(3) > :nth-child(2)').contains("Settled after voting").click()
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 > :nth-child(3) > :nth-child(2) button').should('contain', 'Settled after voting').and('not.contain', 'Submitted')
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(1) > :nth-child(3)").contains("Armenia")
        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(3) > :nth-child(2) button").should('contain', 'Settled after voting').and('not.contain', 'Submitted')
        //Change status in exam view
        cy.get('#feedback-modal #feedback-tbody-1 > :nth-child(4) > :nth-child(2) button').should('not.contain', 'Withdrawn')
        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(4) > :nth-child(2) button.dropdown-toggle").click()
        cy.get('#feedback-modal #feedback-tbody-1 > :nth-child(4) > :nth-child(2)').contains("Withdrawn").click()
        cy.wait("@getFeedbackPartial")

        cy.get('#feedback-modal #feedback-tbody-1 > :nth-child(4) > :nth-child(2) button').should('contain', 'Withdrawn').and('not.contain', 'Submitted')
        //Check in feedback list
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(3)').contains('Armenia')
        cy.get('#feedback-tbody-1 > :nth-child(4) > :nth-child(2) button').should('contain', 'Withdrawn').and('not.contain', 'Submitted')

        cy.logout()
        cy.login("ARM",'1234')
        //Delegations should not be able to change satuses
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(3)').contains('Armenia')
        cy.get('#feedback-tbody-1 button.dropdown-toggle').should('not.exist')
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(1) > :nth-child(3)").contains("Armenia")
        cy.get("#feedback-modal #feedback-tbody-1 button.dropdown-toggle").should('not.exist')
        //Check statuses shown to delegation
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(3)').contains('Armenia')
        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(2)').should('contain', 'Implemented').and('not.contain', 'Submitted')
        cy.get('#feedback-tbody-1 > :nth-child(2) > :nth-child(2)').should('contain', 'Scheduled for voting').and('not.contain', 'Submitted')
        cy.get('#feedback-tbody-1 > :nth-child(3) > :nth-child(2)').should('contain', 'Settled after voting').and('not.contain', 'Submitted')
        cy.get('#feedback-tbody-1 > :nth-child(4) > :nth-child(2)').should('contain', 'Withdrawn').and('not.contain', 'Submitted')

        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(1) > :nth-child(3)").contains("Armenia")
        cy.get('#feedback-modal #feedback-tbody-1 > :nth-child(1) > :nth-child(2)').should('contain', 'Implemented').and('not.contain', 'Submitted')
        cy.get('#feedback-modal #feedback-tbody-1 > :nth-child(2) > :nth-child(2)').should('contain', 'Scheduled for voting').and('not.contain', 'Submitted')
        cy.get('#feedback-modal #feedback-tbody-1 > :nth-child(3) > :nth-child(2)').should('contain', 'Settled after voting').and('not.contain', 'Submitted')
        cy.get('#feedback-modal #feedback-tbody-1 > :nth-child(4) > :nth-child(2)').should('contain', 'Withdrawn').and('not.contain', 'Submitted')

        // Switch phase
        // Translation (exam.feedback = Exam.FEEDBACK_READONLY)
        cy.logout()
        cy.login('admin','1234')
        cy.getExamPhaseByName('Theory', "Translation").then(cy.switchExamPhase)

        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(3)').contains('Armenia')
        cy.get('#feedback-tbody-1 button.dropdown-toggle').should('not.exist')
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(1) > :nth-child(3)").contains("Armenia")
        cy.get("#feedback-modal #feedback-tbody-1 button.dropdown-toggle").should('not.exist')

        cy.logout()
        cy.login('admin', '1234')
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 > :nth-child(1) > :nth-child(3)').contains('Armenia')
        cy.get('#feedback-tbody-1 button.dropdown-toggle').should('not.exist')
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get("#feedback-modal #feedback-tbody-1 > :nth-child(1) > :nth-child(3)").contains("Armenia")
        cy.get("#feedback-modal #feedback-tbody-1 button.dropdown-toggle").should('not.exist')

    })

    it('Test Dis-/Like', function() {
        cy.login("ARM",'1234')
        //Feedbacks are closed on default. No user should be able to dis-/like
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        //Note: both like and dislike have class feedback-like
        cy.get('#feedback-tbody-1 :nth-child(1) > :nth-child(9) span.feedback-like').should('have.class', 'disabled')
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get('#feedback-modal #feedback-tbody-1 :nth-child(1) > :nth-child(6) span.feedback-like').should('have.class', 'disabled')

        cy.logout()
        cy.login('admin', '1234')
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 :nth-child(1) > :nth-child(9) span.feedback-like').should('have.class', 'disabled')
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get('#feedback-modal #feedback-tbody-1 :nth-child(1) > :nth-child(6) span.feedback-like').should('have.class', 'disabled')

        // open feedbacks for question
        cy.visit("control/cockpit")
        cy.get("#id_question_set-1-feedback_status").select("Open")
        cy.get("#submit-id-submit").click()

        // organizers should never be able to edit likes
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 :nth-child(1) > :nth-child(9) span.feedback-like').should('have.class', 'disabled')
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get('#feedback-modal #feedback-tbody-1 :nth-child(1) > :nth-child(6) span.feedback-like').should('have.class', 'disabled')

        //Delegations should now be able to add likes
        cy.logout()
        cy.login("ARM",'1234')
        //Feedbacks are closed on default. No user should be able to dis-/like
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        //Add like
        cy.get('#feedback-tbody-1 :nth-child(1) > :nth-child(9) span.feedback-like-trigger').should('not.have.class', 'disabled')
        cy.get('#feedback-tbody-1 :nth-child(1) > :nth-child(9) span.feedback-like-trigger').click()
        cy.wait("@getFeedbackTable")

        //Check whether both buttons are disabled
        cy.get('#feedback-tbody-1 :nth-child(1) > :nth-child(9) span.feedback-like').should('have.class', 'disabled')
        // Check country code in button
        cy.get('#feedback-tbody-1 :nth-child(1) > :nth-child(9) span.feedback-like-trigger').should('contain', "ARM")
        //Add unlike
        cy.get('#feedback-tbody-1 :nth-child(2) > :nth-child(9) span.feedback-unlike-trigger').should('not.have.class', 'disabled')
        cy.get('#feedback-tbody-1 :nth-child(2) > :nth-child(9) span.feedback-unlike-trigger').click()
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 :nth-child(2) > :nth-child(9) span.feedback-like').should('have.class', 'disabled')
        cy.get('#feedback-tbody-1 :nth-child(2) > :nth-child(9) span.feedback-unlike-trigger').should('contain', "ARM")
        //Switch to exam view
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        //Check un-/likes entered before
        cy.get('#feedback-modal #feedback-tbody-1 :nth-child(1) > :nth-child(6) span.feedback-like').should('have.class', 'disabled')
        cy.get('#feedback-modal #feedback-tbody-1 :nth-child(1) > :nth-child(6) span.feedback-like-trigger').should('contain', "ARM")
        cy.get('#feedback-modal #feedback-tbody-1 :nth-child(2) > :nth-child(6) span.feedback-like').should('have.class', 'disabled')
        cy.get('#feedback-modal #feedback-tbody-1 :nth-child(2) > :nth-child(6) span.feedback-unlike-trigger').should('contain', "ARM")
        //Add like
        cy.get('#feedback-modal #feedback-tbody-1 :nth-child(3) > :nth-child(6) span.feedback-like-trigger').should('not.have.class', 'disabled')
        cy.get('#feedback-modal #feedback-tbody-1 :nth-child(3) > :nth-child(6) span.feedback-like-trigger').click()
        cy.wait("@getFeedbackPartial")

        cy.get('#feedback-modal #feedback-tbody-1 :nth-child(3) > :nth-child(6) span.feedback-like').should('have.class', 'disabled')
        cy.get('#feedback-modal #feedback-tbody-1 :nth-child(3) > :nth-child(6) span.feedback-like-trigger').should('contain', "ARM")
        //Add unlike
        cy.get('#feedback-modal #feedback-tbody-1 :nth-child(4) > :nth-child(6) span.feedback-unlike-trigger').should('not.have.class', 'disabled')
        cy.get('#feedback-modal #feedback-tbody-1 :nth-child(4) > :nth-child(6) span.feedback-unlike-trigger').click()
        cy.wait("@getFeedbackPartial")

        cy.get('#feedback-modal #feedback-tbody-1 :nth-child(4) > :nth-child(6) span.feedback-like').should('have.class', 'disabled')
        cy.get('#feedback-modal #feedback-tbody-1 :nth-child(4) > :nth-child(6) span.feedback-unlike-trigger').should('contain', "ARM")
        //Crosscheck on feedback list
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 :nth-child(3) > :nth-child(9) span.feedback-like').should('have.class', 'disabled')
        cy.get('#feedback-tbody-1 :nth-child(3) > :nth-child(9) span.feedback-like-trigger').should('contain', "ARM")
        cy.get('#feedback-tbody-1 :nth-child(4) > :nth-child(9) span.feedback-like').should('have.class', 'disabled')
        cy.get('#feedback-tbody-1 :nth-child(4) > :nth-child(9) span.feedback-unlike-trigger').should('contain', "ARM")

        // close (org_comment) feedbacks for question
        cy.logout()
        cy.login("admin", "1234")
        cy.visit("control/cockpit")
        cy.get("#id_question_set-1-feedback_status").select("Open")
        cy.get("#submit-id-submit").click()

        // organizers should never be able to edit likes
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 :nth-child(1) > :nth-child(9) span.feedback-like').should('have.class', 'disabled')
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get('#feedback-modal #feedback-tbody-1 :nth-child(1) > :nth-child(6) span.feedback-like').should('have.class', 'disabled')
        //Feedback should be disabled again for delegations
        cy.logout()
        cy.login("ARM",'1234')
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 :nth-child(1) > :nth-child(9) span.feedback-like').should('have.class', 'disabled')
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get('#feedback-modal #feedback-tbody-1 :nth-child(1) > :nth-child(6) span.feedback-like').should('have.class', 'disabled')

        // Switch phase
        // Translation (exam.feedback = Exam.FEEDBACK_READONLY)
        cy.logout()
        cy.login('admin','1234')
        cy.getExamPhaseByName('Theory', "Translation").then(cy.switchExamPhase)

        // organizers should never be able to edit likes
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 :nth-child(1) > :nth-child(9) span.feedback-like').should('have.class', 'disabled')
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get('#feedback-modal #feedback-tbody-1 :nth-child(1) > :nth-child(6) span.feedback-like').should('have.class', 'disabled')
        //Feedback should be disabled again for delegations
        cy.logout()
        cy.login("ARM",'1234')
        cy.visit("exam/feedbacks/list/1")
        cy.wait("@getFeedbackTable")

        cy.get('#feedback-tbody-1 :nth-child(1) > :nth-child(9) span.feedback-like').should('have.class', 'disabled')
        cy.visit("exam/view/1/question/2")
        cy.get("#q0_ti1").click()
        cy.wait("@getFeedbackPartial")

        cy.get('#feedback-modal #feedback-tbody-1 :nth-child(1) > :nth-child(6) span.feedback-like').should('have.class', 'disabled')



    })

})
