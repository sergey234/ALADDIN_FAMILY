import Foundation
import UIKit

/// fsl-13 / fsl-15 / sos — «Я в порядке» / «Нужна помощь» + мягкий статус. Без GPS-трека.
struct FamilyPresenceSnapshot: Codable, Equatable, Identifiable {
    var id: String { memberId }
    let memberId: String
    let displayName: String
    let batteryPercent: Int?
    let lastImOkAt: Date
    let lastOnlineAt: Date
    /// sos — last urgent «need help» tap (nil = never / legacy cache).
    let lastNeedHelpAt: Date?

    init(
        memberId: String,
        displayName: String,
        batteryPercent: Int?,
        lastImOkAt: Date,
        lastOnlineAt: Date,
        lastNeedHelpAt: Date? = nil
    ) {
        self.memberId = memberId
        self.displayName = displayName
        self.batteryPercent = batteryPercent
        self.lastImOkAt = lastImOkAt
        self.lastOnlineAt = lastOnlineAt
        self.lastNeedHelpAt = lastNeedHelpAt
    }

    var isNeedHelpUrgent: Bool {
        guard let helpAt = lastNeedHelpAt else { return false }
        return helpAt >= lastImOkAt
    }
}

enum FamilyPresenceStore {
    private static let key = "aladdin_family_presence_v1"

    static func snapshot(for memberId: String) -> FamilyPresenceSnapshot? {
        load().first { $0.memberId == memberId }
    }

    static func all() -> [FamilyPresenceSnapshot] {
        load().sorted { lhs, rhs in
            let l = max(lhs.lastImOkAt, lhs.lastNeedHelpAt ?? .distantPast)
            let r = max(rhs.lastImOkAt, rhs.lastNeedHelpAt ?? .distantPast)
            return l > r
        }
    }

    static func upsert(_ snap: FamilyPresenceSnapshot) {
        var items = load().filter { $0.memberId != snap.memberId }
        if let existing = load().first(where: { $0.memberId == snap.memberId }),
           snap.lastNeedHelpAt == nil,
           let kept = existing.lastNeedHelpAt {
            // Preserve local urgent flag when server presence has no need-help field.
            items.append(
                FamilyPresenceSnapshot(
                    memberId: snap.memberId,
                    displayName: snap.displayName,
                    batteryPercent: snap.batteryPercent ?? existing.batteryPercent,
                    lastImOkAt: snap.lastImOkAt,
                    lastOnlineAt: snap.lastOnlineAt,
                    lastNeedHelpAt: kept
                )
            )
        } else {
            items.append(snap)
        }
        save(items)
        NotificationCenter.default.post(name: .familyPresenceDidChange, object: nil)
    }

    static func softLine(
        for memberId: String,
        localization: LocalizationManager = .shared
    ) -> String? {
        guard let snap = snapshot(for: memberId) else { return nil }
        let formatter = DateFormatter()
        formatter.locale = localization.locale
        formatter.dateFormat = "HH:mm"

        if snap.isNeedHelpUrgent, let helpAt = snap.lastNeedHelpAt {
            let time = formatter.string(from: helpAt)
            if let battery = snap.batteryPercent {
                return String(
                    format: localization.localized("family_presence_need_help_line_battery"),
                    time,
                    battery
                )
            }
            return String(format: localization.localized("family_presence_need_help_line"), time)
        }

        let time = formatter.string(from: snap.lastImOkAt)
        if let battery = snap.batteryPercent {
            return String(
                format: localization.localized("family_presence_soft_line_battery"),
                time,
                battery
            )
        }
        return String(format: localization.localized("family_presence_soft_line"), time)
    }

    static func isNeedHelpUrgent(for memberId: String) -> Bool {
        snapshot(for: memberId)?.isNeedHelpUrgent ?? false
    }

    private static func load() -> [FamilyPresenceSnapshot] {
        guard let data = UserDefaults.standard.data(forKey: key),
              let decoded = try? JSONDecoder().decode([FamilyPresenceSnapshot].self, from: data) else {
            return []
        }
        return decoded
    }

    private static func save(_ items: [FamilyPresenceSnapshot]) {
        guard let data = try? JSONEncoder().encode(items) else { return }
        UserDefaults.standard.set(data, forKey: key)
    }
}

struct FamilyPresenceAPIResponse: Codable {
    let ok: Bool
    let members: [FamilyPresenceAPIRow]
}

struct FamilyPresenceAPIRow: Codable {
    let memberId: String
    let displayName: String
    let batteryPercent: Int?
    let lastImOkAt: String?
    let lastOnlineAt: String?

    enum CodingKeys: String, CodingKey {
        case memberId = "member_id"
        case displayName = "display_name"
        case batteryPercent = "battery_percent"
        case lastImOkAt = "last_im_ok_at"
        case lastOnlineAt = "last_online_at"
    }

    var parsedImOkAt: Date? { Self.parse(lastImOkAt) }
    var parsedOnlineAt: Date? { Self.parse(lastOnlineAt) }

    private static func parse(_ raw: String?) -> Date? {
        guard let raw, !raw.isEmpty else { return nil }
        let iso = ISO8601DateFormatter()
        iso.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        if let d = iso.date(from: raw) { return d }
        iso.formatOptions = [.withInternetDateTime]
        return iso.date(from: raw)
    }
}

@MainActor
enum FamilyImOkService {
    static func currentBatteryPercent() -> Int? {
        UIDevice.current.isBatteryMonitoringEnabled = true
        let level = UIDevice.current.batteryLevel
        guard level >= 0 else { return nil }
        return Int((level * 100).rounded())
    }

