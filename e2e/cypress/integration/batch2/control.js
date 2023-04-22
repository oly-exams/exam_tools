

function check_exam_settings(settings, selector){
    cy.get(selector + ' > tbody').children().should('have.length', settings.length)
    settings.forEach(function(elem, idx) {
        cy.get( selector + ' > tbody > :nth-child(' + String(idx+1) +') > :nth-child(1)').should('contain', elem[0])
        cy.get( selector + ' > tbody > :nth-child(' + String(idx+1) +') > :nth-child(2)').should('contain', elem[1])
    });
}

function check_changelog(settings, selector){
    cy.get(selector + ' > tbody').children().should('have.length', settings.length)
    settings.forEach(function(elem, idx) {
        cy.get( selector + ' > tbody > :nth-child(' + String(idx+1) +') > :nth-child(1)').should('contain', elem[0])
        cy.get( selector + ' > tbody > :nth-child(' + String(idx+1) +') > :nth-child(2)').should('contain', elem[1])
        cy.get( selector + ' > tbody > :nth-child(' + String(idx+1) +') > :nth-child(3)').should('contain', elem[2])
    });
}

describe('Control', function() {


    before(() => {
        // runs once before all tests in the block
        cy.beforeAllDBInit()
    })

    beforeEach(() => {
        // this runs prior to every test
        cy.beforeEachDBInit()
    })

    it('Test Switch state', function() {
        cy.login('admin','1234')
        cy.visit('control/cockpit')
        //check initial phase
        cy.get('#current-phase-panel .panel-heading').should("contain", "Discussion (Translation)")
        var settings = [
            ["Exam Visibility", "Boardmeeting + Organizer + 2nd level support"],
            ["Can Translate", "Boardmeeting members + organizers"],
            ["Feedback", "Can be opened"],
            ["Submission Printing", "No, not visible"],
            ["Answer Sheet Manual Scan Upload", "Not possible"],
            ["Delegation Scan Access", "No"],
            ["Organizer can see delegation marks", "In moderation and when marks are finalized"],
            ["Organizers can edit marks", "No"],
            ["Delegations can see organizer marks", "No"],
            ["Delegation marking actions", "Nothing"],
            ["Moderation", "Not open"],
        ]
        check_exam_settings(settings, '#current-phase-panel > table');
        cy.get('#current-phase-panel .panel-body').should('contain', "The Exam is visible to the delegations and Feedback can be opened. Translations are possible.")
        cy.get('#current-phase-column form').should('contain', "Feedback")
        cy.get('#switch-phase-5').should('not.exist')

        //Check history
        cy.get('#show-history-button').click()
        cy.get('#history-modal').should('be.visible')
        cy.get('#history-modal .modal-body').children().should('have.length', 2)
        cy.get('#history-modal .modal-body > :nth-child(1) .panel-heading').should('contain', 'Discussion (Translation)')
        var changed_settings = [
            ["Exam Visibility", "Organizer + 2nd level support", "Boardmeeting + Organizer + 2nd level support"],
            ["Can Translate", "Nobody", "Boardmeeting members + organizers"],
            ["Feedback", "Read only", "Can be opened"],
        ]
        var unchanged_settings = [
            ["Submission Printing", "No, not visible"],
            ["Answer Sheet Manual Scan Upload", "Not possible"],
            ["Delegation Scan Access", "No"],
            ["Organizer can see delegation marks", "In moderation and when marks are finalized"],
            ["Organizers can edit marks", "No"],
            ["Delegations can see organizer marks", "No"],
            ["Delegation marking actions", "Nothing"],
            ["Moderation", "Not open"],
        ]
        check_exam_settings(unchanged_settings, '#history-modal .modal-body > :nth-child(1) .phase-settings')
        check_changelog(changed_settings, '#history-modal .modal-body > :nth-child(1) .phase-changelog')
        cy.get('#history-modal button.close').click()

        //Check available phase panel
        cy.get('#phase-panel-12 .panel-heading').should('contain', 'Moderation')
        cy.get('#12-collapse-table').should('not.be.visible')
        cy.get('#phase-panel-12 .collapse-toggle').click()
        cy.get('#12-collapse-table').should('be.visible')
        var settings_moderation = [
            ["Exam Visibility", "Boardmeeting + Organizer + 2nd level support"],
            ["Can Translate", "Nobody"],
            ["Feedback", "Invisible"],
            ["Submission Printing", "No, not visible"],
            ["Answer Sheet Manual Scan Upload", "Not possible"],
            ["Delegation Scan Access", "Participant answer"],
            ["Organizer can see delegation marks", "In moderation and when marks are finalized"],
            ["Organizers can edit marks", "No"],
            ["Delegations can see organizer marks", "Yes"],
            ["Delegation marking actions", "Can enter, submit and finalize marks"],
            ["Moderation", "Can be moderated"],
        ]
        check_exam_settings(settings_moderation, '#phase-panel-12 table.phase-settings');
        cy.get('#phase-panel-12 .panel-body').should('contain', "Moderation is enabled.")
        cy.get('#phase-panel-12 .panel-footer .list-group .list-group-item-warning').should('contain', "Markings submitted for Theory:")
        cy.get('#phase-panel-12 .panel-footer .list-group .list-group-item-warning').invoke("data", "content").should('contain', "Unsubmitted Markings! The following markings have not yet been submitted: CHE - Question: Two Problems in Mechanics - Answer Sheet ARM - Question: Nonlinear Dynamics in Electric Circuits - Answer Sheet AUS - Question: Nonlinear Dynamics in Electric Circuits - Answer Sheet CHE - Question: Nonlinear Dynamics in Electric Circuits - Answer Sheet")


        //Check switch modal
        cy.get('#switch-phase-12').click()
        cy.get('#switch-phase-modal').should('be.visible')
        cy.get('#switch-phase-modal #modalLabel').should('contain', 'Theory').and('contain', 'Moderation')
        cy.get('#switch-phase-modal .modal-body').should('contain', 'Moderation is enabled.')
        var changed_settings = [
            ["Can Translate", "Boardmeeting members + organizers", "Nobody"],
            ["Feedback", "Can be opened", "Invisible"],
            ["Delegation Scan Access", "No", "Participant answer"],
            ["Delegations can see organizer marks", "No", "Yes"],
            ["Delegation marking actions", "Nothing", "Can enter, submit and finalize marks"],
            ["Moderation", "Not open", "Can be moderated"],
        ]
        var unchanged_settings = [
            ["Exam Visibility", "Boardmeeting + Organizer + 2nd level support"],
            ["Submission Printing", "No, not visible"],
            ["Answer Sheet Manual Scan Upload", "Not possible"],
            ["Organizer can see delegation marks", "In moderation and when marks are finalized"],
            ["Organizers can edit marks", "No"],
        ]

        check_exam_settings(unchanged_settings, '#switch-phase-modal .phase-settings')
        check_changelog(changed_settings, '#switch-phase-modal .phase-changelog')
        cy.get('#switch-phase-modal .alert-warning').should('contain', 'Unsubmitted Markings! The following markings have not yet been submitted: CHE - Question: Two Problems in Mechanics - Answer Sheet ARM - Question: Nonlinear Dynamics in Electric Circuits - Answer Sheet AUS - Question: Nonlinear Dynamics in Electric Circuits - Answer Sheet CHE - Question: Nonlinear Dynamics in Electric Circuits - Answer Sheet')
        cy.get('#switch-phase-modal p.other-considerations').should('contain', 'Make sure all delegations submitted their marks.')

        //Switch
        cy.get('#switch-phase-modal #switch-phase-submit').click()
        cy.url().should('contain', 'changed-phase')
        cy.get('#alerts-container').should('contain', 'Changed phase to Moderation')

        //Check new current phase
        cy.get('#current-phase-panel .panel-heading').should("contain", "Moderation")
        // settings_moderation should be unchanged
        check_exam_settings(settings_moderation, '#current-phase-panel > table');
        cy.get('#current-phase-panel .panel-body').should('contain', "Moderation is enabled.")
        cy.get('#current-phase-column form').should('not.exist')
        cy.get('#switch-phase-12').should('not.exist')

        // check new history entry
        cy.get('#show-history-button').click()
        cy.get('#history-modal').should('be.visible')
        cy.get('#history-modal .modal-body').children().should('have.length', 3)
        cy.get('#history-modal .modal-body > :nth-child(1) .panel-heading').should('contain', 'Moderation').and('contain', 'admin at')
        //(un)changed settings should stay the same
        check_exam_settings(unchanged_settings, '#history-modal .modal-body > :nth-child(1) .phase-settings')
        check_changelog(changed_settings, '#history-modal .modal-body > :nth-child(1)  .phase-changelog')
    })

    it("Test Delegation Phase View", function(){
        cy.login("ARM", "1234")
        cy.visit("/")
        cy.get('#exam-summary-container #phase-summary-parent > :nth-child(1)').should('contain', 'Theory').and('contain', 'Discussion (Translation)')
        cy.get('#phase-summary-parent > :nth-child(1) #phase-summary-1').should('not.be.visible')
        cy.get('#phase-summary-parent > :nth-child(1) .panel-heading').click()
        cy.get('#phase-summary-parent > :nth-child(1) #phase-summary-1').should('be.visible')
        cy.get('#phase-summary-1').should('contain', 'In this phase feedback can be entered. You can also start the translation.')

        cy.logout()
        cy.login("admin", "1234")
        //Switch to Preparation (Editing) where visibility=ORGAS_ONLY
        cy.getExamPhaseByName('Theory', "Preparation (Editing)").then(cy.switchExamPhase)

        cy.visit("/")
        cy.get('#exam-summary-container #phase-summary-parent > :nth-child(1)').should('contain', 'Theory').and('contain', 'Preparation (Editing)')

        // No phases should be visible for delegations
        cy.logout()
        cy.login("ARM", "1234")
        cy.visit("/")
        cy.get('#exam-summary-container').should('have.text', '\n\nNo exams available.\n\n')
    })

    it("Test Permissions", function(){
        cy.login("AUS",'1234')
        // Check whether a delegation can access the cockpit
        cy.visit('control/cockpit')
        cy.url().should('contain', 'accounts/login/?next=/control/cockpit')
    })

})
