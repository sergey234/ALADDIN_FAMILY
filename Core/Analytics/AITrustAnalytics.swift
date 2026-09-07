import Foundation

/// AI PM P1 (aipm-12) — unified trust feedback schema (no message text / PII).
/// Surfaces already POST to their backends; this layer unifies local observability + AnalyticsManager.
enum AITrustSurface: String {
    case companion
    case assistant
    case antifake
    case wellness
}

enum AITrustKind: String {
    case helpful
    case notHelpful = "not_helpful"
    case falsePositive = "false_positive"
    case complaint
    case outcome
}

enum AITrustAnalytics {
    static let eventName = "ai_trust_feedback"

    static func track(
        surface: AITrustSurface,
        kind: AITrustKind,
        value: String,
        refId: String? = nil
    ) {
        var params: [String: Any] = [
            "surface": surface.rawValue,
            "kind": kind.rawValue,
            "value": value
        ]
        if let refId, !refId.isEmpty {
            params["ref_id"] = String(refId.prefix(36))
        }
        AnalyticsManager.shared.trackEvent(eventName, parameters: params)
        AITrustMetricsStore.shared.record(
            surface: surface.rawValue,
            kind: kind.rawValue,
            value: value
        )
    }

    /// Map 1–5 star rating → helpful / not_helpful (3 = neutral skip of polarity).
    static func trackAssistantRating(_ rating: Int, resolvedBy: String) {
        let kind: AITrustKind
        let value: String
        switch rating {
        case 1...2:
            kind = .notHelpful
            value = "star_\(rating)"
        case 4...5:
            kind = .helpful
            value = "star_\(rating)"
        default:
            kind = .outcome
            value = "star_\(rating)"
        }
        track(surface: .assistant, kind: kind, value: value, refId: resolvedBy)
    }

    static func trackCompanionVote(_ vote: String, messageId: String?) {
        let normalized = vote.lowercased()
        let kind: AITrustKind = (normalized == "up" || normalized == "helpful") ? .helpful : .notHelpful
        track(surface: .companion, kind: kind, value: normalized, refId: messageId)
    }

    static func trackAntifakeFalsePositive(jobId: String?) {
        track(surface: .antifake, kind: .falsePositive, value: "incorrect", refId: jobId)
    }

    static func trackAntifakeComplaint(isAppeal: Bool, jobId: String?) {
        track(
            surface: .antifake,
            kind: .complaint,
            value: isAppeal ? "appeal" : "report",
            refId: jobId
        )
    }

    static func trackWellnessOutcome(choice: String, helpful: Int, pillar: String) {
        track(
            surface: .wellness,
            kind: .outcome,
            value: "\(choice):\(helpful)",
            refId: pillar
        )
    }
}

/// In-process ring buffer for weekly eval / DEBUG dumps (no network).
final class AITrustMetricsStore {
    static let shared = AITrustMetricsStore()

    private let lock = NSLock()
    private var events: [[String: String]] = []
    private let capacity = 200

    private init() {}

    func record(surface: String, kind: String, value: String) {
        lock.lock()
        defer { lock.unlock() }
        events.append([
            "ts": ISO8601DateFormatter().string(from: Date()),
            "surface": surface,
            "kind": kind,
            "value": value
        ])
        if events.count > capacity {
            events.removeFirst(events.count - capacity)
        }
    }

    func snapshot() -> [[String: String]] {
        lock.lock()
        defer { lock.unlock() }
        return events
    }

    func countsBySurfaceKind() -> [String: Int] {
        lock.lock()
        defer { lock.unlock() }
        var out: [String: Int] = [:]
        for e in events {
            let key = "\(e["surface"] ?? "?"):\(e["kind"] ?? "?")"
            out[key, default: 0] += 1
        }
        return out
    }
}
