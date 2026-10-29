import Foundation
import Speech
import AVFoundation

enum VoiceNotesTranscriptionError: Error {
    case permissionDenied
    case recognizerUnavailable
    case timedOut
    case failed(String)
    /// On-device pack is missing. Partial text is kept. Cloud starts only after a yes on screen.
    case needsCloudConsent(partial: String)
}

struct VoiceNoteSegment: Codable, Equatable {
    var text: String
    var startSec: Double
    var endSec: Double
}

struct VoiceNotesTranscript: Equatable {
    var text: String
    var segments: [VoiceNoteSegment]
    var staysOnDevice: Bool
    var keptFirstMinuteOnly: Bool
}

/// Plain-text helpers for dictation. No network.
enum VoiceNotesTextCleanup {
    /// Whole words only. «это», «ну» and «как бы» stay.
    static func cleaner(_ text: String) -> String {
        let drop: Set<String> = ["э-э", "ээ", "эээ", "э-э-э", "эм", "типа"]
        let words = text.split(whereSeparator: { $0.isWhitespace || $0.isNewline }).map(String.init)
        var out: [String] = []
        var index = 0
        while index < words.count {
            let token = normalize(words[index])
            let next = index + 1 < words.count ? normalize(words[index + 1]) : ""
            if token == "ну" && next == "вот" {
                index += 2
                continue
            }
            if drop.contains(token) {
                index += 1
                continue
            }
            out.append(words[index])
            index += 1
        }
        return out.joined(separator: " ")
    }

    /// One thought, one short line. No network.
    static func makeClear(_ text: String) -> String {
        let sentences = splitSentences(cleaner(text))
        var lines: [String] = []
        for sentence in sentences {
            let bits = sentence.split(separator: ",").map { $0.trimmingCharacters(in: .whitespaces) }.filter { !$0.isEmpty }
            let wordCount = sentence.split(separator: " ").count
            if wordCount > 12 && bits.count > 1 {
                for bit in bits {
                    var line = bit
                    if let last = line.last, ".!?".contains(last) { line.removeLast() }
                    lines.append(line + ".")
                }
            } else {
                lines.append(sentence)
            }
        }
        return lines.joined(separator: "\n")
    }

    static func splitSentences(_ text: String) -> [String] {
        var parts: [String] = []
        var buf = ""
        for ch in text {
            buf.append(ch)
            if ".!?".contains(ch) {
                let trimmed = buf.trimmingCharacters(in: .whitespacesAndNewlines)
                if !trimmed.isEmpty { parts.append(trimmed) }
                buf = ""
            }
        }
        let tail = buf.trimmingCharacters(in: .whitespacesAndNewlines)
        if !tail.isEmpty { parts.append(tail) }
        return parts
    }

    /// Drops the repeated words at a 1-second restart seam.
    static func stripOverlap(newText: String, tail: String) -> String {
        let tailWords = words(tail).suffix(8).map(normalize)
        let newWords = words(newText)
        guard !tailWords.isEmpty, newWords.count >= tailWords.count else { return newText }
        let head = newWords.prefix(tailWords.count).map(normalize)
        if Array(head) == Array(tailWords) {
            return newWords.dropFirst(tailWords.count).joined(separator: " ")
        }
        return newText
    }

    static func words(_ text: String) -> [String] {
        text.split(whereSeparator: { $0.isWhitespace || $0.isNewline }).map(String.init)
    }

    static func normalize(_ word: String) -> String {
        word.trimmingCharacters(in: .punctuationCharacters).lowercased()
    }
}

enum VoiceNotesDictionary {
    static let storageKey = "voice_notes_dictionary_v1"
    static let maxPhrases = 100

    static func load() -> [String] {
        let raw = UserDefaults.standard.stringArray(forKey: storageKey) ?? []
        return Array(raw.prefix(maxPhrases))
    }

    static func save(_ phrases: [String]) {
        var seen = Set<String>()
        var kept: [String] = []
        for phrase in phrases {
            let trimmed = phrase.trimmingCharacters(in: .whitespacesAndNewlines)
            let key = trimmed.lowercased()
            guard !trimmed.isEmpty, !seen.contains(key), kept.count < maxPhrases else { continue }
            seen.insert(key)
            kept.append(trimmed)
        }
        UserDefaults.standard.set(kept, forKey: storageKey)
    }
}

