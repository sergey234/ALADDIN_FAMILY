import AVFoundation

/// P1-13c — TTS ответа компаньона: Premium → neuro (ElevenLabs), иначе AVSpeech (3 голоса).
@MainActor
final class CompanionSpeechOutput: NSObject, ObservableObject {
    @Published private(set) var isSpeaking = false

    private let synthesizer = AVSpeechSynthesizer()
    private let neuroPlayer = CompanionNeuroTTSPlayer()
    var onPlaybackEnded: (() -> Void)?

    override init() {
        super.init()
        synthesizer.delegate = self
        neuroPlayer.onPlaybackEnded = { [weak self] in
            self?.isSpeaking = false
            self?.onPlaybackEnded?()
        }
    }

    func stop() {
        neuroPlayer.stop()
        synthesizer.stopSpeaking(at: .immediate)
        isSpeaking = false
        VoiceAudioSessionCoordinator.shared.release(.companion)
    }

    func speak(_ text: String, personalityPreset: String, characterId: String = "unicorn") {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        stop()

        Task {
            if await neuroPlayer.speak(text: trimmed, characterId: characterId) {
                isSpeaking = true
                return
            }
            speakWithAVSpeech(trimmed, personalityPreset: personalityPreset, characterId: characterId)
        }
    }

    private func speakWithAVSpeech(_ trimmed: String, personalityPreset: String, characterId: String) {
        guard VoiceAudioSessionCoordinator.shared.acquire(.companion, profile: .companionPlayback) else {
            return
        }
        let utterance = AVSpeechUtterance(string: trimmed)
        let lang = LocalizationManager.shared.aiResponseLanguageCode
        utterance.voice = resolveAVSpeechVoice(characterId: characterId, lang: lang)
        switch personalityPreset {
        case "witty":
            utterance.rate = 0.58
            utterance.pitchMultiplier = 1.15
        case "playful":
            utterance.rate = 0.56
            utterance.pitchMultiplier = 1.12
        case "calm":
            utterance.rate = 0.42
            utterance.pitchMultiplier = 0.94
        case "mentor":
            utterance.rate = 0.48
            utterance.pitchMultiplier = 1.02
        default:
            utterance.rate = 0.5
            utterance.pitchMultiplier = 1.0
        }
        applyCharacterVoice(characterId: characterId, utterance: utterance)
        isSpeaking = true
        synthesizer.speak(utterance)
    }

    /// Sprint 1–2: три разных Apple voice id (RU/EN); Premium идёт через neuro API.
    private func resolveAVSpeechVoice(characterId: String, lang: String) -> AVSpeechSynthesisVoice? {
        let isEn = lang == "en"
        let id = Self.avSpeechVoiceIdentifier(characterId: characterId, english: isEn)
        if let id, let voice = AVSpeechSynthesisVoice(identifier: id) {
            return voice
        }
        return AVSpeechSynthesisVoice(language: isEn ? "en-US" : "ru-RU")
    }

    private static func avSpeechVoiceIdentifier(characterId: String, english: Bool) -> String? {
        if english {
            switch characterId {
            case "unicorn": return "com.apple.voice.compact.en-US.Samantha"
            case "genie": return "com.apple.voice.compact.en-US.Aaron"
            case "aladdin": return "com.apple.voice.compact.en-US.Nicky"
            default: return nil
            }
        }
        switch characterId {
        case "unicorn": return "com.apple.voice.compact.ru-RU.Katya"
        case "genie": return "com.apple.voice.compact.ru-RU.Yuri"
        case "aladdin": return "com.apple.voice.compact.ru-RU.Milena"
        default: return nil
        }
    }

    /// HERO-3-15: лёгкая дифференциация TTS по герою (поверх preset).
    private func applyCharacterVoice(characterId: String, utterance: AVSpeechUtterance) {
        switch characterId {
        case "genie":
            utterance.rate = min(utterance.rate * 1.04, AVSpeechUtteranceMaximumSpeechRate)
            utterance.pitchMultiplier = min(utterance.pitchMultiplier * 1.08, 2.0)
        case "unicorn":
            utterance.pitchMultiplier = min(utterance.pitchMultiplier * 1.1, 2.0)
        case "aladdin":
            utterance.rate = max(utterance.rate * 0.96, AVSpeechUtteranceMinimumSpeechRate)
            utterance.pitchMultiplier = max(utterance.pitchMultiplier * 0.98, 0.5)
        default:
            break
        }
    }
}

extension CompanionSpeechOutput: AVSpeechSynthesizerDelegate {
    nonisolated func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) {
        Task { @MainActor in
            if !self.neuroPlayer.isSpeaking {
                self.isSpeaking = false
                VoiceAudioSessionCoordinator.shared.release(.companion)
                self.onPlaybackEnded?()
            }
        }
    }

    nonisolated func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didCancel utterance: AVSpeechUtterance) {
        Task { @MainActor in
            if !self.neuroPlayer.isSpeaking {
                self.isSpeaking = false
                VoiceAudioSessionCoordinator.shared.release(.companion)
                self.onPlaybackEnded?()
            }
        }
    }
}
