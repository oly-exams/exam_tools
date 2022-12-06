
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

    it("Test Official Marking", function () {
        cy.login('admin', '1234')
        // orga marking
        cy.getExamPhaseByName('Theory', "Organizer Marking").then(cy.switchExamPhase)

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
            marking_helpers.CHE_ppnt_names.forEach(function(name, idx){
                cy.get('th').eq(idx+1).find('h4').shouldHaveTrimmedText(name)
            });
        })

        marking_helpers.check_point_form(1,0,'0.00')
        marking_helpers.edit_point_form(1,0, 0.75)
        marking_helpers.check_point_form(1,0,'0.75')

        // too much
        marking_helpers.edit_point_form(1,1,10)
        // negative
        marking_helpers.edit_point_form(1,2,-1)
        // too many digits
        marking_helpers.edit_point_form(1,3,0.1234)
        // NaN
        marking_helpers.edit_point_form(1,4,"abc")
        //empty
        // cypress doesn't let you type(""), so we need to do it by hand
        cy.get("#id_ppnt-1-5-points").clear()

        // add more values for other participants
        marking_helpers.edit_point_form(2,10, 1)
        marking_helpers.edit_point_form(3,10, 1)
        marking_helpers.edit_point_form(4,10, 1)
        marking_helpers.edit_point_form(5,10, 1)

        // check totals
        // change focus to make sure the totals are calculated
        cy.get("#id_ppnt-1-5-points").focus()
        cy.get("#cell_total_0").shouldHaveTrimmedText('-')
        cy.get("#cell_total_1").shouldHaveTrimmedText('1.00')
        cy.get("#cell_total_2").shouldHaveTrimmedText('1.00')
        cy.get("#cell_total_3").shouldHaveTrimmedText('1.00')
        cy.get("#cell_total_4").shouldHaveTrimmedText('1.00')

        cy.get("#submit_button").click()

        // check that errors are displayed
        marking_helpers.check_point_form_error(1,1, true, "The number of points cannot exceed the maximum.")
        marking_helpers.check_point_form_error(1,2, true, "The number of points cannot be negative.")
        marking_helpers.check_point_form_error(1,3, true, "Ensure that there are no more than 2 decimal places.")
        marking_helpers.check_point_form_error(1,4, true, "Enter a number.")
        marking_helpers.check_point_form_error(1,5, true, "This field is required.")

        // check that there are no errors on other fields
        marking_helpers.check_point_form_error(1,0, false)
        marking_helpers.check_point_form_error(2,10, false)
        marking_helpers.check_point_form_error(3,10, false)
        marking_helpers.check_point_form_error(4,10, false)
        marking_helpers.check_point_form_error(5,10, false)

        // correct errors:
        marking_helpers.edit_point_form(1,1,0.5)
        marking_helpers.edit_point_form(1,2,0.14)
        marking_helpers.edit_point_form(1,3,0)
        marking_helpers.edit_point_form(1,4,0.75)
        marking_helpers.edit_point_form(1,5,0)
        marking_helpers.edit_point_form(1,10,1)

        // check totals again
        cy.get("#id_ppnt-1-0-points").focus()
        cy.get("#cell_total_0").shouldHaveTrimmedText('3.14')
        cy.get("#cell_total_1").shouldHaveTrimmedText('1.00')
        cy.get("#cell_total_2").shouldHaveTrimmedText('1.00')
        cy.get("#cell_total_3").shouldHaveTrimmedText('1.00')
        cy.get("#cell_total_4").shouldHaveTrimmedText('1.00')

        // submit again
        cy.get("#submit_button").click()

        cy.url().should('contain', '/marking/official/question/3/delegation/4/confirmed')

        var CHE_ppnt_points = [
            [marking_helpers.CHE_ppnt_names[0], '3.14'],
            [marking_helpers.CHE_ppnt_names[1], '1.00'],
            [marking_helpers.CHE_ppnt_names[2], '1.00'],
            [marking_helpers.CHE_ppnt_names[3], '1.00'],
            [marking_helpers.CHE_ppnt_names[4], '1.00'],
        ]

        cy.get('tbody').within(($tbody)=>{
            CHE_ppnt_points.forEach(function(elem, idx){
                cy.get('tr').eq(idx+1).find('>td').eq(0).shouldHaveTrimmedText(elem[0])
                cy.get('tr').eq(idx+1).find('>td').eq(1).shouldHaveTrimmedText(elem[1])
            });
        })

        cy.visit('/marking/official/question/3/delegation/4')
        // check the points edited before
        marking_helpers.check_point_form(1,1,'0.50')
        marking_helpers.check_point_form(1,2,'0.14')
        marking_helpers.check_point_form(1,3,'0.00')
        marking_helpers.check_point_form(1,4,'0.75')
        marking_helpers.check_point_form(1,5,'0.00')
        marking_helpers.check_point_form(2,10,'1.00')
        marking_helpers.check_point_form(3,10,'1.00')
        marking_helpers.check_point_form(4,10,'1.00')
        marking_helpers.check_point_form(5,10,'1.00')

    })

    it("Test Admin Marking Summary", function () {
        cy.login('admin', '1234')
        // orga marking
        cy.getExamPhaseByName('Theory', "Organizer Marking").then(cy.switchExamPhase)

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

        cy.url().should('contain', "/marking/staff/vO/participant/10/question/3/edit")

        // check/edit some points
        marking_helpers.edit_point_form(-1, 0, "0.00")
        marking_helpers.edit_point_form(-1,0, 0.75)
        marking_helpers.check_point_form(-1,0,'0.75')

        // too much
        marking_helpers.edit_point_form(-1,1,10)
        // negative
        marking_helpers.edit_point_form(-1,2,-1)
        // too many digits
        marking_helpers.edit_point_form(-1,3,0.1234)
        // NaN
        marking_helpers.edit_point_form(-1,4,"abc")
        //empty
        // cypress doesn't let you type(""), so we need to do it by hand
        cy.get("#id_form-5-points").clear()

        cy.get('input[type="submit"]').click()

        // check that errors are displayed
        marking_helpers.check_point_form_error(-1,1, true, "The number of points cannot exceed the maximum.", false)
        marking_helpers.check_point_form_error(-1,2, true, "The number of points cannot be negative.", false)
        marking_helpers.check_point_form_error(-1,3, true, "Ensure that there are no more than 2 decimal places.", false)
        marking_helpers.check_point_form_error(-1,4, true, "Enter a number.", false)
        marking_helpers.check_point_form_error(-1,5, true, "This field is required.", false)

        // correct errors:
        marking_helpers.edit_point_form(-1,1,0.5)
        marking_helpers.edit_point_form(-1,2,0.14)
        marking_helpers.edit_point_form(-1,3,0)
        marking_helpers.edit_point_form(-1,4,0.75)
        marking_helpers.edit_point_form(-1,5,0)
        marking_helpers.edit_point_form(-1,10,1)

        // submit again
        cy.get('input[type="submit"]').click()
        cy.get(".alert-success").should('contain', "Points have been saved.")

        // hard reload to check values
        cy.visit("/marking/staff/vO/participant/10/question/3/edit")

        // check values
        marking_helpers.check_point_form(-1,1,"0.50")
        marking_helpers.check_point_form(-1,2,"0.14")
        marking_helpers.check_point_form(-1,3,"0.00")
        marking_helpers.check_point_form(-1,4,"0.75")
        marking_helpers.check_point_form(-1,5,"0.00")
        marking_helpers.check_point_form(-1,10,"1.00")

    })


    it("Test Delegation Edit", function () {
        cy.login('admin', '1234')
        // deleg marking
        cy.getExamPhaseByName('Theory', "Delegation Marking").then(cy.switchExamPhase)

        cy.logout()
        cy.login('CHE', '1234')
        cy.visit('/marking/detail/1/question/3/edit')

        // check/edit some points
        marking_helpers.edit_point_form(-1, 0, "0.80")
        marking_helpers.edit_point_form(-1,0, 0.75)
        marking_helpers.check_point_form(-1,0,'0.75')

        // too much
        marking_helpers.edit_point_form(-1,1,10)
        // negative
        marking_helpers.edit_point_form(-1,2,-1)
        // too many digits
        marking_helpers.edit_point_form(-1,3,0.1234)
        // NaN
        marking_helpers.edit_point_form(-1,4,"abc")
        //empty
        // cypress doesn't let you type(""), so we need to do it by hand
        cy.get("#id_form-5-points").clear()

        cy.get('input[type="submit"]').click()

        // check that errors are displayed (there are no error classes in this view, so we don't check for them)
        marking_helpers.check_point_form_error(-1,1, true, "The number of points cannot exceed the maximum.", false)
        marking_helpers.check_point_form_error(-1,2, true, "The number of points cannot be negative.", false)
        marking_helpers.check_point_form_error(-1,3, true, "Ensure that there are no more than 2 decimal places.", false)
        marking_helpers.check_point_form_error(-1,4, true, "Enter a number.", false)
        marking_helpers.check_point_form_error(-1,5, true, "This field is required.", false)

        // correct errors:
        marking_helpers.edit_point_form(-1,1,0.5)
        marking_helpers.edit_point_form(-1,2,0.14)
        marking_helpers.edit_point_form(-1,3,0)
        marking_helpers.edit_point_form(-1,4,0.75)
        marking_helpers.edit_point_form(-1,5,0)

        // submit again
        cy.get('input[type="submit"]').click()
        cy.get(".alert-success").should('contain', "Points have been saved.")

        // hard reload to check values
        cy.visit("/marking/detail/1/question/3/edit")

        // check values
        marking_helpers.check_point_form(-1,0,"0.75")
        marking_helpers.check_point_form(-1,1,"0.50")
        marking_helpers.check_point_form(-1,2,"0.14")
        marking_helpers.check_point_form(-1,3,"0.00")
        marking_helpers.check_point_form(-1,4,"0.75")
        marking_helpers.check_point_form(-1,5,"0.00")

        //check values also in readonly view
        cy.visit("/marking/detail/1/question/3")

        // Delegation is the second column
        marking_helpers.check_delegation_points_view(1,["0.75", "0.50", "0.14", "0.00", "0.75", "0.00"])

    })

    it("Test Delegation Edit All", function () {
        cy.login('admin', '1234')
        // deleg marking
        cy.getExamPhaseByName('Theory', "Delegation Marking").then(cy.switchExamPhase)

        cy.logout()
        cy.login('CHE', '1234')
        cy.visit('/marking/detail_all/question/3/edit')

        marking_helpers.check_point_form(-1,0,'0.80')
        marking_helpers.edit_point_form(-1,0, 0.75)
        marking_helpers.check_point_form(-1,0,'0.75')

        // too much
        marking_helpers.edit_point_form(-1,5,10)
        // negative
        marking_helpers.edit_point_form(-1,10,-1)
        // too many digits
        marking_helpers.edit_point_form(-1,15,0.1234)
        // NaN
        marking_helpers.edit_point_form(-1,20,"abc")
        //empty
        // cypress doesn't let you type(""), so we need to do it by hand
        cy.get("#id_form-25-points").clear()

        // add more values for other participants
        marking_helpers.edit_point_form(-1,1, 0.17)
        marking_helpers.edit_point_form(-1,2, 0.17)
        marking_helpers.edit_point_form(-1,3, 0.17)
        marking_helpers.edit_point_form(-1,4, 0.17)


        cy.get('input[type="submit"]').click()

        // check that errors are displayed
        marking_helpers.check_point_form_error(-1,5, true, "The number of points cannot exceed the maximum.")
        marking_helpers.check_point_form_error(-1,10, true, "The number of points cannot be negative.")
        marking_helpers.check_point_form_error(-1,15, true, "Ensure that there are no more than 2 decimal places.")
        marking_helpers.check_point_form_error(-1,20, true, "Enter a number.")
        marking_helpers.check_point_form_error(-1,25, true, "This field is required.")


        // check that there are no errors on other fields
        marking_helpers.check_point_form_error(-1,0, false)
        marking_helpers.check_point_form_error(-1,1, false)
        marking_helpers.check_point_form_error(-1,2, false)
        marking_helpers.check_point_form_error(-1,3, false)
        marking_helpers.check_point_form_error(-1,4, false)

        // correct errors:
        marking_helpers.edit_point_form(-1,5,0.5)
        marking_helpers.edit_point_form(-1,10,0.14)
        marking_helpers.edit_point_form(-1,15,0)
        marking_helpers.edit_point_form(-1,20,0.75)
        marking_helpers.edit_point_form(-1,25,0)

        // submit again
        cy.get('input[type="submit"]').click()

        cy.get(".alert-success").should('contain', "Points have been saved.")

        // hard reload to check values
        cy.visit("/marking/detail_all/question/3/edit")

        // check values
        marking_helpers.check_point_form(-1,0,"0.75")
        marking_helpers.check_point_form(-1,5,"0.50")
        marking_helpers.check_point_form(-1,10,"0.14")
        marking_helpers.check_point_form(-1,15,"0.00")
        marking_helpers.check_point_form(-1,20,"0.75")
        marking_helpers.check_point_form(-1,25,"0.00")
        marking_helpers.check_point_form(-1,1,"0.17")
        marking_helpers.check_point_form(-1,2,"0.17")
        marking_helpers.check_point_form(-1,3,"0.17")
        marking_helpers.check_point_form(-1,4,"0.17")
        //check values also in readonly view
        cy.visit("/marking/detail_all/question/3")

        // CHE-S-1 Del. is column 2
        marking_helpers.check_delegation_points_view(1,["0.75", "0.50", "0.14", "0.00", "0.75", "0.00"])
        // CHE-S-3 Del. is column 5, CHE-S-3 clumn 8,...
        marking_helpers.check_delegation_points_view(4,["0.17",])
        marking_helpers.check_delegation_points_view(7,["0.17",])
        marking_helpers.check_delegation_points_view(10,["0.17",])
        marking_helpers.check_delegation_points_view(13,["0.17",])

    })


    it("Test Delegation Actions",function(){
        cy.login('admin', '1234')
        // deleg Marking
        cy.getExamPhaseByName('Theory', "Delegation Marking").then(cy.switchExamPhase)

        cy.logout()
        cy.login('CHE', '1234')

        cy.visit("/marking/")
        cy.get('a[href="#marking"]').click()
        cy.get("#marking").should('be.visible')
        cy.get('#marking .table-responsive tbody >:last-child >:nth-child(2) .btn').should('contain', "Submit marks to organizers").click()
        cy.url().should('contain', '/marking/confirm/3')
        cy.get("#confirm-table").within(($table)=>{
            // Check just some entries
            marking_helpers.CHE_ppnt_names.forEach((elem, idx)=>{
                cy.get('thead tr th').eq(1+idx).shouldHaveTrimmedText(elem)
            })

            cy.get('>tbody>tr').eq(0).find('>td').eq(0).shouldHaveTrimmedText("A.1")
            cy.get('>tbody>tr').eq(1).find('>td').eq(0).shouldHaveTrimmedText("A.2")
            cy.get('>tbody>tr').eq(1).find('>td').eq(1).shouldHaveTrimmedText("0.50")
            cy.get('>tbody>tr').eq(1).find('>td').eq(2).shouldHaveTrimmedText("0.50")
            cy.get('>tbody>tr').eq(1).find('>td').eq(3).shouldHaveTrimmedText("0.50")
            cy.get('>tbody>tr').eq(1).find('>td').eq(4).shouldHaveTrimmedText("0.50")
            cy.get('>tbody>tr').eq(1).find('>td').eq(5).shouldHaveTrimmedText("0.50")

            cy.get('>tfoot>tr').eq(0).find('>td').eq(0).find('b').shouldHaveTrimmedText("Total:")
            cy.get('>tfoot>tr').eq(0).find('>td').eq(1).find('b').shouldHaveTrimmedText("10.00")
            cy.get('>tfoot>tr').eq(0).find('>td').eq(2).find('b').shouldHaveTrimmedText("10.00")
            cy.get('>tfoot>tr').eq(0).find('>td').eq(3).find('b').shouldHaveTrimmedText("10.00")
            cy.get('>tfoot>tr').eq(0).find('>td').eq(4).find('b').shouldHaveTrimmedText("10.00")
            cy.get('>tfoot>tr').eq(0).find('>td').eq(5).find('b').shouldHaveTrimmedText("10.00")
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
        marking_helpers.test_summary_action_content([marking_helpers.accept_action,])
        cy.get('#marking .table-responsive tbody >:last-child >:nth-child(2) .btn').should('contain', "Accept marks").click()
        cy.url().should('contain', '/marking/confirm/final/3')
        cy.get("div.container h2").should('contain', "Sign off final points")
        cy.get("#confirm-table").within(($table)=>{
            // Check just some entries
            marking_helpers.CHE_ppnt_names.forEach((elem, idx)=>{
                cy.get('thead tr th').eq(1+idx).shouldHaveTrimmedText(elem)
            })

            cy.get('>tbody>tr').eq(0).find('>td').eq(0).shouldHaveTrimmedText("A.1")
            cy.get('>tbody>tr').eq(1).find('>td').eq(0).shouldHaveTrimmedText("A.2")
            cy.get('>tbody>tr').eq(1).find('>td').eq(1).shouldHaveTrimmedText("0.00")
            cy.get('>tbody>tr').eq(1).find('>td').eq(2).shouldHaveTrimmedText("0.00")
            cy.get('>tbody>tr').eq(1).find('>td').eq(3).shouldHaveTrimmedText("0.00")
            cy.get('>tbody>tr').eq(1).find('>td').eq(4).shouldHaveTrimmedText("0.00")
            cy.get('>tbody>tr').eq(1).find('>td').eq(5).shouldHaveTrimmedText("0.00")

            cy.get('>tfoot>tr').eq(0).find('>td').eq(0).find('b').shouldHaveTrimmedText("Total:")
            cy.get('>tfoot>tr').eq(0).find('>td').eq(1).find('b').shouldHaveTrimmedText("0.00")
            cy.get('>tfoot>tr').eq(0).find('>td').eq(2).find('b').shouldHaveTrimmedText("0.00")
            cy.get('>tfoot>tr').eq(0).find('>td').eq(3).find('b').shouldHaveTrimmedText("0.00")
            cy.get('>tfoot>tr').eq(0).find('>td').eq(4).find('b').shouldHaveTrimmedText("0.00")
            cy.get('>tfoot>tr').eq(0).find('>td').eq(5).find('b').shouldHaveTrimmedText("0.00")
        })

        cy.get('#confirm-alert').should('have.class', 'alert-warning').and('contain', "I accept the final markings.")
        cy.get('#confirm-alert input[type="checkbox"]').check()
        cy.get('#reject-button').should('not.exist')
        cy.get('#confirm-button').should('contain', "Accept").click()
        cy.url().should('contain', '/marking/').and('not.contain', 'confirm/final/3')
        cy.get('a[href="#marking"]').click()
        cy.get("#marking").should('be.visible')
        marking_helpers.test_summary_action_content([marking_helpers.finalized_action,])

        marking_helpers.test_delegation_marks_view_all(marking_helpers.CHE_ppnt_ids.slice(0,1), [0,], "0.00")

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
            marking_helpers.AUS_ppnt_names.forEach((elem, idx)=>{
                cy.get('thead tr th').eq(1+idx).shouldHaveTrimmedText(elem)
            })

            cy.get('>tbody>tr').eq(0).find('>td').eq(0).shouldHaveTrimmedText("A.1")
            cy.get('>tbody>tr').eq(1).find('>td').eq(0).shouldHaveTrimmedText("A.2")
            cy.get('>tbody>tr').eq(1).find('>td').eq(1).shouldHaveTrimmedText("0.50")
            cy.get('>tbody>tr').eq(1).find('>td').eq(2).shouldHaveTrimmedText("0.50")


            cy.get('>tfoot>tr').eq(0).find('>td').eq(0).find('b').shouldHaveTrimmedText("Total:")
            cy.get('>tfoot>tr').eq(0).find('>td').eq(1).find('b').shouldHaveTrimmedText("10.00")
            cy.get('>tfoot>tr').eq(0).find('>td').eq(2).find('b').shouldHaveTrimmedText("10.00")
        })

        cy.get('#confirm-alert').should('have.class', 'alert-info').and('contain', "I accept the final markings.")
        cy.get('#confirm-alert input[type="checkbox"]').check()
        cy.get('#reject-button').should('contain', "Reopen moderation")
        cy.get('#confirm-button').should('contain', "Accept").click()

        cy.url().should('contain', '/marking/').and('not.contain', 'confirm/final/3')
        cy.get('a[href="#marking"]').click()
        cy.get("#marking").should('be.visible')
        marking_helpers.test_summary_action_content([marking_helpers.finalized_action,])
        // check marks on viewall
        cy.visit('/marking/detail_all/question/3')
        cy.get("#points-table >tfoot>tr").within(($tr)=>{
            cy.get('>td').eq(3).find('strong').shouldHaveTrimmedText('10.00')
            cy.get('>td').eq(6).find('strong').shouldHaveTrimmedText('10.00')
        })
    })

    it("Test Delegation Actions (Submit Only)",function(){
        cy.login('admin', '1234')
        // deleg Marking (submit only)
        cy.getExamPhaseByName('Theory', "Delegation Marking (Submit only)").then(cy.switchExamPhase)

        cy.logout()
        cy.login('CHE', '1234')

        cy.visit("/marking/")
        cy.get('a[href="#marking"]').click()
        cy.get("#marking").should('be.visible')
        cy.get('#marking .table-responsive tbody >:last-child >:nth-child(2) .btn').should('contain', "Submit marks to organizers").click()
        cy.url().should('contain', '/marking/confirm/3')
        cy.get("#confirm-table").within(($table)=>{
            // Check just some entries
            marking_helpers.CHE_ppnt_names.forEach((elem, idx)=>{
                cy.get('thead tr th').eq(1+idx).shouldHaveTrimmedText(elem)
            })

            cy.get('>tbody>tr').eq(0).find('>td').eq(0).shouldHaveTrimmedText("A.1")
            cy.get('>tbody>tr').eq(1).find('>td').eq(0).shouldHaveTrimmedText("A.2")
            cy.get('>tbody>tr').eq(1).find('>td').eq(1).shouldHaveTrimmedText("0.50")
            cy.get('>tbody>tr').eq(1).find('>td').eq(2).shouldHaveTrimmedText("0.50")
            cy.get('>tbody>tr').eq(1).find('>td').eq(3).shouldHaveTrimmedText("0.50")
            cy.get('>tbody>tr').eq(1).find('>td').eq(4).shouldHaveTrimmedText("0.50")
            cy.get('>tbody>tr').eq(1).find('>td').eq(5).shouldHaveTrimmedText("0.50")

            cy.get('>tfoot>tr').eq(0).find('>td').eq(0).find('b').shouldHaveTrimmedText("Total:")
            cy.get('>tfoot>tr').eq(0).find('>td').eq(1).find('b').shouldHaveTrimmedText("10.00")
            cy.get('>tfoot>tr').eq(0).find('>td').eq(2).find('b').shouldHaveTrimmedText("10.00")
            cy.get('>tfoot>tr').eq(0).find('>td').eq(3).find('b').shouldHaveTrimmedText("10.00")
            cy.get('>tfoot>tr').eq(0).find('>td').eq(4).find('b').shouldHaveTrimmedText("10.00")
            cy.get('>tfoot>tr').eq(0).find('>td').eq(5).find('b').shouldHaveTrimmedText("10.00")
        })

        cy.get('#confirm-alert').should('have.class', 'alert-info').and('contain', "I confirm my version of the markings.")
        cy.get('#reject-button').should('not.exist')
        cy.get('#confirm-alert input[type="checkbox"]').check()
        cy.get('#confirm-button').should('contain', "Confirm").click()

        cy.url().should('contain', '/marking/').and('not.contain', 'confirm/3')
        cy.get('a[href="#marking"]').click()
        cy.get("#marking").should('be.visible')
        marking_helpers.test_summary_action_content_none(1)

        cy.visit('/marking/confirm/final/3')
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

        //check a participant of another delegation
        cy.request({
            failOnStatusCode: false,
            url: '/marking/detail/10/question/3',
        }).its("status").should('eq', 403)

        //check staff pages
        cy.request({
            failOnStatusCode: false,
            url: '/marking/progress',
        }).its("status").should('eq', 403)

        marking_helpers.check_permission_denied_redirect(admin_only_pages.concat(marker_only_pages))

        cy.logout()
        cy.login('admin', '1234')

        marking_helpers.check_permission_denied_redirect(marker_only_pages.concat(deleg_pages))

        cy.logout()
        cy.login('marker', '1234')

        marking_helpers.check_permission_denied_redirect(admin_only_pages.concat(deleg_pages))

    })
})
