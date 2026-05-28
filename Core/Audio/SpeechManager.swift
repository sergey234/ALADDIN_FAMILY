import AVFoundation
import Speech
import Combine

/// Live speech-to-text for AI Assistant (Apple `Speech` framework — on-device or Siri cloud, not ALADDIN API).
final class SpeechManager: ObservableObject {
    static let maxRecordingDurationSec: TimeInterval = 60

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
    private var forceCloudRecognition = false
    private var maxDurationTimer: Timer?
    private var interruptionObserver: NSObjectProtocol?
    private var lastLevelUIUpdate: CFAbsoluteTime = 0
    private var lastStartAttemptAt: Date?
    private let startDebounceSec: TimeInterval = 0.35
    private let startCooldownSec: TimeInterval = 0.65

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

        VoiceAudioSessionCoordinator.shared.release(audioSessionConsumer)
        audioLevel = 0

        DispatchQueue.main.asyncAfter(deadline: .now() + 0.6) { [weak self] in
            guard let self else { return }
            self.deliverPendingCompletionIfNeeded(forcePartial: true)
            self.isStopping = false
            self.isStoppingRecording = false
            self.applyStartCooldown()
        }
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
        // Keep `forceCloudRecognition` / `didAttemptCloudFallback` across engine reset when retrying cloud path.
    }

    private func deliverPendingCompletionIfNeeded(forcePartial: Bool = false) {
        guard !completionDelivered else { return }
        guard let completion = pendingCompletion else { return }
        let text = latestPartialTranscript?.trimmingCharacters(in: .whitespacesAndNewlines)
        if forcePartial || (text?.isEmpty == false) {
            completeOnce(text?.isEmpty == false ? text : nil, completion: completion)
        }
    }

    private func completeOnce(_ text: String?, completion: @escaping (String?) -> Void) {
        guard !completionDelivered else { return }
        completionDelivered = true
        pendingCompletion = nil
        clearCloudFallbackFlags()
        DispatchQueue.main.async {
            self.isPreparingRecording = false
            completion(text)
        }
    }

    private func postSpeechServiceUnavailableIfNeeded() {
        guard !recordingSessionStarted else {
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

            guard VoiceAudioSessionCoordinator.shared.acquire(audioSessionConsumer, profile: .aiLive) else {
                logger.warn("🎤 SpeechManager: Audio session busy")
                isPreparingRecording = false
                completeOnce(nil, completion: completion)
                return
            }

            logger.business("🎤 SpeechManager: Audio session configured successfully")

            pendingCompletion = completion

            let selection: SpeechRecognizerFactory.Selection?
            if forceCloudRecognition {
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
            guard !inputTapInstalled else {
                logger.warn("🎤 SpeechManager: Tap already installed — skipping duplicate install")
                throw NSError(domain: "SpeechManager", code: 2, userInfo: [NSLocalizedDescriptionKey: "Duplicate audio tap"])
            }
            logger.business("🎤 SpeechManager: Installing audio tap (format: \(tapFormat?.sampleRate ?? 0) Hz)")
            inputNode.installTap(onBus: 0, bufferSize: 1024, format: tapFormat) { [weak self] buffer, _ in
                guard let self else { return }
                self.recognitionRequest?.append(buffer)
                let level = AudioLevelMeter.normalizedLevel(from: buffer)
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
                    if SpeechRecognitionErrorClassifier.isOnDeviceModelMissing(error),
                       self.sessionUsedOnDeviceRecognition,
                       self.latestPartialTranscript == nil {
                        self.logger.warn("🎤 SpeechManager: On-device model missing — retrying cloud path")
                        self.finishRecordingSession()
                        self.retryWithCloudRecognition(previousPartial: nil, completion: completion)
                        return
                    }
                    if SpeechRecognitionErrorClassifier.isServiceUnavailable(error) {
                        self.logger.warn("🎤 SpeechManager: Speech service unavailable (\(error))")
                        self.postSpeechServiceUnavailableIfNeeded()
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
        sessionUsedOnDeviceRecognition = false
        if let partial = previousPartial, !partial.isEmpty {
            latestPartialTranscript = partial
        }
        completionDelivered = false
        startRecordingInternal(completion: completion)
    }

    private func clearCloudFallbackFlags() {
        forceCloudRecognition = false
        didAttemptCloudFallback = false
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
