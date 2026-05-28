import Foundation

/// WebSocket голос companion (P1-13d): on-device STT transcript → companion chat → TTS на клиенте.
@MainActor
final class CompanionVoiceSession: ObservableObject {
    @Published private(set) var isConnected = false
    @Published private(set) var emotion: CompanionHeroEmotion = .idle
    @Published private(set) var lastTranscript: String = ""
    @Published private(set) var lastAssistantLine: String = ""
    @Published private(set) var lastCosmeticUnlocked: String?
    @Published private(set) var lastTrustScore: Int?
    @Published private(set) var isAwaitingReply = false
    @Published private(set) var lastErrorCode: String?

    var onAssistantReply: ((String, CompanionHeroEmotion) -> Void)?
    var onError: ((String) -> Void)?

    private var task: URLSessionWebSocketTask?
    private let session = URLSession(configuration: .default)
    private var sessionReady = false
    private var pendingConfig: [String: Any]?
    private var pendingStop: [String: Any]?

    func connect(ephemeralToken: String) async throws {
        disconnect()
        guard let url = AppConfig.companionVoiceWebSocketURL(token: ephemeralToken) else {
            throw URLError(.badURL)
        }
        guard VoiceAudioSessionCoordinator.shared.acquire(.companion, profile: .aiLive) else {
            throw NSError(domain: "CompanionVoice", code: 1, userInfo: [NSLocalizedDescriptionKey: "Audio session busy"])
        }

        sessionReady = false
        pendingConfig = nil
        pendingStop = nil
        lastErrorCode = nil

        let ws = session.webSocketTask(with: url)
        task = ws
        ws.resume()
        isConnected = true
        emotion = .listening
        receiveLoop()
    }

    func disconnect() {
        sendJSON(["type": "session.end"])
        task?.cancel(with: .goingAway, reason: nil)
        task = nil
        isConnected = false
        isAwaitingReply = false
        sessionReady = false
        pendingConfig = nil
        pendingStop = nil
        emotion = .idle
        VoiceAudioSessionCoordinator.shared.release(.companion)
    }

    func sendConfig(
        characterId: String,
        securityExpertMode: Bool?,
        responseLanguage: String?,
        familyId: String?
    ) {
        var payload: [String: Any] = [
            "type": "config",
            "character_id": characterId,
        ]
        if let securityExpertMode {
            payload["security_expert_mode"] = securityExpertMode
        }
        if let responseLanguage, !responseLanguage.isEmpty {
            payload["response_language"] = responseLanguage
        }
        if let familyId, !familyId.isEmpty {
            payload["family_id"] = familyId
        }
        if sessionReady {
            sendJSON(payload)
        } else {
            pendingConfig = payload
        }
    }

    func sendAudioStop(
        transcript: String,
        characterId: String,
        sessionId: String?,
        securityExpertMode: Bool?
    ) {
        var payload: [String: Any] = [
            "type": "audio.stop",
            "transcript": transcript,
            "character_id": characterId,
        ]
        if let sessionId, !sessionId.isEmpty {
            payload["session_id"] = sessionId
        }
        if let securityExpertMode {
            payload["security_expert_mode"] = securityExpertMode
        }
        if sessionReady {
            flushStop(payload)
        } else {
            pendingStop = payload
        }
    }

    func sendPing() {
        sendJSON(["type": "ping"])
    }

    private func flushPendingAfterReady() {
        sessionReady = true
        if let pendingConfig {
            sendJSON(pendingConfig)
            self.pendingConfig = nil
        }
        if let pendingStop {
            flushStop(pendingStop)
            self.pendingStop = nil
        }
    }

    private func flushStop(_ payload: [String: Any]) {
        sendJSON(payload)
        isAwaitingReply = true
        emotion = .thinking
    }

    private func sendJSON(_ object: [String: Any]) {
        guard let data = try? JSONSerialization.data(withJSONObject: object),
              let text = String(data: data, encoding: .utf8) else { return }
        task?.send(.string(text)) { _ in }
    }

    private func receiveLoop() {
        task?.receive { [weak self] result in
            Task { @MainActor in
                guard let self else { return }
                switch result {
                case .failure:
                    self.reportError(code: "connection_lost")
                    self.disconnect()
                case .success(let message):
                    if case .string(let text) = message {
                        self.handleServerMessage(text)
                    }
                    if self.task != nil {
                        self.receiveLoop()
                    }
                }
            }
        }
    }

    private func reportError(code: String, message: String? = nil) {
        lastErrorCode = code
        onError?(message ?? code)
    }

    private func handleServerMessage(_ text: String) {
        guard let data = text.data(using: .utf8),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let type = json["type"] as? String else { return }

        switch type {
        case "listening":
            emotion = .listening
        case "thinking":
            emotion = .thinking
            isAwaitingReply = true
        case "transcript":
            lastTranscript = json["text"] as? String ?? ""
        case "assistant.text":
            isAwaitingReply = false
            let line = json["text"] as? String ?? ""
            lastAssistantLine = line
            let emoRaw = json["emotion"] as? String ?? "happy"
            emotion = CompanionHeroEmotion(rawValue: emoRaw) ?? .speaking
            lastCosmeticUnlocked = json["cosmetic_unlocked"] as? String
            if let trust = json["trust_score"] as? Int {
                lastTrustScore = trust
            }
            onAssistantReply?(line, emotion)
        case "session.ready":
            emotion = .happy
            flushPendingAfterReady()
        case "config.ack":
            break
        case "error":
            isAwaitingReply = false
            emotion = .alert
            let code = json["code"] as? String ?? "voice_error"
            let message = json["message"] as? String
            reportError(code: code, message: message)
        default:
            break
        }
    }
}
