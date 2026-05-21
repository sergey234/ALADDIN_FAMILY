import AVFoundation
import Combine

@MainActor
final class VoiceNotePlaybackController: ObservableObject {
    @Published private(set) var playingNoteId: UUID?
    @Published private(set) var progress: Double = 0

    private var player: AVAudioPlayer?
    private var progressTimer: Timer?

    func toggle(noteId: UUID, filePath: String) {
        if playingNoteId == noteId {
            stop()
            return
        }
        stop()
        let url = URL(fileURLWithPath: filePath)
        guard FileManager.default.fileExists(atPath: url.path) else { return }
        do {
            _ = VoiceAudioSessionCoordinator.shared.acquire(.voiceNotes, profile: .voiceNotes)
            player = try AVAudioPlayer(contentsOf: url)
            player?.prepareToPlay()
            player?.play()
            playingNoteId = noteId
            startProgressTimer()
        } catch {
            VoiceAudioSessionCoordinator.shared.release(.voiceNotes)
        }
    }

    func stop() {
        progressTimer?.invalidate()
        progressTimer = nil
        player?.stop()
        player = nil
        playingNoteId = nil
        progress = 0
        VoiceAudioSessionCoordinator.shared.release(.voiceNotes)
    }

    private func startProgressTimer() {
        progressTimer?.invalidate()
        progressTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            guard let self, let player = self.player, player.duration > 0 else { return }
            Task { @MainActor in
                let duration = player.duration
                if duration.isFinite, duration > 0 {
                    let p = player.currentTime / duration
                    self.progress = min(max(p, 0), 1)
                } else {
                    self.progress = 0
                }
                if !player.isPlaying {
                    self.stop()
                }
            }
        }
    }
}
