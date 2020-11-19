

describe('Polls', function() {

    beforeEach(() => {
        cy.server()
        cy.route("GET", "/poll/staff/partials/drafted").as("getStaffPartialsDrafted");
        cy.route("GET", "/poll/staff/partials/open").as("getStaffPartialsOpen");
        cy.route("GET", "/poll/staff/partials/closed").as("getStaffPartialsClosed");
        cy.route("GET", "/poll/question/**").as("getStaffQuestion");
    })

    it('Test Voting', function() {
        cy.login('admin','1234')
        cy.visit('poll/staff/')

        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen", "@getStaffPartialsClosed"])

        cy.get('#drafted-container #question-2 .btn-toolbar > :nth-child(3) > .btn').click()
        cy.wait("@getStaffQuestion")
        cy.get('[data-min="1"] > .btn').click()
        cy.get('.modal-footer > .btn-primary').click()
        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen"])
        cy.get('#open-container #question-2')
        cy.get('#drafted-container #question-2').should('not.exist')

        cy.logout()

        cy.login('ARM','1234')
        cy.visit('/poll/')
        // Check available questions
        cy.contains('Q2')
        cy.contains('Q1').should('not.exist')
        cy.contains('Q3').should('not.exist')
        // Check voting rights
        cy.contains('Leader A')
        cy.contains('Leader B')
        // Vote with one leader
        cy.get('#id_q2-0-choice_1').click()
        cy.get('.btn').contains('Vote').click()
        cy.url().should('contain', 'poll/voted/')
        cy.get('.btn').contains('Continue Voting').click()
        // Check voting rights
        cy.contains('Leader A').should('not.exist')
        cy.contains('Leader B')
        // Vote with the second leader
        cy.get('#id_q2-0-choice_1').click()
        cy.get('.btn').contains('Vote').click()
        cy.url().should('contain', 'poll/voted/')
        cy.get('.btn').contains('Continue Voting').click()
        cy.contains('no votings')
        cy.logout()

        cy.login('admin','1234')
        cy.visit('poll/question/detail/2/')
        // Check results
        cy.get('#choice-4 > .numvotes').shouldHaveTrimmedText('2')
        cy.get('#choice-5 > .numvotes').shouldHaveTrimmedText('0')

    })

    it('Test Results', function() {
        cy.login('admin','1234')
        cy.visit('poll/question/detail/3/')
        // Check labels
        cy.get('#choice-6-choice-text').shouldHaveTrimmedText('red')
        cy.get('#choice-7-choice-text').shouldHaveTrimmedText('blue')
        cy.get('#choice-8-choice-text').shouldHaveTrimmedText('green')
        // Check results
        cy.get('#choice-6 > .numvotes').shouldHaveTrimmedText('1')
        cy.get('#choice-7 > .numvotes').shouldHaveTrimmedText('2')
        cy.get('#choice-8 > .numvotes').shouldHaveTrimmedText('3')
    })

    it('Test Opening Vote', function() {
        cy.login('admin','1234')
        cy.visit('poll/staff/')

        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen", "@getStaffPartialsClosed"])
        //check # questions
        cy.get('#drafted-container #drafted-questions-table > tbody').children().should('have.length',3)
        cy.get('#open-container #open-questions-table > tbody').children().should('have.length',1)
        cy.get('#closed-container #closed-questions-table > tbody').children().should('have.length',2)

        // Open vote
        cy.get('#drafted-container #question-1 .btn-toolbar > :nth-child(3) > .btn').click()
        cy.wait("@getStaffQuestion")
        cy.get('#question-modal').should('be.visible')
        cy.get('[data-min="1"] > .btn').click()
        cy.get('.modal-footer > .btn-primary').click()
        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen"])

        cy.get('#drafted-container #question-1').should('not.exist')
        // redraft
        cy.get('#open-container #question-1 .btn-toolbar > :nth-child(2) > .btn').click()
        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen"])
        cy.get('#open-container #question-1').should('not.exist')

        //open q1 again
        cy.get('#drafted-container #question-1 .btn-toolbar > :nth-child(3) > .btn').click()
        cy.wait("@getStaffQuestion")
        cy.get('[data-min="1"] > .btn').click()
        cy.get('.modal-footer > .btn-primary').click()
        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen"])

        //open q2
        cy.get('#drafted-container #question-2 .btn-toolbar > :nth-child(3) > .btn').click()
        cy.wait("@getStaffQuestion")
        cy.get('[data-min="1"] > .btn').click()
        cy.get('.modal-footer > .btn-primary').click()
        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen"])
        cy.get('#drafted-container #question-2').should('not.exist')
        // close
        cy.get('#open-container #question-2 .btn-toolbar > :nth-child(3) > .btn').click()
        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen", "@getStaffPartialsClosed"])
        cy.get('#drafted-container #question-2').should('not.exist')
        cy.get('#open-container #question-2').should('not.exist')
        cy.get('#closed-container #question-2')


        cy.login('ARM','1234')
        cy.visit('/poll/')
        // Check if vote is open
        cy.contains('Q1')
        // Wait for vote to close
        cy.wait(60000)
        // Try to vote
        cy.get('#id_q1-0-choice_2').click()
        cy.get('.btn').contains('Vote').click()
        cy.logout()
        cy.login('admin','1234')
        cy.visit('poll/question/detail/1/')
        // Check results
        cy.get('#choice-1 > .numvotes').shouldHaveTrimmedText('0')
        cy.get('#choice-2 > .numvotes').shouldHaveTrimmedText('0')
        cy.get('#choice-3 > .numvotes').shouldHaveTrimmedText('0')
    })

    it("Test Permissions", function(){
        cy.login('AUS','1234')
        // Check whether a delegation can access the staff voting pane
        cy.visit('/poll/staff/')
        cy.url().should('contain', 'accounts/login/?next=/poll/staff/')

        cy.logout()
        cy.login('admin','1234')
        // Check whether an admin can access the delegation voting pane
        cy.request( {
            failOnStatusCode: false,
            url: '/poll/',
        }).its("status").should('eq', 403)
    })

})
