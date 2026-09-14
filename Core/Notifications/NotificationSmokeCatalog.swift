import Foundation
import UserNotifications

/// Canonical catalog of **user-facing** notification kinds + DEBUG soft-test.
/// No VPN / network_protection — not part of ALADDIN user notifications.
enum NotificationSmokeKind: String, CaseIterable, Identifiable {
    case threatBlocked
    case threatDetected
    case suspiciousActivity
    case bypassAttempt
    case familyMemberAdded
    case familyChat
    case aiMessage
    case upgradeSuccess
    case subscriptionRenewal
    case trial
    case trialExpired
    case subscriptionExpired
    case subscriptionExpiredD1
    case subscriptionExpiredD3
    case referralGrant
    case windDown
    case familyHabitReminder
    case familyHabitDuePing
    case mnemoReview
    case antifakePostCall
    case iotCompromised
    case antivirusScanComplete
    case antivirusScanFailed
    case downloadedFileThreat
    case crashDetection
    /// DEBUG only — last in fire-all so product kinds run first.
    case softTest

    var id: String { rawValue }

    /// Whether this kind is a product event parents/kids should see (soft-test = diagnostics).
    var isUserFacing: Bool {
        switch self {
        case .softTest: return false
        default: return true
        }
    }

    var number: Int {
        switch self {
        case .threatBlocked: return 1
        case .threatDetected: return 2
        case .suspiciousActivity: return 3
        case .bypassAttempt: return 4
        case .familyMemberAdded: return 5
        case .familyChat: return 6
        case .aiMessage: return 7
        case .upgradeSuccess: return 8
        case .subscriptionRenewal: return 9
        case .trial: return 10
        case .trialExpired: return 11
        case .subscriptionExpired: return 12
        case .subscriptionExpiredD1: return 13
        case .subscriptionExpiredD3: return 14
        case .referralGrant: return 15
        case .windDown: return 16
        case .familyHabitReminder: return 17
        case .familyHabitDuePing: return 18
        case .mnemoReview: return 19
        case .antifakePostCall: return 20
        case .iotCompromised: return 21
        case .antivirusScanComplete: return 22
        case .antivirusScanFailed: return 23
        case .downloadedFileThreat: return 24
        case .crashDetection: return 25
        case .softTest: return 26
        }
    }

    var titleRU: String {
        switch self {
        case .softTest: return "Soft-test (диагностика)"
        case .threatBlocked: return "Угроза заблокирована"
        case .threatDetected: return "Угроза обнаружена"
        case .suspiciousActivity: return "Подозрительная активность"
        case .bypassAttempt: return "Попытка обхода"
        case .familyMemberAdded: return "Новый член семьи"
        case .familyChat: return "Семейный чат"
        case .aiMessage: return "AI сообщение"
        case .upgradeSuccess: return "Подписка активирована"
        case .subscriptionRenewal: return "Продление подписки (−3/−1)"
        case .trial: return "Trial reminder (−7/−3/−1)"
        case .trialExpired: return "Trial истёк (дожим 0/+1/+3)"
        case .subscriptionExpired: return "Подписка истекла (день 0)"
        case .subscriptionExpiredD1: return "Подписка — дожим D+1"
        case .subscriptionExpiredD3: return "Подписка — дожим D+3"
        case .referralGrant: return "Рефка — дни защиты"
        case .windDown: return "Спокойный вечер"
        case .familyHabitReminder: return "Семейная привычка"
        case .familyHabitDuePing: return "Привычка — due ping"
        case .mnemoReview: return "Мнемоника SRS"
        case .antifakePostCall: return "Antifake после звонка"
        case .iotCompromised: return "IoT compromised"
        case .antivirusScanComplete: return "Антивирус: скан OK/угрозы"
        case .antivirusScanFailed: return "Антивирус: ошибка скана"
        case .downloadedFileThreat: return "Подозрительный файл"
        case .crashDetection: return "Crash detection"
        }
    }

