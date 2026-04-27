import Foundation
import AVFoundation

/// W5-1: one-shot SFX, отдельно от сессии. Громкость снимает с `AudioManager`.
enum AudioOneShotPlayer {
    static func playEffect(resource: String, ext: String = "mp3") {
        guard !AudioManager.shared.isMuted,
              let data = AudioManager.shared.bundledData(named: resource, ext: ext) else { return }
        guard let player = try? AVAudioPlayer(data: data) else { return }
        player.prepareToPlay()
        player.volume = AudioManager.shared.effectiveEffectsGain
        player.play()
    }
}
