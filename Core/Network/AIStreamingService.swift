import Foundation
import Combine
import UIKit

/// 🚀 AI Streaming Service v2 (Clean Consolidated Version - Fixed)
/// Полноценная реализация токен-стриминга для AI-ассистента с поддержкой resume после reconnect/background/kill
/// - AsyncThrowingStream + improved SSE parsing
/// - State persistence via UserDefaults (planned CoreData extension for full offline)
/// - Offline observation via OfflineManager + NotificationCenter for app lifecycle
/// - Error handling, retry logic stub, cancel support
/// Соответствует лучшим практикам 2026 и InstantDB-like streaming + offline-first.
/// This replaces the previous duplicated/broken version.
final class AIStreamingService: ObservableObject {
    
    static let shared = AIStreamingService()
    
    @Published var isStreaming: Bool = false
    @Published var currentStreamMessage: String = ""
    @Published var currentMessageId: String?
    
    /// Вычисляемое свойство, чтобы не участвовать в цикле инициализации с `OfflineManager`.
    private var offlineManager: OfflineManager { OfflineManager.shared }
    private var currentStreamTask: Task<Void, Never>?
    private var accumulatedText: String = ""
    private var lastTokenIndex: Int = 0
    private var cancellables = Set<AnyCancellable>()
    
    // Ключи для сохранения состояния стрима 
    private let streamStateKey = "ai_current_stream_state"
    private let homeChatLastAIActivityKey = "home_chat_last_ai_activity_at"
    
    private init() {
        restoreLastStreamState()
        setupOfflineObservation()
    }
    
    private func setupOfflineObservation() {
        // Auto-resume when back online
        offlineManager.$isOnline
            .sink { [weak self] isOnline in
                guard let self = self, isOnline, !self.currentStreamMessage.isEmpty else { return }
                Task { await self.attemptResumeIfNeeded() }
            }
            .store(in: &cancellables)
        
        // Save state when going to background
        NotificationCenter.default.publisher(for: UIApplication.willResignActiveNotification)
            .sink { [weak self] _ in
                self?.saveCurrentStreamState()
            }
            .store(in: &cancellables)
        
        // Restore when becoming active
        NotificationCenter.default.publisher(for: UIApplication.didBecomeActiveNotification)
            .sink { [weak self] _ in
                self?.restoreStreamStateIfNeeded()
            }
            .store(in: &cancellables)
    }
    
    private func saveCurrentStreamState() {
        guard let messageId = currentMessageId, !accumulatedText.isEmpty else { return }
        
        let state: [String: Any] = [
            "messageId": messageId,
            "lastIndex": lastTokenIndex,
            "accumulatedText": accumulatedText,
            "timestamp": Date().timeIntervalSince1970
        ]
        
        UserDefaults.standard.set(state, forKey: streamStateKey)
        print("💾 AIStreamingService: Saved current stream state before background")
    }
    
    private func restoreStreamStateIfNeeded() {
        guard let state = UserDefaults.standard.dictionary(forKey: streamStateKey),
              let messageId = state["messageId"] as? String,
              let lastIndex = state["lastIndex"] as? Int,
              let savedText = state["accumulatedText"] as? String else {
            return
        }
        
        currentMessageId = messageId
        lastTokenIndex = lastIndex
        accumulatedText = savedText
        currentStreamMessage = savedText
        isStreaming = true
        
        print("♻️ AIStreamingService: Restored stream state after becoming active")
        
        Task {
            do {
                _ = try await resumeStream(messageId: messageId, lastIndex: lastIndex)
            } catch {
                print("⚠️ AIStreamingService: Resume failed on activate: \(error.localizedDescription)")
                clearStreamState()
            }
        }
    }
    
