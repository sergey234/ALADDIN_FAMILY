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

    let mediaKind: AntifakeMediaKind

    private var fileData: Data?
    private let apiService: APIService
    private let localizationManager: LocalizationManager

    private static let pollIntervalNanoseconds: UInt64 = 1_000_000_000
    private static let maxPollAttempts = 30

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
        fileData = data
        selectedFilename = filename
        verdict = nil
        errorMessage = nil
        statusMessage = nil
    }

    func clearSelection() {
        fileData = nil
        selectedFilename = nil
        verdict = nil
        errorMessage = nil
        statusMessage = nil
    }

    func submitCheck() async -> Bool {
        guard AppConfig.authToken != nil else {
            errorMessage = localizationManager.localized("antifake_error_unauthorized")
            return false
        }
        guard let fileData, let selectedFilename else { return false }

        isChecking = true
        errorMessage = nil
        verdict = nil
        requiresPremiumUpgrade = false
        statusMessage = localizationManager.localized("antifake_job_uploading")
        defer {
            isChecking = false
            statusMessage = nil
        }

        do {
            let enqueue = try await uploadMedia(fileData: fileData, filename: selectedFilename)
            let finalVerdict: SecurityVerdict
            switch enqueue {
            case .completed(let verdict):
                finalVerdict = verdict
            case .enqueued(let job):
                statusMessage = localizationManager.localized("antifake_job_analyzing")
                finalVerdict = try await pollUntilComplete(jobId: job.jobId)
            }
            verdict = finalVerdict
            AntifakeHistoryRecorder.record(
                verdict: finalVerdict,
                kind: mediaKind.rawValue,
                summary: selectedFilename ?? mediaKind.rawValue
            )
            return true
        } catch {
            handleCheckError(error)
            return false
        }
    }

    private func uploadMedia(fileData: Data, filename: String) async throws -> AntifakeJobEnqueueResult {
        try await withCheckedThrowingContinuation { continuation in
            apiService.antifakeUploadMedia(
                kind: mediaKind,
                fileData: fileData,
                filename: filename,
                mimeType: Self.mimeType(for: filename, kind: mediaKind),
                extraFormFields: callFormFields()
            ) { result in
                continuation.resume(with: result)
            }
        }
    }

    private func pollUntilComplete(jobId: String) async throws -> SecurityVerdict {
        for _ in 0..<Self.maxPollAttempts {
            let outcome = try await pollJob(jobId: jobId)
            switch outcome {
            case .completed(let verdict):
                return verdict
            case .pending(let pending):
                if pending.status == .failed {
                    throw NetworkError.serviceUnavailable("job_failed")
                }
                try await Task.sleep(nanoseconds: Self.pollIntervalNanoseconds)
            }
        }
        throw NetworkError.timeout
    }

    private func pollJob(jobId: String) async throws -> AntifakeJobPollOutcome {
        try await withCheckedThrowingContinuation { continuation in
            apiService.antifakePollJob(jobId: jobId) { result in
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
}
