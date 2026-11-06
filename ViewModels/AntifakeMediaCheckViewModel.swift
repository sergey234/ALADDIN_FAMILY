import Foundation
import UniformTypeIdentifiers

@MainActor
final class AntifakeMediaCheckViewModel: ObservableObject {

    @Published var selectedFilename: String?
    @Published var verdict: SecurityVerdict?
    @Published var isChecking = false
    @Published var statusMessage: String?
    @Published var errorMessage: String?
    @Published var requiresPremiumUpgrade = false
    @Published var callerId = ""
    @Published var displayName = ""
    @Published var previewURL: URL?
    /// Soft tip after pick (txt / large video) — not a hard block.
    @Published var fileTipMessage: String?

    let mediaKind: AntifakeMediaKind

    private var fileData: Data?
    private var previewTempURL: URL?
    private let apiService: APIService
    private let localizationManager: LocalizationManager
    private var activeCheckTask: Task<Bool, Never>?

    private static let pollIntervalNanoseconds: UInt64 = 1_000_000_000
    private static let softVideoWarnBytes = 12 * 1024 * 1024

    private static let slaSeconds: [AntifakeMediaKind: Int] = [
        .audio: 120,
        .video: 300,
        .call: 180,
        .document: 120
    ]

    /// AG07-A4-3: poll until SLA (not a fixed 30s) so ONNX CPU jobs can finish.
    private var maxPollAttempts: Int {
        Self.slaSeconds[mediaKind] ?? 120
    }

    init(
        mediaKind: AntifakeMediaKind,
        apiService: APIService? = nil,
        localizationManager: LocalizationManager = LocalizationManager()
    ) {
        self.mediaKind = mediaKind
        self.apiService = apiService ?? APIService.shared
        self.localizationManager = localizationManager
    }

    var canSubmit: Bool {
        fileData != nil && !isChecking
    }

    func setSelectedFile(data: Data, filename: String) {
        removePreviewFile()
        fileData = data
        selectedFilename = filename
        verdict = nil
        errorMessage = nil
        statusMessage = nil
        fileTipMessage = tipForSelectedFile(data: data, filename: filename)
        previewURL = writePreviewFile(data: data, filename: filename)
    }

    func clearSelection() {
        cancelCheck()
        removePreviewFile()
        fileData = nil
        selectedFilename = nil
        previewURL = nil
        verdict = nil
        errorMessage = nil
        statusMessage = nil
        fileTipMessage = nil
    }

    /// W1: stop spinner / poll when user taps Cancel.
    func cancelCheck() {
        activeCheckTask?.cancel()
        activeCheckTask = nil
        if isChecking {
            isChecking = false
            statusMessage = nil
            errorMessage = localizationManager.localized("antifake_upload_cancelled")
        }
    }

    @discardableResult
    func submitCheck() async -> Bool {
        activeCheckTask?.cancel()
        let task = Task { @MainActor in
            await self.runCheck()
        }
        activeCheckTask = task
        let ok = await task.value
        if activeCheckTask == task {
            activeCheckTask = nil
        }
        return ok
    }

    private func runCheck() async -> Bool {
        guard AppConfig.authToken != nil else {
            errorMessage = localizationManager.localized("antifake_error_unauthorized")
            return false
        }
        guard let fileData, let selectedFilename else { return false }

        if fileData.count > AntifakeShareConstants.maxDocumentBytes {
            errorMessage = localizationManager.localized("antifake_error_file_too_large")
            return false
        }

        isChecking = true
        errorMessage = nil
        verdict = nil
        requiresPremiumUpgrade = false
        statusMessage = localizationManager.localized("antifake_job_uploading")
        defer {
            if !Task.isCancelled {
                isChecking = false
                statusMessage = nil
            }
        }

        do {
            try Task.checkCancellation()
            let enqueue = try await uploadMedia(fileData: fileData, filename: selectedFilename)
            try Task.checkCancellation()
            let finalVerdict: SecurityVerdict
            switch enqueue {
            case .completed(let verdict):
                finalVerdict = verdict
            case .enqueued(let job):
                statusMessage = slaStatusMessage()
                finalVerdict = try await pollUntilComplete(jobId: job.jobId)
            }
            try Task.checkCancellation()
            verdict = finalVerdict
            AntifakeAnalytics.trackCheckComplete(
                kind: mediaKind.rawValue,
                verdict: finalVerdict.verdict.rawValue,
                source: finalVerdict.source
            )
            AntifakeHistoryRecorder.record(
                verdict: finalVerdict,
                kind: mediaKind.rawValue,
                summary: selectedFilename
            )
            if mediaKind == .call {
                AntifakeLastCallContext.save(callerId: callerId, displayName: displayName)
            }
            return true
        } catch is CancellationError {
            errorMessage = localizationManager.localized("antifake_upload_cancelled")
            isChecking = false
            statusMessage = nil
            return false
        } catch {
            if Task.isCancelled {
                errorMessage = localizationManager.localized("antifake_upload_cancelled")
                isChecking = false
                statusMessage = nil
                return false
            }
            handleCheckError(error)
            return false
        }
    }

