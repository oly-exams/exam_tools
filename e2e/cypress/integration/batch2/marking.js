

function check_permission_denied_redirect(paths) {
    paths.forEach(function (elem, idx) {
        cy.visit(elem)
        cy.url().should('contain', 'accounts/login/?next=' + elem)
    });
}

// Tests the visibility of the marking tab in the delegation marking summary
function test_marking_summary_visibility(should_exist, students = []) {
    cy.visit("/marking/")
    cy.get('a[href="#marking"]').click()
    cy.get("#marking").should('be.visible')
    if (should_exist) {
        cy.get('#marking .table-responsive').within(($table) => {
            students.forEach(function (elem, row) {
                cy.get("tbody >:nth-child(" + String(row + 2) + ")").within(($row) => {
                    cy.get(">:nth-child(1)").shouldHaveTrimmedText(elem[0])
                    elem.slice(1).forEach(function (btns, column) {
                        cy.get(">:nth-child(" + String(column + 2) + ")").within(($btngroup) => {
                            btns.forEach(function (btn, btnidx) {
                                cy.get(">:nth-child(" + String(btnidx + 1) + ") .btn").then(($btn) => {
                                    if (btn['disabled']) {
                                        cy.wrap($btn).should('have.attr', 'disabled');
                                    } else {
                                        cy.wrap($btn).should('not.have.attr', 'disabled');
                                    }
                                    cy.wrap($btn).should('contain', btn['text'])
                                })
                            });
                        })
                    });
                })
            });
        })
    } else {
        cy.get("#marking").children().should('have.length', 2)
        cy.get("#marking > :nth-child(2)").should('contain', "Marking is currently not enabled for any exam.")
    }
}

// Tests the content of the action button (e.g. submit, finalize, etc) in the delegation marking summary
function test_summary_action_content(actions) {
    cy.visit("/marking/")
    cy.get('a[href="#marking"]').click()
    cy.get("#marking").should('be.visible')
    cy.get('#marking .table-responsive tbody >:last-child').within(($footer) => {
        actions.forEach(function (action, idx) {
            cy.get(':nth-child(' + String(idx + 2) + ') .btn').then(($btn) => {
                if (action['disabled']) {
                    cy.wrap($btn).should('have.attr', 'disabled');
                } else {
                    cy.wrap($btn).should('not.have.attr', 'disabled');
                }
                cy.wrap($btn).should('contain', action['text'])
            })
        })
    })
}

// Tests the non-existence of the action button (e.g. submit, finalize, etc) in the delegation marking summary
function test_summary_action_content_none(action_pos) {
    cy.visit("/marking/")
    cy.get('a[href="#marking"]').click()
    cy.get("#marking").should('be.visible')
    cy.get('#marking .table-responsive tbody >:last-child').within(($footer) => {
        cy.get(':nth-child(' + String(action_pos + 1) + ') .btn').should('not.exist')
    })
}

// Tests the visibility of the final points in the delegation marking summary
function test_final_points_visibility(student_points) {
    cy.visit("/marking/")
    cy.get('a[href="#final-points"]').click()
    cy.get("#final-points").should('be.visible')
    student_points.forEach(function (elem, row) {
        elem.forEach(function (val, column) {
            cy.get("#final-points tbody >:nth-child(" + String(row + 2) + ") >:nth-child(" + String(column + 1) + ")").shouldHaveTrimmedText(val)
        });

    });

}

// Tests a selection of marking view/edit views for the delegations
function test_delegation_view_edit_status_question(question_id, student_ids = [], edit_status = 200, view_status = 200) {
    // editall
    cy.request({
        failOnStatusCode: false,
        url: '/marking/detail_all/question/' + question_id + '/edit',
    }).its("status").should('eq', edit_status)
    // viewall
    cy.request({
        failOnStatusCode: false,
        url: '/marking/detail_all/question/' + question_id,
    }).its("status").should('eq', view_status)

    student_ids.forEach(function (id, idx) {
        // edit
        cy.request({
            failOnStatusCode: false,
            url: '/marking/detail/' + id + '/question/' + question_id + '/edit',
        }).its("status").should('eq', edit_status)
        // view
        cy.request({
            failOnStatusCode: false,
            url: '/marking/detail/' + id + '/question/' + question_id,
        }).its("status").should('eq', view_status)
    });

}
// dito with a fixed question
function test_delegation_view_edit_status(student_ids = [], edit_status = 200, view_status = 200) {
    // Check only one question
    var question_ids = [3,]
    question_ids.forEach(function (qid, idx) {
        test_delegation_view_edit_status_question(qid, student_ids, edit_status, view_status)
    });
}

// Tests a selection of marking edit views for the markers
function test_staff_edit_status(question_id, delegation_id, student_ids = [], status = 404) {
    // editall
    cy.request({
        failOnStatusCode: false,
        url: '/marking/official/question/' + question_id + '/delegation/' + delegation_id,
    }).its("status").should('eq', status)

    student_ids.forEach(function (id, idx) {
        // official
        cy.request({
            failOnStatusCode: false,
            url: '/marking/staff/vO/student/' + id + '/question/' + question_id + '/edit',
        }).its("status").should('eq', status)
        // delegation
        cy.request({
            failOnStatusCode: false,
            url: '/marking/staff/vD/student/' + id + '/question/' + question_id + '/edit',
        }).its("status").should('eq', 404)
        // final
        cy.request({
            failOnStatusCode: false,
            url: '/marking/staff/vF/student/' + id + '/question/' + question_id + '/edit',
        }).its("status").should('eq', 404)
    });

}


// Sets the value of a points form field
function edit_point_form(stud_id, field_id, points){
    if(stud_id >= 0){
        cy.get("#id_Stud-"+stud_id+"-"+field_id+"-points").clear().type(points)
    }else{
        cy.get("#id_form-"+field_id+"-points").clear().type(points)
    }
}
// Checks the value of a points form field
function check_point_form(stud_id, field_id, points){
    if(stud_id >= 0){
        cy.get("#id_Stud-"+stud_id+"-"+field_id+"-points").should('have.value', points)
    }else{
        cy.get("#id_form-"+field_id+"-points").should('have.value', points)
    }
}
// Checks error messages of a points form field
function check_point_form_error(stud_id, field_id, should_have_err=true, err_msg="", check_error_class=true){
    if(should_have_err){
        if(stud_id >= 0){
            if(check_error_class){
                cy.get("#id_Stud-"+stud_id+"-"+field_id+"-points").parent().should('have.class', 'has-error')
            }
            cy.get("#id_Stud-"+stud_id+"-"+field_id+"-points").parent().find('li').should("contain", err_msg)
        }else{
            if(check_error_class){
                cy.get("#id_form-"+field_id+"-points").parent().should('have.class', 'has-error')
            }
            cy.get("#id_form-"+field_id+"-points").parent().find('li').should("contain", err_msg)
        }
    }else{
        if(stud_id >= 0){
            cy.get("#id_Stud-"+stud_id+"-"+field_id+"-points").parent().should('not.have.class', 'has-error')
        }else{
            cy.get("#id_form-"+field_id+"-points").parent().should('not.have.class', 'has-error')
        }
    }
}

