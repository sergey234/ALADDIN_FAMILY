import Foundation

/// UX-36 #3 / W1 — единый toast для security-настроек (язык приложения).
@MainActor
enum SecuritySettingsFeedback {
    static func saved(toast: ToastManager = .shared) {
        toast.showSuccess(LocalizationManager.shared.localized("security_settings_toast_saved"))
    }

    static func savedLocal(toast: ToastManager = .shared) {
        toast.showSuccess(LocalizationManager.shared.localized("security_settings_toast_saved_local"))
    }

    static func networkError(toast: ToastManager = .shared) {
        toast.showError(LocalizationManager.shared.localized("security_settings_toast_network_error"))
    }

    static func noPermission(toast: ToastManager = .shared) {
        toast.showError(LocalizationManager.shared.localized("security_settings_toast_no_permission"))
    }

    /// Map common network failures to human copy (no raw HTTP in UI).
    static func from(error: Error, toast: ToastManager = .shared) {
        let network = NetworkError.from(error)
        switch network {
        case .unauthorized, .forbidden, .tokenExpired, .invalidToken, .reauthenticationRequired:
            noPermission(toast: toast)
        default:
            networkError(toast: toast)
        }
    }
}
