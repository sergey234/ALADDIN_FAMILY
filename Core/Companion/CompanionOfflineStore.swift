import Foundation

/// P1-21 — локальный кэш последних thread + черновик сообщения (без push).
enum CompanionOfflineStore {
    private static let threadsKey = "companion_offline_threads_v1"
    private static let messagesPrefix = "companion_offline_thread_msgs_v1_"
    private static let draftPrefix = "companion_draft_v1_"

    private struct CachedBubble: Codable {
        let id: String
        let text: String
        let isUser: Bool
        let feedbackVote: String?
    }

    static func saveThreads(_ threads: [CompanionThreadSummary]) {
        guard let data = try? JSONEncoder().encode(threads) else { return }
        UserDefaults.standard.set(data, forKey: threadsKey)
    }

    static func loadThreads() -> [CompanionThreadSummary] {
        guard let data = UserDefaults.standard.data(forKey: threadsKey),
              let rows = try? JSONDecoder().decode([CompanionThreadSummary].self, from: data) else {
            return []
        }
        return rows
    }

    static func saveMessages(threadId: String, messages: [CompanionChatBubble]) {
        guard !threadId.isEmpty else { return }
        let payload = messages.map {
            CachedBubble(
                id: $0.id.uuidString,
                text: $0.text,
                isUser: $0.isUser,
                feedbackVote: $0.feedbackVote
            )
        }
        guard let data = try? JSONEncoder().encode(payload) else { return }
        UserDefaults.standard.set(data, forKey: messagesPrefix + threadId)
    }

    static func loadMessages(threadId: String) -> [CompanionChatBubble] {
        guard !threadId.isEmpty,
              let data = UserDefaults.standard.data(forKey: messagesPrefix + threadId),
              let rows = try? JSONDecoder().decode([CachedBubble].self, from: data) else {
            return []
        }
        return rows.map {
            CompanionChatBubble(
                id: UUID(uuidString: $0.id) ?? UUID(),
                text: $0.text,
                isUser: $0.isUser,
                feedbackVote: $0.feedbackVote
            )
        }
    }

    static func saveDraft(characterId: String, text: String) {
        UserDefaults.standard.set(text, forKey: draftPrefix + characterId)
    }

    static func loadDraft(characterId: String) -> String {
        UserDefaults.standard.string(forKey: draftPrefix + characterId) ?? ""
    }
}
