import SwiftUI

/// 👴 Elderly Interface View Model
/// Логика для интерфейса пожилых
class ElderlyInterfaceViewModel: ObservableObject {
    
    @Published var elderlyName: String = "Бабушка"
    @Published var isProtected: Bool = true
    @Published var threatsToday: Int = 0
    
    func callFamily() {
        print("Quick dial family members")
    }
    
    func checkSecurity() {
        print("Show security status")
    }
    
    func openInstructions() {
        print("Show help and instructions")
    }
    
    func triggerSOS() {
        print("Emergency SOS activated!")
        // Вызов экстренных служб
    }
}



