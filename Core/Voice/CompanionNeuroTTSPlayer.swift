import AVFoundation
import Foundation

/// Premium neuro-TTS via `POST /api/ai/companion/tts` (ElevenLabs Flash on server).
@MainActor
final class CompanionNeuroTTSPlayer: NSObject, ObservableObject {
    @Published private(set) var isSpeaking = false

    private var player: AVAudioPlayer?
    private let api = CompanionAPIService.shared
    var onPlaybackEnded: (() -> Void)?

    func stop() {
        player?.stop()
        player = nil
        isSpeaking = false
    }

    /// Returns true if audio started; false → caller should use AVSpeech.
    func speak(text: String, characterId: String) async -> Bool {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return false }
        guard CompanionCapabilitiesService.shared.neuroTtsPremiumEnabled else { return false }

        stop()
        do {
            let response = try await api.fetchNeuroTTS(text: trimmed, characterId: characterId)
            guard let data = Data(base64Encoded: response.audioBase64), !data.isEmpty else {
                return false
            }
            try AVAudioSession.sharedInstance().setCategory(.playback, mode: .spokenAudio, options: [.duckOthers])
            try AVAudioSession.sharedInstance().setActive(true)
            let audioPlayer = try AVAudioPlayer(data: data)
            audioPlayer.delegate = self
            player = audioPlayer
            isSpeaking = true
            audioPlayer.prepareToPlay()
            audioPlayer.play()
            return true
        } catch {
            #if DEBUG
            print("CompanionNeuroTTSPlayer: \(error.localizedDescription)")
            #endif
            isSpeaking = false
            return false
        }
    }
}

extension CompanionNeuroTTSPlayer: AVAudioPlayerDelegate {
    nonisolated func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        Task { @MainActor in
            self.isSpeaking = false
            self.player = nil
            self.onPlaybackEnded?()
        }
    }

    nonisolated func audioPlayerDecodeErrorDidOccur(_ player: AVAudioPlayer, error: Error?) {
        Task { @MainActor in
            self.isSpeaking = false
            self.player = nil
            self.onPlaybackEnded?()
        }
    }
}