// Checks the points shown in the delegation view and viewall views
function check_delegation_points_view(column, points){
    cy.get("#points-table tbody").within(($tbody)=>{
        points.forEach(function(elem, idx){
            cy.get('tr').eq(idx).find('td').eq(column).shouldHaveTrimmedText(elem)
        });
    })
}

// Checks that all points in column have value in the delegation view and viewall views
function check_delegation_points_view_value(column, value="-"){
    cy.get("#points-table tbody").within(($tbody)=>{
        cy.get('tr').each(($tr)=>{
            cy.wrap($tr).find('td').eq(column).shouldHaveTrimmedText(value)
        })
    })
}

// Tests all columns for students for value in the delegation view and viewall views
// (Note that stud_ids needs to contain all students of a delegation)
function test_delegation_marks_view_all(stud_ids, columns, value){
    cy.visit("/marking/detail_all/question/3")
    cy.wait(10)
    cy.wrap(stud_ids).each((id, idx)=>{
        // columns contains all subcolumns (off.=0, del.=1, fin.=2) to be tested
        // there are 3 columns per student, and the first one is number 1
        cy.wrap(columns).each((cnum)=>{
            check_delegation_points_view_value(1 + idx*3 + cnum, value)
        })
    })
    cy.wait(10)
    cy.wrap(stud_ids).each(stud_id => {
        // Doing the same thing for each student detail view
        cy.visit("/marking/detail/"+String(stud_id)+"/question/3")
        cy.wait(10)
        cy.wrap(columns).each(cnum => {
            check_delegation_points_view_value(1 + cnum, value)
        });


    });
}

// Checks all entries in the staff marking summary
function test_staff_summary_values(entries){
    cy.get("#summary-table tbody").within(($table)=>{
        entries.forEach((row, row_idx) => {
            cy.get('tr').eq(row_idx).within(($row)=>{
                row.forEach((col, col_idx) => {
                    cy.get('td').eq(col_idx+1).shouldHaveTrimmedText(col)
                });
            })
        });
    })
}


var edit_enabled = { 'disabled': false, 'text': 'Edit marks' }
var edit_disabled = { 'disabled': true, 'text': 'Edit marks' }
var editall_enabled = { 'disabled': false, 'text': 'Edit all marks' }
var editall_disabled = { 'disabled': true, 'text': 'Edit all marks' }
var view_enabled = { 'disabled': false, 'text': 'View marks' }
var viewall_enabled = { 'disabled': false, 'text': 'View all marks' }

var submit_action = { 'disabled': false, 'text': 'Submit marks' }
var accept_action = { 'disabled': false, 'text': 'Accept marks without moderation' }
var sign_off_action = { 'disabled': false, 'text': 'Sign off marks' }
var finalized_action = { 'disabled': true, 'text': 'Marks finalized' }

var view_only = [view_enabled, edit_disabled]
var edit_view = [view_enabled, edit_enabled]
var viewall_only = [viewall_enabled, editall_disabled]
var editall_viewall = [viewall_enabled, editall_enabled]

var CHE_stud_ids = [1, 2, 3, 4, 5]
var CHE_stud_names = [
    "Eugen Pfister (CHE-S-1)",
    "Franz Wrigley Stalder (CHE-S-2)",
    "Bäschteli von Almen (CHE-S-3)",
    "Eduard Ramseier (CHE-S-4)",
    "Fritzli Bühler (CHE-S-5)",
]

var CHE_studs_final = [
    [CHE_stud_names[0], "-", "-"],
    [CHE_stud_names[1], "-", "-"],
    [CHE_stud_names[2], "-", "-"],
    [CHE_stud_names[3], "-", "-"],
    [CHE_stud_names[4], "-", "-"],
]
var CHE_studs_editable = [
    [CHE_stud_names[0], edit_view, edit_view],
    [CHE_stud_names[1], edit_view, edit_view],
    [CHE_stud_names[2], edit_view, edit_view],
    [CHE_stud_names[3], edit_view, edit_view],
    [CHE_stud_names[4], edit_view, edit_view],
    ["", editall_viewall, editall_viewall]
]

var ARM_stud_ids = [10,]
var ARM_stud_names = ["Deep Thought (ARM-S-42)",]
var ARM_studs_final = [
    [ARM_stud_names[0], "-", "-"],
]
var ARM_studs_viewable = [
    [ARM_stud_names[0], view_only, edit_view],
    ["", viewall_only, editall_viewall]
]

var AUS_stud_ids = [6, 7]
var AUS_stud_names = [
    "Arthur Dent (AUS-S-1)",
    "Zaphod Beeblebrox (AUS-S-2)",
]
var AUS_studs_final = [
    [AUS_stud_names[0], "-", "-"],
    [AUS_stud_names[1], "-", "-"],
]
var AUS_studs_viewable = [
    [AUS_stud_names[0], view_only, edit_view],
    [AUS_stud_names[1], view_only, edit_view],
    ["", viewall_only, editall_viewall]
]

var AUT_stud_ids = [8, 9]
var AUT_studs_final = [
    ["Ford Prefect (AUT-S-1)", "20", "20"],
    ["Slartibartfast  (AUT-S-2)", "20", "20"],
]
var AUT_studs_viewable = [
    ["Ford Prefect (AUT-S-1)", view_only, view_only],
    ["Slartibartfast  (AUT-S-2)", view_only, view_only],
    ["", viewall_only, viewall_only]
]

var staff_summary_deleg_entries_only_fin = [
    ["-","-","-"],
    ["10.00","-","10.00"],
    ["10.00","-","10.00"],
    ["10.00","10.00","20.00"],
    ["10.00","10.00","20.00"],
    ["-","-","-"],
    ["-","-","-"],
    ["-","-","-"],
    ["-","-","-"],
    ["-","-","-"],
]

var staff_summary_deleg_entries_subm_fin = [
    ["10.00","-","10.00"],
    ["10.00","-","10.00"],
    ["10.00","-","10.00"],
    ["10.00","10.00","20.00"],
    ["10.00","10.00","20.00"],
    ["-","-","-"],
    ["-","-","-"],
    ["-","-","-"],
    ["-","-","-"],
    ["-","-","-"],
]

