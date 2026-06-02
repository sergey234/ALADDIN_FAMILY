import Foundation

/// SSE-стрим companion с resume после обрыва сети (P1-06, B16).
@MainActor
final class CompanionStreamingService: ObservableObject {
    static let shared = CompanionStreamingService()

    @Published private(set) var isStreaming = false
    @Published private(set) var canResume = false

    private var currentTask: Task<Void, Never>?
    private var accumulatedText = ""
    private var lastTokenIndex = 0
    private var currentMessageId: String?
    private var currentCharacterId = "unicorn"
    private var currentSessionId: String?

    private let stateKey = "companion_stream_state"

    private init() {}

    func streamMessage(
        message: String,
        characterId: String,
        sessionId: String?,
        messageId: String? = nil,
        securityExpertMode: Bool = false,
        chatMode: String = "fast",
        workspaceId: String? = nil,
        attachments: [CompanionAttachmentPayload] = [],
        onEmotion: ((String) -> Void)? = nil,
        onToken: @escaping (String) -> Void,
        onComplete: @escaping (String, CompanionStreamDonePayload?) -> Void,
        onError: @escaping (Error) -> Void
    ) async {
        cancelCurrentStream()
        isStreaming = true
        canResume = false
        accumulatedText = ""
        lastTokenIndex = 0
        let streamMessageId = messageId ?? UUID().uuidString
        currentMessageId = streamMessageId
        currentCharacterId = characterId
        currentSessionId = sessionId

        defer { isStreaming = false }

        let cloudMessage: String
        do {
            if message.isEmpty {
                cloudMessage = ""
            } else {
                cloudMessage = try AIOutboundTextGate.prepareUserMessage(message).cloudText
            }
        } catch {
            onError(error)
            return
        }

        do {
            let stream = try await createStream(
                message: cloudMessage,
                characterId: characterId,
                sessionId: sessionId,
                resumeFromIndex: 0,
                messageId: streamMessageId,
                context: "companion",
                securityExpertMode: securityExpertMode,
                chatMode: chatMode,
                workspaceId: workspaceId,
                attachments: attachments
            )
            var doneMeta: CompanionStreamDonePayload?

            for try await event in stream {
                switch event {
                case .token(let token):
                    accumulatedText += token
                    lastTokenIndex += 1
                    onToken(token)
                case .done(let meta):
                    doneMeta = meta
                case .emotion(let name):
                    onEmotion?(name)
                }
            }

            clearStreamState()
            canResume = false
            onComplete(accumulatedText, doneMeta)
        } catch {
            if !(error is CancellationError) {
                saveStreamState()
                canResume = !accumulatedText.isEmpty
            }
            onError(error)
        }
    }

    func resumeInterruptedStream(
        onToken: @escaping (String) -> Void,
        onComplete: @escaping (String, CompanionStreamDonePayload?) -> Void,
        onError: @escaping (Error) -> Void
    ) async {
        guard let messageId = currentMessageId ?? loadState()?.messageId else {
            onError(NSError(domain: "CompanionStream", code: 1, userInfo: [NSLocalizedDescriptionKey: "Нет сохранённого стрима"]))
            return
        }
        let state = loadState()
        if let state {
            accumulatedText = state.accumulatedText
            lastTokenIndex = state.lastIndex
            currentMessageId = state.messageId
            currentCharacterId = state.characterId
            currentSessionId = state.sessionId
        }
        let startIndex = lastTokenIndex
        let characterId = currentCharacterId
        let sessionId = currentSessionId

        isStreaming = true
        defer { isStreaming = false }

        do {
            let stream = try await createStream(
                message: "",
                characterId: characterId,
                sessionId: sessionId,
                resumeFromIndex: startIndex,
                messageId: messageId,
                context: "resume"
            )
            var doneMeta: CompanionStreamDonePayload?

            for try await event in stream {
                switch event {
                case .token(let token):
                    accumulatedText += token
                    lastTokenIndex += 1
                    onToken(token)
                case .done(let meta):
                    doneMeta = meta
                case .emotion:
                    break
                }
            }

            clearStreamState()
            canResume = false
            onComplete(accumulatedText, doneMeta)
        } catch {
            saveStreamState()
            canResume = true
            onError(error)
        }
    }

    func cancelCurrentStream() {
        currentTask?.cancel()
        currentTask = nil
        isStreaming = false
    }

    private enum StreamEvent {
        case token(String)
        case emotion(String)
        case done(CompanionStreamDonePayload?)
    }

