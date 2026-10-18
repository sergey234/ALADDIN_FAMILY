import Foundation

/// UX-36 W5 + WAVE3 L4 — local UN + soft family-chat + dedicated parent APNs (server).
enum GeofenceFamilyBridge {
    private static let throttleSeconds: TimeInterval = 30 * 60
    private static let throttlePrefix = "geofence_family_bridge_throttle_v1_"
    private static let apiThrottlePrefix = "geofence_family_api_throttle_v1_"
    /// Dedicated APNs path: shorter than chat soft (5 min) so parent gets timely alert.
    private static let apiThrottleSeconds: TimeInterval = 5 * 60

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
    /// Family chat mirror must use E2EE envelope v2 on prod.
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
        Task {
            _ = await FamilyAutoAlertSender.send(
                FamilyAutoAlertEvent(
                    kind: .urgentSignal,
                    displayName: displayName,
                    legacyPlaintext: message
                ),
                localization: localization,
                api: service
            )
        }
    }

    /// WAVE3 L4 — POST /api/family/geofence-event → parent APNs (deploy required on MAIN).
    @MainActor
    static func notifyParentsViaAPIIfNeeded(
        placeName: String,
        isArrival: Bool,
        regionId: String,
        eventType: String,
        localization: LocalizationManager = .shared,
        api: APIService? = nil,
        defaults: UserDefaults = .standard
    ) {
        let throttleKey = "\(apiThrottlePrefix)\(regionId)_\(isArrival ? "in" : "out")"
        let now = Date().timeIntervalSince1970
        let last = defaults.double(forKey: throttleKey)
        if last > 0, now - last < apiThrottleSeconds {
            return
        }
        defaults.set(now, forKey: throttleKey)

        let displayName = currentDisplayName(localization: localization)
        let service = api ?? APIService.shared
        service.postFamilyGeofenceEvent(
            placeName: placeName,
            isArrival: isArrival,
            regionId: regionId,
            eventType: eventType,
            displayName: displayName
        ) { result in
            if case .failure(let error) = result {
                print("⚠️ GeofenceFamilyBridge: geofence-event API failed: \(error.localizedDescription)")
            }
        }
    }

    /// WAVE3 G — «Срочный сигнал семье».
    /// Family chat mirror must use E2EE envelope v2; primary special endpoint stays in FamilyUrgentSignalService.
    @MainActor
    static func notifyParentsUrgentSignal(
        reason: String,
        localization: LocalizationManager = .shared,
        api: APIService? = nil
    ) {
        let service = api ?? APIService.shared
        let displayName = currentDisplayName(localization: localization)
        Task {
            _ = await FamilyAutoAlertSender.send(
                FamilyAutoAlertEvent(
                    kind: .urgentSignal,
                    displayName: displayName,
                    reason: reason
                ),
                localization: localization,
                api: service
            )
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
