import Foundation

/// Hybrid C — единый feedback для Advanced Protection (toast + честные статусы).
/// Safari: не говорить «защита подключена», пока Content Blocker ≠ `.enabled`.
@MainActor
enum ProtectionFeedback {
    enum Kind {
        case on
        case off
        case needsAction
        case info
    }

    static func show(
        _ kind: Kind,
        message: String,
        toast: ToastManager = .shared
    ) {
        print("🛡️ ProtectionFeedback [\(kind)] \(message)")
        switch kind {
        case .on:
            toast.showSuccess(message)
        case .off:
            toast.showInfo(message)
        case .needsAction:
            toast.showWarning(message)
        case .info:
            toast.showInfo(message)
        }
    }

    static func componentOn(name: String, toast: ToastManager = .shared) {
        let L = LocalizationManager.shared
        show(.on, message: String(format: L.localized("protection_feedback_on_fmt"), name), toast: toast)
    }

    static func componentOff(name: String, toast: ToastManager = .shared) {
        let L = LocalizationManager.shared
        show(.off, message: String(format: L.localized("protection_feedback_off_fmt"), name), toast: toast)
    }

    /// App toggle ON, but Safari extension still off — honest, no false "connected".
    static func safariAppEnabledNeedsExtension(toast: ToastManager = .shared) {
        show(.needsAction, message: LocalizationManager.shared.localized("protection_feedback_app_on_safari"), toast: toast)
    }

    static func safariFullyActive(toast: ToastManager = .shared) {
        show(.on, message: LocalizationManager.shared.localized("protection_feedback_safari_active"), toast: toast)
    }

    static func safariAppDisabled(toast: ToastManager = .shared) {
        show(.off, message: LocalizationManager.shared.localized("protection_feedback_safari_off"), toast: toast)
    }

    static func threats(enabledCount: Int, total: Int, toast: ToastManager = .shared) {
        let L = LocalizationManager.shared
        if enabledCount <= 0 {
            show(.off, message: L.localized("protection_feedback_threats_off"), toast: toast)
        } else {
            show(
                .on,
                message: String(format: L.localized("protection_feedback_threats_on_fmt"), enabledCount, total),
                toast: toast
            )
        }
    }

    static func messagesMonitoring(enabled: Bool, toast: ToastManager = .shared) {
        let L = LocalizationManager.shared
        show(
            enabled ? .on : .off,
            message: L.localized(enabled ? "protection_feedback_messages_on" : "protection_feedback_messages_off"),
            toast: toast
        )
    }

    static func screenshotsMonitoring(enabled: Bool, toast: ToastManager = .shared) {
        let L = LocalizationManager.shared
        show(
            enabled ? .on : .off,
            message: L.localized(enabled ? "protection_feedback_screenshots_on" : "protection_feedback_screenshots_off"),
            toast: toast
        )
    }
}
