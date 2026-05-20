import Foundation
import Combine
import UIKit

/// 📤 MediaUploadManager
/// Центральный менеджер загрузки медиа в семейный чат
/// Поддерживает: progress, offline queue, retry, thumbnails, integration with OfflineManager
///
/// Все мутации `@Published` только на главном акторе; колбэки UI и цепочка загрузок
/// откладываются на следующий цикл run loop, чтобы не ловить реентрантность SwiftUI/Combine (watchdog 0x8BADF00D).
@MainActor
final class MediaUploadManager: ObservableObject {
    
    static let shared = MediaUploadManager()
    
    @Published var isUploading = false
    @Published var uploadProgress: [String: Double] = [:] // messageId -> progress
    @Published var pendingUploadsCount = 0
    
    private let apiService = APIService.shared
    private let offlineManager = OfflineManager.shared
    private let chatOfflineManager = FamilyChatOfflineManager.shared
    
    private var pendingUploads: [PendingMediaUpload] = []
    private var cancellables = Set<AnyCancellable>()
    
    private init() {
        loadPendingUploads()
        setupOfflineObserver()
    }
    
    // MARK: - Public API
    
    /// Загрузить медиа с прогрессом и поддержкой offline
    func uploadMedia(
        data: Data,
        type: UploadMediaType,
        forMessageId messageId: String,
        familyId: String? = nil,
        completion: @escaping (Result<String, Error>) -> Void
    ) {
        let pending = PendingMediaUpload(
            id: messageId,
            data: data,
            type: type,
            createdAt: Date(),
            familyId: familyId
        )
        
        pendingUploads.append(pending)
        pendingUploadsCount = pendingUploads.count
        savePendingUploads()
        
        uploadNextPending(completion: completion)
    }
    
    // MARK: - Private
    
    private func uploadNextPending(completion: @escaping (Result<String, Error>) -> Void) {
        guard let pending = pendingUploads.first else {
            completion(.failure(NSError(domain: "MediaUpload", code: -1, userInfo: [NSLocalizedDescriptionKey: "No pending uploads"])))
            return
        }
        
        isUploading = true
        uploadProgress[pending.id] = 0.0

        let useE2EE = AppConfig.isFamilyChatE2EEEnabled && FamilyE2EEManager.shared.isReady
        let familyId = pending.familyId ?? ""

        if useE2EE, !familyId.isEmpty {
            do {
                let enc = try FamilyE2EEMediaCrypto.encryptFile(pending.data)
                apiService.uploadEncryptedMedia(
                    encryptedData: enc.data,
                    contentHash: enc.sha256Hex,
                    familyId: familyId
                ) { [weak self] result in
                    DispatchQueue.main.async {
                        self?.isUploading = false
                        switch result {
                        case .success(let payload):
                            self?.handleSuccessfulE2EEUpload(
                                pending: pending,
                                url: payload.url,
                                hash: payload.hash,
                                keyBase64: enc.keyBase64,
                                completion: completion
                            )
                        case .failure(let error):
                            self?.handleFailedUpload(pending: pending, error: error, completion: completion)
                        }
                    }
                }
            } catch {
                isUploading = false
                completion(.failure(error))
            }
            return
        }

        apiService.uploadMedia(
            data: pending.data,
            type: pending.type.rawValue,
            filename: pending.filename,
            familyId: pending.familyId,
            progress: { [weak self] progress in
                DispatchQueue.main.async {
                    self?.uploadProgress[pending.id] = progress
                }
            }
        ) { [weak self] result in
            DispatchQueue.main.async {
                self?.isUploading = false
                
                switch result {
                case .success(let url):
                    self?.handleSuccessfulUpload(pending: pending, url: url, completion: completion)
                case .failure(let error):
                    self?.handleFailedUpload(pending: pending, error: error, completion: completion)
                }
            }
        }
    }

    /// Результат E2EE upload: URL blob + hash + ключ для envelope.
    struct E2EEMediaUploadResult {
        let url: String
        let hash: String
        let keyBase64: String
    }

