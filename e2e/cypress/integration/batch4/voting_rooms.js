

describe('Voting Rooms', function() {

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
        cy.route("GET", /\/poll\/staff\/room\/\d*\/partials\/drafted/).as("getStaffPartialsDrafted");
        cy.route("GET", /\/poll\/staff\/room\/\d*\/partials\/open/).as("getStaffPartialsOpen");
        cy.route("GET", /\/poll\/staff\/room\/\d*\/partials\/closed/).as("getStaffPartialsClosed");
        cy.route("GET", "/poll/voting/**").as("getStaffVoting");
    })

    it('Test Voting', function() {
        cy.login('admin','1234')
        cy.visit('poll/staff/')

        cy.get("#room-dropdown")
        cy.get('#room-dropdown > a').should('be.visible').click()
        cy.get('#room-dropdown ul').should('contain', 'room1').and('contain', 'room2')
        cy.contains('room1').click()
        cy.url().should('contain', 'poll/staff/room/1')


        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen", "@getStaffPartialsClosed"])

        cy.get('#drafted-container #voting-2 .btn-toolbar > :nth-child(3) > .btn').click()
        cy.wait("@getStaffVoting")
        cy.get('[data-min="1"] > .btn').click()
        cy.get('#voting-modal .modal-footer > .btn-primary').click()
        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen"])
        cy.get('#open-container #voting-2')
        cy.get('#drafted-container #voting-2').should('not.exist')

        cy.logout()

        cy.login('ARM-Leader','1234')
        cy.visit('/poll/')

        // Check room 2 first
        cy.get("#room-dropdown")
        cy.get('#room-dropdown > a').should('be.visible').click()
        cy.get('#room-dropdown ul').should('contain', 'room1').and('contain', 'room2')
        cy.contains('room2').click()
        cy.url().should('contain', 'poll/room/2')
        cy.contains('Q1').should('not.exist')
        cy.contains('Q2').should('not.exist')
        cy.contains('Q3').should('not.exist')

        cy.logout()
        cy.login('admin', '1234')

        // open another question in the second room
        cy.visit('/poll/staff/room/2')
        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen", "@getStaffPartialsClosed"])

        cy.get('#drafted-container #voting-4 .btn-toolbar > :nth-child(3) > .btn').click()
        cy.wait("@getStaffVoting")
        cy.get('[data-min="1"] > .btn').click()
        cy.get('#voting-modal .modal-footer > .btn-primary').click()
        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen"])
        cy.get('#open-container #voting-4')
        cy.get('#drafted-container #voting-4').should('not.exist')

        cy.logout()

        cy.login('ARM-Leader','1234')

        // Visit room 1 first
        cy.visit("/poll/room/1")

        // Check available votings
        cy.contains('Q2')
        cy.contains('Q1').should('not.exist')
        cy.contains('Q3').should('not.exist')
        // Check voting rights
        cy.contains('Leader A')
        cy.contains('Leader B')
        // Vote with one leader
        cy.get('#voting-panel-2').get('#div_id_q2-0-choice').contains('weekday').click()
        cy.screenshot('vote-1', {capture: 'runner'})

        cy.get('.btn').contains('Vote').click()
        cy.url().should('contain', 'poll/voted/room/1')
        cy.get('.btn').contains('Continue Voting').click()
        cy.url().should('contain', 'poll/room/1')
        // Check voting rights
        cy.contains('Leader A').should('not.exist')
        cy.contains('Leader B')
        // Vote with the second leader
        cy.get('#voting-panel-2').get('#div_id_q2-0-choice').contains('weekday').click()
        cy.screenshot('vote-2', {capture: 'runner'})

        cy.get('.btn').contains('Vote').click()
        cy.url().should('contain', 'poll/voted/room/1')
        cy.get('.btn').contains('Continue Voting').click()
        cy.contains('no votings')

        // Check second room
        cy.visit('/poll/room/2')

        // Check available votings
        cy.contains('Q1')
        cy.contains('Q2').should('not.exist')
        cy.contains('Q3').should('not.exist')
        // Check voting rights
        cy.contains('Leader A')
        cy.contains('Leader B')
        // Vote with one leader
        cy.get('#id_q4-0-choice_1').click()
        cy.get('.btn').contains('Vote').click()
        cy.url().should('contain', 'poll/voted/room/2')
        cy.get('.btn').contains('Continue Voting').click()
        cy.url().should('contain', 'poll/room/2')
        // Check voting rights
        cy.contains('Leader A').should('not.exist')
        cy.contains('Leader B')
        // Vote with the second leader
        cy.get('#id_q4-0-choice_1').click()
        cy.get('.btn').contains('Vote').click()
        cy.url().should('contain', 'poll/voted/room/2')
        cy.get('.btn').contains('Continue Voting').click()
        cy.contains('no votings')

        cy.logout()

        cy.login('admin','1234')
        // Check results
        cy.visit('poll/voting/detail/2/')
        cy.screenshot('results', {capture: 'runner'})
        cy.get('#choice-4 > .numvotes').shouldHaveTrimmedText('2')
        cy.get('#choice-5 > .numvotes').shouldHaveTrimmedText('0')

        cy.visit('poll/voting/detail/4/')
        cy.get('#choice-9 > .numvotes').shouldHaveTrimmedText('0')
        cy.get('#choice-10 > .numvotes').shouldHaveTrimmedText('2')
        cy.get('#choice-11 > .numvotes').shouldHaveTrimmedText('0')

    })

    it('Test Admin Rooms', function() {
        cy.login('admin','1234')

        // Visit first room and check all votings
        cy.visit('poll/staff/room/1')

        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen", "@getStaffPartialsClosed"])
        cy.get('#drafted-container #voting-1').should('contain', 'Q1')
        cy.get('#drafted-container #voting-2').should('contain', 'Q2')
        cy.get('#closed-container #voting-3').should('contain', 'Q3')
        cy.get('#drafted-container tbody').children().should('have.length', 2)
        cy.get('#open-container tbody').children().should('have.length', 0)
        cy.get('#closed-container tbody').children().should('have.length', 1)

        cy.visit('poll/staff/room/2')

        cy.wait(["@getStaffPartialsDrafted", "@getStaffPartialsOpen", "@getStaffPartialsClosed"])
        cy.get('#drafted-container #voting-4').should('contain', 'Q1')
        cy.get('#drafted-container #voting-5').should('contain', 'Q2')
        cy.get('#closed-container #voting-6').should('contain', 'Q3')
        cy.get('#drafted-container tbody').children().should('have.length', 2)
        cy.get('#open-container tbody').children().should('have.length', 0)
        cy.get('#closed-container tbody').children().should('have.length', 1)
    })

})