    var typeKey: String {
        switch self {
        case .softTest: return "soft_test"
        case .threatBlocked: return "threat_blocked"
        case .threatDetected: return "threat_detected"
        case .suspiciousActivity: return "suspicious_activity"
        case .bypassAttempt: return "bypass_attempt"
        case .familyMemberAdded: return "family_member_added"
        case .familyChat: return "family_chat"
        case .aiMessage: return "ai_message"
        case .upgradeSuccess: return "upgrade_success"
        case .subscriptionRenewal: return "subscription_renewal"
        case .trial: return "trial"
        case .trialExpired: return "trial_expired"
        case .subscriptionExpired: return "subscription_expired"
        case .subscriptionExpiredD1: return "subscription_expired"
        case .subscriptionExpiredD3: return "subscription_expired"
        case .referralGrant: return "family_referral_a_grant"
        case .windDown: return WindDownScheduler.notificationType
        case .familyHabitReminder: return "family_habit_reminder"
        case .familyHabitDuePing: return "family_habit_due_ping"
        case .mnemoReview: return MnemonicNotificationScheduler.userInfoType
        case .antifakePostCall: return "antifake_post_call"
        case .iotCompromised: return "iot_device_compromised"
        case .antivirusScanComplete: return "antivirus_scan_complete"
        case .antivirusScanFailed: return "antivirus_scan_failed"
        case .downloadedFileThreat: return "downloaded_file_threat"
        case .crashDetection: return "crash_detection"
        }
    }

    var category: NotificationCategory {
        switch self {
        case .threatBlocked, .threatDetected, .suspiciousActivity, .bypassAttempt,
             .iotCompromised, .antivirusScanComplete, .antivirusScanFailed, .downloadedFileThreat:
            return .security
        case .familyMemberAdded, .familyChat:
            return .family
        case .aiMessage:
            return .ai
        case .subscriptionRenewal, .subscriptionExpired, .subscriptionExpiredD1, .subscriptionExpiredD3:
            return .subscription
        case .trial, .trialExpired:
            return .trial
        case .mnemoReview:
            return .mnemo
        case .familyHabitReminder, .familyHabitDuePing:
            return .familyHabit
        case .softTest, .upgradeSuccess, .referralGrant,
             .windDown, .antifakePostCall, .crashDetection:
            return .general
        }
    }

    /// Fires through NotificationManager (safe delay) — same reliability path as soft-test.
    @MainActor
    func fireSmoke() {
        let nm = NotificationManager.shared
        let title = "🧪 \(number). \(titleRU)"
        let body = "Smoke #\(number) type=\(typeKey) — цепочка local OK"
        var info: [String: Any] = [
            "type": typeKey,
            "source": "notification_smoke_matrix",
            "priority": "high",
            "correlation_id": "smoke-\(rawValue)-\(UUID().uuidString)",
        ]
        if self == .windDown {
            info["deepLink"] = "aladdin://wellness/wind-down"
        }
        if self == .antifakePostCall {
            info["deepLink"] = "aladdin://antifake/call-check"
        }
        if self == .familyHabitReminder || self == .familyHabitDuePing {
            info["preset"] = "water"
        }
        if self == .mnemoReview {
            info["category"] = "games"
            info["dueCount"] = 1
        }
        if self == .referralGrant {
            info["days"] = 7
        }
        if self == .downloadedFileThreat {
            info["file_name"] = "smoke-sample.pdf"
        }
        if self == .antivirusScanFailed || self == .antivirusScanComplete {
            info["threats_found"] = self == .antivirusScanComplete ? 1 : 0
        }
        if self == .trialExpired {
            info["days_offset"] = 0
            info["deepLink"] = NotificationManager.tariffsDeepLink
        }
        if self == .subscriptionExpired {
            info["days_offset"] = 0
            info["deepLink"] = NotificationManager.tariffsDeepLink
        }
        if self == .subscriptionExpiredD1 {
            info["days_offset"] = 1
            info["deepLink"] = NotificationManager.tariffsDeepLink
        }
        if self == .subscriptionExpiredD3 {
            info["days_offset"] = 3
            info["deepLink"] = NotificationManager.tariffsDeepLink
        }
        if self == .subscriptionRenewal || self == .trial {
            info["deepLink"] = NotificationManager.tariffsDeepLink
        }

        nm.sendLocalNotification(
            title: title,
            body: body,
            category: category,
            userInfo: info,
            delay: 0.2
        )
    }

    @MainActor
    static func fireAllSequentially(gapSeconds: Double = 2.5) {
        NotificationManager.shared.resetNotificationFrequencyHistory()
        var settings = NotificationManager.shared.notificationSettings
        settings.maxNotificationsPerHour = nil
        NotificationManager.shared.updateNotificationSettings(settings)

        print("🔔 Smoke fire-all: \(allCases.count) kinds (no VPN), gap=\(gapSeconds)s")
        for (index, kind) in allCases.enumerated() {
            let delay = gapSeconds * Double(index)
            DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
                kind.fireSmoke()
            }
        }
    }

    static var userFacingKinds: [NotificationSmokeKind] {
        allCases.filter(\.isUserFacing)
    }
}
