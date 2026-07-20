import AVFoundation
import Foundation

/// p2-10d/e — soft ambient loops for breath exercise (ambient session = Silent Switch).
enum BreathAmbientTrack: String, CaseIterable, Identifiable {
    case rain
    case softNoise

    var id: String { rawValue }

    var resourceName: String {
        switch self {
        case .rain: return "breath_rain"
        case .softNoise: return "breath_soft_noise"
        }
    }

    var titleKey: String {
        switch self {
        case .rain: return "wellness_breath_audio_track_rain"
        case .softNoise: return "wellness_breath_audio_track_noise"
        }
    }
}

enum BreathAmbientAudioSettings {
    private static let enabledKey = "wellness_breath_audio_enabled"
    private static let trackKey = "wellness_breath_audio_track"
    private static let volumeKey = "wellness_breath_audio_volume"

    /// Default ON.
    static var isEnabled: Bool {
        get {
            if UserDefaults.standard.object(forKey: enabledKey) == nil { return true }
            return UserDefaults.standard.bool(forKey: enabledKey)
        }
        set { UserDefaults.standard.set(newValue, forKey: enabledKey) }
    }

    static var track: BreathAmbientTrack {
        get {
            let raw = UserDefaults.standard.string(forKey: trackKey) ?? BreathAmbientTrack.rain.rawValue
            return BreathAmbientTrack(rawValue: raw) ?? .rain
        }
        set { UserDefaults.standard.set(newValue.rawValue, forKey: trackKey) }
    }

    /// Default ~0.3
    static var volume: Float {
        get {
            if UserDefaults.standard.object(forKey: volumeKey) == nil { return 0.3 }
            return min(1, max(0, UserDefaults.standard.float(forKey: volumeKey)))
        }
        set { UserDefaults.standard.set(min(1, max(0, newValue)), forKey: volumeKey) }
    }
}

@MainActor
final class BreathAmbientAudioPlayer {
    static let shared = BreathAmbientAudioPlayer()

    private var player: AVAudioPlayer?

    private init() {}

    func startIfNeeded() {
        guard BreathAmbientAudioSettings.isEnabled else {
            stop()
            return
        }
        configureAmbientSession()
        let track = BreathAmbientAudioSettings.track
        guard let url = Bundle.main.url(forResource: track.resourceName, withExtension: "wav")
                ?? Bundle.main.url(forResource: track.resourceName, withExtension: "wav", subdirectory: "Audio") else {
            stop()
            return
        }
        do {
            let p = try AVAudioPlayer(contentsOf: url)
            p.numberOfLoops = -1
            p.volume = BreathAmbientAudioSettings.volume
            p.prepareToPlay()
            p.play()
            player = p
        } catch {
            player = nil
        }
    }

    func applyVolume() {
        player?.volume = BreathAmbientAudioSettings.volume
    }

    func stop() {
        player?.stop()
        player = nil
    }

    private func configureAmbientSession() {
        let session = AVAudioSession.sharedInstance()
        try? session.setCategory(.ambient, mode: .default, options: [])
        try? session.setActive(true, options: [])
    }
}
