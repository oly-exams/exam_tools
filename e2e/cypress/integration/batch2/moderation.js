
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

    it("Test Reopen Moderation",function(){
        cy.login('admin', '1234')
        // Moderation
        cy.getExamPhaseByName('Theory', "Moderation").then(cy.switchExamPhase)

        cy.logout()
        cy.login('marker', '1234')

        cy.request({
            failOnStatusCode: false,
            url: '/marking/moderate/question/3/delegation/2',
        }).its("status").should('eq', 404)

        cy.logout()
        cy.login("AUS-Leader", '1234')

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
        marking_helpers.test_summary_action_content([marking_helpers.accept_action,])

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
        cy.getExamPhaseByName('Theory', "Delegation Marking").then(cy.switchExamPhase)

        var moderation_pages=[
            '/marking/moderate/question/3/delegation/1',
            '/marking/moderate/question/3/delegation/2',
            '/marking/moderate/question/3/delegation/3',
            '/marking/moderate/question/3/delegation/4'
        ]
        cy.logout()
        cy.login("CHE-Leader", '1234')
        marking_helpers.check_permission_denied_redirect(moderation_pages)

        cy.logout()
        cy.login('marker', '1234')
        cy.request({
            failOnStatusCode: false,
            url: '/marking/moderate/question/3/delegation/1',
        }).its("status").should('eq', 404)

        cy.logout()
        cy.login('admin', '1234')
        // moderation
        cy.getExamPhaseByName('Theory', "Moderation").then(cy.switchExamPhase)

        cy.logout()
        cy.login("CHE-Leader", '1234')
        marking_helpers.check_permission_denied_redirect(moderation_pages)

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
        cy.getExamPhaseByName('Theory', "Moderation").then(cy.switchExamPhase)

        cy.logout()
        cy.login('marker', '1234')
        cy.visit('/marking/moderate/question/3/delegation/1')

        //Check that all fields are empty
        for (let index = 0; index < 13; index++) {
            marking_helpers.check_point_form(10,index,"")
        }

        //Check copy button
        cy.get("#copy-10").click()

        for (let index = 0; index < 13; index++) {
            marking_helpers.check_point_form(10,index,"0")
        }

        marking_helpers.ARM_ppnt_names.forEach((elem, idx)=>{
            cy.get('thead tr th h4').eq(idx).shouldHaveTrimmedText(elem)
        })
        marking_helpers.check_point_form(10,0,'0')
        marking_helpers.edit_point_form(10,0, 0.75)
        marking_helpers.check_point_form(10,0,'0.75')

        // too much
        marking_helpers.edit_point_form(10,1,10)
        // negative
        marking_helpers.edit_point_form(10,2,-1)
        // too many digits
        marking_helpers.edit_point_form(10,3,0.1234)
        // NaN
        marking_helpers.edit_point_form(10,4,"abc")
        //empty
        // cypress doesn't let you type(""), so we need to do it by hand
        cy.get("#id_ppnt-10-5-points").clear()

        // check totals
        // change focus to make sure the totals are calculated
        cy.get("#id_ppnt-10-1-points").focus()
        cy.get("#cell_total_0").shouldHaveTrimmedText('-')

        cy.get("#submit_button").click()

        // check that errors are displayed
        marking_helpers.check_point_form_error(10,1, true, "The number of points cannot exceed the maximum.")
        marking_helpers.check_point_form_error(10,2, true, "Ensure this value is greater than or equal to 0.0.")
        marking_helpers.check_point_form_error(10,3, true, "Ensure that there are no more than 2 decimal places.")
        marking_helpers.check_point_form_error(10,4, true, "Enter a number.")
        marking_helpers.check_point_form_error(10,5, true, "This field is required.")

        // check that there are no errors on other fields
        marking_helpers.check_point_form_error(10,0, false)

        // correct errors:
        marking_helpers.edit_point_form(10,1,0.5)
        marking_helpers.edit_point_form(10,2,0.14)
        marking_helpers.edit_point_form(10,3,0)
        marking_helpers.edit_point_form(10,4,0.75)
        marking_helpers.edit_point_form(10,5,0)
        marking_helpers.edit_point_form(10,10,1)

        // check totals again
        cy.get("#id_ppnt-10-0-points").focus()
        cy.get("#cell_total_0").shouldHaveTrimmedText('3.14')

        // submit again
        cy.get("#submit_button").click()

        cy.url().should('contain', '/marking/moderate/question/3/delegation/1/confirmed')
        // Check total in overview
        cy.get('tbody tr').eq(1).find('td').eq(0).shouldHaveTrimmedText(marking_helpers.ARM_ppnt_names[0])
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
        marking_helpers.test_summary_action_content([marking_helpers.finalized_action,])
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

})
