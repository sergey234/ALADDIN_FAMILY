import Foundation
import UIKit

/// bat-01 — пуш «батарея почти села» семье (без GPS). Не чаще 1 раза в 12 часов.
@MainActor
enum FamilyBatteryCriticalMonitor {
    private static let lastPushKey = "aladdin_battery_critical_last_push_at"
    private static let thresholdPercent = 15
    private static let cooldownSeconds: TimeInterval = 12 * 60 * 60

    static func checkAndNotifyIfNeeded(
        localization: LocalizationManager = .shared,
        apiService: APIService? = nil
    ) {
        UIDevice.current.isBatteryMonitoringEnabled = true
        let level = UIDevice.current.batteryLevel
        guard level >= 0 else { return }
        let percent = Int((level * 100).rounded())
        guard percent <= thresholdPercent else { return }

        let now = Date()
        if let last = UserDefaults.standard.object(forKey: lastPushKey) as? Date,
           now.timeIntervalSince(last) < cooldownSeconds {
            return
        }
        UserDefaults.standard.set(now, forKey: lastPushKey)

        let title = localization.localized("battery_critical_push_title")
        let body = String(
            format: localization.localized("battery_critical_push_body"),
            percent
        )
        NotificationManager.shared.sendLocalNotification(
            title: title,
            body: body,
            category: .family,
            userInfo: ["type": "battery_critical", "percent": percent],
            delay: 0.2
        )

        let api = apiService ?? APIService.shared
        let familyId = UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey)
            ?? UserDefaults.standard.string(forKey: "family_id")
        let name = UserDefaults.standard.string(forKey: "user_display_name")
            ?? UserDefaults.standard.string(forKey: "user_name")
            ?? localization.localized("battery_critical_member_fallback")
        let chatMessage = String(
            format: localization.localized("battery_critical_chat_message"),
            name,
            percent
        )
        api.sendFamilyChatMessage(
            message: chatMessage,
            familyId: familyId,
            messageType: "text",
            voiceUrl: nil,
            voiceDuration: nil,
            mediaUrl: nil,
            mediaType: nil,
            replyToMessageId: nil
        ) { _ in }
    }
}
