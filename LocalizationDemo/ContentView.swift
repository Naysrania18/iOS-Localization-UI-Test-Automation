import SwiftUI

// The two languages the user can pick. The raw value matches the name of the
// language folder (en.lproj / es.lproj) that holds Localizable.strings.
enum AppLanguage: String, CaseIterable, Identifiable {
    case english = "en"
    case spanish = "es"

    var id: String { rawValue }

    // Shown on the toggle. Each language is written in its own language,
    // so these are NOT looked up in Localizable.strings.
    var displayName: String {
        switch self {
        case .english: return "English"
        case .spanish: return "Español"
        }
    }
}

// Looks up a key in the Localizable.strings of the chosen language.
// Normally iOS picks the language from device settings; here we load the
// language folder ourselves so the user can switch inside the app.
func localized(_ key: String, language: AppLanguage) -> String {
    guard let path = Bundle.main.path(forResource: language.rawValue, ofType: "lproj"),
          let bundle = Bundle(path: path) else {
        return key // Fallback: show the key if the folder is missing.
    }
    return bundle.localizedString(forKey: key, value: key, table: "Localizable")
}

struct ContentView: View {
    // @State: when these change, SwiftUI redraws the screen.
    @State private var language: AppLanguage = .english
    @State private var newItemText = ""
    @State private var items: [String] = []

    var body: some View {
        VStack(spacing: 16) {
            // Screen title. This is the label the language test checks.
            Text(localized("title", language: language))
                .font(.largeTitle)
                .accessibilityIdentifier("titleLabel")

            // Language toggle (segmented control).
            Picker("Language", selection: $language) {
                ForEach(AppLanguage.allCases) { lang in
                    Text(lang.displayName).tag(lang)
                }
            }
            .pickerStyle(.segmented)
            .accessibilityIdentifier("languagePicker")

            // Text field + Add button side by side.
            HStack {
                TextField(localized("placeholder", language: language), text: $newItemText)
                    .textFieldStyle(.roundedBorder)
                    .accessibilityIdentifier("textField")

                Button(localized("add", language: language)) {
                    addItem()
                }
                .buttonStyle(.borderedProminent)
                .accessibilityIdentifier("addButton")
            }

            // The list of added items.
            List(items, id: \.self) { item in
                Text(item)
            }
            .accessibilityIdentifier("itemList")
        }
        .padding()
    }

    // Adds the typed text to the list. Empty (or whitespace-only) input is ignored.
    private func addItem() {
        let trimmed = newItemText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        items.append(trimmed)
        newItemText = ""
    }
}

#Preview {
    ContentView()
}
