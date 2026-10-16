import Foundation

/// App Group bridge for Screen Time usage aggregates (main + Monitor/Report extensions).
/// Schema: memberId + deviceId + dayStart (child calendar day) + source=device_activity.
enum ScreenTimeUsageStore {
    static let appGroupId = "group.ai.aladdin"
    static let storageKey = "screen_time_usage_v1"
    static let selectionKey = "screen_time_family_activity_selection_v1"
    static let parentalTimeStatsKey = "parental_time_stats"
    /// Shared with `ScreenTimeAppLimitsBridge` (Bridge writes; Store/extensions only read).
    static let appLimitsRecordsKey = "screen_time_app_limits_v1"
    static let appTokenMapKey = "screen_time_app_token_map_v1"
    /// Parent UI treats aggregates older than this as stale.
    static let staleAfterSeconds: TimeInterval = 6 * 60 * 60

    struct AppMinute: Codable, Equatable, Sendable {
        var tokenHash: String
        var displayName: String?
        var seconds: Int
        var limitSeconds: Int?
    }

    struct Snapshot: Codable, Equatable, Sendable {
        var familyId: String
        var memberId: String
        var deviceId: String
        /// Calendar day key `yyyy-MM-dd` in child timezone.
        var dayStart: String
        var timezone: String
        var totalSeconds: Int
        var apps: [AppMinute]
        var source: String
        var updatedAt: Date

        var isStale: Bool {
            Date().timeIntervalSince(updatedAt) > ScreenTimeUsageStore.staleAfterSeconds
        }

        var isTodayInStoredTimezone: Bool {
            ScreenTimeUsageStore.dayKey(for: Date(), timeZoneIdentifier: timezone) == dayStart
        }
    }

    private static var defaults: UserDefaults {
        UserDefaults(suiteName: appGroupId) ?? .standard
    }

    static func dayKey(for date: Date = Date(), timeZoneIdentifier: String? = nil) -> String {
        var calendar = Calendar(identifier: .gregorian)
        if let timeZoneIdentifier, let tz = TimeZone(identifier: timeZoneIdentifier) {
            calendar.timeZone = tz
        } else {
            calendar.timeZone = .current
        }
        let c = calendar.dateComponents([.year, .month, .day], from: date)
        return String(format: "%04d-%02d-%02d", c.year ?? 0, c.month ?? 0, c.day ?? 0)
    }

    static func currentDeviceId() -> String {
        // Prefer server device id when synced, then vendor id, then stable App Group UUID.
        let candidates = [
            UserDefaults.standard.string(forKey: "current_device_server_id"),
            UserDefaults.standard.string(forKey: "device_id"),
            defaults.string(forKey: "screen_time_device_id")
        ]
        if let id = candidates.compactMap({ $0?.trimmingCharacters(in: .whitespacesAndNewlines) }).first(where: { !$0.isEmpty }) {
            defaults.set(id, forKey: "screen_time_device_id")
            return id
        }
        let id = UUID().uuidString
        defaults.set(id, forKey: "screen_time_device_id")
        return id
    }

    static func load() -> Snapshot? {
        guard let data = defaults.data(forKey: storageKey) else { return nil }
        return try? JSONDecoder().decode(Snapshot.self, from: data)
    }

    @discardableResult
    static func save(_ snapshot: Snapshot) -> Bool {
        guard let data = try? JSONEncoder().encode(snapshot) else { return false }
        defaults.set(data, forKey: storageKey)
        writeParentalTimeStatsCompat(from: snapshot)
        return true
    }

    /// Monitor / main: upsert today's aggregate (rolls to new day key automatically).
    @discardableResult
    static func upsertToday(
        familyId: String,
        memberId: String,
        deviceId: String = currentDeviceId(),
        timezone: String = TimeZone.current.identifier,
        totalSeconds: Int,
        apps: [AppMinute],
        source: String = "device_activity"
    ) -> Snapshot {
        let day = dayKey(timeZoneIdentifier: timezone)
        let snap = Snapshot(
            familyId: familyId,
            memberId: memberId,
            deviceId: deviceId,
            dayStart: day,
            timezone: timezone,
            totalSeconds: max(0, totalSeconds),
            apps: apps,
            source: source,
            updatedAt: Date()
        )
        _ = save(snap)
        return snap
    }

    static func clear() {
        defaults.removeObject(forKey: storageKey)
    }

    /// All social / app slots we surface in parental UI (must match App Limits list).
    /// Self-contained on purpose: this file is also in Monitor/Report extensions.
    /// Do **not** call `ScreenTimeAppLimitsBridge` from here (main-app only + FamilyControls).
    static let trackedAppNames: [String] = [
        "Instagram", "TikTok", "WhatsApp", "Telegram", "YouTube",
        "VK", "Odnoklassniki", "Discord", "Games"
    ]

    private struct LimitsRecordDTO: Codable {
        var displayName: String
        var limitMinutes: Int
        var tokenHash: String?
    }

    /// Match DeviceActivity displayName / tokenHash to a tracked slot.
    static func matchSeconds(in apps: [AppMinute], forDisplayName name: String) -> Int {
        let aliases = aliases(for: name)
        if let byName = apps.first(where: { app in
            let dn = (app.displayName ?? "").lowercased()
            return aliases.contains { dn.contains($0) }
        }) {
            return byName.seconds
        }
        if let hash = tokenHash(forDisplayName: name),
           let byHash = apps.first(where: { $0.tokenHash == hash }) {
            return byHash.seconds
        }
        return 0
    }

