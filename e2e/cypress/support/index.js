// ***********************************************************
// This example support/index.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands'

// Alternatively you can use CommonJS syntax:
// require('./commands')


beforeEach(() => {
    // this runs prior to every test
    // across all files no matter what
})

describe('Hooks', () => {
    before(() => {
        // runs once before all tests in the block
        cy.exec('mv ../ipho.db ../ipho-initial.db')
    })

    beforeEach(() => {
      // runs before each test in the block
      cy.exec('cp ../ipho-initial.db ../ipho.db')
    })

    afterEach(() => {
      // runs after each test in the block
      cy.exec('rm ../ipho.db')
    })

    after(() => {
      // runs once after all tests in the block
      cy.exec('mv ../ipho-initial.db ../ipho.db')
    })
})
