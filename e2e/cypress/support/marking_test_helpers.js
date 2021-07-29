

export function check_permission_denied_redirect(paths) {
    paths.forEach(function (elem, idx) {
        cy.visit(elem)
        cy.url().should('contain', 'accounts/login/?next=' + elem)
    });
}

// Tests the visibility of the marking tab in the delegation marking summary
export function test_marking_summary_visibility(should_exist, students = []) {
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
export function test_summary_action_content(actions) {
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
export function test_summary_action_content_none(action_pos) {
    cy.visit("/marking/")
    cy.get('a[href="#marking"]').click()
    cy.get("#marking").should('be.visible')
    cy.get('#marking .table-responsive tbody >:last-child').within(($footer) => {
        cy.get(':nth-child(' + String(action_pos + 1) + ') .btn').should('not.exist')
    })
}

// Tests the visibility of the final points in the delegation marking summary
export function test_final_points_visibility(student_points) {
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
export function test_delegation_view_edit_status_question(question_id, student_ids = [], edit_status = 200, view_status = 200) {
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
export function test_delegation_view_edit_status(student_ids = [], edit_status = 200, view_status = 200) {
    // Check only one question
    var question_ids = [3,]
    question_ids.forEach(function (qid, idx) {
        test_delegation_view_edit_status_question(qid, student_ids, edit_status, view_status)
    });
}

// Tests a selection of marking edit views for the markers
export function test_staff_edit_status(question_id, delegation_id, student_ids = [], status = 404) {
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
export function edit_point_form(stud_id, field_id, points){
    if(stud_id >= 0){
        cy.get("#id_Stud-"+stud_id+"-"+field_id+"-points").clear().type(points)
    }else{
        cy.get("#id_form-"+field_id+"-points").clear().type(points)
    }
}
// Checks the value of a points form field
export function check_point_form(stud_id, field_id, points){
    if(stud_id >= 0){
        cy.get("#id_Stud-"+stud_id+"-"+field_id+"-points").should('have.value', points)
    }else{
        cy.get("#id_form-"+field_id+"-points").should('have.value', points)
    }
}
// Checks error messages of a points form field
export function check_point_form_error(stud_id, field_id, should_have_err=true, err_msg="", check_error_class=true){
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
export function check_delegation_points_view(column, points){
    cy.get("#points-table tbody").within(($tbody)=>{
        points.forEach(function(elem, idx){
            cy.get('tr').eq(idx).find('td').eq(column).shouldHaveTrimmedText(elem)
        });
    })
}

// Checks that all points in column have value in the delegation view and viewall views
export function check_delegation_points_view_value(column, value="-"){
    cy.get("#points-table tbody").within(($tbody)=>{
        cy.get('tr').each(($tr)=>{
            cy.wrap($tr).find('td').eq(column).shouldHaveTrimmedText(value)
        })
    })
}

// Tests all columns for students for value in the delegation view and viewall views
// (Note that stud_ids needs to contain all students of a delegation)
export function test_delegation_marks_view_all(stud_ids, columns, value){
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
export function test_staff_summary_values(entries){
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


export const edit_enabled = { 'disabled': false, 'text': 'Edit marks' }
export const edit_disabled = { 'disabled': true, 'text': 'Edit marks' }
export const editall_enabled = { 'disabled': false, 'text': 'Edit all marks' }
export const editall_disabled = { 'disabled': true, 'text': 'Edit all marks' }
export const view_enabled = { 'disabled': false, 'text': 'View marks' }
export const viewall_enabled = { 'disabled': false, 'text': 'View all marks' }

export const submit_action = { 'disabled': false, 'text': 'Submit marks to organizers' }
export const accept_action = { 'disabled': false, 'text': 'Accept marks without moderation' }
export const sign_off_action = { 'disabled': false, 'text': 'Sign off marks' }
export const finalized_action = { 'disabled': true, 'text': 'Marks finalized' }

export const view_only = [view_enabled, edit_disabled]
export const edit_view = [view_enabled, edit_enabled]
export const viewall_only = [viewall_enabled, editall_disabled]
export const editall_viewall = [viewall_enabled, editall_enabled]

export const CHE_stud_ids = [1, 2, 3, 4, 5]
export const CHE_stud_names = [
    "Eugen Pfister (CHE-S-1)",
    "Franz Wrigley Stalder (CHE-S-2)",
    "Bäschteli von Almen (CHE-S-3)",
    "Eduard Ramseier (CHE-S-4)",
    "Fritzli Bühler (CHE-S-5)",
]

export const CHE_studs_final = [
    [CHE_stud_names[0], "-", "-"],
    [CHE_stud_names[1], "-", "-"],
    [CHE_stud_names[2], "-", "-"],
    [CHE_stud_names[3], "-", "-"],
    [CHE_stud_names[4], "-", "-"],
]
export const CHE_studs_editable = [
    [CHE_stud_names[0], edit_view, edit_view],
    [CHE_stud_names[1], edit_view, edit_view],
    [CHE_stud_names[2], edit_view, edit_view],
    [CHE_stud_names[3], edit_view, edit_view],
    [CHE_stud_names[4], edit_view, edit_view],
    ["", editall_viewall, editall_viewall]
]

export const ARM_stud_ids = [10,]
export const ARM_stud_names = ["Deep Thought (ARM-S-42)",]
export const ARM_studs_final = [
    [ARM_stud_names[0], "-", "-"],
]
export const ARM_studs_viewable = [
    [ARM_stud_names[0], view_only, edit_view],
    ["", viewall_only, editall_viewall]
]

export const AUS_stud_ids = [6, 7]
export const AUS_stud_names = [
    "Arthur Dent (AUS-S-1)",
    "Zaphod Beeblebrox (AUS-S-2)",
]
export const AUS_studs_final = [
    [AUS_stud_names[0], "-", "-"],
    [AUS_stud_names[1], "-", "-"],
]
export const AUS_studs_viewable = [
    [AUS_stud_names[0], view_only, edit_view],
    [AUS_stud_names[1], view_only, edit_view],
    ["", viewall_only, editall_viewall]
]

export const AUT_stud_ids = [8, 9]
export const AUT_studs_final = [
    ["Ford Prefect (AUT-S-1)", "20", "20"],
    ["Slartibartfast  (AUT-S-2)", "20", "20"],
]
export const AUT_studs_viewable = [
    ["Ford Prefect (AUT-S-1)", view_only, view_only],
    ["Slartibartfast  (AUT-S-2)", view_only, view_only],
    ["", viewall_only, viewall_only]
]

export const staff_summary_deleg_entries_only_fin = [
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

export const staff_summary_deleg_entries_subm_fin = [
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
