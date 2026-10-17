import Foundation
import UserNotifications

/// WAVE3 D1 — Critical Alerts opt-in for urgent family signals (SOS / fall / geofence later).
@MainActor
final class FamilyCriticalAlertsService: ObservableObject {
    static let shared = FamilyCriticalAlertsService()

    static let optedInDefaultsKey = "family_critical_alerts_opt_in"

    @Published var isOptedIn: Bool {
        didSet { UserDefaults.standard.set(isOptedIn, forKey: Self.optedInDefaultsKey) }
    }
    @Published private(set) var lastStatusMessage: String?

    private init() {
        isOptedIn = UserDefaults.standard.bool(forKey: Self.optedInDefaultsKey)
    }

    /// Request notification permission including `.criticalAlert` when policy allows.
    func setOptedIn(_ enabled: Bool) async {
        guard AppStoreBuildPolicy.allowsCriticalAlerts else {
            isOptedIn = false
            lastStatusMessage = LocalizationManager.shared.localized("family_critical_alerts_off_hint")
            return
        }
        if !enabled {
            isOptedIn = false
            lastStatusMessage = LocalizationManager.shared.localized("family_critical_alerts_off_hint")
            return
        }
        let granted = await NotificationManager.shared.requestAuthorization()
        if granted {
            isOptedIn = true
            lastStatusMessage = LocalizationManager.shared.localized("family_critical_alerts_on_hint")
        } else {
            isOptedIn = false
            lastStatusMessage = String(
                format: LocalizationManager.shared.localized("family_critical_alerts_error_fmt"),
                "denied"
            )
        }
    }

    var shouldUseCriticalDelivery: Bool {
        AppStoreBuildPolicy.allowsCriticalAlerts && isOptedIn
    }
}
