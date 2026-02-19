import SwiftUI
import Combine

class SettingsViewModel: ObservableObject {
    // Basic properties for now
    @Published var testProperty: String = "Hello"
}
