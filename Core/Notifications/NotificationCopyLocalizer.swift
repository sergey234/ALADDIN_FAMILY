import Foundation

/// Remaps baked server/local RU (or EN) notification copy to LocalizationManager keys at display time.
enum NotificationCopyLocalizer {
    static func localizedTitle(
        rawType: String,
        bakedTitle: String,
        metadata: [String: String],
        localizationManager: LocalizationManager = .shared
    ) -> String {
        if let key = titleKey(forRawType: rawType) {
            return localizationManager.localized(key)
        }
        if let key = titleKey(forBakedTitle: bakedTitle) {
            return localizationManager.localized(key)
        }
        return bakedTitle
    }

    static func localizedMessage(
        rawType: String,
        bakedMessage: String,
        metadata: [String: String],
        localizationManager: LocalizationManager = .shared
    ) -> String {
        let type = rawType.lowercased()
        switch type {
        case "antivirus_scan_complete":
            let n = Int(metadata["threats_found"] ?? "") ?? 0
            return n > 0
                ? String(format: localizationManager.localized("push_antivirus_complete_body_threats"), n)
                : localizationManager.localized("push_antivirus_complete_body_clean")
        case "antivirus_scan_failed":
            return localizationManager.localized("push_antivirus_failed_body")
        case "downloaded_file_threat":
            let name = metadata["file_name"] ?? extractQuotedFileName(from: bakedMessage) ?? "file"
            return String(format: localizationManager.localized("push_downloaded_file_threat_body"), name)
        case "threat_blocked":
            return remappedOrBaked(
                bakedMessage,
                localizationManager: localizationManager,
                knownBodies: [
                    ("Заблокирован", "push_threat_blocked_body"),
                ]
            )
        case "threat_detected", "security_alert", "threat":
            if let key = bodyKey(forBakedMessage: bakedMessage) {
                return localizationManager.localized(key)
            }
            return bakedMessage
        case "suspicious_activity":
            if let key = bodyKey(forBakedMessage: bakedMessage) {
                return localizationManager.localized(key)
            }
            return bakedMessage
        case "bypass_attempt", "bypass":
            if let key = bodyKey(forBakedMessage: bakedMessage) {
                return localizationManager.localized(key)
            }
            return bakedMessage
        default:
            if let key = bodyKey(forBakedMessage: bakedMessage) {
                // Format bodies that need a count extracted from baked RU text.
                if key == "push_antivirus_complete_body_threats",
                   let n = firstInt(in: bakedMessage) {
                    return String(format: localizationManager.localized(key), n)
                }
                if key == "push_downloaded_file_threat_body",
                   let name = extractQuotedFileName(from: bakedMessage) {
                    return String(format: localizationManager.localized(key), name)
                }
                let localized = localizationManager.localized(key)
                return localized.contains("%") ? bakedMessage : localized
            }
            return bakedMessage
        }
    }

    private static func firstInt(in text: String) -> Int? {
        let digits = text.compactMap { $0.isNumber ? $0 : nil }
        // Prefer first contiguous number
        if let match = text.range(of: #"\d+"#, options: .regularExpression) {
            return Int(text[match])
        }
        _ = digits
        return nil
    }

    private static func titleKey(forRawType rawType: String) -> String? {
        switch rawType.lowercased() {
        case "threat_blocked": return "push_threat_blocked_title"
        case "threat_detected", "security_alert": return "push_threat_detected_title"
        case "suspicious_activity": return "push_suspicious_activity_title"
        case "bypass_attempt", "bypass": return "push_bypass_attempt_title"
        case "family_member_added": return "push_family_member_added_title"
        case "antivirus_scan_complete": return "push_antivirus_complete_title"
        case "antivirus_scan_failed": return "push_antivirus_failed_title"
        case "downloaded_file_threat": return "push_downloaded_file_threat_title"
        case "crash_detection": return "push_crash_detection_title"
        case "iot_device_compromised": return "push_iot_compromised_title"
        case "upgrade_success", "subscription_activated": return "push_upgrade_success_title"
        case "subscription_expired": return "push_subscription_expired_now_title"
        case "ai_message": return "push_ai_assistant_title"
        case "qa_threat": return "push_qa_threat_title"
        default: return nil
        }
    }

