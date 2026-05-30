import AVFoundation
import Speech
import Combine

/// Live speech-to-text for AI Assistant (Apple `Speech` framework — on-device or Siri cloud, not ALADDIN API).
final class SpeechManager: ObservableObject {
    static let maxRecordingDurationSec: TimeInterval = 60
    static let minimumUsefulRecordingSec: TimeInterval = 1.25

    enum LastRecognitionFailure: Equatable {
        case none
        case serviceUnavailable
        case recordingTooShort
        case emptyTranscript
    }

    @Published private(set) var isRecording = false
    @Published private(set) var isPreparingRecording = false
    @Published private(set) var isSpeechInputAvailable = true
    @Published private(set) var livePartialTranscript: String = ""
    @Published private(set) var usesCloudRecognition = false
    @Published private(set) var audioLevel: Double = 0
    @Published private(set) var isStoppingRecording = false
    @Published private(set) var isMicrophoneCoolingDown = false
    @Published var recognizedText: String?

    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    private let audioEngine = AVAudioEngine()
    private var inputTapInstalled = false
    private var isStopping = false
    private var activeRecognizerLocale: String?
    private var latestPartialTranscript: String?
    private var pendingCompletion: ((String?) -> Void)?
    private var completionDelivered = false
    private var sessionUsedOnDeviceRecognition = false
    private var recordingSessionStarted = false
    private var didAttemptCloudFallback = false
    private var didAttemptOnDeviceFallback = false
    private var forceCloudRecognition = false
    private var forceOnDeviceRecognition = false
    private var maxDurationTimer: Timer?
    private var lastSessionRecordingDurationSec: TimeInterval = 0
    private(set) var lastRecognitionFailure: LastRecognitionFailure = .none
    private var interruptionObserver: NSObjectProtocol?
    private var lastLevelUIUpdate: CFAbsoluteTime = 0
    private var lastStartAttemptAt: Date?
    private let startDebounceSec: TimeInterval = 0.35
    private let startCooldownSec: TimeInterval = 0.65
    private var recordingStartedAt: Date?
    private var finalizeAttempt = 0
    private var sawAudioSignalDuringSession = false
    private var fallbackPCMInt16 = Data()
    private var fallbackSampleRate: Double = 16_000
    private var fallbackChannels: UInt16 = 1
    private let fallbackMaxPCMBytes = 480_000

    /// Cloud STT on device often needs >0.6s after `endAudio` for a final result.
    private var finalizeDelaySec: TimeInterval {
        #if targetEnvironment(simulator)
        return 0.65
        #else
        return 1.75
        #endif
    }

    /// Потребитель `AVAudioSession` (на «Мир героев» — `.companion`, иначе `.aiAssistant`).
    var audioSessionConsumer: VoiceAudioSessionCoordinator.Consumer = .aiAssistant

    private let logger = MasterLogger.shared

    init() {
        refreshAvailability()
        registerInterruptionObserver()
    }

    deinit {
        if let interruptionObserver {
            NotificationCenter.default.removeObserver(interruptionObserver)
        }
        maxDurationTimer?.invalidate()
    }

    func refreshAvailability() {
        let available = SpeechRecognizerFactory.isSpeechInputAvailable(
            preferred: LocalizationManager.shared.speechRecognitionLocale
        )
        DispatchQueue.main.async {
            self.isSpeechInputAvailable = available
        }
    }

    /// PCM/WAV captured during companion recording for server STT fallback (companion consumer only).
    func takeFallbackWAVData() -> Data? {
        guard audioSessionConsumer == .companion, !fallbackPCMInt16.isEmpty else { return nil }
        let wav = Self.wrapPCM16AsWAV(
            pcm: fallbackPCMInt16,
            sampleRate: UInt32(max(1, Int(fallbackSampleRate))),
            channels: fallbackChannels
        )
        fallbackPCMInt16.removeAll(keepingCapacity: false)
        return wav
    }

    var hadAudioSignalDuringLastSession: Bool { sawAudioSignalDuringSession }
    var lastRecordingDurationSec: TimeInterval { lastSessionRecordingDurationSec }

    /// Прогрев разрешений при открытии AI — первый тап по микрофону не «висит» 20–30 с.
    func warmUpPermissionsIfNeeded() {
        AVAudioSession.sharedInstance().requestRecordPermission { _ in }
        let status = SFSpeechRecognizer.authorizationStatus()
        if status == .notDetermined {
            SFSpeechRecognizer.requestAuthorization { _ in
                DispatchQueue.main.async { self.refreshAvailability() }
            }
        } else {
            refreshAvailability()
        }
    }

