import Foundation
import Combine

/**
 * 💾 Family Chat Offline Manager
 * Кэш ciphertext в Keychain; очередь pending — только v2 envelope при включённом E2EE.
 */

class FamilyChatOfflineManager: ObservableObject {

    @Published var isOffline: Bool = false
    @Published var pendingMessagesCount: Int = 0
    @Published var isSyncing: Bool = false

    let unifiedStore = UnifiedOfflineStore.shared
    static let shared = FamilyChatOfflineManager()

    private let pendingMessagesKey = "family_chat_pending_messages_v2"
    private let lastSyncKey = "family_chat_last_sync"

    private var cancellables = Set<AnyCancellable>()

    private init() {
        _ = loadPendingMessages()
        observeOfflineManager()
    }

    // MARK: - Cache (Keychain ciphertext-only)

    func cacheMessages(_ messages: [FamilyChatMessageResponse], familyId: String) {
        // Keychain-only cache for ciphertext. Do NOT mirror every GET/poll into UnifiedOfflineStore:
        // that created a new unsynced Core Data row per message per poll → infinite POST
        // /api/offline-storage/data/update (see build 200 fix).
        FamilyChatCiphertextCache.save(messages, familyId: familyId)
        UserDefaults.standard.set(Date(), forKey: lastSyncKey)
    }

    func loadCachedMessages(familyId: String?) -> [FamilyChatMessageResponse] {
        guard let fid = familyId?.trimmingCharacters(in: .whitespacesAndNewlines), !fid.isEmpty else {
            return []
        }
        return FamilyChatCiphertextCache.load(familyId: fid)
    }

    func clearCache(familyId: String?) {
        if let fid = familyId?.trimmingCharacters(in: .whitespacesAndNewlines), !fid.isEmpty {
            FamilyChatCiphertextCache.clear(familyId: fid)
        }
        UserDefaults.standard.removeObject(forKey: lastSyncKey)
    }

    // MARK: - Pending queue

    func addPendingMessage(_ message: PendingChatMessage) {
        var pending = loadPendingMessages()
        pending.append(message)
        savePendingMessages(pending)
        DispatchQueue.main.async {
            self.pendingMessagesCount = pending.count
        }
    }

    func loadPendingMessages() -> [PendingChatMessage] {
        guard let data = UserDefaults.standard.data(forKey: pendingMessagesKey),
              let messages = try? JSONDecoder().decode([PendingChatMessage].self, from: data) else {
            DispatchQueue.main.async { self.pendingMessagesCount = 0 }
            return []
        }
        DispatchQueue.main.async { self.pendingMessagesCount = messages.count }
        return messages
    }

    private func savePendingMessages(_ messages: [PendingChatMessage]) {
        guard let encoded = try? JSONEncoder().encode(messages) else { return }
        UserDefaults.standard.set(encoded, forKey: pendingMessagesKey)
    }

    func removePendingMessage(_ id: UUID) {
        var pending = loadPendingMessages()
        pending.removeAll { $0.id == id }
        savePendingMessages(pending)
        DispatchQueue.main.async { self.pendingMessagesCount = pending.count }
    }

    func clearPendingMessages() {
        UserDefaults.standard.removeObject(forKey: pendingMessagesKey)
        DispatchQueue.main.async { self.pendingMessagesCount = 0 }
    }

    func syncPendingMessages(apiService: APIService, completion: @escaping (Bool) -> Void) {
        let pending = loadPendingMessages()
        guard !pending.isEmpty else {
            completion(true)
            return
        }

        DispatchQueue.main.async { self.isSyncing = true }

        var successCount = 0
        let group = DispatchGroup()

        for message in pending {
            if AppConfig.isFamilyChatE2EEEnabled {
                guard message.envelopeVersion == 2,
                      let cipher = message.ciphertext,
                      !cipher.isEmpty else {
                    continue
                }
            }

            group.enter()
            Task { @MainActor in
                apiService.sendFamilyChatMessage(
                    message: message.envelopeVersion == 2 ? nil : message.text,
                    familyId: message.familyId,
                    messageType: message.messageType,
                    voiceUrl: message.envelopeVersion == 2 ? nil : message.voiceUrl,
                    voiceDuration: message.voiceDuration,
                    mediaUrl: message.envelopeVersion == 2 ? nil : message.mediaUrl,
                    mediaType: message.mediaType,
                    replyToMessageId: message.replyToMessageId,
                    envelopeVersion: message.envelopeVersion,
                    senderDeviceId: message.senderDeviceId,
                    ciphertext: message.ciphertext,
                    mediaCiphertextUrl: message.mediaCiphertextUrl,
                    mediaCiphertextHash: message.mediaCiphertextHash
                ) { result in
                    switch result {
                    case .success:
                        successCount += 1
                        self.removePendingMessage(message.id)
                    case .failure(let error):
                        print("❌ FamilyChatOfflineManager sync: \(error.localizedDescription)")
                    }
                    group.leave()
                }
            }
        }

        group.notify(queue: .main) {
            self.isSyncing = false
            completion(successCount == pending.count)
        }
    }

    private func observeOfflineManager() {
        OfflineManager.shared.$isOnline
            .receive(on: DispatchQueue.main)
            .sink { [weak self] online in
                self?.isOffline = !online
            }
            .store(in: &cancellables)
    }
}

struct PendingChatMessage: Codable, Identifiable {
    let id: UUID
    let text: String?
    let familyId: String?
    let messageType: String?
    let voiceUrl: String?
    let voiceDuration: Double?
    let mediaUrl: String?
    let mediaType: String?
    let replyToMessageId: String?
    let timestamp: Date
    let envelopeVersion: Int?
    let senderDeviceId: String?
    let ciphertext: String?
    let mediaCiphertextUrl: String?
    let mediaCiphertextHash: String?

    init(
        id: UUID = UUID(),
        text: String?,
        familyId: String?,
        messageType: String? = "text",
        voiceUrl: String? = nil,
        voiceDuration: Double? = nil,
        mediaUrl: String? = nil,
        mediaType: String? = nil,
        replyToMessageId: String? = nil,
        envelopeVersion: Int? = nil,
        senderDeviceId: String? = nil,
        ciphertext: String? = nil,
        mediaCiphertextUrl: String? = nil,
        mediaCiphertextHash: String? = nil
    ) {
        self.id = id
        self.text = text
        self.familyId = familyId
        self.messageType = messageType
        self.voiceUrl = voiceUrl
        self.voiceDuration = voiceDuration
        self.mediaUrl = mediaUrl
        self.mediaType = mediaType
        self.replyToMessageId = replyToMessageId
        self.timestamp = Date()
        self.envelopeVersion = envelopeVersion
        self.senderDeviceId = senderDeviceId
        self.ciphertext = ciphertext
        self.mediaCiphertextUrl = mediaCiphertextUrl
        self.mediaCiphertextHash = mediaCiphertextHash
    }
}
