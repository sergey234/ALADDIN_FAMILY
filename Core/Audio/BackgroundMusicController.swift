import Foundation
import AVFoundation

/// W5-1: фоновая музыка и управление `AVAudioPlayer` — отдельно от `AudioManager` (сессия/маршрут).
@MainActor
final class BackgroundMusicController: ObservableObject {
    static let shared = BackgroundMusicController()

    @Published private(set) var isPlaying: Bool = false

    private var currentPlayer: AVAudioPlayer?
    private var wasPlayingBeforeInterruption = false
    private var cacheByKey: [String: AVAudioPlayer] = [:]

    private init() {}

    func play(resource: String, ext: String = "mp3", loops: Int = -1) {
        guard !AudioManager.shared.isMuted,
              let data = AudioManager.shared.bundledData(named: resource, ext: ext) else { return }
        let key = "bg.\(resource).\(ext)"
        if let existing = cacheByKey[key] {
            currentPlayer = existing
            existing.numberOfLoops = loops
            existing.currentTime = 0
            existing.play()
            isPlaying = true
            refreshVolume()
            return
        }
        guard let player = try? AVAudioPlayer(data: data) else { return }
        player.prepareToPlay()
        player.numberOfLoops = loops
        cacheByKey[key] = player
        currentPlayer = player
        isPlaying = true
        refreshVolume()
        player.play()
    }

    func stop() {
        currentPlayer?.stop()
        isPlaying = false
    }

    func refreshVolume() {
        let g = AudioManager.shared.effectiveMusicGain
        currentPlayer?.volume = g
    }

    /// `AVAudioSession` interruption: pause background.
    func pauseForInterruption() {
        if currentPlayer?.isPlaying == true {
            wasPlayingBeforeInterruption = true
            currentPlayer?.pause()
            isPlaying = false
        } else {
            wasPlayingBeforeInterruption = false
        }
    }

    /// Resume if user was listening before a transient interruption.
    func resumeAfterInterruptionIfNeeded() {
        if wasPlayingBeforeInterruption, let p = currentPlayer {
            p.play()
            isPlaying = true
            wasPlayingBeforeInterruption = false
        }
    }

    /// Test seam: true if a player is loaded and at play head (used with interruption simulation).
    var isPlaybackLikely: Bool { currentPlayer != nil }
}