    func startRecording(completion: @escaping (String?) -> Void) {
        logger.business("🎤 SpeechManager: Starting speech recognition process")
        lastRecognitionFailure = .none

        if isMicrophoneCoolingDown {
            logger.warn("🎤 SpeechManager: Start ignored (cooldown)")
            return
        }
        if isPreparingRecording || isStopping || isStoppingRecording {
            logger.warn("🎤 SpeechManager: Start ignored (busy state)")
            return
        }
        if let last = lastStartAttemptAt, Date().timeIntervalSince(last) < startDebounceSec {
            logger.warn("🎤 SpeechManager: Start ignored (debounce)")
            return
        }
        lastStartAttemptAt = Date()

        guard !isRecording else {
            logger.warn("🎤 SpeechManager: Already recording — ignoring duplicate start")
            return
        }

        runOnMain { self.isPreparingRecording = true }

        AVAudioSession.sharedInstance().requestRecordPermission { [weak self] granted in
            guard let self else { return }
            DispatchQueue.main.async {
                guard granted else {
                    self.isPreparingRecording = false
                    NotificationCenter.default.post(name: .microphonePermissionDenied, object: nil)
                    completion(nil)
                    return
                }
                SFSpeechRecognizer.requestAuthorization { status in
                    DispatchQueue.main.async {
                        switch status {
                        case .authorized:
                            self.startRecordingInternal(completion: completion)
                        case .denied, .restricted, .notDetermined:
                            self.isPreparingRecording = false
                            NotificationCenter.default.post(name: .speechRecognitionPermissionDenied, object: nil)
                            completion(nil)
                        @unknown default:
                            self.isPreparingRecording = false
                            NotificationCenter.default.post(name: .speechRecognitionPermissionDenied, object: nil)
                            completion(nil)
                        }
                    }
                }
            }
        }
    }

    func stopRecording() {
        runOnMain { [weak self] in
            self?.stopRecordingOnMain()
        }
    }

    /// Отмена записи без отправки текста (slide-to-cancel).
    func cancelRecording() {
        runOnMain { [weak self] in
            guard let self else { return }
            guard self.isRecording || self.recognitionTask != nil || self.recognitionRequest != nil else { return }
            self.logger.business("🎤 SpeechManager: Recording cancelled by user")
            self.maxDurationTimer?.invalidate()
            self.isStopping = true
            self.recognitionTask?.cancel()
            self.recognitionTask = nil
            self.recognitionRequest = nil
            self.teardownAudioEngine()
            self.isRecording = false
            self.isPreparingRecording = false
            self.livePartialTranscript = ""
            self.usesCloudRecognition = false
            self.audioLevel = 0
            self.completionDelivered = true
            self.pendingCompletion = nil
            self.latestPartialTranscript = nil
            self.isStopping = false
            self.isStoppingRecording = false
            VoiceAudioSessionCoordinator.shared.release(audioSessionConsumer)
            self.applyStartCooldown()
            HapticFeedback.notification(.warning)
        }
    }

    private func stopRecordingOnMain() {
        if isStopping {
            logger.warn("🎤 SpeechManager: stopRecording ignored (already stopping)")
            return
        }
        if !isRecording && recognitionTask == nil && recognitionRequest == nil && !audioEngine.isRunning {
            logger.warn("🎤 SpeechManager: stopRecording ignored (already stopped)")
            deliverPendingCompletionIfNeeded(forcePartial: true)
            return
        }
        isStopping = true
        isStoppingRecording = true
        logger.business("🎤 SpeechManager: Stopping recording (endAudio, no immediate cancel)")

        recognitionRequest?.endAudio()
        teardownAudioEngine()
        isRecording = false
        HapticFeedback.impact(.light)
        audioLevel = 0
        finalizeAttempt = 0
        scheduleFinalizePass()
    }

