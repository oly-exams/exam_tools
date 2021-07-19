

describe('Polls', function() {

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
        cy.route("GET", /(\/poll\/staff\/room\/\d*\/partials\/drafted)|(\/poll\/staff\/room\/partials\/drafted)/).as("getStaffPartialsDrafted");
        cy.route("GET", /(\/poll\/staff\/room\/\d*\/partials\/open)|(\/poll\/staff\/room\/partials\/open)/).as("getStaffPartialsOpen");
        cy.route("GET", /(\/poll\/staff\/room\/\d*\/partials\/closed)|(\/poll\/staff\/room\/partials\/closed)/).as("getStaffPartialsClosed");
        cy.route("GET", /(\/poll\/voting\/add\/room\/.*)|(\/poll\/voting\/add\/main.*)/).as("getCreateVoting");
        cy.route("GET", "/poll/voting/*/").as("getStaffVoting");
    })

    it.only('Test Voting', function() {
        cy.login('admin','1234')
        cy.visit('poll/staff/')

        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen", "@getStaffPartialsClosed"])

        // Open two votings
        cy.get('#drafted-container #voting-2 .btn-toolbar > :nth-child(3) > .btn').click()
        cy.wait("@getStaffVoting")
        cy.get('[data-min="2"] > .btn').click()
        cy.get('#voting-modal .modal-footer > .btn-primary').click()
        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen"])
        cy.get('#open-container #voting-2')
        cy.get('#drafted-container #voting-2').should('not.exist')

        cy.get('#drafted-container #voting-1 .btn-toolbar > :nth-child(3) > .btn').click()
        cy.wait("@getStaffVoting")
        cy.get('[data-min="2"] > .btn').click()
        cy.get('#voting-modal .modal-footer > .btn-primary').click()
        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen"])
        cy.get('#open-container #voting-1')
        cy.get('#drafted-container #voting-1').should('not.exist')

        cy.logout()

        cy.login('ARM','1234')
        cy.visit('/poll/')
        // Check available votings
        cy.contains('Q2')
        cy.contains('Q1')
        cy.contains('Q3').should('not.exist')
        // Check voting rights
        cy.get('#voting-panel-1').contains('Leader A')
        cy.get('#voting-panel-2').contains('Leader A')
        cy.get('#voting-panel-1').contains('Leader B')
        cy.get('#voting-panel-2').contains('Leader B')

        // Vote with one leader
        //cy.get('#id_q2-0-choice_1').click()
        cy.get('#voting-panel-2').get('#div_id_q2-0-choice').contains('weekday').click()
        cy.screenshot('vote-1', {capture: 'runner'})

        cy.get('#voting-panel-2 .btn').contains('Vote').click()
        cy.url().should('contain', 'poll/voted/')
        cy.get('.btn').contains('Continue Voting').click()
        // Check voting rights
        cy.get('#voting-panel-1').contains('Leader A')
        cy.get('#voting-panel-2').contains('Leader A').should('not.exist')
        cy.get('#voting-panel-1').contains('Leader B')
        cy.get('#voting-panel-2').contains('Leader B')
        // Vote with the second leader
        //cy.get('#id_q2-0-choice_1').click()
        cy.get('#voting-panel-2').get('#div_id_q2-0-choice').contains('weekday').click()
        cy.screenshot('vote-2', {capture: 'runner'})

        cy.get('#voting-panel-2 .btn').contains('Vote').click()
        cy.url().should('contain', 'poll/voted/')
        cy.get('.btn').contains('Continue Voting').click()

        cy.contains('Q1')
        cy.contains('Q2').should('not.exist')
        // Vote on the second voting
        cy.get('#id_q1-0-choice_1').click()
        cy.get('#id_q1-1-choice_1').click()

        cy.get('#voting-panel-1 .btn').contains('Vote').click()
        cy.url().should('contain', 'poll/voted/')
        cy.get('.btn').contains('Continue Voting').click()

        cy.contains('no votings')
        cy.logout()

        cy.login('admin','1234')
        cy.visit('poll/voting/detail/2/')
        // Check results
        cy.screenshot('results', {capture: 'runner'})
        cy.get('#choice-4 > .numvotes').shouldHaveTrimmedText('2')
        cy.get('#choice-5 > .numvotes').shouldHaveTrimmedText('0')

    })

    it('Test Results', function() {
        cy.login('admin','1234')
        cy.visit('poll/voting/detail/3/')
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
        //check # votings
        cy.get('#drafted-container #drafted-votings-table > tbody').children().should('have.length',2)
        cy.get('#open-container #open-votings-table > tbody').children().should('have.length',0)
        cy.get('#closed-container #closed-votings-table > tbody').children().should('have.length',1)

        // Open vote
        cy.get('#drafted-container #voting-1 .btn-toolbar > :nth-child(3) > .btn').click()
        cy.wait("@getStaffVoting")
        cy.get('#voting-modal').should('be.visible')
        cy.get('[data-min="1"] > .btn').click()
        cy.get('#voting-modal .modal-footer > .btn-primary').click()
        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen"])

        cy.get('#drafted-container #voting-1').should('not.exist')
        // redraft
        cy.get('#open-container #voting-1 .btn-toolbar > :nth-child(2) > .btn').click()
        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen"])
        cy.get('#open-container #voting-1').should('not.exist')

        //open q1 again
        cy.get('#drafted-container #voting-1 .btn-toolbar > :nth-child(3) > .btn').click()
        cy.wait("@getStaffVoting")
        cy.get('[data-min="1"] > .btn').click()
        cy.get('#voting-modal .modal-footer > .btn-primary').click()
        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen"])

        //open q2
        cy.get('#drafted-container #voting-2 .btn-toolbar > :nth-child(3) > .btn').click()
        cy.wait("@getStaffVoting")
        cy.get('[data-min="1"] > .btn').click()
        cy.get('#voting-modal .modal-footer > .btn-primary').click()
        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen"])
        cy.get('#drafted-container #voting-2').should('not.exist')
        // close
        cy.get('#open-container #voting-2 .btn-toolbar > :nth-child(3) > .btn').click()
        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen", "@getStaffPartialsClosed"])
        cy.get('#drafted-container #voting-2').should('not.exist')
        cy.get('#open-container #voting-2').should('not.exist')
        cy.get('#closed-container #voting-2')


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
        cy.visit('poll/voting/detail/1/')
        // Check results
        cy.get('#choice-1 > .numvotes').shouldHaveTrimmedText('0')
        cy.get('#choice-2 > .numvotes').shouldHaveTrimmedText('0')
        cy.get('#choice-3 > .numvotes').shouldHaveTrimmedText('0')
    })

    it('Test Feedback in Votes', function() {
        cy.login('admin','1234')
        cy.visit('poll/staff/')

        // Add a voting with feedbacks
        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen", "@getStaffPartialsClosed"])
        cy.get('#drafted-container').contains('Create new').click()

        cy.wait("@getCreateVoting")
        cy.get("#voting-modal").should('be.visible').within(()=>{
            cy.wait(1500)
            cy.get("#id_voting-title").clear().type('Q4')
            cy.wait(1500)
            cy.typeCKeditor("id_voting-content", "Q4 content")
            cy.get("#id_voting-feedbacks").select(['1', '2'])
            cy.get("#id_choices-0-label").type("A")
            cy.get("#id_choices-0-choice_text").type("a")
            cy.get("#id_choices-1-label").type("B")
            cy.get("#id_choices-1-choice_text").type("b")
            cy.get('button[type="submit"]').click()
        })

        cy.wait("@getStaffPartialsDrafted")
        // Check feedbacks in drafted votings
        cy.get("#voting-4 :nth-child(2)").should('contain', "#1").and('contain', "#2")

        cy.visit("/poll/voting/detail/4/")
        cy.get("#feedback-div").should('contain', "#1 (T Q-1)").and('contain', "#2 (T Q-1)")

        cy.visit("/poll/voting/large/4/")
        cy.get("#feedback-table tbody").children().should('have.length', 2)
        cy.get("#feedback-table tbody").within(()=>{
            cy.get('#feedback-1 :nth-child(1)').should('contain', 1)
            cy.get('#feedback-1 :nth-child(2)').should('contain', "ARM")
            cy.get('#feedback-2 :nth-child(1)').should('contain', 2)
            cy.get('#feedback-2 :nth-child(2)').should('contain', "AUS")
        })

        // Open Voting
        cy.visit('poll/staff/')
        cy.get('#drafted-container #voting-4 .btn-toolbar > :nth-child(3) > .btn').click()
        cy.wait("@getStaffVoting")
        cy.get('#voting-modal').should('be.visible')
        cy.get('[data-min="1"] > .btn').click()
        cy.get('#voting-modal .modal-footer > .btn-primary').click()
        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen"])

        // Check feedbacks on delegation page
        cy.logout()
        cy.login('ARM','1234')
        cy.visit('/poll/')
        cy.get('#voting-panel-4').within(()=>{
            cy.contains("Q4")
            cy.get("#feedback-table-4 tbody").children().should('have.length', 2)
            cy.get("#feedback-table-4 tbody").within(()=>{
                cy.get('#feedback-1-voting-4 :nth-child(1)').should('contain', 1)
                cy.get('#feedback-1-voting-4 :nth-child(2)').should('contain', "ARM")
                cy.get('#feedback-2-voting-4 :nth-child(1)').should('contain', 2)
                cy.get('#feedback-2-voting-4 :nth-child(2)').should('contain', "AUS")
            })
        })
    })

    it("Test Permissions", function(){
        cy.login('AUS','1234')
        // Check whether a delegation can access the staff voting pane
        cy.visit('/poll/staff/')
        cy.url().should('contain', 'accounts/login/?next=/poll/staff/')
        cy.visit('/poll/voting/large/1')
        cy.url().should('contain', 'accounts/login/?next=/poll/voting/large/1')
        cy.visit('/poll/voting/detail/1')
        cy.url().should('contain', 'accounts/login/?next=/poll/voting/detail/1')

        cy.logout()
        cy.login('admin','1234')
        // Check whether an admin can access the delegation voting pane
        cy.request( {
            failOnStatusCode: false,
            url: '/poll/',
        }).its("status").should('eq', 403)
    })

})
