import XCTest
@testable import ALADDIN

final class ScreenTimeUsageStoreStatsTests: XCTestCase {

    func testMatchSecondsByDisplayNameAliases() {
        let apps: [ScreenTimeUsageStore.AppMinute] = [
            .init(tokenHash: "h1", displayName: "Instagram", seconds: 600, limitSeconds: 1800),
            .init(tokenHash: "h2", displayName: "TikTok", seconds: 120, limitSeconds: 1200),
            .init(tokenHash: "h3", displayName: "VK", seconds: 300, limitSeconds: 1800)
        ]
        XCTAssertEqual(ScreenTimeUsageStore.matchSeconds(in: apps, forDisplayName: "Instagram") / 60, 10)
        XCTAssertEqual(ScreenTimeUsageStore.matchSeconds(in: apps, forDisplayName: "TikTok") / 60, 2)
        XCTAssertEqual(ScreenTimeUsageStore.matchSeconds(in: apps, forDisplayName: "VK") / 60, 5)
        XCTAssertEqual(ScreenTimeUsageStore.matchSeconds(in: apps, forDisplayName: "Telegram"), 0)
    }

    func testBuildPayloadIncludesAllTrackedApps() {
        let apps: [ScreenTimeUsageStore.AppMinute] = [
            .init(tokenHash: "h1", displayName: "YouTube", seconds: 900, limitSeconds: nil)
        ]
        let payload = ScreenTimeUsageStore.buildParentalTimeStatsPayload(
            source: "device_activity",
            totalSeconds: 900,
            apps: apps,
            memberId: "m1",
            deviceId: "d1",
            dayStart: "2026-10-16",
            updatedAt: "2026-10-16T12:00:00Z"
        )
        XCTAssertEqual(payload["totalTimeUsed"], "15 min")
        XCTAssertEqual(payload["youtubeUsed"], "15 min")
        XCTAssertEqual(payload["instagramUsed"], "0 min")
        XCTAssertEqual(payload["tiktokUsed"], "0 min")
        XCTAssertEqual(payload["telegramUsed"], "0 min")
        XCTAssertEqual(payload["whatsappUsed"], "0 min")
        XCTAssertEqual(payload["vkUsed"], "0 min")
        XCTAssertEqual(payload["odnoklassnikiUsed"], "0 min")
        XCTAssertEqual(payload["discordUsed"], "0 min")
        XCTAssertEqual(payload["gamesUsed"], "0 min")
        let csv = payload["trackedAppsCSV"] ?? ""
        for name in ScreenTimeUsageStore.trackedAppNames {
            XCTAssertTrue(csv.contains(name), "missing \(name) in CSV")
        }
    }

    func testNoBridgeTypeDependencyInStoreKeys() {
        XCTAssertEqual(ScreenTimeUsageStore.appLimitsRecordsKey, "screen_time_app_limits_v1")
        XCTAssertEqual(ScreenTimeUsageStore.appTokenMapKey, "screen_time_app_token_map_v1")
        XCTAssertEqual(ScreenTimeAppLimitsBridge.recordsKey, ScreenTimeUsageStore.appLimitsRecordsKey)
        XCTAssertEqual(ScreenTimeAppLimitsBridge.mapKey, ScreenTimeUsageStore.appTokenMapKey)
    }
}
