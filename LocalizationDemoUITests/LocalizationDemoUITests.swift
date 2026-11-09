import XCTest

final class LocalizationDemoUITests: XCTestCase {

    var app: XCUIApplication!

    // Runs before every test: launch a fresh copy of the app.
    override func setUpWithError() throws {
        continueAfterFailure = false // Stop a test at its first failure.
        app = XCUIApplication()
        app.launch()
    }

    // 1. Adding an item shows it in the list.
    func testAddingItemShowsItInList() throws {
        let textField = app.textFields["textField"]
        XCTAssertTrue(textField.waitForExistence(timeout: 5))

        textField.tap()
        textField.typeText("Buy milk")
        app.buttons["addButton"].tap()

        let itemList = app.collectionViews["itemList"].exists
            ? app.collectionViews["itemList"] : app.tables["itemList"]
        XCTAssertTrue(itemList.staticTexts["Buy milk"].waitForExistence(timeout: 5))
    }

    // 2. The language toggle changes the title from English to Spanish.
    func testLanguageToggleSwitchesTitleToSpanish() throws {
        let title = app.staticTexts["titleLabel"]
        XCTAssertTrue(title.waitForExistence(timeout: 5))
        XCTAssertEqual(title.label, "My To-Do List")

        app.segmentedControls["languagePicker"].buttons["Español"].tap()

        XCTAssertEqual(title.label, "Mi lista de tareas")
    }

    // 3. Tapping Add with no text does nothing.
    func testAddingEmptyTextDoesNothing() throws {
        let addButton = app.buttons["addButton"]
        XCTAssertTrue(addButton.waitForExistence(timeout: 5))

        addButton.tap()

        // No rows should exist anywhere in the app.
        XCTAssertEqual(app.cells.count, 0)
    }
}
