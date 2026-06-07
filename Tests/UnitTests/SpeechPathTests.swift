import XCTest
@testable import ALADDIN

final class SpeechPathTests: XCTestCase {

    func testSpeechRecognizerFactoryReturnsAvailableRecognizer() {
        let locale = Locale(identifier: "en-US")
        let selection = SpeechRecognizerFactory.bestForLiveRecognition(preferred: locale)
        if let selection {
            XCTAssertTrue(selection.recognizer.isAvailable)
            #if targetEnvironment(simulator)
            XCTAssertFalse(selection.useOnDeviceRecognition)
            #endif
        }
    }

    func testIsSpeechInputAvailableUsesCloudPath() {
        let locale = Locale(identifier: "en-US")
        let cloud = SpeechRecognizerFactory.cloudOnly(preferred: locale) != nil
        XCTAssertEqual(SpeechRecognizerFactory.isSpeechInputAvailable(preferred: locale), cloud)
    }

    func testCloudOnlyReturnsNonOnDeviceFlagWhenCloudExists() throws {
        let locale = Locale(identifier: "en-US")
        guard let cloud = SpeechRecognizerFactory.cloudOnly(preferred: locale) else {
            throw XCTSkip("Cloud recognizer not available in CI/simulator")
        }
        XCTAssertTrue(cloud.recognizer.isAvailable)
    }

    func testBenignErrorClassification() {
        let err = NSError(domain: "kAFAssistantErrorDomain", code: 216)
        XCTAssertTrue(SpeechRecognitionErrorClassifier.isBenign(err))
        XCTAssertFalse(SpeechRecognitionErrorClassifier.isServiceUnavailable(err))
    }

    func testOnDeviceMissingErrorClassification() {
        let err = NSError(domain: "kAFAssistantErrorDomain", code: 1101)
        XCTAssertTrue(SpeechRecognitionErrorClassifier.isOnDeviceModelMissing(err))
        XCTAssertFalse(SpeechRecognitionErrorClassifier.isServiceUnavailable(err))
    }

    func testRetryPromptErrorClassification() {
        let retry = NSError(domain: "kAFAssistantErrorDomain", code: 203)
        XCTAssertTrue(SpeechRecognitionErrorClassifier.isRetryPrompt(retry))
        let unsuccessful = NSError(domain: "EARErrorDomain", code: 3)
        XCTAssertTrue(SpeechRecognitionErrorClassifier.isRetryPrompt(unsuccessful))
    }

    func testServiceUnavailableClassification() {
        let err = NSError(domain: "SiriCoreSiriConnectionErrorDomain", code: 1)
        XCTAssertTrue(SpeechRecognitionErrorClassifier.isServiceUnavailable(err))
    }

    func testAudioLevelMeterNormalization() {
        let low = AudioLevelMeter.normalizedLevel(fromAveragePower: -60)
        let high = AudioLevelMeter.normalizedLevel(fromAveragePower: 0)
        XCTAssertLessThan(low, high)
        XCTAssertGreaterThanOrEqual(high, 0)
        XCTAssertLessThanOrEqual(high, 1)
    }

    func testVoiceAudioSessionCoordinatorAcquireRelease() {
        let coordinator = VoiceAudioSessionCoordinator.shared
        coordinator.forceReleaseAll()
        XCTAssertTrue(coordinator.acquire(.aiAssistant, profile: .aiLive))
        XCTAssertEqual(coordinator.activeConsumer, .aiAssistant)
        coordinator.release(.aiAssistant)
        XCTAssertNil(coordinator.activeConsumer)
    }

    func testVoiceAudioSessionCoordinatorBlocksSecondConsumer() {
        let coordinator = VoiceAudioSessionCoordinator.shared
        coordinator.forceReleaseAll()
        XCTAssertTrue(coordinator.acquire(.voiceNotes, profile: .voiceNotes))
        XCTAssertFalse(coordinator.acquire(.aiAssistant, profile: .aiLive))
        coordinator.release(.voiceNotes)
    }

    func testMaxRecordingDurationsMatchProductSpec() {
        XCTAssertEqual(SpeechManager.maxRecordingDurationSec, 60, accuracy: 0.001)
        XCTAssertEqual(VoiceNotesViewModel.maxRecordingDurationSec, 600)
        XCTAssertEqual(VoiceNotesViewModel.recordingWarningBeforeEndSec, 30)
    }

    func testVoiceRecordingInterruptedNotificationName() {
        XCTAssertEqual(
            Notification.Name.voiceRecordingInterrupted.rawValue,
            "VoiceRecordingInterrupted"
        )
    }

    func testWaveformSamplerReturnsStableBarCount() {
        let samples = VoiceNoteWaveformSampler.samples(forFilePath: "/nonexistent/path.m4a", barCount: 24)
        XCTAssertEqual(samples.count, 24)
        XCTAssertTrue(samples.allSatisfy { $0 >= 4 && $0 <= 22 })
    }
}