    private static func titleKey(forBakedTitle title: String) -> String? {
        let t = title.trimmingCharacters(in: .whitespacesAndNewlines)
        let map: [String: String] = [
            "🛡️ Угроза заблокирована": "push_threat_blocked_title",
            "Угроза заблокирована": "push_threat_blocked_title",
            "🛡️ Обнаружена угроза": "push_threat_detected_title",
            "Угроза обнаружена": "push_threat_detected_title",
            "⚠️ Подозрительная активность": "push_suspicious_activity_title",
            "Подозрительная активность": "push_suspicious_activity_title",
            "🚨 Попытка обхода": "push_bypass_attempt_title",
            "Попытка обхода": "push_bypass_attempt_title",
            "👨‍👩‍👧‍👦 Новый член семьи": "push_family_member_added_title",
            "Новый член семьи": "push_family_member_added_title",
            "Антивирусное сканирование завершено": "push_antivirus_complete_title",
            "Antivirus scan complete": "push_antivirus_complete_title",
            "Ошибка антивирусного сканирования": "push_antivirus_failed_title",
            "Antivirus scan failed": "push_antivirus_failed_title",
            "Подозрительный файл обнаружен": "push_downloaded_file_threat_title",
            "Suspicious file detected": "push_downloaded_file_threat_title",
            "🚨 Авария обнаружена": "push_crash_detection_title",
            "⚠️ Устройство скомпрометировано": "push_iot_compromised_title",
            "🎉 Поздравляем!": "push_upgrade_success_title",
            "Подписка закончилась": "push_subscription_expired_now_title",
            "🤖 AI Помощник": "push_ai_assistant_title",
            "🧪 Тестовая угроза (QA)": "push_qa_threat_title",
            // Smoke matrix labels (settings screen)
            "Антивирус: скан OK/угрозы": "push_antivirus_complete_title",
            "Антивирус: ошибка скана": "push_antivirus_failed_title",
            "Подозрительный файл": "push_downloaded_file_threat_title",
        ]
        return map[t]
    }

    private static func bodyKey(forBakedMessage message: String) -> String? {
        let m = message.trimmingCharacters(in: .whitespacesAndNewlines)
        let exact: [String: String] = [
            "Угроз не обнаружено. Система в безопасности.": "push_antivirus_complete_body_clean",
            "No threats found. Your system is safe.": "push_antivirus_complete_body_clean",
            "Не удалось выполнить сканирование. Проверьте подключение к интернету.": "push_antivirus_failed_body",
            "Could not complete the scan. Check your internet connection.": "push_antivirus_failed_body",
            "Проверьте ситуацию и при необходимости вызовите экстренные службы": "push_crash_detection_body",
            "Ваша подписка успешно активирована! Теперь доступны все функции защиты.": "push_upgrade_success_body",
            "Сценарий smoke-test: проверка цепочки detect -> notifications UI": "push_qa_threat_body",
        ]
        if let key = exact[m] { return key }
        if m.hasPrefix("Обнаружено ") && m.contains("угроз") {
            return "push_antivirus_complete_body_threats"
        }
        if m.hasPrefix("Found ") && m.contains("threat") {
            return "push_antivirus_complete_body_threats"
        }
        if m.contains("может содержать угрозу") || m.contains("may contain a threat") {
            return "push_downloaded_file_threat_body"
        }
        return nil
    }

    private static func remappedOrBaked(
        _ baked: String,
        localizationManager: LocalizationManager,
        knownBodies: [(String, String)]
    ) -> String {
        for (needle, key) in knownBodies where baked.contains(needle) {
            return localizationManager.localized(key)
        }
        return baked
    }

    private static func extractQuotedFileName(from message: String) -> String? {
        if let r1 = message.range(of: #"'(.*?)'"#, options: .regularExpression) {
            return String(message[r1]).trimmingCharacters(in: CharacterSet(charactersIn: "'"))
        }
        if let r2 = message.range(of: #""(.*?)""#, options: .regularExpression) {
            return String(message[r2]).trimmingCharacters(in: CharacterSet(charactersIn: "\""))
        }
        return nil
    }
}