/// Live dictation on the phone. Restarts the old recognizer near 50 seconds and keeps the text.
/// Does not use the companion path that starts Russian in the Apple cloud.
/// SpeechAnalyzer is not in the iOS 18.4 SDK this project compiles with, so a long live note uses this restart.
final class VoiceNotesLiveTranscriber {
    private let queue = DispatchQueue(label: "ai.aladdin.voice-notes.live")
    private var request: SFSpeechAudioBufferRecognitionRequest?
    private var task: SFSpeechRecognitionTask?
    private var recognizer: SFSpeechRecognizer?
    private var committed: [String] = []
    private var partial = ""
    private var segments: [VoiceNoteSegment] = []
    private var taskOffset: TimeInterval = 0
    private var taskStarted = Date()
    private var overlapTail = ""
    private var stopped = false
    private let dictionary: [String]
    private let onUpdate: (String) -> Void
    private let onNeedsCloud: (String) -> Void

    init(dictionary: [String], onUpdate: @escaping (String) -> Void, onNeedsCloud: @escaping (String) -> Void) {
        self.dictionary = Array(dictionary.prefix(VoiceNotesDictionary.maxPhrases))
        self.onUpdate = onUpdate
        self.onNeedsCloud = onNeedsCloud
    }

    func start() {
        queue.async { [weak self] in
            self?.openTask()
        }
    }

    func append(_ buffer: AVAudioPCMBuffer) {
        guard let copy = Self.copy(buffer) else { return }
        queue.async { [weak self] in
            self?.consume(copy)
        }
    }

    func pause() {
        queue.async { [weak self] in
            self?.commitPartial()
            self?.endTask()
        }
    }

    func resume() {
        queue.async { [weak self] in
            guard let self, !self.stopped else { return }
            self.openTask()
        }
    }

    func finish(completion: @escaping (VoiceNotesTranscript) -> Void) {
        queue.async {
            self.stopped = true
            self.request?.endAudio()
            self.queue.asyncAfter(deadline: .now() + 1.2) {
                self.commitPartial()
                self.endTask()
                let text = self.committed.joined(separator: " ").trimmingCharacters(in: .whitespacesAndNewlines)
                completion(VoiceNotesTranscript(
                    text: text,
                    segments: self.segments,
                    staysOnDevice: true,
                    keptFirstMinuteOnly: false
                ))
            }
        }
    }

