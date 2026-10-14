import Foundation

/// UX-36 W5 — hybrid place events: local UN + in-app inbox + soft family-chat (APNs path parents already have).
enum GeofenceFamilyBridge {
    private static let throttleSeconds: TimeInterval = 30 * 60
    private static let throttlePrefix = "geofence_family_bridge_throttle_v1_"

    /// Returns true if this place+direction is outside the soft-notify throttle window.
    static func shouldSoftNotify(
        regionId: String,
        isArrival: Bool,
        now: Date = Date(),
        defaults: UserDefaults = .standard
    ) -> Bool {
        let throttleKey = "\(throttlePrefix)\(regionId)_\(isArrival ? "in" : "out")"
        let last = defaults.double(forKey: throttleKey)
        if last > 0, now.timeIntervalSince1970 - last < throttleSeconds {
            return false
        }
        defaults.set(now.timeIntervalSince1970, forKey: throttleKey)
        return true
    }

    /// Soft-notify family via chat (existing push pipeline). Throttled per place+direction.
    @MainActor
    static func softNotifyFamilyIfNeeded(
        placeName: String,
        isArrival: Bool,
        regionId: String,
        localization: LocalizationManager = .shared,
        api: APIService? = nil
    ) {
        guard shouldSoftNotify(regionId: regionId, isArrival: isArrival) else { return }

        let displayName = Self.currentDisplayName(localization: localization)
        let templateKey = isArrival ? "geofence_family_chat_arrived" : "geofence_family_chat_left"
        let message = String(
            format: localization.localized(templateKey),
            displayName,
            placeName
        ).trimmingCharacters(in: .whitespacesAndNewlines)
        guard !message.isEmpty else { return }

        let service = api ?? APIService.shared
        let familyId = UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey)
            ?? UserDefaults.standard.string(forKey: "family_id")
        service.sendFamilyChatMessage(
            message: message,
            familyId: familyId,
            messageType: "text",
            voiceUrl: nil,
            voiceDuration: nil,
            mediaUrl: nil,
            mediaType: nil,
            replyToMessageId: nil
        ) { result in
            if case .failure = result {
                // Keep local path honest — soft enqueue as ImOK-style offline item.
                FamilyImOkOfflineQueue.enqueue(message: message, kind: "geofence")
            }
        }
    }

    private static func currentDisplayName(localization: LocalizationManager) -> String {
        let raw = (UserDefaults.standard.string(forKey: "user_name")
            ?? UserDefaults.standard.string(forKey: "user_display_name")
            ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        if !raw.isEmpty, !raw.hasPrefix("MEM_") {
            return raw
        }
        return localization.localized("family_you")
    }
}
