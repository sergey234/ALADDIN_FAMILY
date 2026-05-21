import Foundation
import AVFoundation

final class VoiceNotesRecorderService: NSObject, AVAudioRecorderDelegate {
    private var recorder: AVAudioRecorder?
    private var currentURL: URL?
    private var levelTimer: Timer?

    var onInterruptedAndAutoSaved: (() -> Void)?
    var onRouteChanged: (() -> Void)?
    var onAudioLevel: ((Float) -> Void)?

    private(set) var currentAudioLevel: Float = 0

    var isRecording: Bool { recorder?.isRecording == true }

    override init() {
        super.init()
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleInterruption(_:)),
            name: AVAudioSession.interruptionNotification,
            object: nil
        )
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleRouteChange(_:)),
            name: AVAudioSession.routeChangeNotification,
            object: nil
        )
    }

    deinit {
        NotificationCenter.default.removeObserver(self)
        stopLevelTimer()
    }

    func start() throws -> URL {
        if isRecording, let url = currentURL { return url }

        guard VoiceAudioSessionCoordinator.shared.acquire(.voiceNotes, profile: .voiceNotes) else {
            throw NSError(domain: "VoiceNotesRecorderService", code: 2, userInfo: [NSLocalizedDescriptionKey: "Audio session busy"])
        }

        let dir = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let url = dir.appendingPathComponent("voice_note_\(UUID().uuidString).m4a")
        let settings: [String: Any] = [
            AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
            AVSampleRateKey: 44_100,
            AVNumberOfChannelsKey: 1,
            AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue
        ]

        let rec = try AVAudioRecorder(url: url, settings: settings)
        rec.delegate = self
        rec.isMeteringEnabled = true
        rec.prepareToRecord()
        guard rec.record() else {
            VoiceAudioSessionCoordinator.shared.release(.voiceNotes)
            throw NSError(domain: "VoiceNotesRecorderService", code: 1, userInfo: [NSLocalizedDescriptionKey: "Failed to start recording"])
        }
        recorder = rec
        currentURL = url
        startLevelTimer()
        return url
    }

    func pause() {
        recorder?.pause()
        stopLevelTimer()
    }

    func resume() {
        recorder?.record()
        startLevelTimer()
    }

    func stop() -> URL? {
        stopLevelTimer()
        recorder?.stop()
        let url = currentURL
        recorder = nil
        currentURL = nil
        currentAudioLevel = 0
        onAudioLevel?(0)
        VoiceAudioSessionCoordinator.shared.release(.voiceNotes)
        return url
    }

    func cancel() {
        let url = stop()
        if let url { try? FileManager.default.removeItem(at: url) }
    }

    private func startLevelTimer() {
        levelTimer?.invalidate()
        levelTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            guard let self, let recorder = self.recorder else { return }
            recorder.updateMeters()
            let level = recorder.averagePower(forChannel: 0)
            self.currentAudioLevel = level
            self.onAudioLevel?(level)
        }
    }

    private func stopLevelTimer() {
        levelTimer?.invalidate()
        levelTimer = nil
    }

    @objc
    private func handleInterruption(_ notification: Notification) {
        guard let userInfo = notification.userInfo,
              let raw = userInfo[AVAudioSessionInterruptionTypeKey] as? UInt,
              let type = AVAudioSession.InterruptionType(rawValue: raw) else { return }
        if type == .began, isRecording {
            _ = stop()
            onInterruptedAndAutoSaved?()
        }
    }

    @objc
    private func handleRouteChange(_ notification: Notification) {
        if isRecording {
            onRouteChanged?()
        }
    }
}