    /// Человек сам нажал «я ок» — короткое сообщение семье + локальный мягкий статус.
    static func sendImOk(
        displayName: String,
        localization: LocalizationManager = .shared,
        apiService: APIService? = nil
    ) async -> Result<Void, Error> {
        let api = apiService ?? APIService.shared
        let memberId = (UserDefaults.standard.string(forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey) ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let battery = currentBatteryPercent()
        let now = Date()
        let resolvedId = memberId.isEmpty ? "local_self" : memberId
        let previousHelp = FamilyPresenceStore.snapshot(for: resolvedId)?.lastNeedHelpAt

        FamilyPresenceStore.upsert(
            FamilyPresenceSnapshot(
                memberId: resolvedId,
                displayName: displayName,
                batteryPercent: battery,
                lastImOkAt: now,
                lastOnlineAt: now,
                lastNeedHelpAt: previousHelp
            )
        )

        let batteryPart: String
        if let battery {
            batteryPart = String(format: localization.localized("im_ok_message_battery"), battery)
        } else {
            batteryPart = ""
        }
        let message = String(
            format: localization.localized("im_ok_family_chat_message"),
            displayName,
            batteryPart
        ).trimmingCharacters(in: .whitespacesAndNewlines)

        let chatResult = await sendFamilyChat(message: message, api: api)

        _ = await postImOkPresence(battery: battery, apiService: api)

        NotificationManager.shared.sendLocalNotification(
            title: localization.localized("im_ok_confirm_title"),
            body: localization.localized("im_ok_confirm_body"),
            category: .family,
            userInfo: ["type": "im_ok_sent"],
            delay: 0.15
        )

        switch chatResult {
        case .success:
            return .success(())
        case .failure(let error):
            return .failure(error)
        }
    }

    /// sos — зеркало Im OK: срочное «нужна помощь» (чат семьи + локальный urgent статус). Без GPS.
    static func sendNeedHelp(
        displayName: String,
        localization: LocalizationManager = .shared,
        apiService: APIService? = nil
    ) async -> Result<Void, Error> {
        let api = apiService ?? APIService.shared
        let memberId = (UserDefaults.standard.string(forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey) ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let battery = currentBatteryPercent()
        let now = Date()
        let resolvedId = memberId.isEmpty ? "local_self" : memberId
        let previousImOk = FamilyPresenceStore.snapshot(for: resolvedId)?.lastImOkAt ?? now

        FamilyPresenceStore.upsert(
            FamilyPresenceSnapshot(
                memberId: resolvedId,
                displayName: displayName,
                batteryPercent: battery,
                lastImOkAt: previousImOk,
                lastOnlineAt: now,
                lastNeedHelpAt: now
            )
        )

        let batteryPart: String
        if let battery {
            batteryPart = String(format: localization.localized("im_ok_message_battery"), battery)
        } else {
            batteryPart = ""
        }
        let message = String(
            format: localization.localized("need_help_family_chat_message"),
            displayName,
            batteryPart
        ).trimmingCharacters(in: .whitespacesAndNewlines)

        let chatResult = await sendFamilyChat(message: message, api: api)

        // Critical local alert (same device ack). Parent channel = family chat message.
        NotificationManager.shared.sendLocalNotification(
            title: localization.localized("need_help_push_title"),
            body: String(
                format: localization.localized("need_help_push_body"),
                displayName
            ),
            category: .family,
            userInfo: [
                "type": "need_help",
                "deepLink": "aladdin://family"
            ],
            delay: 0.15,
            sound: .default
        )

        NotificationManager.shared.sendLocalNotification(
            title: localization.localized("need_help_confirm_sent_title"),
            body: localization.localized("need_help_confirm_sent_body"),
            category: .family,
            userInfo: ["type": "need_help_sent"],
            delay: 0.35
        )

        switch chatResult {
        case .success:
            return .success(())
        case .failure(let error):
            return .failure(error)
        }
    }

    private static func sendFamilyChat(message: String, api: APIService) async -> Result<Void, Error> {
        let familyId = UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey)
            ?? UserDefaults.standard.string(forKey: "family_id")
        return await withCheckedContinuation { continuation in
            api.sendFamilyChatMessage(
                message: message,
                familyId: familyId,
                messageType: "text",
                voiceUrl: nil,
                voiceDuration: nil,
                mediaUrl: nil,
                mediaType: nil,
                replyToMessageId: nil
            ) { result in
                switch result {
                case .success:
                    continuation.resume(returning: .success(()))
                case .failure(let error):
                    continuation.resume(returning: .failure(error))
                }
            }
        }
    }

    private static func postImOkPresence(battery: Int?, apiService: APIService) async -> Bool {
        await withCheckedContinuation { continuation in
            apiService.postFamilyImOk(batteryPercent: battery) { result in
                continuation.resume(returning: (try? result.get()) != nil)
            }
        }
    }

    static func refreshPresenceFromServer(apiService: APIService? = nil) async {
        let api = apiService ?? APIService.shared
        let remote: [FamilyPresenceSnapshot] = await withCheckedContinuation { continuation in
            api.getFamilyPresence { result in
                switch result {
                case .success(let list):
                    continuation.resume(returning: list)
                case .failure:
                    continuation.resume(returning: [])
                }
            }
        }
        for snap in remote {
            FamilyPresenceStore.upsert(snap)
        }
    }
}