    /// Основной метод для стриминга (используется в ViewModel)
    func streamMessage(
        message: String,
        context: String = "general",
        messageId: String? = nil,
        onToken: @escaping (String) -> Void,
        onComplete: @escaping (String) -> Void,
        onError: @escaping (Error) -> Void
    ) async {
        isStreaming = true
        markAIActivity()
        SyncEngine.shared.publish(domain: .aiStreaming, operation: "stream_start", state: .syncing)
        accumulatedText = ""
        lastTokenIndex = 0
        currentStreamMessage = ""
        let newMessageId = messageId ?? UUID().uuidString
        currentMessageId = newMessageId
        
        defer { 
            isStreaming = false 
        }
        
        let cloudMessage: String
        do {
            if message.isEmpty && context == "resume" {
                cloudMessage = message
            } else {
                cloudMessage = try AIOutboundTextGate.prepareUserMessage(message).cloudText
            }
        } catch {
            await MainActor.run { onError(error) }
            isStreaming = false
            return
        }

        do {
            let stream = try await createStreamingRequest(
                message: cloudMessage,
                context: context,
                resumeFromIndex: lastTokenIndex,
                messageId: newMessageId
            )
            
            for try await token in stream {
                markAIActivity()
                accumulatedText += token
                currentStreamMessage = accumulatedText
                lastTokenIndex += 1
                SyncEngine.shared.publish(
                    domain: .aiStreaming,
                    operation: "stream_token",
                    state: .syncing,
                    recordId: newMessageId,
                    metadata: ["tokenIndex": "\(lastTokenIndex)"]
                )
                
                await MainActor.run {
                    onToken(token)
                }
            }
            
            await MainActor.run {
                onComplete(accumulatedText)
                self.clearStreamState()
            }
            SyncEngine.shared.publish(domain: .aiStreaming, operation: "stream_complete", state: .synced, recordId: newMessageId)
            
        } catch {
            await MainActor.run {
                onError(error)
            }
            // Keep state for retry/resume on transient errors
            if !(error is CancellationError) {
                saveCurrentStreamState()
            }
            SyncEngine.shared.publish(
                domain: .aiStreaming,
                operation: "stream_error",
                state: .error(error.localizedDescription),
                recordId: newMessageId
            )
        }
    }
    
    /// Для использования из APIService
    func createStreamingRequestForService(
        message: String,
        context: String = "general",
        messageId: String? = nil
    ) async throws -> AsyncThrowingStream<String, Error> {
        let cloudMessage = try AIOutboundTextGate.prepareUserMessage(message).cloudText
        return try await createStreamingRequest(
            message: cloudMessage,
            context: context,
            resumeFromIndex: 0,
            messageId: messageId
        )
    }
    
