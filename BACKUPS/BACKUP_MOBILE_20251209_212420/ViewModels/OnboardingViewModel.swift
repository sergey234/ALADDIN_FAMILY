import SwiftUI
import Security

/// 👋 Onboarding View Model
/// Логика для экрана онбординга
/// ⚠️ ВНИМАНИЕ: Этот ViewModel НЕ используется в 14_OnboardingScreen.swift
/// Он используется только в других версиях онбординга (если есть)
/// Текущий онбординг использует свой массив pages с 7 страницами!
class OnboardingViewModel: ObservableObject {
    
    @Published var currentPage: Int = 0
    @Published var isCompleted: Bool = false
    
    // ⚠️ УСТАРЕВШЕЕ: Это значение не используется в 14_OnboardingScreen.swift
    // Реальный онбординг использует pages.count (должно быть 7)
    // ❌ НЕ ИСПОЛЬЗУЕТСЯ в текущем онбординге!
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
        // Сохраняем статус онбординга
        // TODO: В будущем заменить на Keychain для безопасности
        UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
    }
}



