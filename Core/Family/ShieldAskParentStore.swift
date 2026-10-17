import Foundation

/// WAVE3 B2/B4 — read App Group flag written by `ALADDINShieldAction`.
@MainActor
enum ShieldAskParentStore {
    private static let appGroupId = "group.ai.aladdin"
    private static let askParentKey = "shield_ask_parent_pending_v1"

    struct Pending: Equatable {
        let requestedAt: Date
        let kind: String
    }

    static func consumePending() -> Pending? {
        guard let defaults = UserDefaults(suiteName: appGroupId),
              let raw = defaults.dictionary(forKey: askParentKey),
              (raw["pending"] as? Bool) == true else {
            return nil
        }
        let ts = raw["requested_at"] as? TimeInterval ?? Date().timeIntervalSince1970
        let kind = (raw["kind"] as? String) ?? "application"
        defaults.removeObject(forKey: askParentKey)
        defaults.synchronize()
        return Pending(requestedAt: Date(timeIntervalSince1970: ts), kind: kind)
    }

    /// Local parent banner when child asked to unlock (push path = B4 later).
    static func presentLocalParentAlertIfNeeded(
        localization: LocalizationManager = .shared
    ) {
        guard let pending = consumePending() else { return }
        NotificationManager.shared.sendLocalNotification(
            title: localization.localized("shield_ask_parent_push_title"),
            body: localization.localized("shield_ask_parent_push_body"),
            category: .family,
            userInfo: [
                "type": "shield_ask_parent",
                "kind": pending.kind,
                "deepLink": "aladdin://family/limits",
            ],
            delay: 0.2
        )
    }
}