    private func scheduleFinalizePass() {
        DispatchQueue.main.asyncAfter(deadline: .now() + finalizeDelaySec) { [weak self] in
            guard let self else { return }
            let partial = self.latestPartialTranscript?.trimmingCharacters(in: .whitespacesAndNewlines)
            if partial?.isEmpty == false {
                self.deliverPendingCompletionIfNeeded(forcePartial: true)
                self.finishStopUIState()
                return
            }
            if self.recognitionTask != nil, self.finalizeAttempt < 2 {
                self.finalizeAttempt += 1
                self.logger.business("🎤 SpeechManager: Waiting for speech final (\(self.finalizeAttempt))")
                self.scheduleFinalizePass()
                return
            }
            #if !targetEnvironment(simulator)
            if self.finalizeAttempt == 0 {
                self.finalizeAttempt = 1
                self.logger.business("🎤 SpeechManager: Waiting extra beat for cloud final transcript")
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.85) { [weak self] in
                    guard let self else { return }
                    self.deliverPendingCompletionIfNeeded(forcePartial: true)
                    self.finishStopUIState()
                }
                return
            }
            #endif
            self.deliverPendingCompletionIfNeeded(forcePartial: true)
            self.finishStopUIState()
        }
    }

    /// Companion TTS may leave `.playback` on `AVAudioSession`; reset before mic.
    private func acquireAudioSessionForRecording() -> Bool {
        if VoiceAudioSessionCoordinator.shared.acquire(audioSessionConsumer, profile: .aiLive) {
            return true
        }
        guard audioSessionConsumer == .companion else { return false }
        VoiceAudioSessionCoordinator.shared.forceReleaseAll()
        try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
        return VoiceAudioSessionCoordinator.shared.acquire(audioSessionConsumer, profile: .aiLive)
    }

    private func finishStopUIState() {
        isStopping = false
        isStoppingRecording = false
        applyStartCooldown()
    }

    // MARK: - Private

    private func removeInputTapIfInstalled() {
        guard inputTapInstalled else { return }
        audioEngine.inputNode.removeTap(onBus: 0)
        inputTapInstalled = false
    }

    /// Apple requires removing the input tap **before** stopping `AVAudioEngine` — otherwise SIGABRT.
    private func teardownAudioEngine() {
        removeInputTapIfInstalled()
        if audioEngine.isRunning {
            audioEngine.stop()
        }
        audioEngine.reset()
    }

    private func resetEngineForNewRecordingSession() {
        teardownAudioEngine()
        recognitionTask?.cancel()
        recognitionTask = nil
        recognitionRequest = nil
        latestPartialTranscript = nil
        completionDelivered = false
        recordingSessionStarted = false
        sessionUsedOnDeviceRecognition = false
        sawAudioSignalDuringSession = false
        fallbackPCMInt16.removeAll(keepingCapacity: false)
        fallbackSampleRate = 16_000
        fallbackChannels = 1
        // Keep fallback flags across engine reset when retrying alternate path.
    }

    private func deliverPendingCompletionIfNeeded(forcePartial: Bool = false) {
        guard !completionDelivered else { return }
        guard let completion = pendingCompletion else { return }
        let text = latestPartialTranscript?.trimmingCharacters(in: .whitespacesAndNewlines)
        let text = latestPartialTranscript?.trimmingCharacters(in: .whitespacesAndNewlines)
        if text?.isEmpty != false,
           sawAudioSignalDuringSession,
           !didAttemptOnDeviceFallback,
           sessionUsedOnDeviceRecognition == false,
           SpeechRecognizerFactory.onDeviceOnly(preferred: LocalizationManager.shared.speechRecognitionLocale) != nil {
            logger.warn("🎤 SpeechManager: Empty cloud transcript after audio signal — retrying on-device path")
            finishRecordingSession()
            retryWithOnDeviceRecognition(previousPartial: nil, completion: completion)
            return
        }
        if text?.isEmpty != false,
           sawAudioSignalDuringSession,
           !didAttemptCloudFallback,
           !forceOnDeviceRecognition {
            logger.warn("🎤 SpeechManager: Empty transcript after audio signal — retrying cloud path")
            finishRecordingSession()
            retryWithCloudRecognition(previousPartial: nil, completion: completion)
            return
        }
        if forcePartial || (text?.isEmpty == false) {
            completeOnce(text?.isEmpty == false ? text : nil, completion: completion)
        }
    }

    private func completeOnce(_ text: String?, completion: @escaping (String?) -> Void) {
        guard !completionDelivered else { return }
        if let start = recordingStartedAt {
            lastSessionRecordingDurationSec = Date().timeIntervalSince(start)
        }
        if text?.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty != false {
            if lastSessionRecordingDurationSec > 0,
               lastSessionRecordingDurationSec < Self.minimumUsefulRecordingSec {
                lastRecognitionFailure = .recordingTooShort
            } else if lastRecognitionFailure == .none {
                lastRecognitionFailure = .emptyTranscript
            }
        } else {
            lastRecognitionFailure = .none
        }
        completionDelivered = true
        pendingCompletion = nil
        clearRecognitionFallbackFlags()
        recordingStartedAt = nil
        VoiceAudioSessionCoordinator.shared.release(audioSessionConsumer)
        DispatchQueue.main.async {
            self.isPreparingRecording = false
            completion(text)
        }
    }

    private func postSpeechServiceUnavailableIfNeeded(force: Bool = false) {
        guard force || !recordingSessionStarted else {
            logger.warn("🎤 SpeechManager: Suppressed unavailable alert (session had started)")
            return
        }
        isSpeechInputAvailable = false
        NotificationCenter.default.post(name: .speechServiceUnavailable, object: nil)
    }

    private func startRecordingInternal(completion: @escaping (String?) -> Void) {
        do {
            resetEngineForNewRecordingSession()
            isStopping = false

            guard self.acquireAudioSessionForRecording() else {
                logger.warn("🎤 SpeechManager: Audio session busy")
                isPreparingRecording = false
                completeOnce(nil, completion: completion)
                return
            }

            logger.business("🎤 SpeechManager: Audio session configured successfully")

            pendingCompletion = completion
            lastRecognitionFailure = .none

            let selection: SpeechRecognizerFactory.Selection?
            if forceOnDeviceRecognition {
                selection = SpeechRecognizerFactory.onDeviceOnly(
                    preferred: LocalizationManager.shared.speechRecognitionLocale
                )
            } else if audioSessionConsumer == .companion {
                selection = SpeechRecognizerFactory.cloudOnly(
                    preferred: LocalizationManager.shared.speechRecognitionLocale
                )
            } else if forceCloudRecognition {
                selection = SpeechRecognizerFactory.cloudOnly(
                    preferred: LocalizationManager.shared.speechRecognitionLocale
                )
            } else {
                selection = SpeechRecognizerFactory.bestForLiveRecognition(
                    preferred: LocalizationManager.shared.speechRecognitionLocale
                )
            }
            guard let selection else {
                logger.warn("🎤 SpeechManager: No speech recognizer available (preferred \(LocalizationManager.shared.speechRecognitionLocale.identifier))")
                isPreparingRecording = false
                postSpeechServiceUnavailableIfNeeded()
                completeOnce(nil, completion: completion)
                return
            }

            let speechRecognizer = selection.recognizer
            activeRecognizerLocale = speechRecognizer.locale.identifier
            sessionUsedOnDeviceRecognition = selection.useOnDeviceRecognition
            DispatchQueue.main.async {
                self.livePartialTranscript = ""
                self.usesCloudRecognition = !selection.useOnDeviceRecognition
            }
            let modeLabel = selection.useOnDeviceRecognition ? "onDevice" : "cloud(Siri)"
            #if targetEnvironment(simulator)
            logger.business("🎤 SpeechManager: Using recognizer \(speechRecognizer.locale.identifier), mode=\(modeLabel) [Simulator — cloud only]")
            #else
            logger.business("🎤 SpeechManager: Using recognizer \(speechRecognizer.locale.identifier), mode=\(modeLabel)")
            #endif

            recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
            guard let recognitionRequest else {
                VoiceAudioSessionCoordinator.shared.release(audioSessionConsumer)
                completeOnce(nil, completion: completion)
                return
            }

            recognitionRequest.shouldReportPartialResults = true
            if selection.useOnDeviceRecognition {
                recognitionRequest.requiresOnDeviceRecognition = true
            }

            recognitionTask = speechRecognizer.recognitionTask(with: recognitionRequest) { [weak self] result, error in
                guard let self else { return }
                self.runOnMain {
                    self.handleRecognitionEvent(result: result, error: error, completion: completion)
                }
            }

            let inputNode = audioEngine.inputNode
            audioEngine.prepare()
            let tapFormat = Self.validTapFormat(for: inputNode)
            guard tapFormat != nil else {
                logger.error("🎤 SpeechManager: Invalid input tap format — cannot start recording")
                throw NSError(domain: "SpeechManager", code: 3, userInfo: [NSLocalizedDescriptionKey: "Invalid audio input format"])
            }
            guard !inputTapInstalled else {
                logger.warn("🎤 SpeechManager: Tap already installed — skipping duplicate install")
                throw NSError(domain: "SpeechManager", code: 2, userInfo: [NSLocalizedDescriptionKey: "Duplicate audio tap"])
            }
            logger.business("🎤 SpeechManager: Installing audio tap (format: \(tapFormat?.sampleRate ?? 0) Hz)")
            inputNode.installTap(onBus: 0, bufferSize: 1024, format: tapFormat) { [weak self] buffer, _ in
                guard let self else { return }
                self.recognitionRequest?.append(buffer)
                let level = AudioLevelMeter.normalizedLevel(from: buffer)
                if level > 0.02 {
                    self.sawAudioSignalDuringSession = true
                }
                if self.audioSessionConsumer == .companion {
                    self.appendFallbackPCM(from: buffer)
                }
                let now = CFAbsoluteTimeGetCurrent()
                guard now - self.lastLevelUIUpdate > 0.05 else { return }
                self.lastLevelUIUpdate = now
                DispatchQueue.main.async {
                    self.audioLevel = level
                }
            }
            inputTapInstalled = true

            try audioEngine.start()

            isPreparingRecording = false
            isRecording = true
            recordingSessionStarted = true
            recordingStartedAt = Date()
            startMaxDurationTimer()
            HapticFeedback.impact(.medium)
            logger.business("🎤 SpeechManager: Recording started")

        } catch {
            logger.error("🎤 SpeechManager: Failed to start recording", error: error)
            isPreparingRecording = false
            finishRecordingSession()
            VoiceAudioSessionCoordinator.shared.release(audioSessionConsumer)
            completeOnce(nil, completion: completion)
        }
    }

    private func handleRecognitionEvent(
        result: SFSpeechRecognitionResult?,
        error: Error?,
        completion: @escaping (String?) -> Void
    ) {
                if let result {
                    let text = result.bestTranscription.formattedString
                    if !text.isEmpty {
                        self.latestPartialTranscript = text
                        self.livePartialTranscript = text
                    }
                    if result.isFinal {
                        self.logger.business("🎤 SpeechManager: Final transcript (\(text.count) chars)")
                        self.finishRecordingSession()
                        self.completeOnce(text.isEmpty ? nil : text, completion: completion)
                        return
                    }
                }

                if let error {
                    if SpeechRecognitionErrorClassifier.isBenign(error) {
                        self.finishRecordingSession()
                        let partial = self.latestPartialTranscript ?? result?.bestTranscription.formattedString
                        self.completeOnce(partial?.isEmpty == false ? partial : nil, completion: completion)
                        return
                    }
                    if SpeechRecognitionErrorClassifier.isRetryPrompt(error),
                       self.latestPartialTranscript == nil,
                       !self.didAttemptCloudFallback {
                        self.logger.warn("🎤 SpeechManager: Siri Retry — switching to cloud path")
                        self.finishRecordingSession()
                        self.retryWithCloudRecognition(previousPartial: nil, completion: completion)
                        return
                    }
                    if SpeechRecognitionErrorClassifier.isOnDeviceModelMissing(error),
                       self.sessionUsedOnDeviceRecognition,
                       self.latestPartialTranscript == nil {
                        self.logger.warn("🎤 SpeechManager: On-device model missing — retrying cloud path")
                        self.finishRecordingSession()
                        self.retryWithCloudRecognition(previousPartial: nil, completion: completion)
                        return
                    }
                    if SpeechRecognitionErrorClassifier.isServiceUnavailable(error),
                       !self.sessionUsedOnDeviceRecognition,
                       !self.didAttemptOnDeviceFallback,
                       SpeechRecognizerFactory.onDeviceOnly(
                           preferred: LocalizationManager.shared.speechRecognitionLocale
                       ) != nil {
                        self.logger.warn("🎤 SpeechManager: Siri cloud unavailable (1107) — retrying on-device path")
                        self.lastRecognitionFailure = .serviceUnavailable
                        self.finishRecordingSession()
                        self.retryWithOnDeviceRecognition(previousPartial: nil, completion: completion)
                        return
                    }
                    if SpeechRecognitionErrorClassifier.isServiceUnavailable(error) {
                        self.logger.warn("🎤 SpeechManager: Speech service unavailable (\(error))")
                        self.lastRecognitionFailure = .serviceUnavailable
                        self.postSpeechServiceUnavailableIfNeeded(force: true)
                    } else {
                        self.logger.warn("🎤 SpeechManager: Recognition error: \(error.localizedDescription)")
                    }
                    self.finishRecordingSession()
                    let partial = self.latestPartialTranscript ?? result?.bestTranscription.formattedString
                    self.completeOnce(partial?.isEmpty == false ? partial : nil, completion: completion)
                }
    }

    private static func validTapFormat(for inputNode: AVAudioInputNode) -> AVAudioFormat? {
        let output = inputNode.outputFormat(forBus: 0)
        if output.sampleRate > 0, output.channelCount > 0 {
            return output
        }
        let input = inputNode.inputFormat(forBus: 0)
        if input.sampleRate > 0, input.channelCount > 0 {
            return input
        }
        return nil
    }

    private func runOnMain(_ block: @escaping () -> Void) {
        if Thread.isMainThread {
            block()
        } else {
            DispatchQueue.main.async(execute: block)
        }
    }

    /// Fallback when ru-RU on-device pack is not downloaded (common on TestFlight devices).
    private func retryWithCloudRecognition(previousPartial: String?, completion: @escaping (String?) -> Void) {
        guard !didAttemptCloudFallback else {
            completeOnce(previousPartial, completion: completion)
            return
        }
        guard SpeechRecognizerFactory.cloudOnly(
            preferred: LocalizationManager.shared.speechRecognitionLocale
        ) != nil else {
            completeOnce(previousPartial, completion: completion)
            return
        }
        didAttemptCloudFallback = true
        forceCloudRecognition = true
        forceOnDeviceRecognition = false
        sessionUsedOnDeviceRecognition = false
        if let partial = previousPartial, !partial.isEmpty {
            latestPartialTranscript = partial
        }
        completionDelivered = false
        startRecordingInternal(completion: completion)
    }

    /// Fallback when Siri cloud returns 1107/1111 on device (common on iOS 26 beta).
    private func retryWithOnDeviceRecognition(previousPartial: String?, completion: @escaping (String?) -> Void) {
        guard !didAttemptOnDeviceFallback else {
            completeOnce(previousPartial, completion: completion)
            return
        }
        guard SpeechRecognizerFactory.onDeviceOnly(
            preferred: LocalizationManager.shared.speechRecognitionLocale
        ) != nil else {
            completeOnce(previousPartial, completion: completion)
            return
        }
        didAttemptOnDeviceFallback = true
        forceOnDeviceRecognition = true
        forceCloudRecognition = false
        sessionUsedOnDeviceRecognition = true
        if let partial = previousPartial, !partial.isEmpty {
            latestPartialTranscript = partial
        }
        completionDelivered = false
        startRecordingInternal(completion: completion)
    }

    private func clearRecognitionFallbackFlags() {
        forceCloudRecognition = false
        forceOnDeviceRecognition = false
        didAttemptCloudFallback = false
        didAttemptOnDeviceFallback = false
    }

    private func finishRecordingSession() {
        runOnMain { [weak self] in
            guard let self else { return }
            self.maxDurationTimer?.invalidate()
            self.maxDurationTimer = nil
            self.recognitionTask?.cancel()
            self.recognitionTask = nil
            self.recognitionRequest = nil
            self.teardownAudioEngine()
            self.isRecording = false
            self.livePartialTranscript = ""
            self.usesCloudRecognition = false
            self.audioLevel = 0
            if !self.isStopping {
                VoiceAudioSessionCoordinator.shared.release(audioSessionConsumer)
            }
        }
    }

    private func startMaxDurationTimer() {
        maxDurationTimer?.invalidate()
        let timer = Timer(timeInterval: Self.maxRecordingDurationSec, repeats: false) { [weak self] _ in
            guard let self else { return }
            self.logger.warn("🎤 SpeechManager: Max duration reached — auto stop")
            self.stopRecordingOnMain()
        }
        RunLoop.main.add(timer, forMode: .common)
        maxDurationTimer = timer
    }

    private func appendFallbackPCM(from buffer: AVAudioPCMBuffer) {
        guard fallbackPCMInt16.count < fallbackMaxPCMBytes else { return }
        let format = buffer.format
        fallbackSampleRate = format.sampleRate
        fallbackChannels = UInt16(max(1, min(2, Int(format.channelCount))))
        let frameCount = Int(buffer.frameLength)
        guard frameCount > 0 else { return }

        if let channelData = buffer.floatChannelData {
            var local = Data()
            local.reserveCapacity(min(frameCount * 2, fallbackMaxPCMBytes - fallbackPCMInt16.count))
            for frame in 0..<frameCount {
                var sample: Float32 = 0
                for ch in 0..<Int(format.channelCount) {
                    sample += channelData[ch][frame]
                }
                sample /= Float32(max(1, format.channelCount))
                let clamped = max(-1, min(1, sample))
                var int16 = Int16(clamped * Float32(Int16.max))
                withUnsafeBytes(of: &int16) { local.append(contentsOf: $0) }
                if fallbackPCMInt16.count + local.count >= fallbackMaxPCMBytes { break }
            }
            fallbackPCMInt16.append(local)
        } else if let channelData = buffer.int16ChannelData {
            let byteCount = frameCount * MemoryLayout<Int16>.size * Int(format.channelCount)
            let ptr = UnsafeRawBufferPointer(start: channelData[0], count: byteCount)
            fallbackPCMInt16.append(Data(ptr.prefix(fallbackMaxPCMBytes - fallbackPCMInt16.count)))
        }
    }

    private static func wrapPCM16AsWAV(pcm: Data, sampleRate: UInt32, channels: UInt16) -> Data {
        let bitsPerSample: UInt16 = 16
        let byteRate = sampleRate * UInt32(channels) * UInt32(bitsPerSample / 8)
        let blockAlign = channels * (bitsPerSample / 8)
        var header = Data()
        header.append(contentsOf: "RIFF".utf8)
        var chunkSize = UInt32(36 + pcm.count).littleEndian
        withUnsafeBytes(of: &chunkSize) { header.append(contentsOf: $0) }
        header.append(contentsOf: "WAVE".utf8)
        header.append(contentsOf: "fmt ".utf8)
        var subchunk1Size = UInt32(16).littleEndian
        withUnsafeBytes(of: &subchunk1Size) { header.append(contentsOf: $0) }
        var audioFormat = UInt16(1).littleEndian
        withUnsafeBytes(of: &audioFormat) { header.append(contentsOf: $0) }
        var ch = channels.littleEndian
        withUnsafeBytes(of: &ch) { header.append(contentsOf: $0) }
        var sr = sampleRate.littleEndian
        withUnsafeBytes(of: &sr) { header.append(contentsOf: $0) }
        var br = byteRate.littleEndian
        withUnsafeBytes(of: &br) { header.append(contentsOf: $0) }
        var ba = blockAlign.littleEndian
        withUnsafeBytes(of: &ba) { header.append(contentsOf: $0) }
        var bps = bitsPerSample.littleEndian
        withUnsafeBytes(of: &bps) { header.append(contentsOf: $0) }
        header.append(contentsOf: "data".utf8)
        var dataSize = UInt32(pcm.count).littleEndian
        withUnsafeBytes(of: &dataSize) { header.append(contentsOf: $0) }
        var out = header
        out.append(pcm)
        return out
    }

    private func registerInterruptionObserver() {
        interruptionObserver = NotificationCenter.default.addObserver(
            forName: AVAudioSession.interruptionNotification,
            object: AVAudioSession.sharedInstance(),
            queue: .main
        ) { [weak self] notification in
            self?.handleAudioInterruption(notification)
        }
    }

    private func applyStartCooldown() {
        isMicrophoneCoolingDown = true
        DispatchQueue.main.asyncAfter(deadline: .now() + startCooldownSec) { [weak self] in
            self?.isMicrophoneCoolingDown = false
        }
    }

    private func handleAudioInterruption(_ notification: Notification) {
        guard let raw = notification.userInfo?[AVAudioSessionInterruptionTypeKey] as? UInt,
              let type = AVAudioSession.InterruptionType(rawValue: raw) else { return }
        guard type == .began, isRecording || isStopping else { return }
        logger.warn("🎤 SpeechManager: Audio session interrupted — stopping")
        stopRecording()
        deliverPendingCompletionIfNeeded(forcePartial: true)
        NotificationCenter.default.post(
            name: .voiceRecordingInterrupted,
            object: nil,
            userInfo: ["source": "ai"]
        )
    }

}

extension Notification.Name {
    static let speechPermissionDenied = Notification.Name("SpeechPermissionDenied")
    static let speechServiceUnavailable = Notification.Name("SpeechServiceUnavailable")
}