    private func openTask() {
        guard !stopped, task == nil else { return }
        guard SFSpeechRecognizer.authorizationStatus() == .authorized else { return }
        let locale = LocalizationManager.shared.speechRecognitionLocale
        guard let selection = SpeechRecognizerFactory.onDeviceOnly(preferred: locale) else {
            onNeedsCloud(currentText())
            return
        }
        recognizer = selection.recognizer
        let request = SFSpeechAudioBufferRecognitionRequest()
        request.shouldReportPartialResults = true
        request.requiresOnDeviceRecognition = true
        request.taskHint = .dictation
        request.contextualStrings = dictionary
        if #available(iOS 16.0, *) {
            request.addsPunctuation = true
        }
        self.request = request
        taskStarted = Date()
        task = selection.recognizer.recognitionTask(with: request) { [weak self] result, error in
            self?.queue.async {
                self?.handle(result: result, error: error)
            }
        }
    }

    private func consume(_ buffer: AVAudioPCMBuffer) {
        guard !stopped else { return }
        if task == nil { openTask() }
        if Date().timeIntervalSince(taskStarted) >= 50 {
            rotate()
        }
        request?.append(buffer)
    }

    private func rotate() {
        overlapTail = wordsTail(partial.isEmpty ? (committed.last ?? "") : partial)
        commitPartial()
        taskOffset += Date().timeIntervalSince(taskStarted)
        endTask()
        openTask()
    }

    private func handle(result: SFSpeechRecognitionResult?, error: Error?) {
        if let error {
            let ns = error as NSError
            if ns.domain == "kAFAssistantErrorDomain", ns.code == 1101 {
                endTask()
                onNeedsCloud(currentText())
                return
            }
            commitPartial()
            return
        }
        guard let result else { return }
        let raw = result.bestTranscription.formattedString
        let text = VoiceNotesTextCleanup.stripOverlap(newText: raw, tail: overlapTail)
        if result.isFinal {
            if !text.isEmpty { committed.append(text) }
            partial = ""
            appendSegments(result.bestTranscription)
        } else {
            partial = text
        }
        onUpdate(currentText())
    }

    private func appendSegments(_ transcription: SFTranscription) {
        for segment in transcription.segments {
            let start = taskOffset + segment.timestamp
            segments.append(VoiceNoteSegment(
                text: segment.substring,
                startSec: start,
                endSec: start + segment.duration
            ))
        }
    }

    private func commitPartial() {
        let text = partial.trimmingCharacters(in: .whitespacesAndNewlines)
        if !text.isEmpty { committed.append(text) }
        partial = ""
    }

    private func endTask() {
        request?.endAudio()
        task?.cancel()
        request = nil
        task = nil
    }

    private func currentText() -> String {
        (committed + [partial]).filter { !$0.isEmpty }.joined(separator: " ")
    }

    private func wordsTail(_ text: String) -> String {
        VoiceNotesTextCleanup.words(text).suffix(8).joined(separator: " ")
    }

    private static func copy(_ buffer: AVAudioPCMBuffer) -> AVAudioPCMBuffer? {
        guard let copy = AVAudioPCMBuffer(pcmFormat: buffer.format, frameCapacity: buffer.frameLength) else { return nil }
        copy.frameLength = buffer.frameLength
        let channels = Int(buffer.format.channelCount)
        if let src = buffer.floatChannelData, let dst = copy.floatChannelData {
            for channel in 0..<channels {
                dst[channel].update(from: src[channel], count: Int(buffer.frameLength))
            }
        } else if let src = buffer.int16ChannelData, let dst = copy.int16ChannelData {
            for channel in 0..<channels {
                dst[channel].update(from: src[channel], count: Int(buffer.frameLength))
            }
        } else {
            return nil
        }
        return copy
    }
}

final class VoiceNotesTranscriptionService {
    /// Finished file on this SDK: one clip, the first minute. No slicing and no glue.
    func transcribeFile(
        url: URL,
        allowCloud: Bool,
        dictionary: [String],
        completion: @escaping (Result<VoiceNotesTranscript, Error>) -> Void
    ) {
        SFSpeechRecognizer.requestAuthorization { [weak self] status in
            guard status == .authorized else {
                completion(.failure(VoiceNotesTranscriptionError.permissionDenied))
                return
            }
            self?.prepareFile(url: url, allowCloud: allowCloud, dictionary: dictionary, completion: completion)
        }
    }

    private func prepareFile(
        url: URL,
        allowCloud: Bool,
        dictionary: [String],
        completion: @escaping (Result<VoiceNotesTranscript, Error>) -> Void
    ) {
        let asset = AVURLAsset(url: url)
        asset.loadValuesAsynchronously(forKeys: ["duration"]) {
            var seconds = CMTimeGetSeconds(asset.duration)
            if !seconds.isFinite || seconds < 0 { seconds = 0 }
            guard seconds > 60 else {
                self.recognize(
                    url: url,
                    allowCloud: allowCloud,
                    dictionary: dictionary,
                    keptFirstMinuteOnly: false,
                    completion: completion
                )
                return
            }
            let output = FileManager.default.temporaryDirectory.appendingPathComponent("voice_note_min_\(UUID().uuidString).m4a")
            guard let export = AVAssetExportSession(asset: asset, presetName: AVAssetExportPresetAppleM4A) else {
                self.recognize(url: url, allowCloud: allowCloud, dictionary: dictionary, keptFirstMinuteOnly: true, completion: completion)
                return
            }
            export.outputURL = output
            export.outputFileType = .m4a
            export.timeRange = CMTimeRange(start: .zero, duration: CMTime(seconds: 60, preferredTimescale: 600))
            export.exportAsynchronously {
                let target = export.status == .completed ? output : url
                self.recognize(
                    url: target,
                    allowCloud: allowCloud,
                    dictionary: dictionary,
                    keptFirstMinuteOnly: true,
                    completion: completion
                )
            }
        }
    }

