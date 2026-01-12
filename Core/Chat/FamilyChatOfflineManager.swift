import Foundation
import Combine

/**
 * 💾 Family Chat Offline Manager
 * Кэширование и синхронизация сообщений в офлайн режиме
 */

class FamilyChatOfflineManager: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var isOffline: Bool = false
    @Published var pendingMessagesCount: Int = 0
    @Published var isSyncing: Bool = false
    
    // MARK: - Singleton
    
    static let shared = FamilyChatOfflineManager()
    
    // MARK: - Private Properties
    
    private let messagesCacheKey = "family_chat_messages_cache"
    private let pendingMessagesKey = "family_chat_pending_messages"
    private let lastSyncKey = "family_chat_last_sync"
    
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    private init() {
        _ = loadPendingMessages()
        observeNetworkStatus()
    }
    
    // MARK: - Cache Methods
    
    /// Сохраняет сообщения в кэш
    func cacheMessages(_ messages: [FamilyChatMessageResponse]) {
        guard let encoded = try? JSONEncoder().encode(messages) else {
            print("❌ FamilyChatOfflineManager: Ошибка кодирования сообщений")
            return
        }
        
        UserDefaults.standard.set(encoded, forKey: messagesCacheKey)
        UserDefaults.standard.set(Date(), forKey: lastSyncKey)
        
        print("✅ FamilyChatOfflineManager: Сохранено \(messages.count) сообщений в кэш")
    }
    
    /// Загружает сообщения из кэша
    func loadCachedMessages() -> [FamilyChatMessageResponse] {
        guard let data = UserDefaults.standard.data(forKey: messagesCacheKey),
              let messages = try? JSONDecoder().decode([FamilyChatMessageResponse].self, from: data) else {
            return []
        }
        
        print("✅ FamilyChatOfflineManager: Загружено \(messages.count) сообщений из кэша")
        return messages
    }
    
    /// Очищает кэш
    func clearCache() {
        UserDefaults.standard.removeObject(forKey: messagesCacheKey)
        UserDefaults.standard.removeObject(forKey: lastSyncKey)
        print("✅ FamilyChatOfflineManager: Кэш очищен")
    }
    
    // MARK: - Pending Messages Queue
    
    /// Добавляет сообщение в очередь отправки
    func addPendingMessage(_ message: PendingChatMessage) {
        var pending = loadPendingMessages()
        pending.append(message)
        savePendingMessages(pending)
        
        DispatchQueue.main.async {
            self.pendingMessagesCount = pending.count
        }
        
        print("✅ FamilyChatOfflineManager: Добавлено сообщение в очередь (\(pending.count) в очереди)")
    }
    
    /// Загружает очередь сообщений
    func loadPendingMessages() -> [PendingChatMessage] {
        guard let data = UserDefaults.standard.data(forKey: pendingMessagesKey),
              let messages = try? JSONDecoder().decode([PendingChatMessage].self, from: data) else {
            DispatchQueue.main.async {
                self.pendingMessagesCount = 0
            }
            return []
        }
        
        DispatchQueue.main.async {
            self.pendingMessagesCount = messages.count
        }
        
        return messages
    }
    
    /// Сохраняет очередь сообщений
    private func savePendingMessages(_ messages: [PendingChatMessage]) {
        guard let encoded = try? JSONEncoder().encode(messages) else {
            print("❌ FamilyChatOfflineManager: Ошибка кодирования очереди")
            return
        }
        
        UserDefaults.standard.set(encoded, forKey: pendingMessagesKey)
    }
    
    /// Удаляет сообщение из очереди
    func removePendingMessage(_ id: UUID) {
        var pending = loadPendingMessages()
        pending.removeAll { $0.id == id }
        savePendingMessages(pending)
        
        DispatchQueue.main.async {
            self.pendingMessagesCount = pending.count
        }
    }
    
    /// Очищает очередь
    func clearPendingMessages() {
        UserDefaults.standard.removeObject(forKey: pendingMessagesKey)
        DispatchQueue.main.async {
            self.pendingMessagesCount = 0
        }
        print("✅ FamilyChatOfflineManager: Очередь очищена")
    }
    
    // MARK: - Sync Methods
    
    /// Синхронизирует очередь сообщений с сервером
    func syncPendingMessages(apiService: APIService, completion: @escaping (Bool) -> Void) {
        let pending = loadPendingMessages()
        guard !pending.isEmpty else {
            completion(true)
            return
        }
        
        DispatchQueue.main.async {
            self.isSyncing = true
        }
        
        var successCount = 0
        let group = DispatchGroup()
        
        for message in pending {
            group.enter()
            
            apiService.sendFamilyChatMessage(
                message: message.text,
                familyId: message.familyId,
                messageType: message.messageType,
                voiceUrl: message.voiceUrl,
                voiceDuration: message.voiceDuration,
                mediaUrl: message.mediaUrl,
                mediaType: message.mediaType,
                replyToMessageId: message.replyToMessageId,
                completion: { result in
                    switch result {
                    case .success(_):
                        successCount += 1
                        self.removePendingMessage(message.id)
                    case .failure(let error):
                        print("❌ FamilyChatOfflineManager: Ошибка отправки сообщения \(message.id): \(error.localizedDescription)")
                    }
                    group.leave()
                }
            )
        }
        
        group.notify(queue: .main) {
            self.isSyncing = false
            let allSynced = successCount == pending.count
            print("✅ FamilyChatOfflineManager: Синхронизация завершена (\(successCount)/\(pending.count))")
            completion(allSynced)
        }
    }
    
    // MARK: - Network Status
    
    private func observeNetworkStatus() {
        // Используем существующий NetworkingManager если есть
        // Или простую проверку через URLSession
        Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { [weak self] _ in
            self?.checkNetworkStatus()
        }
    }
    
    private func checkNetworkStatus() {
        // Простая проверка доступности сети
        let url = URL(string: "https://www.google.com")!
        let task = URLSession.shared.dataTask(with: url) { [weak self] _, response, _ in
            DispatchQueue.main.async {
                if let httpResponse = response as? HTTPURLResponse {
                    self?.isOffline = httpResponse.statusCode != 200
                } else {
                    self?.isOffline = true
                }
            }
        }
        task.resume()
    }
}

// MARK: - Pending Chat Message

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
    
    init(id: UUID = UUID(), text: String?, familyId: String?, messageType: String? = "text", voiceUrl: String? = nil, voiceDuration: Double? = nil, mediaUrl: String? = nil, mediaType: String? = nil, replyToMessageId: String? = nil) {
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
    }
}

