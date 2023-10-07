

export function check_permission_denied_redirect(paths) {
    Cypress.on('uncaught:exception', (err, runnable) => {
        return false;
      });
    paths.forEach(function (elem, idx) {
        cy.visit(elem)
        cy.url().should('contain', 'accounts/login/?next=' + elem)
    });
}

// Tests the visibility of the marking tab in the delegation marking summary
export function test_marking_summary_visibility(should_exist, participants = []) {
    cy.visit("/marking/")
    cy.get('a[href="#marking"]').click()
    cy.get("#marking").should('be.visible')
    if (should_exist) {
        cy.get('#marking .table-responsive').within(($table) => {
            participants.forEach(function (elem, row) {
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
export function test_final_points_visibility(participant_points) {
    cy.visit("/marking/")
    cy.get('a[href="#final-points"]').click()
    cy.get("#final-points").should('be.visible')
    participant_points.forEach(function (elem, row) {
        elem.forEach(function (val, column) {
            cy.get("#final-points tbody >:nth-child(" + String(row + 2) + ") >:nth-child(" + String(column + 1) + ")").shouldHaveTrimmedText(val)
        });

    });

}

// Tests a selection of marking view/edit views for the delegations
export function test_delegation_view_edit_status_question(question_id, participant_ids = [], edit_status = 200, view_status = 200) {
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

    participant_ids.forEach(function (id, idx) {
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
export function test_delegation_view_edit_status(participant_ids = [], edit_status = 200, view_status = 200) {
    // Check only one question
    var question_ids = [3,]
    question_ids.forEach(function (qid, idx) {
        test_delegation_view_edit_status_question(qid, participant_ids, edit_status, view_status)
    });
}

// Tests a selection of marking edit views for the markers
export function test_staff_edit_status(question_id, delegation_id, participant_ids = [], status = 404) {
    // editall
    cy.request({
        failOnStatusCode: false,
        url: '/marking/official/question/' + question_id + '/delegation/' + delegation_id,
    }).its("status").should('eq', status)

    participant_ids.forEach(function (id, idx) {
        // official
        cy.request({
            failOnStatusCode: false,
            url: '/marking/staff/vO/participant/' + id + '/question/' + question_id + '/edit',
        }).its("status").should('eq', status)
        // delegation
        cy.request({
            failOnStatusCode: false,
            url: '/marking/staff/vD/participant/' + id + '/question/' + question_id + '/edit',
        }).its("status").should('eq', 404)
        // final
        cy.request({
            failOnStatusCode: false,
            url: '/marking/staff/vF/participant/' + id + '/question/' + question_id + '/edit',
        }).its("status").should('eq', 404)
    });

}


// Sets the value of a points form field
export function edit_point_form(ppnt_id, field_id, points){
    if(ppnt_id >= 0){
        cy.get("#id_ppnt-"+ppnt_id+"-"+field_id+"-points").clear().type(points)
    }else{
        cy.get("#id_form-"+field_id+"-points").clear().type(points)
    }
}
// Checks the value of a points form field
export function check_point_form(ppnt_id, field_id, points){
    if(ppnt_id >= 0){
        cy.get("#id_ppnt-"+ppnt_id+"-"+field_id+"-points").should('have.value', points)
    }else{
        cy.get("#id_form-"+field_id+"-points").should('have.value', points)
    }
}
// Checks error messages of a points form field
export function check_point_form_error(ppnt_id, field_id, should_have_err=true, err_msg="", check_error_class=true){
    if(should_have_err){
        if(ppnt_id >= 0){
            if(check_error_class){
                cy.get("#id_ppnt-"+ppnt_id+"-"+field_id+"-points").parent().should('have.class', 'has-error')
            }
            cy.get("#id_ppnt-"+ppnt_id+"-"+field_id+"-points").parent().find('li').should("contain", err_msg)
        }else{
            if(check_error_class){
                cy.get("#id_form-"+field_id+"-points").parent().should('have.class', 'has-error')
            }
            cy.get("#id_form-"+field_id+"-points").parent().find('li').should("contain", err_msg)
        }
    }else{
        if(ppnt_id >= 0){
            cy.get("#id_ppnt-"+ppnt_id+"-"+field_id+"-points").parent().should('not.have.class', 'has-error')
        }else{
            cy.get("#id_form-"+field_id+"-points").parent().should('not.have.class', 'has-error')
        }
    }
}

// Checks the points shown in the delegation view and viewall views
export function check_delegation_points_view(column, points){
    cy.get("#points-table > tbody").within(($tbody)=>{
        points.forEach(function(elem, idx){
            cy.get('> tr').eq(idx).find('td table tr td div').eq(column).shouldHaveTrimmedText(elem)
        });
    })
}

// Checks that all points in column have value in the delegation view and viewall views
export function check_delegation_points_view_value(column, value="-"){
    cy.get("#points-table>tbody").within(($tbody)=>{
        cy.get('>tr').each(($tr)=>{
            cy.wrap($tr).find('>td').eq(column).shouldHaveTrimmedText(value)
        })
    })
}

// Tests all columns for participants for value in the delegation view and viewall views
// (Note that ppnt_ids needs to contain all participants of a delegation)
export function test_delegation_marks_view_all(ppnt_ids, columns, value){
    cy.visit("/marking/detail_all/question/3")
    cy.wait(10)
    cy.wrap(ppnt_ids).each((id, idx)=>{
        // columns contains all subcolumns (off.=0, del.=1, fin.=2) to be tested
        // there are 3 columns per participant, and the first one is number 1
        cy.wrap(columns).each((cnum)=>{
            check_delegation_points_view_value(1 + idx*3 + cnum, value)
        })
    })
    cy.wait(10)
    cy.wrap(ppnt_ids).each(ppnt_id => {
        // Doing the same thing for each participant detail view
        cy.visit("/marking/detail/"+String(ppnt_id)+"/question/3")
        cy.wait(10)
        cy.wrap(columns).each(cnum => {
            check_delegation_points_view_value(1 + cnum, value)
        });


    });
}

// Checks all entries in the staff marking summary
export function test_staff_summary_values(entries){
    cy.get("#summary-table>tbody").within(($table)=>{
        entries.forEach((row, row_idx) => {
            cy.get('>tr').eq(row_idx).within(($row)=>{
                row.forEach((col, col_idx) => {
                    cy.get('>td').eq(col_idx+1).shouldHaveTrimmedText(col)
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
export const accept_action = { 'disabled': false, 'text': 'Sign off official marks without moderation' }
export const sign_off_action = { 'disabled': false, 'text': 'Sign off final marks from moderation' }
export const finalized_action = { 'disabled': true, 'text': 'Final marks signed off' }

export const view_only = [view_enabled, edit_disabled]
export const edit_view = [view_enabled, edit_enabled]
export const viewall_only = [viewall_enabled, editall_disabled]
export const editall_viewall = [viewall_enabled, editall_enabled]

export const CHE_ppnt_ids = [1, 2, 3, 4, 5]
export const CHE_ppnt_names = [
    "Eugen Pfister (CHE-S-1)",
    "Franz Wrigley Stalder (CHE-S-2)",
    "Bäschteli von Almen (CHE-S-3)",
    "Eduard Ramseier (CHE-S-4)",
    "Fritzli Bühler (CHE-S-5)",
]

export const CHE_ppnts_final = [
    [CHE_ppnt_names[0], "-", "-"],
    [CHE_ppnt_names[1], "-", "-"],
    [CHE_ppnt_names[2], "-", "-"],
    [CHE_ppnt_names[3], "-", "-"],
    [CHE_ppnt_names[4], "-", "-"],
]
export const CHE_ppnts_editable = [
    [CHE_ppnt_names[0], edit_view, edit_view],
    [CHE_ppnt_names[1], edit_view, edit_view],
    [CHE_ppnt_names[2], edit_view, edit_view],
    [CHE_ppnt_names[3], edit_view, edit_view],
    [CHE_ppnt_names[4], edit_view, edit_view],
    ["", editall_viewall, editall_viewall]
]

export const ARM_ppnt_ids = [10,]
export const ARM_ppnt_names = ["Deep Thought (ARM-S-42)",]
export const ARM_ppnts_final = [
    [ARM_ppnt_names[0], "-", "-"],
]
export const ARM_ppnts_viewable = [
    [ARM_ppnt_names[0], view_only, edit_view],
    ["", viewall_only, editall_viewall]
]

export const AUS_ppnt_ids = [6, 7]
export const AUS_ppnt_names = [
    "Arthur Dent (AUS-S-1)",
    "Zaphod Beeblebrox (AUS-S-2)",
]
export const AUS_ppnts_final = [
    [AUS_ppnt_names[0], "-", "-"],
    [AUS_ppnt_names[1], "-", "-"],
]
export const AUS_ppnts_viewable = [
    [AUS_ppnt_names[0], view_only, edit_view],
    [AUS_ppnt_names[1], view_only, edit_view],
    ["", viewall_only, editall_viewall]
]

export const AUT_ppnt_ids = [8, 9]
export const AUT_ppnts_final = [
    ["Ford Prefect (AUT-S-1)", "20.00", "20.00"],
    ["Slartibartfast  (AUT-S-2)", "20.00", "20.00"],
]
export const AUT_ppnts_viewable = [
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
