import CoreLocation
import Foundation
import UIKit

/// fsl-13 / fsl-15 / sos — «Я в порядке» / «Нужна помощь» + мягкий статус.
/// Im OK = без GPS. Need Help (L7) = опционально одна точка When In Use (не трек).
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
        let needle = memberId.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !needle.isEmpty else { return nil }
        let all = load()
        if let exact = all.first(where: { $0.memberId == needle }) { return exact }
        // ProdQA S25: local_self / MEM_* / server id drift — match by suffix or display name later via candidates.
        return all.first { snap in
            snap.memberId.hasSuffix(needle) || needle.hasSuffix(snap.memberId)
        }
    }

    /// Resolve presence across id aliases (server / local / canonical) + optional display name.
    static func snapshot(matchingIds ids: [String], displayName: String? = nil) -> FamilyPresenceSnapshot? {
        for id in ids {
            let trimmed = id.trimmingCharacters(in: .whitespacesAndNewlines)
            guard !trimmed.isEmpty else { continue }
            if let snap = snapshot(for: trimmed) { return snap }
        }
        // ProdQA S25: when ids drift (local_self vs MEM_*), bind by display name.
        if let displayName {
            let needle = displayName.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
            if !needle.isEmpty {
                if let byName = load().first(where: {
                    $0.displayName.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() == needle
                }) {
                    return byName
                }
            }
        }
        return nil
    }

    static func softLine(
        matchingIds ids: [String],
        displayName: String? = nil,
        localization: LocalizationManager = .shared
    ) -> String? {
        guard let snap = snapshot(matchingIds: ids, displayName: displayName) else { return nil }
        return softLine(for: snap.memberId, localization: localization)
    }

    static func isNeedHelpUrgent(matchingIds ids: [String], displayName: String? = nil) -> Bool {
        snapshot(matchingIds: ids, displayName: displayName)?.isNeedHelpUrgent ?? false
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
        // Drop stale local_self row once we have a real server member id for same person.
        if snap.memberId != "local_self" {
            let name = snap.displayName.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
            items.removeAll {
                $0.memberId == "local_self"
                    && $0.displayName.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() == name
            }
        }
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
        let stamp: (Date) -> String = { presenceStamp(for: $0, localization: localization) }

        if snap.isNeedHelpUrgent, let helpAt = snap.lastNeedHelpAt {
            let when = stamp(helpAt)
            if let battery = snap.batteryPercent {
                return String(
                    format: localization.localized("family_presence_need_help_line_battery"),
                    when,
                    battery
                )
            }
            return String(format: localization.localized("family_presence_need_help_line"), when)
        }

        let when = stamp(snap.lastImOkAt)
        if let battery = snap.batteryPercent {
            return String(
                format: localization.localized("family_presence_soft_line_battery"),
                when,
                battery
            )
        }
        return String(format: localization.localized("family_presence_soft_line"), when)
    }

    /// «сегодня · 15:00» / «вчера · 15:00» / «16 окт · 15:00» — дата всегда видна вне «сегодня».
    static func presenceStamp(
        for date: Date,
        localization: LocalizationManager = .shared
    ) -> String {
        let calendar = Calendar.current
        let timeFormatter = DateFormatter()
        timeFormatter.locale = localization.locale
        timeFormatter.dateFormat = "HH:mm"
        let time = timeFormatter.string(from: date)

        if calendar.isDateInToday(date) {
            return String(format: localization.localized("family_presence_stamp_today"), time)
        }
        if calendar.isDateInYesterday(date) {
            return String(format: localization.localized("family_presence_stamp_yesterday"), time)
        }
        let dayFormatter = DateFormatter()
        dayFormatter.locale = localization.locale
        dayFormatter.setLocalizedDateFormatFromTemplate("dMMM")
        let day = dayFormatter.string(from: date)
        return String(format: localization.localized("family_presence_stamp_date"), day, time)
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

enum FamilyAutoAlertKind: String, Codable, Equatable {
    case imOk = "im_ok"
    case needHelp = "need_help"
    case batteryCritical = "battery_critical"
    case urgentSignal = "urgent_signal"
}

struct FamilyAutoAlertEvent: Codable, Equatable, Identifiable {
    let id: String
    let kind: FamilyAutoAlertKind
    let displayName: String
    let batteryPercent: Int?
    let locationSuffix: String?
    let reason: String?
    let createdAt: Date
    let legacyPlaintext: String?

    init(
        id: String = UUID().uuidString,
        kind: FamilyAutoAlertKind,
        displayName: String,
        batteryPercent: Int? = nil,
        locationSuffix: String? = nil,
        reason: String? = nil,
        createdAt: Date = Date(),
        legacyPlaintext: String? = nil
    ) {
        self.id = id
        self.kind = kind
        self.displayName = displayName
        self.batteryPercent = batteryPercent
        self.locationSuffix = locationSuffix
        self.reason = reason
        self.createdAt = createdAt
        self.legacyPlaintext = legacyPlaintext
    }
}

enum FamilyAutoAlertError: LocalizedError {
    case missingFamilyId
    case e2eeNotReady

    var errorDescription: String? {
        switch self {
        case .missingFamilyId:
            return "Family id is missing"
        case .e2eeNotReady:
            return "Family E2EE is not ready"
        }
    }
}

@MainActor
enum FamilyAutoAlertSender {
    static func send(
        _ event: FamilyAutoAlertEvent,
        localization: LocalizationManager = .shared,
        api: APIService? = nil,
        enqueueOnFailure: Bool = true
    ) async -> Result<Void, Error> {
        let service = api ?? APIService.shared
        let familyId = UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey)
            ?? UserDefaults.standard.string(forKey: "family_id")
        guard let familyId, !familyId.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            if enqueueOnFailure { FamilyImOkOfflineQueue.enqueue(event) }
            return .failure(FamilyAutoAlertError.missingFamilyId)
        }

        let e2ee = FamilyE2EEManager.shared
        if !e2ee.isReady {
            await e2ee.bootstrap(familyId: familyId)
        }
        guard e2ee.isReady else {
            if enqueueOnFailure { FamilyImOkOfflineQueue.enqueue(event) }
            return .failure(FamilyAutoAlertError.e2eeNotReady)
        }

        do {
            let encrypted = try e2ee.encryptOutgoing(
                plaintext: message(for: event, localization: localization),
                messageType: "text",
                familyId: familyId
            )
            return await sendEncrypted(encrypted, familyId: familyId, api: service, event: event, enqueueOnFailure: enqueueOnFailure)
        } catch {
            if enqueueOnFailure { FamilyImOkOfflineQueue.enqueue(event) }
            return .failure(error)
        }
    }

    private static func sendEncrypted(
        _ encrypted: (ciphertext: String, senderDeviceId: String),
        familyId: String,
        api: APIService,
        event: FamilyAutoAlertEvent,
        enqueueOnFailure: Bool
    ) async -> Result<Void, Error> {
        await withCheckedContinuation { continuation in
            api.sendFamilyChatMessage(
                message: nil,
                familyId: familyId,
                messageType: "text",
                voiceUrl: nil,
                voiceDuration: nil,
                mediaUrl: nil,
                mediaType: nil,
                replyToMessageId: nil,
                envelopeVersion: 2,
                senderDeviceId: encrypted.senderDeviceId,
                ciphertext: encrypted.ciphertext
            ) { result in
                switch result {
                case .success:
                    continuation.resume(returning: .success(()))
                case .failure(let error):
                    if enqueueOnFailure { FamilyImOkOfflineQueue.enqueue(event) }
                    continuation.resume(returning: .failure(error))
                }
            }
        }
    }

    private static func message(for event: FamilyAutoAlertEvent, localization: LocalizationManager) -> String {
        if let legacy = event.legacyPlaintext, !legacy.isEmpty {
            return legacy
        }

        switch event.kind {
        case .imOk:
            let batteryPart = event.batteryPercent.map { String(format: localization.localized("im_ok_message_battery"), $0) } ?? ""
            return String(format: localization.localized("im_ok_family_chat_message"), event.displayName, batteryPart)
        case .needHelp:
            let batteryPart = event.batteryPercent.map { String(format: localization.localized("im_ok_message_battery"), $0) } ?? ""
            let locationPart = event.locationSuffix ?? ""
            return String(format: localization.localized("need_help_family_chat_message"), event.displayName, batteryPart + locationPart)
        case .batteryCritical:
            let battery = event.batteryPercent ?? 0
            return String(format: localization.localized("battery_critical_chat_message"), event.displayName, battery)
        case .urgentSignal:
            let title = localization.localized("family_urgent_signal_title")
            let reason = event.reason ?? localization.localized("family_urgent_signal_body")
            return "\(title): \(event.displayName) · \(reason)"
        }
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

        let chatResult = await FamilyAutoAlertSender.send(
            FamilyAutoAlertEvent(
                kind: .imOk,
                displayName: displayName,
                batteryPercent: battery
            ),
            localization: localization,
            api: api
        )

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

    /// sos / L7 — срочное «нужна помощь» + optional one-shot location (When In Use). Не continuous GPS.
    static func sendNeedHelp(
        displayName: String,
        localization: LocalizationManager = .shared,
        apiService: APIService? = nil,
        attachLocation: Bool = true
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

        var locationPart = ""
        if attachLocation, UserDefaults.standard.object(forKey: "parental_sos_enabled") as? Bool != false {
            if let pin = await captureSOSLocationPin(localization: localization, api: api) {
                locationPart = pin
            }
        }

        let chatResult = await FamilyAutoAlertSender.send(
            FamilyAutoAlertEvent(
                kind: .needHelp,
                displayName: displayName,
                batteryPercent: battery,
                locationSuffix: locationPart.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? nil : locationPart
            ),
            localization: localization,
            api: api
        )

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
                "member_id": resolvedId,
                "display_name": displayName,
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

    /// WAVE3 L7 — one precise fix for SOS only; never starts region/significant monitoring.
    private static func captureSOSLocationPin(
        localization: LocalizationManager,
        api: APIService
    ) async -> String? {
        let lm = LocationManager.shared
        switch lm.authorizationStatus {
        case .notDetermined:
            lm.requestAuthorization(always: false)
        case .denied, .restricted:
            return " " + localization.localized("need_help_location_unavailable")
        default:
            break
        }
        guard lm.hasRequiredAuthorization() else {
            return " " + localization.localized("need_help_location_unavailable")
        }
        do {
            let location = try await lm.getCurrentLocationForPlaceSetup()
            let lat = location.coordinate.latitude
            let lon = location.coordinate.longitude
            _ = await withCheckedContinuation { (cont: CheckedContinuation<Void, Never>) in
                api.reportLocation(latitude: lat, longitude: lon, speed: nil) { _ in
                    cont.resume()
                }
            }
            if let line = await GeofenceGeocodingService.shared.reverseGeocodeAddressLine(for: location) {
                return " " + String(format: localization.localized("need_help_location_named"), line)
            }
            return " " + String(format: localization.localized("need_help_location_coords"), lat, lon)
        } catch {
            return " " + localization.localized("need_help_location_unavailable")
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