    /// Создаёт AsyncThrowingStream для SSE
    private func createStreamingRequest(
        message: String,
        context: String,
        resumeFromIndex: Int,
        messageId: String?
    ) async throws -> AsyncThrowingStream<String, Error> {
        AsyncThrowingStream { continuation in
            guard let url = streamingEndpointURL() else {
                continuation.yield(with: .failure(NSError(domain: "AIStreaming", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid endpoint"])))
                return
            }
            
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("text/event-stream", forHTTPHeaderField: "Accept")
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.timeoutInterval = 180
            
            if let token = AppConfig.authToken {
                request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
            }
            
            let body: [String: Any] = [
                "message": message,
                "context": context,
                "resumeFromIndex": resumeFromIndex,
                "messageId": messageId ?? UUID().uuidString,
                "stream": true,
                "response_language": LocalizationManager.shared.aiResponseLanguageCode
            ]
            
            do {
                request.httpBody = try JSONSerialization.data(withJSONObject: body)
            } catch {
                continuation.yield(with: .failure(error))
                return
            }
            
            func isTransient(_ error: Error) -> Bool {
                let e = error as NSError
                if e.domain == NSURLErrorDomain {
                    switch e.code {
                    case NSURLErrorTimedOut, NSURLErrorNetworkConnectionLost, NSURLErrorNotConnectedToInternet,
                         NSURLErrorCannotConnectToHost, NSURLErrorDNSLookupFailed:
                        return true
                    default:
                        return false
                    }
                }
                return false
            }
            
            let streamTask = Task { [weak self] in
                defer {
                    self?.currentStreamTask = nil
                }
                
                for attempt in 0...2 {
                    do {
                        try Task.checkCancellation()
                        let (bytes, response) = try await URLSession.shared.bytes(for: request)
                        
                        if let http = response as? HTTPURLResponse, !(200...299).contains(http.statusCode) {
                            throw NSError(
                                domain: "AIStreaming",
                                code: http.statusCode,
                                userInfo: [NSLocalizedDescriptionKey: "HTTP \(http.statusCode) while streaming"]
                            )
                        }
                        
                        for try await line in bytes.lines {
                            try Task.checkCancellation()
                            guard line.hasPrefix("data: ") else { continue }
                            
                            let payload = String(line.dropFirst(6)).trimmingCharacters(in: .whitespacesAndNewlines)
                            if payload == "[DONE]" {
                                continuation.finish()
                                return
                            }
                            
                            guard let jsonData = payload.data(using: .utf8),
                                  let dict = try? JSONSerialization.jsonObject(with: jsonData) as? [String: Any] else {
                                continue
                            }
                            
                            if let token = dict["token"] as? String, !token.isEmpty {
                                continuation.yield(token)
                            } else if let done = dict["done"] as? Bool, done {
                                continuation.finish()
                                return
                            } else if let errMsg = dict["error"] as? String {
                                continuation.yield(with: .failure(NSError(domain: "AIStreaming", code: -2, userInfo: [NSLocalizedDescriptionKey: errMsg])))
                                return
                            }
                        }
                        
                        continuation.finish()
                        return
                    } catch is CancellationError {
                        continuation.finish()
                        return
                    } catch {
                        if attempt < 2, isTransient(error) {
                            let delayNs = UInt64(pow(2.0, Double(attempt)) * 1_000_000_000)
                            try? await Task.sleep(nanoseconds: delayNs)
                            continue
                        }
                        continuation.yield(with: .failure(error))
                        return
                    }
                }
            }
            
            currentStreamTask = streamTask
            continuation.onTermination = { [weak self] _ in
                self?.currentStreamTask?.cancel()
            }
        }
    }
    
    private func streamingEndpointURL() -> URL? {
        let endpoint = AppConfig.Endpoint.aiAssistantStream
        if endpoint.hasPrefix("http://") || endpoint.hasPrefix("https://") {
            return URL(string: endpoint)
        }
        return URL(string: AppConfig.apiBaseURL + endpoint)
    }
    
    /// Resume logic
    func resumeStream(messageId: String, lastIndex: Int) async throws -> AsyncThrowingStream<String, Error> {
        print("🔄 AIStreamingService: Resuming stream for messageId=\(messageId), lastIndex=\(lastIndex)")
        saveStreamState(messageId: messageId, lastIndex: lastIndex, accumulatedText: accumulatedText)
        
        return try await createStreamingRequest(
            message: "",
            context: "resume",
            resumeFromIndex: lastIndex,
            messageId: messageId
        )
    }
    
    private func saveStreamState(messageId: String, lastIndex: Int, accumulatedText: String) {
        let state: [String: Any] = [
            "messageId": messageId,
            "lastIndex": lastIndex,
            "accumulatedText": accumulatedText,
            "timestamp": Date().timeIntervalSince1970
        ]
        UserDefaults.standard.set(state, forKey: streamStateKey)
        let checkpoint = AIStreamCheckpoint(
            messageId: messageId,
            lastIndex: lastIndex,
            accumulatedText: accumulatedText,
            updatedAt: Date()
        )
        Task {
            _ = await UnifiedOfflineStore.shared.save(checkpoint, type: .aiInteraction, priority: .critical)
        }
        print("💾 AIStreamingService: Saved stream state for message \(messageId) at index \(lastIndex)")
    }
    
    private func restoreLastStreamState() {
        guard let state = UserDefaults.standard.dictionary(forKey: streamStateKey),
              let messageId = state["messageId"] as? String,
              let lastIndex = state["lastIndex"] as? Int,
              let savedText = state["accumulatedText"] as? String else {
            return
        }
        
        currentMessageId = messageId
        lastTokenIndex = lastIndex
        accumulatedText = savedText
        currentStreamMessage = savedText
        
        print("♻️ AIStreamingService: Restored stream state for message \(messageId), \(lastIndex) tokens")
    }
    
    private func attemptResumeIfNeeded() async {
        guard let state = UserDefaults.standard.dictionary(forKey: streamStateKey),
              let messageId = state["messageId"] as? String,
              let lastIndex = state["lastIndex"] as? Int else {
            return
        }
        
        do {
            _ = try await resumeStream(messageId: messageId, lastIndex: lastIndex)
        } catch {
            print("⚠️ AIStreamingService: Failed to auto-resume: \(error.localizedDescription)")
        }
    }
    
    func clearStreamState() {
        UserDefaults.standard.removeObject(forKey: streamStateKey)
        currentMessageId = nil
        accumulatedText = ""
        lastTokenIndex = 0
        currentStreamMessage = ""
        print("🧹 AIStreamingService: Stream state cleared")
    }
    
    func cancelCurrentStream() {
        currentStreamTask?.cancel()
        currentStreamTask = nil
        isStreaming = false
        clearStreamState()
        SyncEngine.shared.publish(domain: .aiStreaming, operation: "stream_cancel", state: .idle)
    }
    
    deinit {
        cancellables.removeAll()
    }

    private func markAIActivity() {
        UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: homeChatLastAIActivityKey)
    }
}

/// Снимок незавершённого AI-стрима для `UnifiedOfflineStore` (тип `.aiInteraction`).
private struct AIStreamCheckpoint: Codable {
    let messageId: String
    let lastIndex: Int
    let accumulatedText: String
    let updatedAt: Date
}
