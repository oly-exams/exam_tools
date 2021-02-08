
import * as marking_helpers from '../../support/marking_test_helpers.js'

describe('Marking', function () {

    before(() => {
        // runs once before all tests in the block
        cy.beforeAllDBInit()
    })

    beforeEach(() => {
        // this runs prior to every test
        cy.beforeEachDBInit()
    })

    it("Test General Visibility (Translation phase)", function () {

        cy.login('CHE', '1234')
        marking_helpers.test_marking_summary_visibility(false)
        marking_helpers.test_final_points_visibility(marking_helpers.CHE_ppnts_final)
        marking_helpers.test_delegation_view_edit_status(marking_helpers.CHE_ppnt_ids, 404)

        cy.logout()
        cy.login('ARM', '1234')
        marking_helpers.test_marking_summary_visibility(false)
        marking_helpers.test_final_points_visibility(marking_helpers.ARM_ppnts_final)
        marking_helpers.test_delegation_view_edit_status(marking_helpers.ARM_ppnt_ids, 404)

        cy.logout()
        cy.login('AUS', '1234')
        marking_helpers.test_marking_summary_visibility(false)
        marking_helpers.test_final_points_visibility(marking_helpers.AUS_ppnts_final)
        marking_helpers.test_delegation_view_edit_status(marking_helpers.AUS_ppnt_ids, 404)

        cy.logout()
        cy.login('AUT', '1234')
        marking_helpers.test_marking_summary_visibility(false)
        marking_helpers.test_final_points_visibility(marking_helpers.AUT_ppnts_final)
        marking_helpers.test_delegation_view_edit_status(marking_helpers.AUT_ppnt_ids, 404)

        cy.logout()
        cy.login("marker", '1234')
        marking_helpers.test_staff_edit_status(3, 4, marking_helpers.CHE_ppnt_ids, 404)
        marking_helpers.test_staff_edit_status(3, 1, marking_helpers.ARM_ppnt_ids, 404)
        marking_helpers.test_staff_edit_status(3, 2, marking_helpers.AUS_ppnt_ids, 404)
        marking_helpers.test_staff_edit_status(3, 3, marking_helpers.AUT_ppnt_ids, 404)

    })

    it("Test General Visibility (Organizer Marking phase)", function () {
        cy.login('admin', '1234')
        // orga Marking
        cy.getExamPhaseByName('Theory', "Organizer Marking").then(cy.switchExamPhase)

        //checking only one delegation for time reasons
        cy.logout()
        cy.login('CHE', '1234')
        marking_helpers.test_marking_summary_visibility(false)
        marking_helpers.test_delegation_view_edit_status(marking_helpers.CHE_ppnt_ids, 404)

        //checking only that we can visit without error
        cy.logout()
        cy.login("marker", '1234')
        //CHE OPEN
        //Normal marking
        marking_helpers.test_staff_edit_status(3, 4, marking_helpers.CHE_ppnt_ids, 200)

        //ARM SUBMITTED_FOR_MODERATION
        marking_helpers.test_staff_edit_status(3, 1, marking_helpers.ARM_ppnt_ids, 200)

        // AUS LOCKED_BY_MOD
        marking_helpers.test_staff_edit_status(3, 2, marking_helpers.AUS_ppnt_ids, 200)

        //AUT FINAL
        marking_helpers.test_staff_edit_status(3, 3, marking_helpers.AUT_ppnt_ids, 404)

    })

    it("Test General Visibility (Delegation Marking phase)", function () {
        cy.login('admin', '1234')
        // deleg marking
        cy.getExamPhaseByName('Theory', "Delegation Marking").then(cy.switchExamPhase)

        cy.logout()
        cy.login('CHE', '1234')
        marking_helpers.test_marking_summary_visibility(true, marking_helpers.CHE_ppnts_editable)
        marking_helpers.test_summary_action_content([marking_helpers.submit_action,])
        marking_helpers.test_final_points_visibility(marking_helpers.CHE_ppnts_final)
        marking_helpers.test_delegation_view_edit_status(marking_helpers.CHE_ppnt_ids, 200)

        cy.logout()
        cy.login('ARM', '1234')
        marking_helpers.test_marking_summary_visibility(true, marking_helpers.ARM_ppnts_viewable)
        marking_helpers.test_summary_action_content([marking_helpers.accept_action,])
        marking_helpers.test_final_points_visibility(marking_helpers.ARM_ppnts_final)
        marking_helpers.test_delegation_view_edit_status(marking_helpers.ARM_ppnt_ids, 404)

        cy.logout()
        cy.login('AUS', '1234')
        marking_helpers.test_marking_summary_visibility(true, marking_helpers.AUS_ppnts_viewable)
        marking_helpers.test_summary_action_content([marking_helpers.sign_off_action,])
        marking_helpers.test_final_points_visibility(marking_helpers.AUS_ppnts_final)
        marking_helpers.test_delegation_view_edit_status(marking_helpers.AUS_ppnt_ids, 404)

        cy.logout()
        cy.login('AUT', '1234')
        marking_helpers.test_marking_summary_visibility(true, marking_helpers.AUT_ppnts_viewable)
        marking_helpers.test_summary_action_content([marking_helpers.finalized_action,])
        marking_helpers.test_final_points_visibility(marking_helpers.AUT_ppnts_final)
        marking_helpers.test_delegation_view_edit_status(marking_helpers.AUT_ppnt_ids, 404)

        //checking only that we can visit without error
        cy.logout()
        cy.login("marker", '1234')
        //CHE OPEN
        //Normal marking
        marking_helpers.test_staff_edit_status(3, 4, marking_helpers.CHE_ppnt_ids, 200)

        //ARM SUBMITTED_FOR_MODERATION
        // Now markers can only edit unsubmitted marks
        marking_helpers.test_staff_edit_status(3, 1, marking_helpers.ARM_ppnt_ids, 404)

        // AUS LOCKED_BY_MOD
        // Now markers can only edit unsubmitted marks
        marking_helpers.test_staff_edit_status(3, 2, marking_helpers.AUS_ppnt_ids, 404)

        //AUT FINAL
        marking_helpers.test_staff_edit_status(3, 3, marking_helpers.AUT_ppnt_ids, 404)
    })

    it("Test General Visibility (Delegation Marking (Submit only) phase)", function () {
        cy.login('admin', '1234')
        // deleg marking (submit only)
        cy.getExamPhaseByName('Theory', "Delegation Marking (Submit only)").then(cy.switchExamPhase)

        cy.logout()
        cy.login('CHE', '1234')
        marking_helpers.test_marking_summary_visibility(true, marking_helpers.CHE_ppnts_editable)
        marking_helpers.test_summary_action_content([marking_helpers.submit_action,])
        // Only test final points for one deleg, the main difference are the actions
        marking_helpers.test_final_points_visibility(marking_helpers.CHE_ppnts_final)
        marking_helpers.test_delegation_view_edit_status(marking_helpers.CHE_ppnt_ids, 200)

        cy.logout()
        cy.login('ARM', '1234')
        marking_helpers.test_marking_summary_visibility(true, marking_helpers.ARM_ppnts_viewable)
        marking_helpers.test_summary_action_content_none(1)
        marking_helpers.test_delegation_view_edit_status(marking_helpers.ARM_ppnt_ids, 404)

        cy.logout()
        cy.login('AUS', '1234')
        marking_helpers.test_marking_summary_visibility(true, marking_helpers.AUS_ppnts_viewable)
        marking_helpers.test_summary_action_content_none(1)
        marking_helpers.test_delegation_view_edit_status(marking_helpers.AUS_ppnt_ids, 404)

        cy.logout()
        cy.login('AUT', '1234')
        marking_helpers.test_marking_summary_visibility(true, marking_helpers.AUT_ppnts_viewable)
        marking_helpers.test_summary_action_content([marking_helpers.finalized_action,])
        marking_helpers.test_delegation_view_edit_status(marking_helpers.AUT_ppnt_ids, 404)

        //checking only that we can visit without error
        cy.logout()
        cy.login("marker", '1234')
        //CHE OPEN
        //Normal marking
        marking_helpers.test_staff_edit_status(3, 4, marking_helpers.CHE_ppnt_ids, 200)

        //ARM SUBMITTED_FOR_MODERATION
        // Now markers can only edit unsubmitted marks
        marking_helpers.test_staff_edit_status(3, 1, marking_helpers.ARM_ppnt_ids, 404)

        // AUS LOCKED_BY_MOD
        // Now markers can only edit unsubmitted marks
        marking_helpers.test_staff_edit_status(3, 2, marking_helpers.AUS_ppnt_ids, 404)

        //AUT FINAL
        marking_helpers.test_staff_edit_status(3, 3, marking_helpers.AUT_ppnt_ids, 404)
    })


    it("Test Marks Visibility  (Translation phase)", function () {
        // Testing only the first participant in each array, otherwise the test takes ~10min
        cy.login('CHE', '1234')
        marking_helpers.test_delegation_marks_view_all(marking_helpers.CHE_ppnt_ids.slice(0, 1), [0, 2], "-")

        cy.logout()
        cy.login('ARM', '1234')
        marking_helpers.test_delegation_marks_view_all(marking_helpers.ARM_ppnt_ids.slice(0, 1), [0, 2], "-")

        cy.logout()
        cy.login('AUS', '1234')
        marking_helpers.test_delegation_marks_view_all(marking_helpers.AUS_ppnt_ids.slice(0, 1), [0,], "-")

        cy.logout()
        cy.login('AUT', '1234')
        marking_helpers.test_delegation_marks_view_all(marking_helpers.AUT_ppnt_ids.slice(0, 1), [0,], "-")

        cy.logout()
        cy.login('marker', '1234')
        cy.wait(10)
        cy.visit('http://localhost:8000/marking/staff?version=F')
        marking_helpers.test_staff_summary_values(marking_helpers.staff_summary_deleg_entries_only_fin)
        cy.wait(10)
        cy.visit('http://localhost:8000/marking/staff?version=D')
        marking_helpers.test_staff_summary_values(marking_helpers.staff_summary_deleg_entries_only_fin)
    })

    it("Test Marks Visibility  (Organizer Marking phase)", function () {
        cy.login('admin', '1234')
        // orga Marking
        cy.getExamPhaseByName('Theory', "Organizer Marking").then(cy.switchExamPhase)

        // Test only one delegation for time reasons
        cy.logout()
        cy.login('ARM', '1234')
        marking_helpers.test_delegation_marks_view_all(marking_helpers.ARM_ppnt_ids.slice(0, 1), [0, 2], "-")

        cy.logout()
        cy.login('marker', '1234')
        cy.visit('http://localhost:8000/marking/staff?version=D')
        marking_helpers.test_staff_summary_values(marking_helpers.staff_summary_deleg_entries_only_fin)
    })

    it("Test Marks Visibility  (Delegation Marking phase)", function () {
        cy.login('admin', '1234')
        // deleg Marking
        cy.getExamPhaseByName('Theory', "Delegation Marking").then(cy.switchExamPhase)

        cy.logout()
        cy.login('CHE', '1234')
        marking_helpers.test_delegation_marks_view_all(marking_helpers.CHE_ppnt_ids.slice(0, 1), [0,], "-")

        cy.logout()
        cy.login('ARM', '1234')
        marking_helpers.test_delegation_marks_view_all(marking_helpers.ARM_ppnt_ids.slice(0, 1), [0,], "0.00")

        cy.logout()
        cy.login('marker', '1234')
        cy.visit('http://localhost:8000/marking/staff?version=D')
        marking_helpers.test_staff_summary_values(marking_helpers.staff_summary_deleg_entries_only_fin, "-")
    })

    it("Test Marks Visibility  (Delegation Marking (Submit only) phase)", function () {
        cy.login('admin', '1234')
        // deleg Marking (submit only)
        cy.getExamPhaseByName('Theory', "Delegation Marking (Submit only)").then(cy.switchExamPhase)

        cy.logout()
        cy.login('CHE', '1234')
        marking_helpers.test_delegation_marks_view_all(marking_helpers.CHE_ppnt_ids.slice(0, 1), [0,], "0.00")

        cy.logout()
        cy.login('ARM', '1234')
        marking_helpers.test_delegation_marks_view_all(marking_helpers.ARM_ppnt_ids.slice(0, 1), [0,], "0.00")

        cy.logout()
        cy.login('marker', '1234')
        // Marker should now be able to see more delegation marks
        cy.visit('http://localhost:8000/marking/staff?version=D')
        marking_helpers.test_staff_summary_values(marking_helpers.staff_summary_deleg_entries_subm_fin)
    })

})
