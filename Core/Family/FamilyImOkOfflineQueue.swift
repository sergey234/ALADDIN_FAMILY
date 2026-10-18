import Foundation

/// qa-10: when family chat/E2EE is not ready, keep auto-alert events for later encrypted flush.
enum FamilyImOkOfflineQueue {
    private static let legacyDefaultsKey = "family_imok_offline_queue_v1"
    private static let fallbackDefaultsKey = "family_auto_alert_queue_fallback_v1"
    private static let scopedKey = "family_auto_alert_queue_v1"
    private static let maxItems = 20

    struct Item: Codable, Equatable {
        let id: String
        let message: String
        let kind: String // "im_ok" | "need_help"
        let createdAt: Date
    }

    static func enqueue(_ event: FamilyAutoAlertEvent) {
        var items = loadEvents()
        guard !items.contains(where: { $0.id == event.id }) else { return }
        items.append(event)
        if items.count > maxItems {
            items = Array(items.suffix(maxItems))
        }
        if !saveEvents(items) {
            saveFallbackEvents(items, defaults: .standard)
        }
    }

    static func enqueue(message: String, kind: String, defaults: UserDefaults = .standard) {
        let trimmed = message.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        let mappedKind = mapKind(kind)
        enqueue(FamilyAutoAlertEvent(kind: mappedKind, displayName: "", legacyPlaintext: trimmed))
    }

    static func load(defaults: UserDefaults = .standard) -> [Item] {
        loadEvents(defaults: defaults).map {
            Item(
                id: $0.id,
                message: $0.legacyPlaintext ?? $0.kind.rawValue,
                kind: $0.kind.rawValue,
                createdAt: $0.createdAt
            )
        }
    }

    static func clear(defaults: UserDefaults = .standard) {
        KeychainManager.shared.delete(scopedKey: scopedKey)
        defaults.removeObject(forKey: legacyDefaultsKey)
        defaults.removeObject(forKey: fallbackDefaultsKey)
    }

    /// Attempt to send queued events as E2EE v2 messages; removes only successes.
    /// Runs on MainActor because `APIService` is `@MainActor`.
    /// Note: do not use `api: APIService = .shared` — default args are nonisolated.
    @MainActor
    static func flush(api: APIService? = nil, defaults: UserDefaults = .standard) async {
        let service = api ?? APIService.shared
        let pending = loadEvents(defaults: defaults)
        guard !pending.isEmpty else { return }
        var remaining: [FamilyAutoAlertEvent] = []
        var deliveredCount = 0
        for event in pending {
            let result = await FamilyAutoAlertSender.send(event, api: service, enqueueOnFailure: false)
            if case .success = result {
                deliveredCount += 1
            } else {
                remaining.append(event)
            }
        }
        if saveEvents(remaining) {
            defaults.removeObject(forKey: fallbackDefaultsKey)
        } else {
            saveFallbackEvents(remaining, defaults: defaults)
        }
        // W5: when offline queue finally reaches family chat — soft local ack (inbox + banner).
        if deliveredCount > 0 {
            let loc = LocalizationManager.shared
            NotificationManager.shared.sendLocalNotification(
                title: loc.localized("im_ok_queue_delivered_title"),
                body: loc.localized("im_ok_queue_delivered_body"),
                category: .family,
                userInfo: [
                    "type": "im_ok_queue_delivered",
                    "event_id": "imok-flush-\(Int(Date().timeIntervalSince1970))",
                    "deepLink": "aladdin://family"
                ],
                delay: 0.2
            )
        }
    }

    private static func loadEvents(defaults: UserDefaults = .standard) -> [FamilyAutoAlertEvent] {
        var items: [FamilyAutoAlertEvent] = []
        if let data = KeychainManager.shared.loadData(scopedKey: scopedKey),
           let decoded = try? JSONDecoder().decode([FamilyAutoAlertEvent].self, from: data) {
            items = decoded
        }

        let fallback = loadFallbackEvents(defaults: defaults)
        if !fallback.isEmpty {
            let knownIds = Set(items.map(\.id))
            items.append(contentsOf: fallback.filter { !knownIds.contains($0.id) })
        }

        let legacy = loadLegacy(defaults: defaults)
        if !legacy.isEmpty {
            let migrated = legacy.map {
                FamilyAutoAlertEvent(
                    id: $0.id,
                    kind: mapKind($0.kind),
                    displayName: "",
                    createdAt: $0.createdAt,
                    legacyPlaintext: $0.message
                )
            }
            let knownIds = Set(items.map(\.id))
            items.append(contentsOf: migrated.filter { !knownIds.contains($0.id) })
        }

        if !fallback.isEmpty || !legacy.isEmpty {
            items = Array(items.suffix(maxItems))
            if saveEvents(items) {
                defaults.removeObject(forKey: fallbackDefaultsKey)
                defaults.removeObject(forKey: legacyDefaultsKey)
            } else if !fallback.isEmpty {
                saveFallbackEvents(items, defaults: defaults)
            }
        }

        return Array(items.suffix(maxItems))
    }

    private static func loadLegacy(defaults: UserDefaults) -> [Item] {
        guard let data = defaults.data(forKey: legacyDefaultsKey),
              let items = try? JSONDecoder().decode([Item].self, from: data) else {
            return []
        }
        return items
    }

    private static func loadFallbackEvents(defaults: UserDefaults) -> [FamilyAutoAlertEvent] {
        guard let data = defaults.data(forKey: fallbackDefaultsKey),
              let items = try? JSONDecoder().decode([FamilyAutoAlertEvent].self, from: data) else {
            return []
        }
        return items
    }

    private static func saveFallbackEvents(_ items: [FamilyAutoAlertEvent], defaults: UserDefaults) {
        guard let data = try? JSONEncoder().encode(Array(items.suffix(maxItems))) else { return }
        defaults.set(data, forKey: fallbackDefaultsKey)
    }

    private static func mapKind(_ raw: String) -> FamilyAutoAlertKind {
        if let kind = FamilyAutoAlertKind(rawValue: raw) { return kind }
        switch raw {
        case "family_urgent", "urgent", "geofence", "sos_family_alarm":
            return .urgentSignal
        default:
            return .needHelp
        }
    }

    @discardableResult
    private static func saveEvents(_ items: [FamilyAutoAlertEvent]) -> Bool {
        guard let data = try? JSONEncoder().encode(items) else { return false }
        KeychainManager.shared.save(data, scopedKey: scopedKey)
        guard let persisted = KeychainManager.shared.loadData(scopedKey: scopedKey),
              let decoded = try? JSONDecoder().decode([FamilyAutoAlertEvent].self, from: persisted) else {
            return false
        }
        return decoded == items
    }
}
