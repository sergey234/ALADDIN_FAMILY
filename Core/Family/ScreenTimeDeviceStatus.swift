import Foundation

/// UI status for Screen Time on a family device (Devices list / detail).
enum ScreenTimeDeviceStatus: Equatable {
    case unavailableInThisBuild
    case needsAuthOnChild
    case active(usedMinutes: Int, limitLabel: String, updatedAt: Date)
    case noData
    case stale

    var localizationKey: String {
        switch self {
        case .unavailableInThisBuild: return "screen_time_device_unavailable_build"
        case .needsAuthOnChild: return "screen_time_device_needs_auth"
        case .active: return "screen_time_device_active"
        case .noData: return "screen_time_device_no_data"
        case .stale: return "screen_time_device_stale"
        }
    }

    /// Resolve status for a server device id (and optional owner hint).
    static func resolve(deviceId: String, ownerName: String = "") -> ScreenTimeDeviceStatus {
        if !AppStoreBuildPolicy.allowsSystemFamilyControls {
            return .unavailableInThisBuild
        }
        let snap = ScreenTimeUsageStore.load()
        let ud = UserDefaults.standard
        let stats = ScreenTimeUsageStore.loadParentalTimeStats()
        let sourceOK = stats?["source"] == "device_activity" || stats?["source"] == "server"

        if let snap {
            let matchesDevice = snap.deviceId == deviceId
                || snap.deviceId.isEmpty
                || (stats?["deviceId"] == deviceId)
            if matchesDevice || ownerLooksLikeChild(ownerName) {
                if snap.isStale { return .stale }
                if snap.totalSeconds > 0 || !snap.apps.isEmpty || sourceOK {
                    let used = snap.totalSeconds / 60
                    let limit = ud.string(forKey: "parental_screen_time_limit") ?? "3h/day"
                    return .active(usedMinutes: used, limitLabel: limit, updatedAt: snap.updatedAt)
                }
            }
        }

        if sourceOK, let used = stats?["totalTimeUsed"], !used.isEmpty {
            if let updatedStr = stats?["updatedAt"],
               let updated = ISO8601DateFormatter().date(from: updatedStr),
               Date().timeIntervalSince(updated) > ScreenTimeUsageStore.staleAfterSeconds {
                return .stale
            }
            let mins = Self.parseMinutes(from: used)
            let limit = stats?["totalTimeLimit"] ?? ud.string(forKey: "parental_screen_time_limit") ?? "3h/day"
            return .active(usedMinutes: mins, limitLabel: limit, updatedAt: Date())
        }

        let authHint = UserDefaults(suiteName: ScreenTimeUsageStore.appGroupId)?
            .string(forKey: "screen_time_last_monitor_reason")
        if authHint == nil && ownerLooksLikeChild(ownerName) {
            return .needsAuthOnChild
        }
        return .noData
    }

    private static func ownerLooksLikeChild(_ owner: String) -> Bool {
        // Soft heuristic only for UI copy; never trust for security.
        if FamilyScreenTimeEligibility.isSupervisedDevice() { return true }
        return !owner.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    private static func parseMinutes(from stored: String) -> Int {
        let lower = stored.lowercased()
        if let r = lower.range(of: #"(\d+)\s*(min|мин)"#, options: .regularExpression) {
            return Int(lower[r].filter(\.isNumber)) ?? 0
        }
        if let r = lower.range(of: #"(\d+)\s*h"#, options: .regularExpression) {
            let h = Int(lower[r].filter(\.isNumber)) ?? 0
            return h * 60
        }
        return Int(lower.filter(\.isNumber)) ?? 0
    }

    func displayLine(localization: LocalizationManager) -> String {
        switch self {
        case .unavailableInThisBuild:
            return localization.localized(localizationKey)
        case .needsAuthOnChild:
            return localization.localized(localizationKey)
        case .active(let used, let limit, _):
            let usedLabel = ParentalScreenTimeFormat.formatMinutes(used, localization: localization)
            let limitLabel = ParentalScreenTimeFormat.display(stored: limit, localization: localization)
            return String(
                format: localization.localized("screen_time_device_active_fmt"),
                usedLabel,
                limitLabel
            )
        case .noData:
            return localization.localized(localizationKey)
        case .stale:
            return localization.localized(localizationKey)
        }
    }
}
