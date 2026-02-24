import SwiftUI

// Master Logger for child interface logging
private let logger = MasterLogger.shared

/// 👶 Child Interface View Model
/// Логика для детского интерфейса
class ChildInterfaceViewModel: ObservableObject {
    
    @Published var childName: String = "Маша"
    @Published var timeRemaining: String = "45 минут"
    @Published var timeRemainingPercent: Double = 0.25
    
    func openGames() {
        logger.business("Child opened games section")
        print("Open games section")
    }

    func openEducation() {
        logger.business("Child opened education section")
        print("Open education section")
    }

    func openCreativity() {
        logger.business("Child opened creativity section")
        print("Open creativity section")
    }

    func openVideos() {
        logger.business("Child opened videos section")
        print("Open videos section")
    }
}