    private static func tokenHash(forDisplayName name: String) -> String? {
        let map = (defaults.dictionary(forKey: appTokenMapKey) as? [String: String])
            ?? (UserDefaults.standard.dictionary(forKey: appTokenMapKey) as? [String: String])
            ?? [:]
        return map[name.lowercased()]
    }

    private static func loadLimitRecords() -> [LimitsRecordDTO] {
        let data = defaults.data(forKey: appLimitsRecordsKey)
            ?? UserDefaults.standard.data(forKey: appLimitsRecordsKey)
        if let data,
           let decoded = try? JSONDecoder().decode([LimitsRecordDTO].self, from: data),
           !decoded.isEmpty {
            return decoded
        }
        return []
    }

    private static func aliases(for displayName: String) -> [String] {
        switch displayName.lowercased() {
        case "instagram": return ["instagram"]
        case "tiktok": return ["tiktok"]
        case "whatsapp": return ["whatsapp"]
        case "telegram": return ["telegram"]
        case "youtube": return ["youtube"]
        case "vk": return ["vk", "vkontakte"]
        case "odnoklassniki": return ["odnoklassniki", "ok.ru", "одноклассники"]
        case "discord": return ["discord"]
        case "games": return ["games", "game"]
        default: return [displayName.lowercased()]
        }
    }

    static func statsKeyUsed(_ displayName: String) -> String {
        "\(displayName.lowercased().replacingOccurrences(of: " ", with: "_"))Used"
    }

    static func statsKeyLimit(_ displayName: String) -> String {
        "\(displayName.lowercased().replacingOccurrences(of: " ", with: "_"))LimitStat"
    }

    /// Compatible cache for FamilyTimeControlModal — **all** tracked apps, not only IG/TT.
    static func writeParentalTimeStatsCompat(from snapshot: Snapshot) {
        let payload = buildParentalTimeStatsPayload(
            source: snapshot.source,
            totalSeconds: snapshot.totalSeconds,
            apps: snapshot.apps,
            memberId: snapshot.memberId,
            deviceId: snapshot.deviceId,
            dayStart: snapshot.dayStart,
            updatedAt: ISO8601DateFormatter().string(from: snapshot.updatedAt)
        )
        applyServerPayload(payload)
    }

    static func buildParentalTimeStatsPayload(
        source: String,
        totalSeconds: Int,
        apps: [AppMinute],
        memberId: String = "",
        deviceId: String = "",
        dayStart: String = "",
        updatedAt: String = ""
    ) -> [String: String] {
        let totalMin = max(0, totalSeconds) / 60
        var payload: [String: String] = [
            "source": source,
            "totalTimeUsed": "\(totalMin) min",
            "totalTimeLimit": UserDefaults.standard.string(forKey: "parental_screen_time_limit") ?? "3h/day",
            "memberId": memberId,
            "deviceId": deviceId,
            "dayStart": dayStart,
            "updatedAt": updatedAt
        ]
        let records = loadLimitRecords()
        var ordered = trackedAppNames
        for rec in records {
            let n = rec.displayName
            if !ordered.contains(where: { $0.lowercased() == n.lowercased() }) {
                ordered.append(n)
            }
        }
        for name in ordered {
            let usedMin = matchSeconds(in: apps, forDisplayName: name) / 60
            let limitMin: Int = {
                if let rec = records.first(where: { $0.displayName.lowercased() == name.lowercased() }) {
                    return rec.limitMinutes
                }
                let legacyKey = "parental_\(name.lowercased().replacingOccurrences(of: " ", with: "_"))_limit"
                if let s = UserDefaults.standard.string(forKey: legacyKey) {
                    let digits = s.filter(\.isNumber)
                    if let v = Int(digits), v > 0 { return v }
                }
                switch name.lowercased() {
                case "tiktok": return 20
                case "youtube": return 45
                case "whatsapp", "telegram", "games": return 60
                default: return 30
                }
            }()
            payload[statsKeyUsed(name)] = "\(usedMin) min"
            payload[statsKeyLimit(name)] = "\(limitMin) min"
            if name.lowercased() == "instagram" {
                payload["instagramUsed"] = "\(usedMin) min"
                payload["instagramLimitStat"] = "\(limitMin) min"
            }
            if name.lowercased() == "tiktok" {
                payload["tiktokUsed"] = "\(usedMin) min"
                payload["tiktokLimitStat"] = "\(limitMin) min"
            }
        }
        payload["trackedAppsCSV"] = ordered.joined(separator: ",")
        return payload
    }

    static func applyServerPayload(_ payload: [String: String]) {
        // App Group first — Monitor/Report extensions only share this suite with main.
        defaults.set(payload, forKey: parentalTimeStatsKey)
        UserDefaults.standard.set(payload, forKey: parentalTimeStatsKey)
    }

    /// Prefer App Group (written by extensions), then main `standard`.
    static func loadParentalTimeStats() -> [String: String]? {
        if let ag = defaults.dictionary(forKey: parentalTimeStatsKey) as? [String: String], !ag.isEmpty {
            // Mirror into main standard so older readers still see data.
            UserDefaults.standard.set(ag, forKey: parentalTimeStatsKey)
            return ag
        }
        return UserDefaults.standard.dictionary(forKey: parentalTimeStatsKey) as? [String: String]
    }
}
