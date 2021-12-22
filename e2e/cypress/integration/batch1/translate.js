

describe('Translation', function() {

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
        cy.route("GET", "/exam/languages/add").as("getLanguagePartial");
        cy.route("POST", "/exam/languages/add").as("postLanguagePartial");
        cy.route("GET", "/exam/languages/edit/*").as("getLanguageEditPartial");
        cy.route("POST", "/exam/languages/edit/*").as("postLanguageEditPartial");
        cy.route("GET", "/exam/translation/add/*").as("getTranslationPartial");
        cy.route("GET", "/exam/translation/list/*").as("getTranslationList");
        cy.route("POST", "/exam/editor/*/question/*/orig/*/lang/*").as("postSaveEditor");
    })

    it('Test create Language', function() {
        cy.login("CHE",'1234')
        cy.visit('exam/languages')

        cy.get('#no-languages-container .btn.btn-lg').click()
        cy.wait("@getLanguagePartial")

        cy.get('#language-modal').should('be.visible')
        //Sometimes cypress continues without writing the whole string, this seems to fix it.
        cy.wait(1500)
        cy.get('#language-modal #id_name').clear().type('Language1')
        cy.wait(1500)
        cy.get('#language-modal #id_name').should('have.value','Language1')
        cy.get('#language-modal #id_style').select('German')
        cy.get('#language-modal .accordion-toggle').click()

        cy.get('#id_direction').should('have.value', 'ltr')
        cy.get('#id_polyglossia').should('have.value', 'german')
        cy.get('#id_polyglossia_options').should('have.value', '')
        cy.get('#id_font').should('have.value', 'notosans')

        //Test some presets
        cy.get('#language-modal #id_style').select('Arabic')
        cy.get('#id_direction').should('have.value', 'rtl')
        cy.get('#id_polyglossia').should('have.value', 'arabic')
        cy.get('#id_polyglossia_options').should('have.value', 'numerals=maghrib')
        cy.get('#id_font').should('have.value', 'notokufiarabic')

        cy.get('#language-modal #id_style').select('Chinese (simplified)')
        cy.get('#id_direction').should('have.value', 'ltr')
        cy.get('#id_polyglossia').should('have.value', 'english')
        cy.get('#id_polyglossia_options').should('have.value', '')
        cy.get('#id_font').should('have.value', 'notosanssc')

        cy.get('#language-modal #id_style').select('Persian')
        cy.get('#id_direction').should('have.value', 'rtl')
        cy.get('#id_polyglossia').should('have.value', 'persian')
        cy.get('#id_polyglossia_options').should('have.value', 'numerals=western')
        cy.get('#id_font').should('have.value', 'notokufiarabic')

        cy.get('#language-modal #id_style').select('English')
        cy.get('#id_direction').should('have.value', 'ltr')
        cy.get('#id_polyglossia').should('have.value', 'english')
        cy.get('#id_polyglossia_options').should('have.value', '')
        cy.get('#id_font').should('have.value', 'notosans')

        //Create
        cy.get('#language-modal').contains("Create").click()
        cy.wait("@postLanguagePartial")

        //Modal should now be closed
        cy.get('#language-modal').should('not.be.visible')
        cy.contains("Language1")
        cy.contains("edit").click()
        cy.wait("@getLanguageEditPartial")

        //Check edit modal
        cy.get('#language-modal').should('be.visible')
        cy.get('#language-modal #id_name').should('have.value', 'Language1')
        cy.get('#id_direction').should('have.value', 'ltr')
        cy.get('#id_polyglossia').should('have.value', 'english')
        cy.get('#id_polyglossia_options').should('have.value', '')
        cy.get('#id_font').should('have.value', 'notosans')

        //Add a translation:
        cy.visit('exam/translation/list')
        cy.wait("@getTranslationList")

        cy.get('#exam-tbody-1 > :nth-child(1) > :nth-child(5)').should('not.contain', 'edit')
        cy.get('h3 > .btn').contains("Add translation").click()
        cy.wait("@getTranslationPartial")

        cy.get('#id_language').select("Language1 (Switzerland)")
        cy.get('#translation-modal .btn').contains("Add").click()
        cy.wait("@getTranslationList")

        cy.get('#exam-tbody-1 > :nth-child(1) > :nth-child(5)').should('contain', 'edit')

    })

    it('Test Add Translation', function() {
        cy.login('ARM','1234')
        cy.visit('exam/translation/list')
        cy.wait("@getTranslationList")

        cy.get('#exam-tbody-1 > :nth-child(1) > :nth-child(5)').should('not.contain', 'edit')
        cy.get('h3 > .btn').contains("Add translation").click()
        cy.wait("@getTranslationPartial")

        cy.get('#translation-modal').should('be.visible')
        cy.get('#id_language').select("TestLanguage (Armenia)")
        cy.get('#translation-modal .btn').contains("Add").click()
        cy.wait("@getTranslationList")

        cy.get(':nth-child(1) > :nth-child(5) > :nth-child(1) > .btn-warning').should("contain", "edit")
        cy.get('#exam-tbody-1 > :nth-child(1) > :nth-child(5) .btn').contains('edit').click()

        //Test whether editor opens
        cy.url().should("contain", "exam/editor/1/question/1/orig/1/lang/5")
    })

    it('Test Basic Editor Functions', function() {
        cy.login("AUS",'1234')
        cy.wait(500)
        cy.visit('exam/editor/1/question/1/orig/1/lang/2')

        //Check loaded data, test typing
        cy.get("#id_q0_ti1").should("have.value", "Translation AUS")
        cy.get("#id_q0_ti1").clear().type("Test1")
        cy.get("#id_q0_ti1").should("have.value","Test1")
        cy.typeCKeditor("id_q0_pa1", "Test2")
        cy.readCKeditor("id_q0_pa1").should("contain", "Test2")

        //Test copy
        cy.typeCKeditor("id_q0_ls2_li1", "Test3")
        cy.readCKeditor("id_q0_ls2_li1").should("contain", "Test3")
        cy.get("#q0_ls2_li1-copy").click({animationDistanceThreshold: 20})
        cy.readCKeditor("id_q0_ls2_li1").should("contain", "You must not open the envelopes containing the problems before the sound signal indicating the beginning of the examination.")

        //Save
        cy.get("#navbar-safe-button").click()
        cy.wait("@postSaveEditor")
        cy.get("#save-status").contains("a few seconds ago")

        //Hard Reload
        cy.visit("exam/editor/1/question/1/orig/1/lang/2")

        //Test values
        cy.get("#id_q0_ti1").should("have.value","Test1")
        cy.readCKeditor("id_q0_pa1").should("contain", "Test2")
        cy.readCKeditor("id_q0_ls2_li1").should("contain", "You must not open the envelopes containing the problems before the sound signal indicating the beginning of the examination.")

        // Test different target
        cy.visit("exam/editor/1/question/1/orig/1/lang/2")
        cy.get("#dropdown-select-target > a").click({animationDistanceThreshold: 20})
        cy.get("#dropdown-select-target").contains("TestLanguage2").click({animationDistanceThreshold: 20})
        cy.url().should("contain","exam/editor/1/question/1/orig/1/lang/3")
        cy.get("#id_q0_ti1").should("have.value","Translation AUS 2")
        cy.get("#id_q0_ti1").clear().type("LAN2_1")
        cy.get("#id_q0_ti1").should("have.value","LAN2_1")
        cy.typeCKeditor("id_q0_pa1", "LAN2_2")
        cy.readCKeditor("id_q0_pa1").should("contain", "LAN2_2")
        //Save
        cy.get("#navbar-safe-button").click()
        cy.wait("@postSaveEditor")

        //Load first language and check that nothing has been saved there
        cy.visit("exam/editor/1/question/1/orig/1/lang/2")
        cy.get("#id_q0_ti1").should("have.value","Test1")
        cy.readCKeditor("id_q0_pa1").should("contain", "Test2")

    })

    it('Test Advanced Editor Functions', function() {
        cy.login("AUS",'1234')
        cy.wait(500)
        cy.visit('exam/editor/1/question/1/orig/1/lang/2')

        // Test compare view
        cy.get("#dropdown-compare-source > button ").click({animationDistanceThreshold: 20})
        cy.get("#dropdown-compare-source ").contains("v1").click({animationDistanceThreshold: 20})
        cy.url().should("contain","exam/editor/1/question/1/orig_diff/1v1/lang/2")
        cy.get("#q0_ti1-original del:nth-of-type(1)").shouldHaveTrimmedText("Version")
        cy.get("#q0_ti1-original del:nth-of-type(2)").shouldHaveTrimmedText("1")
        cy.get("#q0_ti1-original ins:nth-of-type(1)").shouldHaveTrimmedText("Theoretical")
        cy.get("#q0_ti1-original ins:nth-of-type(2)").shouldHaveTrimmedText("Examination (30 points)")

        // Test different source
        cy.visit("exam/editor/1/question/1/orig/1/lang/2")
        cy.get("#dropdown-select-source > a").click({animationDistanceThreshold: 20})
        cy.get("#dropdown-select-source").contains("TestLanguage3 (Austria)").click({animationDistanceThreshold: 20})
        cy.url().should("contain","exam/editor/1/question/1/orig/4/lang/2")
        cy.get("#q0_ti1-original").shouldHaveTrimmedText("Translation AUT")

        // Test edit Language
        cy.visit("exam/editor/1/question/1/orig/1/lang/3")
        cy.wait(500)
        cy.get("#language-settings").click({animationDistanceThreshold: 20})
        cy.wait("@getLanguageEditPartial")

        cy.get("#language-modal").should("be.visible")
        cy.get("#id_name").should("have.value", "TestLanguage2")
        cy.get("#id_style").select("Afrikaans")
        cy.get("#language-modal .btn").contains("Save").click()
        cy.wait("@postLanguageEditPartial")


        cy.visit("exam/editor/1/question/1/orig/1/lang/3")
        cy.get("#language-settings").click({animationDistanceThreshold: 20})
        cy.wait("@getLanguageEditPartial")

        cy.get("#language-modal").should("be.visible")
        cy.get("#id_name").should("have.value", "TestLanguage2")
        cy.get("#id_style").should("have.value", "afrikaans")

        //Test copy all
        cy.visit("exam/editor/1/question/1/orig/1/lang/3")
        cy.get("#copy-all").click({animationDistanceThreshold: 20})
        cy.get("#copy-modal").should("be.visible")
        cy.wait(500)
        cy.get("#copy-modal .btn").contains("Confirm").click()
        cy.get("#id_q0_ti1").should("have.value","General instructions: Theoretical Examination (30 points)")
        cy.readCKeditor("id_q0_ls3_li5").should("contain", "A list of physical constants is given on the next page.")

    })

    it("Test Permissions", function(){
        cy.visit("/")
        cy.login("AUS",'1234')
        // Check whether a translation of another delegation can be edited
        cy.request( {
            failOnStatusCode: false,
            url: 'exam/editor/1/question/1/orig/1/lang/4',
        }).its("status").should('eq', 403)

        // Switch phase
        // Preparation (exam.can_translate = Exam.CAN_TRANSLATE_NOBODY)
        cy.logout()
        cy.login('admin','1234')
        cy.getExamPhaseByName('Theory', "Preparation (Editing)").then(cy.switchExamPhase)

        cy.logout()
        cy.login("AUS", '1234')
        cy.visit('exam/translation/list')
        cy.get('h3 > .btn').should('not.exist')
        cy.get('#exam-tbody-1').should('not.exist')
        cy.visit('exam/submission/list')
        //Check that there are no exams available
        cy.get("#language-list-open").children().should('have.length', 1)
        cy.get("#language-list-open").contains("No open exam.")
        cy.request( {
            failOnStatusCode: false,
            url: 'exam/editor/1/question/1/orig/1/lang/2',
        }).its("status").should('eq', 404)

        // Switch phase
        // Preparation (Translating) (exam.can_translate = Exam.CAN_TRANSLATE_ORGANIZER)
        cy.logout()
        cy.login('admin','1234')
        cy.getExamPhaseByName('Theory', "Preparation (Translating)").then(cy.switchExamPhase)

        cy.logout()
        cy.login("AUS", '1234')
        cy.visit('exam/translation/list')
        cy.get('h3 > .btn').should('not.exist')
        cy.get('#exam-tbody-1').should('not.exist')
        cy.visit('exam/submission/list')
        //Check that there are no exams available
        cy.get("#language-list-open").children().should('have.length', 1)
        cy.get("#language-list-open").contains("No open exam.")
        cy.request( {
            failOnStatusCode: false,
            url: 'exam/editor/1/question/1/orig/1/lang/2',
        }).its("status").should('eq', 404)

    })

})
