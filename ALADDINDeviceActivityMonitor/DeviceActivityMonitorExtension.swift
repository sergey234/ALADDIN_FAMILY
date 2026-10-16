import DeviceActivity
import Foundation
import ManagedSettings

/// Primary writer for Screen Time day aggregates (PROD P-WRITE).
final class DeviceActivityMonitorExtension: DeviceActivityMonitor {
    private let store = ManagedSettingsStore()

    override func intervalDidStart(for activity: DeviceActivityName) {
        super.intervalDidStart(for: activity)
        refreshUsageSnapshot(reason: "intervalDidStart")
    }

    override func intervalDidEnd(for activity: DeviceActivityName) {
        super.intervalDidEnd(for: activity)
        refreshUsageSnapshot(reason: "intervalDidEnd")
    }

    override func eventDidReachThreshold(_ event: DeviceActivityEvent.Name, activity: DeviceActivityName) {
        super.eventDidReachThreshold(event, activity: activity)
        refreshUsageSnapshot(reason: "threshold:\(event.rawValue)")
        // Persist a lightweight event flag for in-app notifications (v1.1).
        let defaults = UserDefaults(suiteName: ScreenTimeUsageStore.appGroupId) ?? .standard
        defaults.set(Date().timeIntervalSince1970, forKey: "screen_time_last_threshold_at")
        defaults.set(event.rawValue, forKey: "screen_time_last_threshold_event")
    }

    override func intervalWillStartWarning(for activity: DeviceActivityName) {
        super.intervalWillStartWarning(for: activity)
    }

    override func intervalWillEndWarning(for activity: DeviceActivityName) {
        super.intervalWillEndWarning(for: activity)
    }

    /// DeviceActivity does not expose per-app minutes here; we bump `updatedAt` and keep last known totals
    /// so parent sync sees liveness. Detailed minutes come from Report filter context when available,
    /// or from main app refresh after user opens ALADDIN on child.
    private func refreshUsageSnapshot(reason: String) {
        let defaults = UserDefaults(suiteName: ScreenTimeUsageStore.appGroupId) ?? .standard
        let familyId = defaults.string(forKey: "screen_time_family_id")
            ?? UserDefaults.standard.string(forKey: "family_id")
            ?? ""
        let memberId = defaults.string(forKey: "screen_time_member_id")
            ?? UserDefaults.standard.string(forKey: "your_member_id")
            ?? ""
        let previous = ScreenTimeUsageStore.load()
        let apps = previous?.apps ?? []
        let total = previous?.totalSeconds ?? 0
        _ = ScreenTimeUsageStore.upsertToday(
            familyId: familyId.isEmpty ? (previous?.familyId ?? "") : familyId,
            memberId: memberId.isEmpty ? (previous?.memberId ?? "") : memberId,
            totalSeconds: total,
            apps: apps
        )
        defaults.set(reason, forKey: "screen_time_last_monitor_reason")
        defaults.set(Date().timeIntervalSince1970, forKey: "screen_time_last_monitor_at")
    }
}
