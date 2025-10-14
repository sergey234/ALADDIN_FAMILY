import SwiftUI

/**
 * 🧭 Navigation Manager
 * Управление навигацией в приложении
 * Централизованный роутер для всех переходов
 */

class NavigationManager: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var path = NavigationPath()
    
    // MARK: - Navigation Methods
    
    /**
     * Перейти к экрану
     */
    func navigate(to destination: NavigationDestination) {
        path.append(destination)
    }
    
    /**
     * Вернуться назад
     */
    func goBack() {
        if !path.isEmpty {
            path.removeLast()
        }
    }
    
    /**
     * Вернуться на главную (очистить стек)
     */
    func goToRoot() {
        path = NavigationPath()
    }
    
    /**
     * Вернуться на N экранов назад
     */
    func goBack(steps: Int) {
        for _ in 0..<steps {
            if !path.isEmpty {
                path.removeLast()
            }
        }
    }
    
    // MARK: - Convenience Methods
    
    func openFamily() {
        navigate(to: .family)
    }
    
    func openVPN() {
        navigate(to: .vpn)
    }
    
    func openAnalytics() {
        navigate(to: .analytics)
    }
    
    func openAI() {
        navigate(to: .aiAssistant)
    }
    
    func openParentalControl() {
        navigate(to: .parentalControl)
    }
    
    func openSettings() {
        navigate(to: .settings)
    }
    
    func openTariffs() {
        navigate(to: .tariffs)
    }
    
    func openProfile() {
        navigate(to: .profile)
    }
    
    func openNotifications() {
        navigate(to: .notifications)
    }
    
    func openSupport() {
        navigate(to: .support)
    }
    
    func openLogin() {
        navigate(to: .login)
    }
    
    func openRegistration() {
        navigate(to: .registration)
    }
    
    func openForgotPassword() {
        navigate(to: .forgotPassword)
    }
    
    func openPrivacyPolicy() {
        navigate(to: .privacyPolicy)
    }
    
    func openTermsOfService() {
        navigate(to: .termsOfService)
    }
    
    func openDevices() {
        navigate(to: .devices)
    }
    
    func openReferral() {
        navigate(to: .referral)
    }
    
    func openDeviceDetail(deviceId: String) {
        navigate(to: .deviceDetail(deviceId: deviceId))
    }
    
    func openFamilyChat(memberId: String) {
        navigate(to: .familyChat(memberId: memberId))
    }
    
    func openVPNEnergyStats() {
        navigate(to: .vpnEnergyStats)
    }
    
    func openPaymentQR(tariff: Tariff) {
        navigate(to: .paymentQR(tariff: tariff))
    }
}

// MARK: - Navigation Destinations

enum NavigationDestination: Hashable {
    // Основные экраны (14)
    case main
    case family
    case vpn
    case analytics
    case aiAssistant
    case parentalControl
    case childInterface
    case elderlyInterface
    case settings
    case tariffs
    case profile
    case notifications
    case support
    case onboarding
    
    // Дополнительные экраны (11)
    case login
    case registration
    case forgotPassword
    case privacyPolicy
    case termsOfService
    case devices
    case referral
    case deviceDetail(deviceId: String)
    case familyChat(memberId: String)
    case vpnEnergyStats
    case paymentQR(tariff: Tariff)
}

