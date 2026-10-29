import Foundation
import AVFoundation

final class VoiceNotesRecorderService: NSObject, AVAudioRecorderDelegate {
    private var recorder: AVAudioRecorder?
    private var engine: AVAudioEngine?
    private var audioFile: AVAudioFile?
    private var currentURL: URL?
    private var levelTimer: Timer?
    private let fileLock = NSLock()

    var onInterruptedAndAutoSaved: (() -> Void)?
    var onRouteChanged: (() -> Void)?
    var onAudioLevel: ((Float) -> Void)?
    /// PCM from the mic tap. Empty when the recorder falls back to `AVAudioRecorder`.
    var onBuffer: ((AVAudioPCMBuffer) -> Void)?

    private(set) var currentAudioLevel: Float = 0

    var isRecording: Bool { recorder?.isRecording == true || engine?.isRunning == true }

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
        do {
            try startEngine(url: url)
            currentURL = url
            return url
        } catch {
            engine?.stop()
            engine = nil
            audioFile = nil
        }

        do {
            try startRecorder(url: url)
            currentURL = url
            return url
        } catch {
            VoiceAudioSessionCoordinator.shared.release(.voiceNotes)
            throw error
        }
    }

    func pause() {
        engine?.pause()
        recorder?.pause()
        stopLevelTimer()
    }

    func resume() {
        if engine != nil {
            try? engine?.start()
        } else {
            recorder?.record()
            startLevelTimer()
        }
    }

    func stop() -> URL? {
        stopLevelTimer()
        engine?.inputNode.removeTap(onBus: 0)
        engine?.stop()
        engine = nil
        fileLock.lock()
        audioFile = nil
        fileLock.unlock()
        recorder?.stop()
        recorder = nil
        let url = currentURL
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

    private func startEngine(url: URL) throws {
        let engine = AVAudioEngine()
        let input = engine.inputNode
        let format = input.outputFormat(forBus: 0)
        guard format.sampleRate > 0, format.channelCount > 0 else {
            throw NSError(domain: "VoiceNotesRecorderService", code: 3, userInfo: nil)
        }
        let settings: [String: Any] = [
            AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
            AVSampleRateKey: format.sampleRate,
            AVNumberOfChannelsKey: 1,
            AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue
        ]
        let file = try AVAudioFile(forWriting: url, settings: settings)
        let fileFormat = file.processingFormat
        input.installTap(onBus: 0, bufferSize: 4096, format: format) { [weak self] buffer, _ in
            self?.write(buffer, to: file, fileFormat: fileFormat)
            self?.onBuffer?(buffer)
            self?.publishLevel(buffer)
        }
        engine.prepare()
        try engine.start()
        self.engine = engine
        self.audioFile = file
    }

    private func write(_ buffer: AVAudioPCMBuffer, to file: AVAudioFile, fileFormat: AVAudioFormat) {
        fileLock.lock()
        defer { fileLock.unlock() }
        if buffer.format == fileFormat {
            try? file.write(from: buffer)
            return
        }
        guard let converter = AVAudioConverter(from: buffer.format, to: fileFormat) else { return }
        let ratio = fileFormat.sampleRate / buffer.format.sampleRate
        let capacity = AVAudioFrameCount(Double(buffer.frameLength) * ratio) + 32
        guard let out = AVAudioPCMBuffer(pcmFormat: fileFormat, frameCapacity: max(capacity, 1)) else { return }
        var consumed = false
        var error: NSError?
        converter.convert(to: out, error: &error) { _, status in
            if consumed {
                status.pointee = .noDataNow
                return nil
            }
            consumed = true
            status.pointee = .haveData
            return buffer
        }
        if error == nil, out.frameLength > 0 {
            try? file.write(from: out)
        }
    }

    private func publishLevel(_ buffer: AVAudioPCMBuffer) {
        guard let channel = buffer.floatChannelData?[0] else { return }
        let count = Int(buffer.frameLength)
        guard count > 0 else { return }
        var sum: Float = 0
        for index in 0..<count {
            let sample = channel[index]
            sum += sample * sample
        }
        let rms = sqrt(sum / Float(count))
        let db = 20 * log10(max(rms, 0.000_01))
        currentAudioLevel = db
        onAudioLevel?(db)
    }

    private func startRecorder(url: URL) throws {
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
            throw NSError(domain: "VoiceNotesRecorderService", code: 1, userInfo: [NSLocalizedDescriptionKey: "Failed to start recording"])
        }
        recorder = rec
        startLevelTimer()
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
        if type == .began, isRecording || currentURL != nil {
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
