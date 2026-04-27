import Foundation
import AVFoundation

enum AppSoundEffect: String, CaseIterable {
    case click
    case success
    case error
    case tapSoft
    case tapStrong
    case cardOpen
    case cardClose
    case swipe
    case whoosh
    case reward
    case levelUp
    case streak
    case notification
    case alert
    case warning
    case toggleOn
    case toggleOff
    case modalOpen
    case modalClose
    case complete
}

enum SoundPriority: Int {
    case low = 0
    case medium = 1
    case high = 2
    case critical = 3
}

final class SoundEffectPlayer {
    static let shared = SoundEffectPlayer()

    private var currentPriority: SoundPriority = .low
    private var lastEffectPlayTime: TimeInterval = 0
    private var lastEffect: AppSoundEffect?
    private let speechSynth = AVSpeechSynthesizer()

    private init() {}

    func play(_ effect: AppSoundEffect, priority: SoundPriority = .medium) {
        guard priority.rawValue >= currentPriority.rawValue else { return }

        let now = ProcessInfo.processInfo.systemUptime
        if priority != .critical {
            let minGap = PerformanceBudget.soundMinInterval(priority: priority)
            if now - lastEffectPlayTime < minGap { return }
            if lastEffect == effect, now - lastEffectPlayTime < PerformanceBudget.soundSameEffectMinInterval {
                return
            }
        }

        lastEffectPlayTime = now
        lastEffect = effect
        currentPriority = priority
        defer { currentPriority = .low }

        // Tries local assets first; if missing, keeps UX responsive with no crash.
        AudioOneShotPlayer.playEffect(resource: effect.rawValue, ext: "mp3")
    }

    func playVoicePrompt(_ text: String, languageCode: String = "ru-RU", priority: SoundPriority = .high) {
        guard priority.rawValue >= currentPriority.rawValue else { return }
        currentPriority = priority
        defer { currentPriority = .low }

        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = AVSpeechSynthesisVoice(language: languageCode)
        utterance.rate = 0.5
        speechSynth.speak(utterance)
    }
}

