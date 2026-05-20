import Foundation

/// E1 — ciphertext-only cache for Family Chat (Keychain, not UserDefaults plaintext).
enum FamilyChatCiphertextCache {
    private static func cacheKey(familyId: String) -> String {
        "family_chat_cipher_cache_\(familyId)"
    }

    /// Strip decrypted plaintext before persistence.
    static func sanitizeForStorage(_ message: FamilyChatMessageResponse) -> FamilyChatMessageResponse {
        let env = message.envelopeVersion ?? 1
        guard env == 2 else { return message }
        return FamilyChatMessageResponse(
            id: message.id,
            sender: message.sender,
            text: nil,
            timestamp: message.timestamp,
            isCurrentUser: message.isCurrentUser,
            messageType: message.messageType,
            voiceUrl: nil,
            voiceDuration: message.voiceDuration,
            mediaUrl: nil,
            mediaThumbnailUrl: nil,
            mediaType: message.mediaType,
            replyToMessageId: message.replyToMessageId,
            reactions: message.reactions,
            readStatus: message.readStatus,
            readAt: message.readAt,
            editedAt: message.editedAt,
            envelopeVersion: env,
            senderDeviceId: message.senderDeviceId,
            ciphertext: message.ciphertext,
            ciphertextContentType: message.ciphertextContentType,
            isLegacyPlaintext: false,
            mediaCiphertextUrl: message.mediaCiphertextUrl,
            mediaCiphertextHash: message.mediaCiphertextHash
        )
    }

    static func save(_ messages: [FamilyChatMessageResponse], familyId: String) {
        let fid = familyId.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !fid.isEmpty else { return }
        let sanitized = messages.map { sanitizeForStorage($0) }
        guard let data = try? JSONEncoder().encode(sanitized) else { return }
        KeychainManager.shared.save(data, scopedKey: cacheKey(familyId: fid))
    }

    static func load(familyId: String) -> [FamilyChatMessageResponse] {
        let fid = familyId.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !fid.isEmpty,
              let data = KeychainManager.shared.loadData(scopedKey: cacheKey(familyId: fid)),
              let messages = try? JSONDecoder().decode([FamilyChatMessageResponse].self, from: data) else {
            return []
        }
        return messages
    }

    static func clear(familyId: String) {
        let fid = familyId.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !fid.isEmpty else { return }
        KeychainManager.shared.delete(scopedKey: cacheKey(familyId: fid))
    }
}
