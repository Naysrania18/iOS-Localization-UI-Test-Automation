# iOS Localization & UI Test Automation

A tiny SwiftUI to-do list that shows localization. Type an item, tap **Add**, and
switch the UI between **English** and **Español** with the toggle at the top.
Strings live in `en.lproj/Localizable.strings` and `es.lproj/Localizable.strings`.

Target: Xcode 15+, iOS 17 simulator, Swift 5.9.

## File structure

```
iOSLocalizationUITestAutomation/
├── README.md
├── project.yml                      # XcodeGen spec (creates the .xcodeproj)
├── iOSLocalizationUITestAutomation/                # app target
│   ├── iOSLocalizationUITestAutomationApp.swift    # app entry point
│   ├── ContentView.swift            # the screen + language lookup
│   ├── en.lproj/Localizable.strings
│   └── es.lproj/Localizable.strings
└── iOSLocalizationUITestAutomationUITests/         # UI test target
    └── iOSLocalizationUITestAutomationUITests.swift
```

Accessibility identifiers: `textField`, `addButton`, `itemList`, plus
`languagePicker` and `titleLabel` (used by the language test).

## Open in Xcode

Option A (XcodeGen, quickest):
1. `brew install xcodegen`
2. In this folder run `xcodegen generate`
3. Open `iOSLocalizationUITestAutomation.xcodeproj`

Option B (manual):
1. Xcode > File > New > Project > iOS App (Interface: SwiftUI, Language: Swift), name it `iOSLocalizationUITestAutomation`.
2. Replace the generated Swift files with the ones here and add the two `.lproj` folders
   (tick "Copy items" and your app target).
3. File > New > Target > **UI Testing Bundle**, name it `iOSLocalizationUITestAutomationUITests`, and replace its test file.

## Run the tests

- In Xcode: pick an iPhone simulator (iOS 17), press **Cmd+U**, or click the diamond next to a test.
- Command line:
  ```
  xcodebuild test -scheme iOSLocalizationUITestAutomation \
    -destination 'platform=iOS Simulator,name=iPhone 15'
  ```

## The tests

1. `testAddingItemShowsItInList`: type "Buy milk", tap Add, check it appears in the list.
2. `testLanguageToggleSwitchesTitleToSpanish`: the title changes from "My To-Do List" to "Mi lista de tareas".
3. `testAddingEmptyTextDoesNothing`: Add with no text leaves the list empty.

## Note

This was written without access to Xcode (on Windows), so it hasn't been built or run.
If a test fails on first run, the most likely cause is the list's element type
(`tables` vs `collectionViews`) in your iOS version; check with Xcode's Accessibility Inspector.

## AI-assisted localization tools (`ai-localization-tools/`)

A separate Python + LLM add-on (runs on Windows, no Mac needed) that sits alongside
the Swift app and XCUITests without changing them:

- `generate_test_cases.py`: asks Claude to suggest localization UI test case ideas for each string
  in `Localizable.strings`, and saves them to `generated_test_cases.md`.
- `check_translations.py`: runs simple checks, then asks Claude to review the Spanish translations
  against the English source and flag suspect ones.

Both need an `ANTHROPIC_API_KEY`. The LLM output is assistive only and must be human-reviewed.
See [`ai-localization-tools/README.md`](ai-localization-tools/README.md) for setup and usage.