describe('Marking', function () {

    it("Test General Visibility (Translation phase)", function () {

        cy.login('CHE', '1234')
        test_marking_summary_visibility(false)
        test_final_points_visibility(CHE_studs_final)
        test_delegation_view_edit_status(CHE_stud_ids, 404)

        cy.logout()
        cy.login('ARM', '1234')
        test_marking_summary_visibility(false)
        test_final_points_visibility(ARM_studs_final)
        test_delegation_view_edit_status(ARM_stud_ids, 404)

        cy.logout()
        cy.login('AUS', '1234')
        test_marking_summary_visibility(false)
        test_final_points_visibility(AUS_studs_final)
        test_delegation_view_edit_status(AUS_stud_ids, 404)

        cy.logout()
        cy.login('AUT', '1234')
        test_marking_summary_visibility(false)
        test_final_points_visibility(AUT_studs_final)
        test_delegation_view_edit_status(AUT_stud_ids, 404)

        cy.logout()
        cy.login("marker", '1234')
        test_staff_edit_status(3, 4, CHE_stud_ids, 404)
        test_staff_edit_status(3, 1, ARM_stud_ids, 404)
        test_staff_edit_status(3, 2, AUS_stud_ids, 404)
        test_staff_edit_status(3, 3, AUT_stud_ids, 404)

    })

    it("Test General Visibility (Organizer Marking phase)", function () {
        cy.login('admin', '1234')
        // orga Marking
        cy.switchExamPhase(1, 9)

        //checking only one delegation for time reasons
        cy.logout()
        cy.login('CHE', '1234')
        test_marking_summary_visibility(false)
        test_delegation_view_edit_status(CHE_stud_ids, 404)

        //checking only that we can visit without error
        cy.logout()
        cy.login("marker", '1234')
        //CHE OPEN
        //Normal marking
        test_staff_edit_status(3, 4, CHE_stud_ids, 200)

        //ARM SUBMITTED_FOR_MODERATION
        test_staff_edit_status(3, 1, ARM_stud_ids, 200)

        // AUS LOCKED_BY_MOD
        test_staff_edit_status(3, 2, AUS_stud_ids, 200)

        //AUT FINAL
        test_staff_edit_status(3, 3, AUT_stud_ids, 404)

    })

    it("Test General Visibility (Delegation Marking phase)", function () {
        cy.login('admin', '1234')
        // deleg marking
        cy.switchExamPhase(1, 10)

        cy.logout()
        cy.login('CHE', '1234')
        test_marking_summary_visibility(true, CHE_studs_editable)
        test_summary_action_content([submit_action,])
        test_final_points_visibility(CHE_studs_final)
        test_delegation_view_edit_status(CHE_stud_ids, 200)

        cy.logout()
        cy.login('ARM', '1234')
        test_marking_summary_visibility(true, ARM_studs_viewable)
        test_summary_action_content([accept_action,])
        test_final_points_visibility(ARM_studs_final)
        test_delegation_view_edit_status(ARM_stud_ids, 404)

        cy.logout()
        cy.login('AUS', '1234')
        test_marking_summary_visibility(true, AUS_studs_viewable)
        test_summary_action_content([sign_off_action,])
        test_final_points_visibility(AUS_studs_final)
        test_delegation_view_edit_status(AUS_stud_ids, 404)

        cy.logout()
        cy.login('AUT', '1234')
        test_marking_summary_visibility(true, AUT_studs_viewable)
        test_summary_action_content([finalized_action,])
        test_final_points_visibility(AUT_studs_final)
        test_delegation_view_edit_status(AUT_stud_ids, 404)

        //checking only that we can visit without error
        cy.logout()
        cy.login("marker", '1234')
        //CHE OPEN
        //Normal marking
        test_staff_edit_status(3, 4, CHE_stud_ids, 200)

        //ARM SUBMITTED_FOR_MODERATION
        // Now markers can only edit unsubmitted marks
        test_staff_edit_status(3, 1, ARM_stud_ids, 404)

        // AUS LOCKED_BY_MOD
        // Now markers can only edit unsubmitted marks
        test_staff_edit_status(3, 2, AUS_stud_ids, 404)

        //AUT FINAL
        test_staff_edit_status(3, 3, AUT_stud_ids, 404)
    })

    it("Test General Visibility (Delegation Marking (Submit only) phase)", function () {
        cy.login('admin', '1234')
        // deleg marking (submit only)
        cy.switchExamPhase(1, 11)

        cy.logout()
        cy.login('CHE', '1234')
        test_marking_summary_visibility(true, CHE_studs_editable)
        test_summary_action_content([submit_action,])
        // Only test final points for one deleg, the main difference are the actions
        test_final_points_visibility(CHE_studs_final)
        test_delegation_view_edit_status(CHE_stud_ids, 200)

        cy.logout()
        cy.login('ARM', '1234')
        test_marking_summary_visibility(true, ARM_studs_viewable)
        test_summary_action_content_none(1)
        test_delegation_view_edit_status(ARM_stud_ids, 404)

        cy.logout()
        cy.login('AUS', '1234')
        test_marking_summary_visibility(true, AUS_studs_viewable)
        test_summary_action_content_none(1)
        test_delegation_view_edit_status(AUS_stud_ids, 404)

        cy.logout()
        cy.login('AUT', '1234')
        test_marking_summary_visibility(true, AUT_studs_viewable)
        test_summary_action_content([finalized_action,])
        test_delegation_view_edit_status(AUT_stud_ids, 404)

        //checking only that we can visit without error
        cy.logout()
        cy.login("marker", '1234')
        //CHE OPEN
        //Normal marking
        test_staff_edit_status(3, 4, CHE_stud_ids, 200)

        //ARM SUBMITTED_FOR_MODERATION
        // Now markers can only edit unsubmitted marks
        test_staff_edit_status(3, 1, ARM_stud_ids, 404)

        // AUS LOCKED_BY_MOD
        // Now markers can only edit unsubmitted marks
        test_staff_edit_status(3, 2, AUS_stud_ids, 404)

        //AUT FINAL
        test_staff_edit_status(3, 3, AUT_stud_ids, 404)
    })


    it("Test Marks Visibility  (Translation phase)", function () {
        // Testing only the first student in each array, otherwise the test takes ~10min
        cy.login('CHE', '1234')
        test_delegation_marks_view_all(CHE_stud_ids.slice(0,1), [0,2], "-")

        cy.logout()
        cy.login('ARM', '1234')
        test_delegation_marks_view_all(ARM_stud_ids.slice(0,1), [0,2], "-")

        cy.logout()
        cy.login('AUS', '1234')
        test_delegation_marks_view_all(AUS_stud_ids.slice(0,1), [0,], "-")

        cy.logout()
        cy.login('AUT', '1234')
        test_delegation_marks_view_all(AUT_stud_ids.slice(0,1), [0,], "-")

        cy.logout()
        cy.login('marker', '1234')
        cy.wait(10)
        cy.visit('http://localhost:8000/marking/staff?version=F')
        test_staff_summary_values(staff_summary_deleg_entries_only_fin)
        cy.wait(10)
        cy.visit('http://localhost:8000/marking/staff?version=D')
        test_staff_summary_values(staff_summary_deleg_entries_only_fin)
    })

    it("Test Marks Visibility  (Organizer Marking phase)", function () {
        cy.login('admin', '1234')
        // orga Marking
        cy.switchExamPhase(1, 9)

        // Test only one delegation for time reasons
        cy.logout()
        cy.login('ARM', '1234')
        test_delegation_marks_view_all(ARM_stud_ids.slice(0,1), [0,2], "-")

        cy.logout()
        cy.login('marker', '1234')
        cy.visit('http://localhost:8000/marking/staff?version=D')
        test_staff_summary_values(staff_summary_deleg_entries_only_fin)
    })

    it("Test Marks Visibility  (Delegation Marking phase)", function () {
        cy.login('admin', '1234')
        // deleg Marking
        cy.switchExamPhase(1, 10)

        cy.logout()
        cy.login('CHE', '1234')
        test_delegation_marks_view_all(CHE_stud_ids.slice(0,1), [0,], "-")

        cy.logout()
        cy.login('ARM', '1234')
        test_delegation_marks_view_all(ARM_stud_ids.slice(0,1), [0,], "0.00")

        cy.logout()
        cy.login('marker', '1234')
        cy.visit('http://localhost:8000/marking/staff?version=D')
        test_staff_summary_values(staff_summary_deleg_entries_only_fin, "-")
    })

    it("Test Marks Visibility  (Delegation Marking (Submit only) phase)", function () {
        cy.login('admin', '1234')
        // deleg Marking (submit only)
        cy.switchExamPhase(1, 11)

        cy.logout()
        cy.login('CHE', '1234')
        test_delegation_marks_view_all(CHE_stud_ids.slice(0,1), [0,], "0.00")

        cy.logout()
        cy.login('ARM', '1234')
        test_delegation_marks_view_all(ARM_stud_ids.slice(0,1), [0,], "0.00")

        cy.logout()
        cy.login('marker', '1234')
        // Marker should now be able to see more delegation marks
        cy.visit('http://localhost:8000/marking/staff?version=D')
        test_staff_summary_values(staff_summary_deleg_entries_subm_fin)
    })


    it("Test Official Marking", function () {
        cy.login('admin', '1234')
        // orga marking
        cy.switchExamPhase(1, 9)

        // Test index
        cy.logout()
        cy.login('marker', '1234')
        cy.visit('/marking/official')
        cy.get('#question-dropdown > a').should('be.visible').click()
        cy.get('#question-dropdown ul').should('contain', 'T-1 Theory - Two Problems in Mechanics - Answer Sheet').and('contain', 'T-2 Theory - Nonlinear Dynamics in Electric Circuits - Answer Sheet')
        cy.contains('T-1 Theory').click()
        cy.url().should('contain', '/marking/official/question/3')
        cy.get('#delegation-dropdown > a').should('be.visible').click()
        cy.get('#delegation-dropdown ul').should('contain', 'Armenia (ARM)').and('contain', 'Switzerland (CHE)')
        cy.contains('CHE').click()

        cy.url().should('contain', '/marking/official/question/3/delegation/4')
        cy.get('form table thead').within(($thead)=>{
            CHE_stud_names.forEach(function(name, idx){
                cy.get('th').eq(idx+1).find('h4').shouldHaveTrimmedText(name)
            });
        })

        check_point_form(1,0,'0.00')
        edit_point_form(1,0, 0.75)
        check_point_form(1,0,'0.75')

        // too much
        edit_point_form(1,1,10)
        // negative
        edit_point_form(1,2,-1)
        // too many digits
        edit_point_form(1,3,0.1234)
        // NaN
        edit_point_form(1,4,"abc")
        //empty
        // cypress doesn't let you type(""), so we need to do it by hand
        cy.get("#id_Stud-1-5-points").clear()

        // add more values for other students
        edit_point_form(2,10, 1)
        edit_point_form(3,10, 1)
        edit_point_form(4,10, 1)
        edit_point_form(5,10, 1)

        // check totals
        // change focus to make sure the totals are calculated
        cy.get("#id_Stud-1-5-points").focus()
        cy.get("#cell_total_0").shouldHaveTrimmedText('-')
        cy.get("#cell_total_1").shouldHaveTrimmedText('1.00')
        cy.get("#cell_total_2").shouldHaveTrimmedText('1.00')
        cy.get("#cell_total_3").shouldHaveTrimmedText('1.00')
        cy.get("#cell_total_4").shouldHaveTrimmedText('1.00')

        cy.get("#submit_button").click()

        // check that errors are displayed
        check_point_form_error(1,1, true, "The number of points cannot exceed the maximum.")
        check_point_form_error(1,2, true, "Ensure this value is greater than or equal to 0.0.")
        check_point_form_error(1,3, true, "Ensure that there are no more than 2 decimal places.")
        check_point_form_error(1,4, true, "Enter a number.")
        check_point_form_error(1,5, true, "This field is required.")

        // check that there are no errors on other fields
        check_point_form_error(1,0, false)
        check_point_form_error(2,10, false)
        check_point_form_error(3,10, false)
        check_point_form_error(4,10, false)
        check_point_form_error(5,10, false)

        // correct errors:
        edit_point_form(1,1,0.5)
        edit_point_form(1,2,0.14)
        edit_point_form(1,3,0)
        edit_point_form(1,4,0.75)
        edit_point_form(1,5,0)
        edit_point_form(1,10,1)

        // check totals again
        cy.get("#id_Stud-1-0-points").focus()
        cy.get("#cell_total_0").shouldHaveTrimmedText('3.14')
        cy.get("#cell_total_1").shouldHaveTrimmedText('1.00')
        cy.get("#cell_total_2").shouldHaveTrimmedText('1.00')
        cy.get("#cell_total_3").shouldHaveTrimmedText('1.00')
        cy.get("#cell_total_4").shouldHaveTrimmedText('1.00')

        // submit again
        cy.get("#submit_button").click()

        cy.url().should('contain', '/marking/official/question/3/delegation/4/confirmed')

        var CHE_stud_points = [
            [CHE_stud_names[0], '3.14'],
            [CHE_stud_names[1], '1.00'],
            [CHE_stud_names[2], '1.00'],
            [CHE_stud_names[3], '1.00'],
            [CHE_stud_names[4], '1.00'],
        ]

        cy.get('tbody').within(($tbody)=>{
            CHE_stud_points.forEach(function(elem, idx){
                cy.get('tr').eq(idx+1).find('td').eq(0).shouldHaveTrimmedText(elem[0])
                cy.get('tr').eq(idx+1).find('td').eq(1).shouldHaveTrimmedText(elem[1])
            });
        })

        cy.visit('/marking/official/question/3/delegation/4')
        // check the points edited before
        check_point_form(1,1,'0.50')
        check_point_form(1,2,'0.14')
        check_point_form(1,3,'0.00')
        check_point_form(1,4,'0.75')
        check_point_form(1,5,'0.00')
        check_point_form(2,10,'1.00')
        check_point_form(3,10,'1.00')
        check_point_form(4,10,'1.00')
        check_point_form(5,10,'1.00')

    })

    it("Test Admin Marking Summary", function () {
        cy.login('admin', '1234')
        // orga marking
        cy.switchExamPhase(1, 9)

        // Test index
        cy.logout()
        cy.login('marker', '1234')
        cy.visit('http://localhost:8000/marking/staff')
        cy.get("#summary-table tbody").within(($table)=>{
            //check not editable markings
            cy.get('tr').eq(3).within(($row)=>{
                cy.get('td').eq(0).shouldHaveTrimmedText("AUT-S-1")
                cy.get('td').eq(1).find('i').should("have.class", "fa fa-ban")
                cy.get('a').should('not.exist')
            })
            //check editable
            cy.get('tr').eq(0).within(($row)=>{
                cy.get('td').eq(0).shouldHaveTrimmedText("ARM-S-42")
                cy.get('td').eq(1).find('i').should("have.class", "fa fa-pencil")
                cy.get('td').eq(1).find('a').click()
            })

        })

        cy.url().should('contain', "/marking/staff/vO/student/10/question/3/edit")

        // check/edit some points
        edit_point_form(-1, 0, "0.00")
        edit_point_form(-1,0, 0.75)
        check_point_form(-1,0,'0.75')

        // too much
        edit_point_form(-1,1,10)
        // negative
        edit_point_form(-1,2,-1)
        // too many digits
        edit_point_form(-1,3,0.1234)
        // NaN
        edit_point_form(-1,4,"abc")
        //empty
        // cypress doesn't let you type(""), so we need to do it by hand
        cy.get("#id_form-5-points").clear()

        cy.get('input[type="submit"]').click()

        // check that errors are displayed
        check_point_form_error(-1,1, true, "The number of points cannot exceed the maximum.", false)
        check_point_form_error(-1,2, true, "Ensure this value is greater than or equal to 0.0.", false)
        check_point_form_error(-1,3, true, "Ensure that there are no more than 2 decimal places.", false)
        check_point_form_error(-1,4, true, "Enter a number.", false)
        check_point_form_error(-1,5, true, "This field is required.", false)

        // correct errors:
        edit_point_form(-1,1,0.5)
        edit_point_form(-1,2,0.14)
        edit_point_form(-1,3,0)
        edit_point_form(-1,4,0.75)
        edit_point_form(-1,5,0)
        edit_point_form(-1,10,1)

        // submit again
        cy.get('input[type="submit"]').click()
        cy.get(".alert-success").should('contain', "Points have been saved.")

        // hard reload to check values
        cy.visit("/marking/staff/vO/student/10/question/3/edit")

        // check values
        check_point_form(-1,1,"0.50")
        check_point_form(-1,2,"0.14")
        check_point_form(-1,3,"0.00")
        check_point_form(-1,4,"0.75")
        check_point_form(-1,5,"0.00")
        check_point_form(-1,10,"1.00")

    })


    it("Test Delegation Edit", function () {
        cy.login('admin', '1234')
        // deleg marking
        cy.switchExamPhase(1, 10)

        cy.logout()
        cy.login('CHE', '1234')
        cy.visit('/marking/detail/1/question/3/edit')

        // check/edit some points
        edit_point_form(-1, 0, "0.80")
        edit_point_form(-1,0, 0.75)
        check_point_form(-1,0,'0.75')

        // too much
        edit_point_form(-1,1,10)
        // negative
        edit_point_form(-1,2,-1)
        // too many digits
        edit_point_form(-1,3,0.1234)
        // NaN
        edit_point_form(-1,4,"abc")
        //empty
        // cypress doesn't let you type(""), so we need to do it by hand
        cy.get("#id_form-5-points").clear()

        cy.get('input[type="submit"]').click()

        // check that errors are displayed (there are no error classes in this view, so we don't check for them)
        check_point_form_error(-1,1, true, "The number of points cannot exceed the maximum.", false)
        check_point_form_error(-1,2, true, "Ensure this value is greater than or equal to 0.0.", false)
        check_point_form_error(-1,3, true, "Ensure that there are no more than 2 decimal places.", false)
        check_point_form_error(-1,4, true, "Enter a number.", false)
        check_point_form_error(-1,5, true, "This field is required.", false)

        // correct errors:
        edit_point_form(-1,1,0.5)
        edit_point_form(-1,2,0.14)
        edit_point_form(-1,3,0)
        edit_point_form(-1,4,0.75)
        edit_point_form(-1,5,0)

        // submit again
        cy.get('input[type="submit"]').click()
        cy.get(".alert-success").should('contain', "Points have been saved.")

        // hard reload to check values
        cy.visit("/marking/detail/1/question/3/edit")

        // check values
        check_point_form(-1,0,"0.75")
        check_point_form(-1,1,"0.50")
        check_point_form(-1,2,"0.14")
        check_point_form(-1,3,"0.00")
        check_point_form(-1,4,"0.75")
        check_point_form(-1,5,"0.00")

        //check values also in readonly view
        cy.visit("/marking/detail/1/question/3")

        // Delegation is the second column
        check_delegation_points_view(2,["0.75", "0.50", "0.14", "0.00", "0.75", "0.00"])

    })

    it("Test Delegation Edit All", function () {
        cy.login('admin', '1234')
        // deleg marking
        cy.switchExamPhase(1, 10)

        cy.logout()
        cy.login('CHE', '1234')
        cy.visit('/marking/detail_all/question/3/edit')

        check_point_form(-1,0,'0.80')
        edit_point_form(-1,0, 0.75)
        check_point_form(-1,0,'0.75')

        // too much
        edit_point_form(-1,5,10)
        // negative
        edit_point_form(-1,10,-1)
        // too many digits
        edit_point_form(-1,15,0.1234)
        // NaN
        edit_point_form(-1,20,"abc")
        //empty
        // cypress doesn't let you type(""), so we need to do it by hand
        cy.get("#id_form-25-points").clear()

        // add more values for other students
        edit_point_form(-1,1, 0.17)
        edit_point_form(-1,2, 0.17)
        edit_point_form(-1,3, 0.17)
        edit_point_form(-1,4, 0.17)


        cy.get('input[type="submit"]').click()

        // check that errors are displayed
        check_point_form_error(-1,5, true, "The number of points cannot exceed the maximum.")
        check_point_form_error(-1,10, true, "Ensure this value is greater than or equal to 0.0.")
        check_point_form_error(-1,15, true, "Ensure that there are no more than 2 decimal places.")
        check_point_form_error(-1,20, true, "Enter a number.")
        check_point_form_error(-1,25, true, "This field is required.")


        // check that there are no errors on other fields
        check_point_form_error(-1,0, false)
        check_point_form_error(-1,1, false)
        check_point_form_error(-1,2, false)
        check_point_form_error(-1,3, false)
        check_point_form_error(-1,4, false)

        // correct errors:
        edit_point_form(-1,5,0.5)
        edit_point_form(-1,10,0.14)
        edit_point_form(-1,15,0)
        edit_point_form(-1,20,0.75)
        edit_point_form(-1,25,0)

        // submit again
        cy.get('input[type="submit"]').click()

        cy.get(".alert-success").should('contain', "Points have been saved.")

        // hard reload to check values
        cy.visit("/marking/detail_all/question/3/edit")

        // check values
        check_point_form(-1,0,"0.75")
        check_point_form(-1,5,"0.50")
        check_point_form(-1,10,"0.14")
        check_point_form(-1,15,"0.00")
        check_point_form(-1,20,"0.75")
        check_point_form(-1,25,"0.00")
        check_point_form(-1,1,"0.17")
        check_point_form(-1,2,"0.17")
        check_point_form(-1,3,"0.17")
        check_point_form(-1,4,"0.17")
        //check values also in readonly view
        cy.visit("/marking/detail_all/question/3")

        // CHE-S-1 Del. is column 2
        check_delegation_points_view(2,["0.75", "0.50", "0.14", "0.00", "0.75", "0.00"])
        // CHE-S-3 Del. is column 5, CHE-S-3 clumn 8,...
        check_delegation_points_view(5,["0.17",])
        check_delegation_points_view(8,["0.17",])
        check_delegation_points_view(11,["0.17",])
        check_delegation_points_view(14,["0.17",])

    })


    it("Test Delegation Actions",function(){
        cy.login('admin', '1234')
        // deleg Marking
        cy.switchExamPhase(1, 10)

        cy.logout()
        cy.login('CHE', '1234')

        cy.visit("/marking/")
        cy.get('a[href="#marking"]').click()
        cy.get("#marking").should('be.visible')
        cy.get('#marking .table-responsive tbody >:last-child >:nth-child(2) .btn').should('contain', "Submit marks").click()
        cy.url().should('contain', '/marking/confirm/3')
        cy.get("#confirm-table").within(($table)=>{
            // Check just some entries
            CHE_stud_names.forEach((elem, idx)=>{
                cy.get('thead tr th').eq(1+idx).shouldHaveTrimmedText(elem)
            })

            cy.get('tbody tr').eq(0).find('td').eq(0).shouldHaveTrimmedText("A.1")
            cy.get('tbody tr').eq(1).find('td').eq(0).shouldHaveTrimmedText("A.2")
            cy.get('tbody tr').eq(1).find('td').eq(1).shouldHaveTrimmedText("0.50")
            cy.get('tbody tr').eq(1).find('td').eq(2).shouldHaveTrimmedText("0.50")
            cy.get('tbody tr').eq(1).find('td').eq(3).shouldHaveTrimmedText("0.50")
            cy.get('tbody tr').eq(1).find('td').eq(4).shouldHaveTrimmedText("0.50")
            cy.get('tbody tr').eq(1).find('td').eq(5).shouldHaveTrimmedText("0.50")

            cy.get('tfoot tr').eq(0).find('td').eq(0).find('b').shouldHaveTrimmedText("Total:")
            cy.get('tfoot tr').eq(0).find('td').eq(1).find('b').shouldHaveTrimmedText("10.00")
            cy.get('tfoot tr').eq(0).find('td').eq(2).find('b').shouldHaveTrimmedText("10.00")
            cy.get('tfoot tr').eq(0).find('td').eq(3).find('b').shouldHaveTrimmedText("10.00")
            cy.get('tfoot tr').eq(0).find('td').eq(4).find('b').shouldHaveTrimmedText("10.00")
            cy.get('tfoot tr').eq(0).find('td').eq(5).find('b').shouldHaveTrimmedText("10.00")
        })

        cy.get('#confirm-alert').should('have.class', 'alert-info').and('contain', "I confirm my version of the markings.")
        cy.get('#reject-button').should('not.exist')
        cy.get('#confirm-button').should('contain', "Confirm").click()
        cy.get('#confirm-alert').should('have.class', 'alert-danger').and('contain', "You have to confirm the marking before continuing.")
        cy.get('#confirm-alert input[type="checkbox"]').check()
        cy.get('#confirm-button').should('contain', "Confirm").click()

        cy.url().should('contain', '/marking/').and('not.contain', 'confirm/3')
        cy.get('a[href="#marking"]').click()
        cy.get("#marking").should('be.visible')
        test_summary_action_content([accept_action,])
        cy.get('#marking .table-responsive tbody >:last-child >:nth-child(2) .btn').should('contain', "Accept marks").click()
        cy.url().should('contain', '/marking/confirm/final/3')
        cy.get("div.container h2").should('contain', "Sign off final points")
        cy.get("#confirm-table").within(($table)=>{
            // Check just some entries
            CHE_stud_names.forEach((elem, idx)=>{
                cy.get('thead tr th').eq(1+idx).shouldHaveTrimmedText(elem)
            })

            cy.get('tbody tr').eq(0).find('td').eq(0).shouldHaveTrimmedText("A.1")
            cy.get('tbody tr').eq(1).find('td').eq(0).shouldHaveTrimmedText("A.2")
            cy.get('tbody tr').eq(1).find('td').eq(1).shouldHaveTrimmedText("0.00")
            cy.get('tbody tr').eq(1).find('td').eq(2).shouldHaveTrimmedText("0.00")
            cy.get('tbody tr').eq(1).find('td').eq(3).shouldHaveTrimmedText("0.00")
            cy.get('tbody tr').eq(1).find('td').eq(4).shouldHaveTrimmedText("0.00")
            cy.get('tbody tr').eq(1).find('td').eq(5).shouldHaveTrimmedText("0.00")

            cy.get('tfoot tr').eq(0).find('td').eq(0).find('b').shouldHaveTrimmedText("Total:")
            cy.get('tfoot tr').eq(0).find('td').eq(1).find('b').shouldHaveTrimmedText("0.00")
            cy.get('tfoot tr').eq(0).find('td').eq(2).find('b').shouldHaveTrimmedText("0.00")
            cy.get('tfoot tr').eq(0).find('td').eq(3).find('b').shouldHaveTrimmedText("0.00")
            cy.get('tfoot tr').eq(0).find('td').eq(4).find('b').shouldHaveTrimmedText("0.00")
            cy.get('tfoot tr').eq(0).find('td').eq(5).find('b').shouldHaveTrimmedText("0.00")
        })

        cy.get('#confirm-alert').should('have.class', 'alert-warning').and('contain', "I accept the final markings.")
        cy.get('#confirm-alert input[type="checkbox"]').check()
        cy.get('#reject-button').should('not.exist')
        cy.get('#confirm-button').should('contain', "Accept").click()
        cy.url().should('contain', '/marking/').and('not.contain', 'confirm/final/3')
        cy.get('a[href="#marking"]').click()
        cy.get("#marking").should('be.visible')
        test_summary_action_content([finalized_action,])

        test_delegation_marks_view_all(CHE_stud_ids.slice(0,1), [0,], "0.00")

        cy.logout()
        cy.login('AUS', '1234')

        cy.visit("/marking/")
        cy.get('a[href="#marking"]').click()
        cy.get("#marking").should('be.visible')
        cy.get('#marking .table-responsive tbody >:last-child >:nth-child(2) .btn').should('contain', "Sign off marks").click()
        cy.url().should('contain', '/marking/confirm/final/3')
        cy.get("div.container h2").should('contain', "Sign off final points")
        cy.get("#confirm-table").within(($table)=>{
            // Check just some entries
            AUS_stud_names.forEach((elem, idx)=>{
                cy.get('thead tr th').eq(1+idx).shouldHaveTrimmedText(elem)
            })

            cy.get('tbody tr').eq(0).find('td').eq(0).shouldHaveTrimmedText("A.1")
            cy.get('tbody tr').eq(1).find('td').eq(0).shouldHaveTrimmedText("A.2")
            cy.get('tbody tr').eq(1).find('td').eq(1).shouldHaveTrimmedText("0.50")
            cy.get('tbody tr').eq(1).find('td').eq(2).shouldHaveTrimmedText("0.50")


            cy.get('tfoot tr').eq(0).find('td').eq(0).find('b').shouldHaveTrimmedText("Total:")
            cy.get('tfoot tr').eq(0).find('td').eq(1).find('b').shouldHaveTrimmedText("10.00")
            cy.get('tfoot tr').eq(0).find('td').eq(2).find('b').shouldHaveTrimmedText("10.00")
        })

        cy.get('#confirm-alert').should('have.class', 'alert-info').and('contain', "I accept the final markings.")
        cy.get('#confirm-alert input[type="checkbox"]').check()
        cy.get('#reject-button').should('contain', "Reopen moderation")
        cy.get('#confirm-button').should('contain', "Accept").click()

        cy.url().should('contain', '/marking/').and('not.contain', 'confirm/final/3')
        cy.get('a[href="#marking"]').click()
        cy.get("#marking").should('be.visible')
        test_summary_action_content([finalized_action,])
        // check marks on viewall
        cy.visit('/marking/detail_all/question/3')
        cy.get("#points-table tfoot tr").within(($tr)=>{
            cy.get('td').eq(3).find('strong').shouldHaveTrimmedText('10.00')
            cy.get('td').eq(6).find('strong').shouldHaveTrimmedText('10.00')
        })
    })

    it("Test Delegation Actions (Submit Only)",function(){
        cy.login('admin', '1234')
        // deleg Marking (submit only)
        cy.switchExamPhase(1, 11)

        cy.logout()
        cy.login('CHE', '1234')

        cy.visit("/marking/")
        cy.get('a[href="#marking"]').click()
        cy.get("#marking").should('be.visible')
        cy.get('#marking .table-responsive tbody >:last-child >:nth-child(2) .btn').should('contain', "Submit marks").click()
        cy.url().should('contain', '/marking/confirm/3')
        cy.get("#confirm-table").within(($table)=>{
            // Check just some entries
            CHE_stud_names.forEach((elem, idx)=>{
                cy.get('thead tr th').eq(1+idx).shouldHaveTrimmedText(elem)
            })

            cy.get('tbody tr').eq(0).find('td').eq(0).shouldHaveTrimmedText("A.1")
            cy.get('tbody tr').eq(1).find('td').eq(0).shouldHaveTrimmedText("A.2")
            cy.get('tbody tr').eq(1).find('td').eq(1).shouldHaveTrimmedText("0.50")
            cy.get('tbody tr').eq(1).find('td').eq(2).shouldHaveTrimmedText("0.50")
            cy.get('tbody tr').eq(1).find('td').eq(3).shouldHaveTrimmedText("0.50")
            cy.get('tbody tr').eq(1).find('td').eq(4).shouldHaveTrimmedText("0.50")
            cy.get('tbody tr').eq(1).find('td').eq(5).shouldHaveTrimmedText("0.50")

            cy.get('tfoot tr').eq(0).find('td').eq(0).find('b').shouldHaveTrimmedText("Total:")
            cy.get('tfoot tr').eq(0).find('td').eq(1).find('b').shouldHaveTrimmedText("10.00")
            cy.get('tfoot tr').eq(0).find('td').eq(2).find('b').shouldHaveTrimmedText("10.00")
            cy.get('tfoot tr').eq(0).find('td').eq(3).find('b').shouldHaveTrimmedText("10.00")
            cy.get('tfoot tr').eq(0).find('td').eq(4).find('b').shouldHaveTrimmedText("10.00")
            cy.get('tfoot tr').eq(0).find('td').eq(5).find('b').shouldHaveTrimmedText("10.00")
        })

        cy.get('#confirm-alert').should('have.class', 'alert-info').and('contain', "I confirm my version of the markings.")
        cy.get('#reject-button').should('not.exist')
        cy.get('#confirm-alert input[type="checkbox"]').check()
        cy.get('#confirm-button').should('contain', "Confirm").click()

        cy.url().should('contain', '/marking/').and('not.contain', 'confirm/3')
        cy.get('a[href="#marking"]').click()
        cy.get("#marking").should('be.visible')
        test_summary_action_content_none(1)

        cy.visit('/marking/confirm/final/3')
    })



    it("Test Reopen Moderation",function(){
        cy.login('admin', '1234')
        // Moderation
        cy.switchExamPhase(1, 12)

        cy.logout()
        cy.login('marker', '1234')

        cy.request({
            failOnStatusCode: false,
            url: '/marking/moderate/question/3/delegation/2',
        }).its("status").should('eq', 404)

        cy.logout()
        cy.login('AUS', '1234')

        cy.visit("/marking/")
        cy.get('a[href="#marking"]').click()
        cy.get("#marking").should('be.visible')
        cy.get('#marking .table-responsive tbody >:last-child >:nth-child(2) .btn').should('contain', "Sign off marks").click()
        cy.url().should('contain', '/marking/confirm/final/3')
        cy.get("div.container h2").should('contain', "Sign off final points")
        cy.get("#confirm-table").within(($table)=>{
            // Check just some entries
            AUS_stud_names.forEach((elem, idx)=>{
                cy.get('thead tr th').eq(1+idx).shouldHaveTrimmedText(elem)
            })
            cy.get('tbody tr').eq(0).find('td').eq(0).shouldHaveTrimmedText("A.1")
            cy.get('tbody tr').eq(1).find('td').eq(0).shouldHaveTrimmedText("A.2")
            cy.get('tbody tr').eq(1).find('td').eq(1).shouldHaveTrimmedText("0.50")
            cy.get('tbody tr').eq(1).find('td').eq(2).shouldHaveTrimmedText("0.50")

            cy.get('tfoot tr').eq(0).find('td').eq(0).find('b').shouldHaveTrimmedText("Total:")
            cy.get('tfoot tr').eq(0).find('td').eq(1).find('b').shouldHaveTrimmedText("10.00")
            cy.get('tfoot tr').eq(0).find('td').eq(2).find('b').shouldHaveTrimmedText("10.00")
        })

        cy.get('#confirm-alert').should('have.class', 'alert-info').and('contain', "I accept the final markings.")
        cy.get('#confirm-alert input[type="checkbox"]').check()
        cy.get('#reject-button').should('contain', "Reopen moderation").click()

        cy.url().should('contain', '/marking/').and('not.contain', 'confirm/final/3')
        cy.get('a[href="#marking"]').click()
        cy.get("#marking").should('be.visible')
        test_summary_action_content([accept_action,])

        cy.logout()
        cy.login('marker', '1234')

        cy.request({
            failOnStatusCode: false,
            url: '/marking/moderate/question/3/delegation/2',
        }).its("status").should('eq', 200)
    })

    it("Test Moderation Visibility",function(){
        cy.login('admin', '1234')
        // deleg marking
        cy.switchExamPhase(1, 10)

        var moderation_pages=[
            '/marking/moderate/question/3/delegation/1',
            '/marking/moderate/question/3/delegation/2',
            '/marking/moderate/question/3/delegation/3',
            '/marking/moderate/question/3/delegation/4'
        ]
        cy.logout()
        cy.login('CHE', '1234')
        check_permission_denied_redirect(moderation_pages)

        cy.logout()
        cy.login('marker', '1234')
        cy.request({
            failOnStatusCode: false,
            url: '/marking/moderate/question/3/delegation/1',
        }).its("status").should('eq', 404)

        cy.logout()
        cy.login('admin', '1234')
        // moderation
        cy.switchExamPhase(1, 12)

        cy.logout()
        cy.login('CHE', '1234')
        check_permission_denied_redirect(moderation_pages)

        cy.logout()
        cy.login('marker', '1234')
        cy.request({
            failOnStatusCode: false,
            url: '/marking/moderate/question/3/delegation/1',
        }).its("status").should('eq', 200)
        cy.request({
            failOnStatusCode: false,
            url: '/marking/moderate/question/3/delegation/2',
        }).its("status").should('eq', 404)
        cy.request({
            failOnStatusCode: false,
            url: '/marking/moderate/question/3/delegation/3',
        }).its("status").should('eq', 404)
        cy.request({
            failOnStatusCode: false,
            url: '/marking/moderate/question/3/delegation/4',
        }).its("status").should('eq', 200)
    })

    it("Test Moderation",function(){
        cy.logout()
        cy.login('admin', '1234')
        // moderation
        cy.switchExamPhase(1, 12)

        cy.logout()
        cy.login('marker', '1234')
        cy.visit('/marking/moderate/question/3/delegation/1')

        //Check that all fields are empty
        for (let index = 0; index < 13; index++) {
            check_point_form(10,index,"")
        }

        //Check copy button
        cy.get("#copy-10").click()

        for (let index = 0; index < 13; index++) {
            check_point_form(10,index,"0")
        }

        ARM_stud_names.forEach((elem, idx)=>{
            cy.get('thead tr th h4').eq(idx).shouldHaveTrimmedText(elem)
        })
        check_point_form(10,0,'0')
        edit_point_form(10,0, 0.75)
        check_point_form(10,0,'0.75')

        // too much
        edit_point_form(10,1,10)
        // negative
        edit_point_form(10,2,-1)
        // too many digits
        edit_point_form(10,3,0.1234)
        // NaN
        edit_point_form(10,4,"abc")
        //empty
        // cypress doesn't let you type(""), so we need to do it by hand
        cy.get("#id_Stud-10-5-points").clear()

        // check totals
        // change focus to make sure the totals are calculated
        cy.get("#id_Stud-10-1-points").focus()
        cy.get("#cell_total_0").shouldHaveTrimmedText('-')

        cy.get("#submit_button").click()

        // check that errors are displayed
        check_point_form_error(10,1, true, "The number of points cannot exceed the maximum.")
        check_point_form_error(10,2, true, "Ensure this value is greater than or equal to 0.0.")
        check_point_form_error(10,3, true, "Ensure that there are no more than 2 decimal places.")
        check_point_form_error(10,4, true, "Enter a number.")
        check_point_form_error(10,5, true, "This field is required.")

        // check that there are no errors on other fields
        check_point_form_error(10,0, false)

        // correct errors:
        edit_point_form(10,1,0.5)
        edit_point_form(10,2,0.14)
        edit_point_form(10,3,0)
        edit_point_form(10,4,0.75)
        edit_point_form(10,5,0)
        edit_point_form(10,10,1)

        // check totals again
        cy.get("#id_Stud-10-0-points").focus()
        cy.get("#cell_total_0").shouldHaveTrimmedText('3.14')

        // submit again
        cy.get("#submit_button").click()

        cy.url().should('contain', '/marking/moderate/question/3/delegation/1/confirmed')
        // Check total in overview
        cy.get('tbody tr').eq(1).find('td').eq(0).shouldHaveTrimmedText(ARM_stud_names[0])
        cy.get('tbody tr').eq(1).find('td').eq(1).shouldHaveTrimmedText("3.14")

        //Marking should not be accessible anymore
        cy.request({
            failOnStatusCode: false,
            url: '/marking/moderate/question/3/delegation/1',
        }).its("status").should('eq', 404)

        // Check marks and status for delegation
        cy.logout()
        cy.login('ARM', '1234')

        cy.visit("/marking/")
        cy.get('a[href="#marking"]').click()
        cy.get("#marking").should('be.visible')
        cy.get('#marking .table-responsive tbody >:last-child >:nth-child(2) .btn').should('contain', "Sign off marks").click()
        cy.url().should('contain', '/marking/confirm/final/3')
        cy.get("div.container h2").should('contain', "Sign off final points")
        cy.get("#confirm-table").within(($table)=>{
            // Check nonzero entries
            cy.get('tbody tr').eq(0).find('td').eq(1).shouldHaveTrimmedText("0.75")
            cy.get('tbody tr').eq(1).find('td').eq(1).shouldHaveTrimmedText("0.50")
            cy.get('tbody tr').eq(2).find('td').eq(1).shouldHaveTrimmedText("0.14")
            cy.get('tbody tr').eq(3).find('td').eq(1).shouldHaveTrimmedText("0.00")
            cy.get('tbody tr').eq(4).find('td').eq(1).shouldHaveTrimmedText("0.75")
            cy.get('tbody tr').eq(5).find('td').eq(1).shouldHaveTrimmedText("0.00")
            cy.get('tbody tr').eq(10).find('td').eq(1).shouldHaveTrimmedText("1.00")

            cy.get('tfoot tr').eq(0).find('td').eq(0).find('b').shouldHaveTrimmedText("Total:")
            cy.get('tfoot tr').eq(0).find('td').eq(1).find('b').shouldHaveTrimmedText("3.14")
        })

        cy.get('#confirm-alert input[type="checkbox"]').check()
        cy.get('#confirm-button').should('contain', "Accept").click()

        cy.url().should('contain', '/marking/').and('not.contain', 'confirm/final/3')
        cy.get('a[href="#marking"]').click()
        cy.get("#marking").should('be.visible')
        test_summary_action_content([finalized_action,])
        // check marks on viewall
        cy.visit('/marking/detail_all/question/3')
        cy.get("#points-table tbody").within(($tbody)=>{
            cy.get('tr').eq(0).find('td').eq(3).shouldHaveTrimmedText("0.75")
            cy.get('tr').eq(1).find('td').eq(3).shouldHaveTrimmedText("0.50")
            cy.get('tr').eq(2).find('td').eq(3).shouldHaveTrimmedText("0.14")
            cy.get('tr').eq(3).find('td').eq(3).shouldHaveTrimmedText("0.00")
            cy.get('tr').eq(4).find('td').eq(3).shouldHaveTrimmedText("0.75")
            cy.get('tr').eq(5).find('td').eq(3).shouldHaveTrimmedText("0.00")
            cy.get('tr').eq(10).find('td').eq(3).shouldHaveTrimmedText("1.00")
        })
        cy.get("#points-table tfoot tr").within(($tr)=>{
            cy.get('td').eq(3).find('strong').shouldHaveTrimmedText('3.14')
        })

    })


    it("Test Permissions", function () {
        var admin_only_pages = [
            "/marking/staff/import",
            "/marking/marking-submissions",
            "/marking/all/export.csv",
            "/marking/all/export-total.csv",
        ]
        var marker_only_pages = [
            "/marking/official",
            "/marking/staff",
            "/marking/moderate",
        ]

        var deleg_pages = [
            "/marking/",
        ]
        cy.login('AUS', '1234')

        //check a student of another delegation
        cy.request({
            failOnStatusCode: false,
            url: '/marking/detail/10/question/3',
        }).its("status").should('eq', 403)

        //check staff pages
        cy.request({
            failOnStatusCode: false,
            url: '/marking/progress',
        }).its("status").should('eq', 403)

        check_permission_denied_redirect(admin_only_pages.concat(marker_only_pages))

        cy.logout()
        cy.login('admin', '1234')

        check_permission_denied_redirect(marker_only_pages.concat(deleg_pages))

        cy.logout()
        cy.login('marker', '1234')

        check_permission_denied_redirect(admin_only_pages.concat(deleg_pages))

    })
})
