import Foundation
import UIKit

/// fsl-13 / fsl-15 — «Я в порядке» + мягкий статус (заряд / время нажатия). Без GPS-трека.
struct FamilyPresenceSnapshot: Codable, Equatable, Identifiable {
    var id: String { memberId }
    let memberId: String
    let displayName: String
    let batteryPercent: Int?
    let lastImOkAt: Date
    let lastOnlineAt: Date
}

enum FamilyPresenceStore {
    private static let key = "aladdin_family_presence_v1"

    static func snapshot(for memberId: String) -> FamilyPresenceSnapshot? {
        load().first { $0.memberId == memberId }
    }

    static func all() -> [FamilyPresenceSnapshot] {
        load().sorted { $0.lastImOkAt > $1.lastImOkAt }
    }

    static func upsert(_ snap: FamilyPresenceSnapshot) {
        var items = load().filter { $0.memberId != snap.memberId }
        items.append(snap)
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
        // Default arg cannot touch MainActor `APIService.shared` (nonisolated eval).
        let api = apiService ?? APIService.shared
        let memberId = (UserDefaults.standard.string(forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey) ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let battery = currentBatteryPercent()
        let now = Date()
        let resolvedId = memberId.isEmpty ? "local_self" : memberId

        FamilyPresenceStore.upsert(
            FamilyPresenceSnapshot(
                memberId: resolvedId,
                displayName: displayName,
                batteryPercent: battery,
                lastImOkAt: now,
                lastOnlineAt: now
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

        let familyId = UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey)
            ?? UserDefaults.standard.string(forKey: "family_id")

        let chatResult: Result<Void, Error> = await withCheckedContinuation { continuation in
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

        // Best-effort server presence (deploy separately); chat is primary signal.
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
            // Presence already local — still useful on this device.
            return .failure(error)
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
