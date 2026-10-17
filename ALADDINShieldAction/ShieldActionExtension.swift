import Foundation
import ManagedSettings

/// WAVE3 B2 — child taps Ask Parent / Close on the system shield.
final class ShieldActionExtension: ShieldActionDelegate {
    private static let appGroupId = "group.ai.aladdin"
    private static let askParentKey = "shield_ask_parent_pending_v1"

    override func handle(
        action: ShieldAction,
        for application: ApplicationToken,
        completionHandler: @escaping (ShieldActionResponse) -> Void
    ) {
        switch action {
        case .primaryButtonPressed:
            // Close (matches ShieldConfiguration primary = Close)
            completionHandler(.close)
        case .secondaryButtonPressed:
            recordAskParent(kind: "application")
            completionHandler(.defer)
        @unknown default:
            completionHandler(.close)
        }
    }

    override func handle(
        action: ShieldAction,
        for webDomain: WebDomainToken,
        completionHandler: @escaping (ShieldActionResponse) -> Void
    ) {
        switch action {
        case .primaryButtonPressed:
            completionHandler(.close)
        case .secondaryButtonPressed:
            recordAskParent(kind: "web")
            completionHandler(.defer)
        @unknown default:
            completionHandler(.close)
        }
    }

    override func handle(
        action: ShieldAction,
        for category: ActivityCategoryToken,
        completionHandler: @escaping (ShieldActionResponse) -> Void
    ) {
        switch action {
        case .primaryButtonPressed:
            completionHandler(.close)
        case .secondaryButtonPressed:
            recordAskParent(kind: "category")
            completionHandler(.defer)
        @unknown default:
            completionHandler(.close)
        }
    }

    private func recordAskParent(kind: String) {
        guard let defaults = UserDefaults(suiteName: Self.appGroupId) else { return }
        let payload: [String: Any] = [
            "requested_at": Date().timeIntervalSince1970,
            "kind": kind,
            "pending": true,
        ]
        defaults.set(payload, forKey: Self.askParentKey)
        defaults.synchronize()
    }
}
