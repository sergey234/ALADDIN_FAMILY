import DeviceActivity
import SwiftUI

@main
struct ALADDINDeviceActivityReportExtension: DeviceActivityReportExtension {
    var body: some DeviceActivityReportScene {
        TotalActivityReport { summary in
            Text(summary)
                .font(.headline)
                .padding()
        }
    }
}

extension DeviceActivityReport.Context {
    static let totalActivity = Self("aladdin.totalActivity")
}

/// Report scene: configuration is a display string; content is any SwiftUI View.
/// (Do not use `Text<String>` — `Text` is no longer generic.)
struct TotalActivityReport<Content: View>: DeviceActivityReportScene {
    let context: DeviceActivityReport.Context = .totalActivity
    let content: (String) -> Content

    func makeConfiguration(
        representing data: DeviceActivityResults<DeviceActivityData>
    ) async -> String {
        var totalSeconds = 0
        for await deviceData in data {
            for await segment in deviceData.activitySegments {
                totalSeconds += Int(segment.totalActivityDuration)
            }
        }

        let defaults = UserDefaults(suiteName: ScreenTimeUsageStore.appGroupId) ?? .standard
        let familyId = defaults.string(forKey: "screen_time_family_id") ?? ""
        let memberId = defaults.string(forKey: "screen_time_member_id") ?? ""
        let previousApps = ScreenTimeUsageStore.load()?.apps ?? []
        _ = ScreenTimeUsageStore.upsertToday(
            familyId: familyId,
            memberId: memberId,
            totalSeconds: totalSeconds,
            apps: previousApps
        )

        let minutes = totalSeconds / 60
        return "\(minutes) min"
    }
}