    private func tipForSelectedFile(data: Data, filename: String) -> String? {
        let ext = (filename as NSString).pathExtension.lowercased()
        if mediaKind == .document, ["txt", "rtf", "text"].contains(ext) {
            return localizationManager.localized("antifake_doc_prefer_photo")
        }
        if mediaKind == .video, data.count >= Self.softVideoWarnBytes {
            return localizationManager.localized("antifake_video_size_hint")
        }
        return nil
    }

    private func slaStatusMessage() -> String {
        let seconds = Self.slaSeconds[mediaKind] ?? 120
        let template = localizationManager.localized("antifake_job_analyzing_sla")
        return String(format: template, locale: localizationManager.locale, "\(seconds)")
    }

    private func uploadMedia(fileData: Data, filename: String) async throws -> AntifakeJobEnqueueResult {
        try await withCheckedThrowingContinuation { continuation in
            var resumed = false
            apiService.antifakeUploadMedia(
                kind: mediaKind,
                fileData: fileData,
                filename: filename,
                mimeType: Self.mimeType(for: filename, kind: mediaKind),
                extraFormFields: callFormFields()
            ) { result in
                guard !resumed else { return }
                resumed = true
                continuation.resume(with: result)
            }
        }
    }

    private func pollUntilComplete(jobId: String) async throws -> SecurityVerdict {
        for _ in 0..<maxPollAttempts {
            try Task.checkCancellation()
            let outcome = try await pollJob(jobId: jobId)
            switch outcome {
            case .completed(let verdict):
                return verdict
            case .pending(let pending):
                if pending.status == .failed {
                    throw NetworkError.serviceUnavailable("job_failed")
                }
                statusMessage = slaStatusMessage()
                try await Task.sleep(nanoseconds: Self.pollIntervalNanoseconds)
            }
        }
        throw NetworkError.timeout
    }

    private func pollJob(jobId: String) async throws -> AntifakeJobPollOutcome {
        try await withCheckedThrowingContinuation { continuation in
            var resumed = false
            apiService.antifakePollJob(jobId: jobId) { result in
                guard !resumed else { return }
                resumed = true
                continuation.resume(with: result)
            }
        }
    }

    private func handleCheckError(_ error: Error) {
        let presentation = AntifakeCheckFailureHandler.present(
            error: error,
            localizationManager: localizationManager
        )
        requiresPremiumUpgrade = presentation.requiresPremiumUpgrade
        errorMessage = presentation.errorMessage
    }

    private func callFormFields() -> [String: String]? {
        guard mediaKind == .call else { return nil }
        var fields: [String: String] = [:]
        let cid = callerId.trimmingCharacters(in: .whitespacesAndNewlines)
        let name = displayName.trimmingCharacters(in: .whitespacesAndNewlines)
        if !cid.isEmpty { fields["caller_id"] = cid }
        if !name.isEmpty { fields["display_name"] = name }
        return fields.isEmpty ? nil : fields
    }

    static func allowedContentTypes(for kind: AntifakeMediaKind) -> [UTType] {
        switch kind {
        case .audio, .call:
            return [.audio, .mpeg4Audio, .mp3, .wav, .aiff]
        case .video:
            return [.movie, .mpeg4Movie, .quickTimeMovie, .video]
        case .document:
            // Prefer photo/PDF in picker order; keep plainText but tip warns (W1 Q28).
            return [.pdf, .image, .jpeg, .png, .heic, .plainText, .rtf]
        }
    }

    static func mimeType(for filename: String, kind: AntifakeMediaKind) -> String {
        let ext = (filename as NSString).pathExtension.lowercased()
        switch ext {
        case "mp3": return "audio/mpeg"
        case "m4a", "aac": return "audio/mp4"
        case "wav": return "audio/wav"
        case "mp4", "m4v": return "video/mp4"
        case "mov": return "video/quicktime"
        case "pdf": return "application/pdf"
        case "jpg", "jpeg": return "image/jpeg"
        case "png": return "image/png"
        case "heic": return "image/heic"
        case "txt": return "text/plain"
        default:
            switch kind {
            case .audio, .call: return "audio/mpeg"
            case .video: return "video/mp4"
            case .document: return "application/octet-stream"
            }
        }
    }

    private func writePreviewFile(data: Data, filename: String) -> URL? {
        let ext = (filename as NSString).pathExtension.lowercased()
        let isDocumentImage = mediaKind == .document
            && ["jpg", "jpeg", "png", "heic", "webp"].contains(ext)
        guard mediaKind == .audio || mediaKind == .video || mediaKind == .call || isDocumentImage else {
            return nil
        }
        let safeExt = ext.isEmpty ? "bin" : ext
        let url = FileManager.default.temporaryDirectory
            .appendingPathComponent("antifake_preview_\(UUID().uuidString).\(safeExt)")
        do {
            try data.write(to: url, options: .atomic)
            previewTempURL = url
            return url
        } catch {
            return nil
        }
    }

    private func removePreviewFile() {
        if let url = previewTempURL {
            try? FileManager.default.removeItem(at: url)
        }
        previewTempURL = nil
    }
}
