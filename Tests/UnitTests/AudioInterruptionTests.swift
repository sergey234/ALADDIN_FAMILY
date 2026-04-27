import XCTest
import AVFoundation
@testable import ALADDIN

@MainActor
final class AudioInterruptionTests: XCTestCase {

    private var wasMuted: Bool = false

    override func setUp() async throws {
        wasMuted = AudioManager.shared.isMuted
        AudioManager.shared.setMuted(false)
    }

    override func tearDown() async throws {
        AudioManager.shared.setMuted(wasMuted)
        BackgroundMusicController.shared.stop()
    }

    func testEffectiveGainsAreZeroWhenMuted() {
        AudioManager.shared.setMuted(true)
        XCTAssertEqual(AudioManager.shared.effectiveMusicGain, 0, accuracy: 0.0001)
        XCTAssertEqual(AudioManager.shared.effectiveEffectsGain, 0, accuracy: 0.0001)
    }

    func testSimulatedInterruptionBeganPausesBackground() throws {
        let session = AVAudioSession.sharedInstance()
        BackgroundMusicController.shared.stop()
        guard AudioManager.shared.bundledData(named: "click", ext: "mp3") != nil else {
            throw XCTSkip("SFX not in test bundle; ensure folder Audio in Copy Bundle Resources.")
        }
        BackgroundMusicController.shared.play(resource: "click", ext: "mp3")
        let e = self.expectation(description: "avplayer")
        DispatchQueue.main.async { e.fulfill() }
        wait(for: [e], timeout: 0.3)
        XCTAssert(BackgroundMusicController.shared.isPlaying || BackgroundMusicController.shared.isPlaybackLikely, "BGM should start or at least have a current player after play()")

        let n = Notification(
            name: AVAudioSession.interruptionNotification,
            object: session,
            userInfo: [AVAudioSessionInterruptionTypeKey: AVAudioSession.InterruptionType.began.rawValue]
        )
        AudioManager.shared.processInterruption(n)
        XCTAssertFalse(BackgroundMusicController.shared.isPlaying, "Interruption should set BGM to not playing")
    }

    func testProcessInterruptionBeganWithUnknownPayloadDoesNotCrash() {
        let n = Notification(name: AVAudioSession.interruptionNotification, object: nil, userInfo: [:])
        AudioManager.shared.processInterruption(n)
    }
}
