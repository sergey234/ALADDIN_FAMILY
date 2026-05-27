import Foundation

/// WebSocket голос companion (P1-13): on-device STT transcript → companion chat → TTS на клиенте.
@MainActor
final class CompanionVoiceSession: ObservableObject {
    @Published private(set) var isConnected = false
    @Published private(set) var emotion: CompanionHeroEmotion = .idle
    @Published private(set) var lastTranscript: String = ""
    @Published private(set) var lastAssistantLine: String = ""
    @Published private(set) var lastCosmeticUnlocked: String?
    @Published private(set) var isAwaitingReply = false

    var onAssistantReply: ((String, CompanionHeroEmotion) -> Void)?

    private var task: URLSessionWebSocketTask?
    private let session = URLSession(configuration: .default)

    func connect(ephemeralToken: String) async throws {
        disconnect()
        guard let url = AppConfig.companionVoiceWebSocketURL(token: ephemeralToken) else {
            throw URLError(.badURL)
        }
        guard VoiceAudioSessionCoordinator.shared.acquire(.companion, profile: .aiLive) else {
            throw NSError(domain: "CompanionVoice", code: 1, userInfo: [NSLocalizedDescriptionKey: "Audio session busy"])
        }

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
        sendJSON(payload)
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
        sendJSON(payload)
        isAwaitingReply = true
        emotion = .thinking
    }

    func sendPing() {
        sendJSON(["type": "ping"])
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
            onAssistantReply?(line, emotion)
        case "session.ready":
            emotion = .happy
        case "error":
            isAwaitingReply = false
            emotion = .alert
        default:
            break
        }
    }
}
