import Foundation

/// qa-10: when family chat is down, keep ImOK / NeedHelp text for later flush (honest local-first).
enum FamilyImOkOfflineQueue {
    private static let key = "family_imok_offline_queue_v1"
    private static let maxItems = 20

    struct Item: Codable, Equatable {
        let id: String
        let message: String
        let kind: String // "im_ok" | "need_help"
        let createdAt: Date
    }

    static func enqueue(message: String, kind: String, defaults: UserDefaults = .standard) {
        let trimmed = message.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        var items = load(defaults: defaults)
        items.append(Item(id: UUID().uuidString, message: trimmed, kind: kind, createdAt: Date()))
        if items.count > maxItems {
            items = Array(items.suffix(maxItems))
        }
        save(items, defaults: defaults)
    }

    static func load(defaults: UserDefaults = .standard) -> [Item] {
        guard let data = defaults.data(forKey: key),
              let items = try? JSONDecoder().decode([Item].self, from: data) else {
            return []
        }
        return items
    }

    static func clear(defaults: UserDefaults = .standard) {
        defaults.removeObject(forKey: key)
    }

    /// Attempt to send queued messages; removes only successes.
    /// Runs on MainActor because `APIService` is `@MainActor`.
    /// Note: do not use `api: APIService = .shared` — default args are nonisolated.
    @MainActor
    static func flush(api: APIService? = nil, defaults: UserDefaults = .standard) async {
        let service = api ?? APIService.shared
        let pending = load(defaults: defaults)
        guard !pending.isEmpty else { return }
        var remaining: [Item] = []
        let familyId = UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey)
            ?? UserDefaults.standard.string(forKey: "family_id")
        for item in pending {
            let ok: Bool = await withCheckedContinuation { continuation in
                service.sendFamilyChatMessage(
                    message: item.message,
                    familyId: familyId,
                    messageType: "text",
                    voiceUrl: nil,
                    voiceDuration: nil,
                    mediaUrl: nil,
                    mediaType: nil,
                    replyToMessageId: nil
                ) { result in
                    continuation.resume(returning: (try? result.get()) != nil)
                }
            }
            if !ok { remaining.append(item) }
        }
        save(remaining, defaults: defaults)
    }

    private static func save(_ items: [Item], defaults: UserDefaults) {
        guard let data = try? JSONEncoder().encode(items) else { return }
        defaults.set(data, forKey: key)
    }
}
