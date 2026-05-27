import AVFoundation

/// P1-13c — TTS ответа компаньона (AVSpeech) с тоном personality preset.
@MainActor
final class CompanionSpeechOutput: NSObject, ObservableObject {
    @Published private(set) var isSpeaking = false

    private let synthesizer = AVSpeechSynthesizer()

    override init() {
        super.init()
        synthesizer.delegate = self
    }

    func stop() {
        synthesizer.stopSpeaking(at: .immediate)
        isSpeaking = false
    }

    func speak(_ text: String, personalityPreset: String) {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        stop()

        let utterance = AVSpeechUtterance(string: trimmed)
        let lang = LocalizationManager.shared.aiResponseLanguageCode
        utterance.voice = AVSpeechSynthesisVoice(language: lang == "en" ? "en-US" : "ru-RU")
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
        isSpeaking = true
        synthesizer.speak(utterance)
    }
}

extension CompanionSpeechOutput: AVSpeechSynthesizerDelegate {
    nonisolated func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) {
        Task { @MainActor in
            self.isSpeaking = false
        }
    }

    nonisolated func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didCancel utterance: AVSpeechUtterance) {
        Task { @MainActor in
            self.isSpeaking = false
        }
    }
}
