import AVFoundation

/// Единая точка владения `AVAudioSession` для AI / Диктофон / Семейный чат.
final class VoiceAudioSessionCoordinator {
    static let shared = VoiceAudioSessionCoordinator()

    enum Consumer: String {
        case aiAssistant
        case voiceNotes
        case familyChat
        case companion
    }

    struct SessionProfile {
        let category: AVAudioSession.Category
        let mode: AVAudioSession.Mode
        let options: AVAudioSession.CategoryOptions

        static let aiLive = SessionProfile(
            category: .playAndRecord,
            mode: .measurement,
            options: [.duckOthers, .defaultToSpeaker, .allowBluetooth]
        )
        static let voiceNotes = SessionProfile(
            category: .playAndRecord,
            mode: .default,
            options: [.defaultToSpeaker, .allowBluetooth]
        )
        static let familyChat = SessionProfile(
            category: .playAndRecord,
            mode: .default,
            options: [.defaultToSpeaker, .allowBluetooth]
        )
        /// Companion TTS (ElevenLabs / AVSpeech) — отдельно от mic `.aiLive`.
        static let companionPlayback = SessionProfile(
            category: .playback,
            mode: .spokenAudio,
            options: [.duckOthers]
        )
    }

    private(set) var activeConsumer: Consumer?
    private let lock = NSLock()

    private init() {}

    /// Возвращает `false`, если сессия занята другим потребителем.
    @discardableResult
    func acquire(_ consumer: Consumer, profile: SessionProfile) -> Bool {
        lock.lock()
        defer { lock.unlock() }
        if let active = activeConsumer, active != consumer {
            NotificationCenter.default.post(
                name: .voiceAudioSessionBusy,
                object: nil,
                userInfo: ["active": active.rawValue, "requested": consumer.rawValue]
            )
            return false
        }
        activeConsumer = consumer
        do {
            let session = AVAudioSession.sharedInstance()
            try session.setCategory(profile.category, mode: profile.mode, options: profile.options)
            try session.setActive(true, options: .notifyOthersOnDeactivation)
            return true
        } catch {
            activeConsumer = nil
            return false
        }
    }

    func release(_ consumer: Consumer) {
        lock.lock()
        defer { lock.unlock() }
        guard activeConsumer == consumer else { return }
        activeConsumer = nil
        try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
    }

    func forceReleaseAll() {
        lock.lock()
        defer { lock.unlock() }
        activeConsumer = nil
        try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
    }
}

extension Notification.Name {
    static let voiceAudioSessionBusy = Notification.Name("VoiceAudioSessionBusy")
    static let microphonePermissionDenied = Notification.Name("MicrophonePermissionDenied")
    static let speechRecognitionPermissionDenied = Notification.Name("SpeechRecognitionPermissionDenied")
    static let voiceRecordingInterrupted = Notification.Name("VoiceRecordingInterrupted")
    static let voiceNoteSendToAI = Notification.Name("VoiceNoteSendToAI")
}