    private func recognize(
        url: URL,
        allowCloud: Bool,
        dictionary: [String],
        keptFirstMinuteOnly: Bool,
        completion: @escaping (Result<VoiceNotesTranscript, Error>) -> Void
    ) {
        let locale = LocalizationManager.shared.speechRecognitionLocale
        let selection: SpeechRecognizerFactory.Selection?
        if allowCloud {
            selection = SpeechRecognizerFactory.cloudOnly(preferred: locale)
        } else {
            selection = SpeechRecognizerFactory.onDeviceOnly(preferred: locale)
        }
        guard let selection else {
            if allowCloud {
                completion(.failure(VoiceNotesTranscriptionError.recognizerUnavailable))
            } else {
                completion(.failure(VoiceNotesTranscriptionError.needsCloudConsent(partial: "")))
            }
            return
        }

        let request = SFSpeechURLRecognitionRequest(url: url)
        request.shouldReportPartialResults = true
        request.taskHint = .dictation
        request.contextualStrings = Array(dictionary.prefix(VoiceNotesDictionary.maxPhrases))
        if selection.useOnDeviceRecognition {
            request.requiresOnDeviceRecognition = true
        }
        if #available(iOS 16.0, *) {
            request.addsPunctuation = true
        }

        let lock = NSLock()
        var finished = false
        var lastText = ""
        var lastSegments: [VoiceNoteSegment] = []
        func finish(_ result: Result<VoiceNotesTranscript, Error>) {
            lock.lock()
            defer { lock.unlock() }
            guard !finished else { return }
            finished = true
            completion(result)
        }

        let task = selection.recognizer.recognitionTask(with: request) { result, error in
            if let error {
                let ns = error as NSError
                lock.lock()
                let kept = lastText
                let segs = lastSegments
                lock.unlock()
                if !allowCloud && selection.useOnDeviceRecognition && ns.domain == "kAFAssistantErrorDomain" && ns.code == 1101 {
                    finish(.failure(VoiceNotesTranscriptionError.needsCloudConsent(partial: kept)))
                    return
                }
                if !kept.isEmpty {
                    finish(.success(VoiceNotesTranscript(
                        text: kept,
                        segments: segs,
                        staysOnDevice: selection.useOnDeviceRecognition,
                        keptFirstMinuteOnly: keptFirstMinuteOnly
                    )))
                    return
                }
                finish(.failure(VoiceNotesTranscriptionError.failed(error.localizedDescription)))
                return
            }
            guard let result else { return }
            let text = result.bestTranscription.formattedString
            let segments = result.bestTranscription.segments.map { segment in
                VoiceNoteSegment(
                    text: segment.substring,
                    startSec: segment.timestamp,
                    endSec: segment.timestamp + segment.duration
                )
            }
            lock.lock()
            lastText = text
            lastSegments = segments
            lock.unlock()
            if result.isFinal {
                finish(.success(VoiceNotesTranscript(
                    text: text,
                    segments: segments,
                    staysOnDevice: selection.useOnDeviceRecognition,
                    keptFirstMinuteOnly: keptFirstMinuteOnly
                )))
            }
        }

        DispatchQueue.global().asyncAfter(deadline: .now() + 120) {
            lock.lock()
            let done = finished
            let kept = lastText
            let segs = lastSegments
            lock.unlock()
            guard !done else { return }
            task.cancel()
            if !kept.isEmpty {
                finish(.success(VoiceNotesTranscript(
                    text: kept,
                    segments: segs,
                    staysOnDevice: selection.useOnDeviceRecognition,
                    keptFirstMinuteOnly: keptFirstMinuteOnly
                )))
            } else {
                finish(.failure(VoiceNotesTranscriptionError.timedOut))
            }
        }
    }
}
