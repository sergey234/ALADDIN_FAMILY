import SwiftUI

/// 👶 Child Interface View Model
/// Логика для детского интерфейса
class ChildInterfaceViewModel: ObservableObject {
    
    @Published var childName: String = "Маша"
    @Published var timeRemaining: String = "45 минут"
    @Published var timeRemainingPercent: Double = 0.25
    
    func openGames() {
        print("Open games section")
    }
    
    func openEducation() {
        print("Open education section")
    }
    
    func openCreativity() {
        print("Open creativity section")
    }
    
    func openVideos() {
        print("Open videos section")
    }
}