    private var lastE2EEUploadMeta: [String: E2EEMediaUploadResult] = [:]

    func lastE2EEUpload(forMessageId id: String) -> E2EEMediaUploadResult? {
        lastE2EEUploadMeta[id]
    }

    private func handleSuccessfulE2EEUpload(
        pending: PendingMediaUpload,
        url: String,
        hash: String,
        keyBase64: String,
        completion: @escaping (Result<String, Error>) -> Void
    ) {
        lastE2EEUploadMeta[pending.id] = E2EEMediaUploadResult(url: url, hash: hash, keyBase64: keyBase64)
        handleSuccessfulUpload(pending: pending, url: url, completion: completion)
    }
    
    private func handleSuccessfulUpload(pending: PendingMediaUpload, url: String, completion: @escaping (Result<String, Error>) -> Void) {
        print("✅ MediaUploadManager: Successfully uploaded \(pending.type) -> \(url)")
        
        // Удаляем из очереди
        pendingUploads.removeAll { $0.id == pending.id }
        pendingUploadsCount = pendingUploads.count
        savePendingUploads()
        uploadProgress.removeValue(forKey: pending.id)
        
        let hasMore = !pendingUploads.isEmpty
        // Откладываем колбэк и следующую загрузку: иначе обновление сообщений в SwiftUI
        // может реентрантно зайти в Combine во время текущего objectWillChange.
        DispatchQueue.main.async { [weak self] in
            completion(.success(url))
            guard let self, hasMore else { return }
            self.uploadNextPending(completion: { _ in })
        }
    }
    
    private func handleFailedUpload(pending: PendingMediaUpload, error: Error, completion: @escaping (Result<String, Error>) -> Void) {
        print("❌ MediaUploadManager: Upload failed for \(pending.id): \(error.localizedDescription)")
        
        // Добавляем в offline очередь
        offlineManager.addToPendingQueue(
            operation: { [weak self] in
                guard let self else { throw error }
                try await self.retryUpload(pending: pending)
                return ()
            },
            error: NetworkError.unknown(error)
        )
        
        DispatchQueue.main.async {
            completion(.failure(error))
        }
    }
    
    private func retryUpload(pending: PendingMediaUpload) async throws {
        // Логика повторной попытки
        print("🔄 Retrying upload for message \(pending.id)")
        // Повторная загрузка будет вызвана через OfflineManager
    }
    
    private func setupOfflineObserver() {
        offlineManager.$isOnline
            .receive(on: DispatchQueue.main)
            .sink { [weak self] isOnline in
                guard let self else { return }
                if isOnline && !self.pendingUploads.isEmpty {
                    self.processPendingUploads()
                }
            }
            .store(in: &cancellables)
    }
    
    private func processPendingUploads() {
        guard !pendingUploads.isEmpty else { return }
        uploadNextPending { _ in }
    }
    
    // MARK: - Persistence
    
    private func savePendingUploads() {
        if let encoded = try? JSONEncoder().encode(pendingUploads) {
            UserDefaults.standard.set(encoded, forKey: "pending_media_uploads")
        }
    }
    
    private func loadPendingUploads() {
        guard let data = UserDefaults.standard.data(forKey: "pending_media_uploads"),
              let decoded = try? JSONDecoder().decode([PendingMediaUpload].self, from: data) else {
            return
        }
        pendingUploads = decoded
        pendingUploadsCount = pendingUploads.count
    }
}

// MARK: - Supporting Types

enum UploadMediaType: String, Codable {
    case image, video, audio, voice
}

struct PendingMediaUpload: Codable, Identifiable {
    let id: String
    let data: Data
    let type: UploadMediaType
    let createdAt: Date
    var familyId: String?
    
    var filename: String {
        switch type {
        case .image: return "image_\(Int(createdAt.timeIntervalSince1970)).jpg"
        case .video: return "video_\(Int(createdAt.timeIntervalSince1970)).mp4"
        case .audio, .voice: return "voice_\(Int(createdAt.timeIntervalSince1970)).m4a"
        }
    }
}
