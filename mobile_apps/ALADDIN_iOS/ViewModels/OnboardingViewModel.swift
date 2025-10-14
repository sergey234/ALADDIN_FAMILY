import SwiftUI

/// 👋 Onboarding View Model
/// Логика для экрана онбординга
class OnboardingViewModel: ObservableObject {
    
    @Published var currentPage: Int = 0
    @Published var isCompleted: Bool = false
    
    let totalPages: Int = 4
    
    func nextPage() {
        if currentPage < totalPages - 1 {
            currentPage += 1
        } else {
            completeOnboarding()
        }
    }
    
    func skipOnboarding() {
        completeOnboarding()
    }
    
    private func completeOnboarding() {
        isCompleted = true
        UserDefaults.standard.set(true, forKey: "hasCompletedOnboarding")
    }
}



