import Foundation

/// M-02 — Funnel metrics: enable Call Directory → sync → check (no message text / phone PII).
enum AntifakeAnalyticsEvent: String {
    case cdEnable = "antifake_cd_enable"
    case cdSync = "antifake_cd_sync"
    case checkComplete = "antifake_check_complete"
}

enum AntifakeAnalytics {
    static func track(
        _ event: AntifakeAnalyticsEvent,
        extra: [String: String] = [:]
    ) {
        var params: [String: Any] = ["event": event.rawValue]
        for (key, value) in extra where !value.isEmpty {
            params[key] = value
        }
        AnalyticsManager.shared.trackEvent(event.rawValue, parameters: params)
    }

    static func trackCheckComplete(kind: String, verdict: String, source: String) {
        track(
            .checkComplete,
            extra: [
                "kind": kind,
                "verdict": verdict,
                "source": source
            ]
        )
    }
}
