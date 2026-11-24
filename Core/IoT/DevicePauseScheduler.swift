import Foundation

/// fsl-04 — timed «pause» via existing block/unblock APIs (not Apple Screen Time).
enum DevicePauseKind: String, Codable, Equatable {
    case familyPhone
    case iot
}

struct DevicePauseRecord: Codable, Equatable {
    let deviceId: String
    let kind: DevicePauseKind
    let endsAt: Date
    let startedAt: Date
}

enum DevicePauseScheduler {
    static let pauseDurationSeconds: TimeInterval = 60 * 60
    private static let storageKey = "aladdin_device_pauses_v1"

    static func activePause(deviceId: String) -> DevicePauseRecord? {
        processExpiredLocallyOnly()
        return load().first { $0.deviceId == deviceId && $0.endsAt > Date() }
    }

    static func isPaused(_ deviceId: String) -> Bool {
        activePause(deviceId: deviceId) != nil
    }

    static func remainingMinutes(deviceId: String) -> Int? {
        guard let pause = activePause(deviceId: deviceId) else { return nil }
        let seconds = pause.endsAt.timeIntervalSinceNow
        guard seconds > 0 else { return nil }
        return max(1, Int(ceil(seconds / 60)))
    }

    static func activeEndsAt(deviceId: String) -> Date? {
        guard let pause = activePause(deviceId: deviceId) else { return nil }
        return pause.endsAt
    }

    /// Records a timed close after a successful block API call.
    @discardableResult
    static func schedulePause(deviceId: String, kind: DevicePauseKind, endsAt: Date) -> DevicePauseRecord {
        var records = load().filter { $0.deviceId != deviceId }
        let record = DevicePauseRecord(
            deviceId: deviceId,
            kind: kind,
            endsAt: endsAt,
            startedAt: Date()
        )
        records.append(record)
        save(records)
        return record
    }

    /// One hour. Kept for the hidden smart-home pause and older call sites.
    @discardableResult
    static func schedulePause(deviceId: String, kind: DevicePauseKind) -> DevicePauseRecord {
        schedulePause(
            deviceId: deviceId,
            kind: kind,
            endsAt: Date().addingTimeInterval(pauseDurationSeconds)
        )
    }

    static func cancel(deviceId: String) {
        save(load().filter { $0.deviceId != deviceId })
    }

    /// Returns expired pauses (and removes them from storage) so callers can unblock via API.
    static func consumeExpired() -> [DevicePauseRecord] {
        let now = Date()
        var kept: [DevicePauseRecord] = []
        var expired: [DevicePauseRecord] = []
        for record in load() {
            if record.endsAt <= now {
                expired.append(record)
            } else {
                kept.append(record)
            }
        }
        save(kept)
        return expired
    }

    /// Drop expired rows without API (safe for UI reads).
    private static func processExpiredLocallyOnly() {
        let now = Date()
        let kept = load().filter { $0.endsAt > now }
        if kept.count != load().count {
            save(kept)
        }
    }

    private static func load() -> [DevicePauseRecord] {
        guard let data = UserDefaults.standard.data(forKey: storageKey),
              let decoded = try? JSONDecoder().decode([DevicePauseRecord].self, from: data) else {
            return []
        }
        return decoded
    }

    private static func save(_ records: [DevicePauseRecord]) {
        guard let data = try? JSONEncoder().encode(records) else { return }
        UserDefaults.standard.set(data, forKey: storageKey)
    }
}

/// How long a parent closes a child's phone. Morning means the next 07:00.
enum ChildPhoneCloseChoice: String, CaseIterable, Identifiable {
    case oneHour
    case twoHours
    case threeHours
    case untilMorning

    var id: String { rawValue }

    var titleKey: String {
        switch self {
        case .oneHour: return "child_phone_close_1h"
        case .twoHours: return "child_phone_close_2h"
        case .threeHours: return "child_phone_close_3h"
        case .untilMorning: return "child_phone_close_morning"
        }
    }

    func endsAt(now: Date = Date(), calendar: Calendar = .current) -> Date {
        switch self {
        case .oneHour:
            return now.addingTimeInterval(60 * 60)
        case .twoHours:
            return now.addingTimeInterval(2 * 60 * 60)
        case .threeHours:
            return now.addingTimeInterval(3 * 60 * 60)
        case .untilMorning:
            var parts = calendar.dateComponents([.year, .month, .day], from: now)
            parts.hour = 7
            parts.minute = 0
            parts.second = 0
            let thisMorning = calendar.date(from: parts) ?? now
            if thisMorning > now.addingTimeInterval(60) {
                return thisMorning
            }
            return calendar.date(byAdding: .day, value: 1, to: thisMorning)
                ?? now.addingTimeInterval(8 * 60 * 60)
        }
    }

    static func clockString(_ date: Date, locale: Locale) -> String {
        let formatter = DateFormatter()
        formatter.locale = locale
        formatter.dateFormat = "HH:mm"
        return formatter.string(from: date)
    }
}

/// Applies expired pause auto-unblocks through existing APIs.
@MainActor
enum DevicePauseAutoUnblock {
    static func processExpiredIfNeeded(apiService: APIService? = nil) async {
        // Default arg cannot touch MainActor `APIService.shared` (nonisolated eval).
        let api = apiService ?? APIService.shared
        let expired = DevicePauseScheduler.consumeExpired()
        guard !expired.isEmpty else { return }

        for record in expired {
            switch record.kind {
            case .familyPhone:
                await withCheckedContinuation { (continuation: CheckedContinuation<Void, Never>) in
                    api.unblockDevice(deviceId: record.deviceId) { _ in
                        continuation.resume()
                    }
                }
            case .iot:
                _ = try? await api.unblockIoTDevice(deviceId: record.deviceId)
            }
        }
        NotificationCenter.default.post(name: NSNotification.Name("FamilyDevicesDidChange"), object: nil)
    }
}