    private func createStream(
        message: String,
        characterId: String,
        sessionId: String?,
        resumeFromIndex: Int,
        messageId: String,
        context: String,
        securityExpertMode: Bool = false,
        chatMode: String = "fast",
        workspaceId: String? = nil,
        attachments: [CompanionAttachmentPayload] = []
    ) async throws -> AsyncThrowingStream<StreamEvent, Error> {
        AsyncThrowingStream { continuation in
            let task = Task {
                do {
                    try await self.runSSE(
                        message: message,
                        characterId: characterId,
                        sessionId: sessionId,
                        resumeFromIndex: resumeFromIndex,
                        messageId: messageId,
                        context: context,
                        securityExpertMode: securityExpertMode,
                        chatMode: chatMode,
                        workspaceId: workspaceId,
                        attachments: attachments,
                        continuation: continuation
                    )
                } catch is CancellationError {
                    continuation.finish()
                } catch {
                    continuation.finish(throwing: error)
                }
            }
            self.currentTask = task
            continuation.onTermination = { _ in task.cancel() }
        }
    }

    private func runSSE(
        message: String,
        characterId: String,
        sessionId: String?,
        resumeFromIndex: Int,
        messageId: String,
        context: String,
        securityExpertMode: Bool,
        chatMode: String,
        workspaceId: String?,
        attachments: [CompanionAttachmentPayload],
        continuation: AsyncThrowingStream<StreamEvent, Error>.Continuation
    ) async throws {
        guard let url = URL(string: AppConfig.apiBaseURL + AppConfig.Endpoint.aiCompanionStream) else {
            throw NSError(domain: "CompanionStream", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid URL"])
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("text/event-stream", forHTTPHeaderField: "Accept")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 180

        if let token = AppConfig.authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        let fid = FamilyLocalStore.loadPersistedFamilyId()
        if !fid.isEmpty {
            request.setValue(fid, forHTTPHeaderField: "X-Aladdin-Family-Id")
        }

        var body: [String: Any] = [
            "message": message,
            "character_id": characterId,
            "context": context,
            "resumeFromIndex": resumeFromIndex,
            "messageId": messageId,
            "stream": true,
            "input_mode": "text",
            "response_language": LocalizationManager.shared.aiResponseLanguageCode
        ]
        if let sessionId, !sessionId.isEmpty {
            body["session_id"] = sessionId
        }
        if securityExpertMode {
            body["security_expert_mode"] = true
        }
        body["chat_mode"] = chatMode
        if let workspaceId, !workspaceId.isEmpty {
            body["workspace_id"] = workspaceId
        }
        if !attachments.isEmpty {
            body["attachments"] = attachments.map { att in
                var row: [String: Any] = ["kind": att.kind, "filename": att.filename]
                if let mime = att.mimeType { row["mime_type"] = mime }
                if let b64 = att.contentB64 { row["content_b64"] = b64 }
                return row
            }
        }
        if let pillar = WellnessSessionStore.activePillar, !pillar.isEmpty {
            body["wellness_pillar"] = pillar
        }
        request.httpBody = try JSONSerialization.data(withJSONObject: body)

        let (bytes, response) = try await URLSession.shared.bytes(for: request)
        if let http = response as? HTTPURLResponse, !(200...299).contains(http.statusCode) {
            throw NSError(
                domain: "CompanionStream",
                code: http.statusCode,
                userInfo: [NSLocalizedDescriptionKey: "HTTP \(http.statusCode)"]
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
            guard let data = payload.data(using: .utf8),
                  let dict = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
                continue
            }
            if let token = dict["token"] as? String, !token.isEmpty {
                continuation.yield(.token(token))
            } else if let text = dict["text"] as? String, !text.isEmpty {
                continuation.yield(.token(text))
            } else if let emotion = dict["emotion"] as? String {
                continuation.yield(.emotion(emotion))
            } else if let done = dict["done"] as? Bool, done {
                let meta = try? JSONDecoder().decode(CompanionStreamDonePayload.self, from: data)
                continuation.yield(.done(meta))
            }
        }
        continuation.finish()
    }

    private struct SavedState: Codable {
        let messageId: String
        let lastIndex: Int
        let accumulatedText: String
        let characterId: String
        let sessionId: String?
    }

    private func saveStreamState() {
        guard let messageId = currentMessageId else { return }
        let state = SavedState(
            messageId: messageId,
            lastIndex: lastTokenIndex,
            accumulatedText: accumulatedText,
            characterId: currentCharacterId,
            sessionId: currentSessionId
        )
        if let data = try? JSONEncoder().encode(state) {
            UserDefaults.standard.set(data, forKey: stateKey)
        }
    }

    private func loadState() -> SavedState? {
        guard let data = UserDefaults.standard.data(forKey: stateKey) else { return nil }
        return try? JSONDecoder().decode(SavedState.self, from: data)
    }

    private func clearStreamState() {
        UserDefaults.standard.removeObject(forKey: stateKey)
    }

    /// Восстанавливает локальное состояние после обрыва; возвращает уже полученный текст.
    func syncPendingFromDisk() -> String? {
        guard let state = loadState() else {
            canResume = false
            return nil
        }
        currentMessageId = state.messageId
        lastTokenIndex = state.lastIndex
        accumulatedText = state.accumulatedText
        currentCharacterId = state.characterId
        currentSessionId = state.sessionId
        canResume = true
        return state.accumulatedText.isEmpty ? nil : state.accumulatedText
    }
}
