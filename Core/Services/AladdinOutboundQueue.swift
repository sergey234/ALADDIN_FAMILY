import Foundation
import Network

protocol AladdinOutboundDelivering: Sendable {
    func deliverCheckin(_ draft: WellnessCheckinDraft) async throws
    func deliverHabitConfig(_ config: FamilyHabitRemindersConfig) async throws
}

struct AladdinLiveOutboundDeliverer: AladdinOutboundDelivering {
    func deliverCheckin(_ draft: WellnessCheckinDraft) async throws {
        try await Task { @MainActor in
            _ = try await WellnessAPIService.shared.postCheckin(
                mood: draft.mood,
                sleepHours: draft.sleepHours > 0 ? draft.sleepHours : nil,
                stressLevel: draft.stressLevel > 0 ? draft.stressLevel : nil
            )
        }.value
    }

    func deliverHabitConfig(_ config: FamilyHabitRemindersConfig) async throws {
        try await Task { @MainActor in
            try await FamilyHabitRemindersService.shared.pushServerOnly(config: config)
        }.value
    }
}

/// Decide whether a failed delivery may honestly sit in the outbound queue.
enum AladdinOutboundErrorPolicy {
    /// Auth / client errors will never succeed by waiting for network — do not enqueue or keep.
    static func shouldEnqueue(_ error: Error) -> Bool {
        !isPermanentFailure(error)
    }

    static func isPermanentFailure(_ error: Error) -> Bool {
        if let network = error as? NetworkError {
            switch network {
            case .unauthorized, .forbidden, .badRequest:
                return true
            case .httpError(let code), .invalidStatusCode(let code):
                return (400..<500).contains(code) && code != 408 && code != 429
            default:
                return false
            }
        }
        let ns = error as NSError
        if ns.domain == NSURLErrorDomain { return false }
        if ns.domain == "AladdinHTTP", (400..<500).contains(ns.code), ns.code != 408, ns.code != 429 {
            return true
        }
        return false
    }
}

/// Exponential backoff for transient 5xx / network failures (plan E).
enum AladdinOutboundBackoff {
    static let maxSeconds: TimeInterval = 300

    static func delaySeconds(afterFailures: Int) -> TimeInterval {
        let capped = max(0, min(afterFailures, 8))
        return min(maxSeconds, pow(2, Double(capped)))
    }
}

/// Local-first outbound jobs. Persist + flush on foreground / network.
actor AladdinOutboundQueue {
    static let shared = AladdinOutboundQueue()

    static let storageKey = "aladdin_outbound_queue_v1"
    static let failuresKey = "aladdin_outbound_queue_failures_v1"
    static let backoffUntilKey = "aladdin_outbound_queue_backoff_until_v1"

    enum Job: Codable, Equatable {
        case checkin(WellnessCheckinDraft)
        case habitConfig(FamilyHabitRemindersConfig)
    }

    private let defaults: UserDefaults
    private let deliverer: AladdinOutboundDelivering
    private var pathMonitor: NWPathMonitor?
    private var isFlushing = false

    init(
        defaults: UserDefaults = .standard,
        deliverer: AladdinOutboundDelivering = AladdinLiveOutboundDeliverer()
    ) {
        self.defaults = defaults
        self.deliverer = deliverer
    }

    func enqueueCheckin(_ draft: WellnessCheckinDraft) {
        var jobs = load()
        jobs.removeAll {
            if case .checkin = $0 { return true }
            return false
        }
        jobs.append(.checkin(draft))
        save(jobs)
        // Fresh user action — allow immediate flush attempt.
        clearBackoff()
    }

    func enqueueHabitConfig(_ config: FamilyHabitRemindersConfig) {
        var jobs = load()
        jobs.removeAll {
            if case .habitConfig = $0 { return true }
            return false
        }
        jobs.append(.habitConfig(config))
        save(jobs)
        clearBackoff()
    }

    func pendingCount() -> Int {
        load().count
    }

    func hasPendingCheckin() -> Bool {
        load().contains {
            if case .checkin = $0 { return true }
            return false
        }
    }

    func hasPendingHabitConfig() -> Bool {
        load().contains {
            if case .habitConfig = $0 { return true }
            return false
        }
    }

    func backoffUntil(now: Date = Date()) -> Date? {
        guard let until = defaults.object(forKey: Self.backoffUntilKey) as? Date, until > now else {
            return nil
        }
        return until
    }

    @discardableResult
    func flush(now: Date = Date()) async -> Int {
        guard !isFlushing else { return load().count }
        if let until = backoffUntil(now: now) {
            return load().count
        }
        isFlushing = true
        defer { isFlushing = false }
        var remaining: [Job] = []
        var hadTransientFailure = false
        for job in load() {
            do {
                switch job {
                case .checkin(let draft):
                    try await deliverer.deliverCheckin(draft)
                case .habitConfig(let config):
                    try await deliverer.deliverHabitConfig(config)
                }
            } catch {
                // Permanent 4xx auth/client: drop — never promise “will sync later”.
                if AladdinOutboundErrorPolicy.isPermanentFailure(error) {
                    continue
                }
                remaining.append(job)
                hadTransientFailure = true
            }
        }
        save(remaining)
        if remaining.isEmpty {
            clearBackoff()
        } else if hadTransientFailure {
            recordTransientFailure(now: now)
        }
        return remaining.count
    }

    func startPathMonitor() {
        guard pathMonitor == nil else { return }
        let monitor = NWPathMonitor()
        pathMonitor = monitor
        // Actor is not a class — no `[weak self]`. Use shared singleton to avoid retain cycle via handler.
        monitor.pathUpdateHandler = { path in
            guard path.status == .satisfied else { return }
            Task {
                _ = await AladdinOutboundQueue.shared.flush()
            }
        }
        monitor.start(queue: DispatchQueue.global(qos: .utility))
    }

    private func recordTransientFailure(now: Date) {
        let failures = defaults.integer(forKey: Self.failuresKey) + 1
        defaults.set(failures, forKey: Self.failuresKey)
        let delay = AladdinOutboundBackoff.delaySeconds(afterFailures: failures)
        defaults.set(now.addingTimeInterval(delay), forKey: Self.backoffUntilKey)
    }

    private func clearBackoff() {
        defaults.set(0, forKey: Self.failuresKey)
        defaults.removeObject(forKey: Self.backoffUntilKey)
    }

    private func load() -> [Job] {
        guard let data = defaults.data(forKey: Self.storageKey) else { return [] }
        let dec = JSONDecoder()
        dec.dateDecodingStrategy = .iso8601
        return (try? dec.decode([Job].self, from: data)) ?? []
    }

    private func save(_ jobs: [Job]) {
        let enc = JSONEncoder()
        enc.dateEncodingStrategy = .iso8601
        defaults.set(try? enc.encode(jobs), forKey: Self.storageKey)
    }
}
