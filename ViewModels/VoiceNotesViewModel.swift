import Foundation
import SwiftUI
import UIKit
import AVFoundation
import Speech

@MainActor
final class VoiceNotesViewModel: ObservableObject {
    static let maxRecordingDurationSec = 600
    static let recordingWarningBeforeEndSec = 30

    enum RecordingState: String {
        case idle
        case recording
        case paused
        case processing
        case saved
        case failed
    }

    struct VoiceNoteItem: Identifiable {
        let id: UUID
        var title: String
        let createdAt: Date
        var durationSec: Int
        var transcriptPreview: String
        var summary: String
        var summaryConfidence: Double
        var summaryVersion: Int
        var tags: [String]
        var audioPath: String
        var segments: [VoiceNoteSegment] = []
        var sourceTranscript: String = ""
        var keptFirstMinuteOnly: Bool = false
    }
    
    enum NotesFilter: String, CaseIterable {
        case all
        case today
        case yesterday
        case projects
        case ideas
        case reminds

        var titleKey: String {
            switch self {
            case .all: return "voice_notes_filter_all"
            case .today: return "voice_notes_section_today"
            case .yesterday: return "voice_notes_section_yesterday"
            case .projects: return "voice_notes_section_projects"
            case .ideas: return "voice_notes_section_ideas"
            case .reminds: return "voice_notes_section_reminds"
            }
        }
    }

    @Published var recordingState: RecordingState = .idle
    @Published var elapsedSec: Int = 0
    @Published var currentStatusText: String = ""
    @Published var noiseLevel: Double = 0.0
    @Published var notes: [VoiceNoteItem] = []
    @Published var canUndoDelete: Bool = false
    @Published var localOnlyModeEnabled: Bool = true
    @Published var liveTranscript: String = ""
    @Published var speechUsesAppleCloud = false
    @Published var showCloudConsent = false
    @Published var showPresetConsent = false
    @Published var dictionaryPhrases: [String] = []
    @Published var longFileNotice = false
    @Published var speechSiteLink = false
    @Published var showImporter = false
    @Published var presetStructure: VoiceNotesStructureResult?
    private var pendingCloudNoteId: UUID?
    private var sendCurrentRecordingToApple = false
    private var pendingPreset: PendingPreset?
    private var presetContinuation: (() -> Void)?
    private var liveTranscriber: VoiceNotesLiveTranscriber?
    private let speaker = AVSpeechSynthesizer()

    private enum PendingPreset {
        case family(UUID)
        case minutes(UUID)
    }
    @Published var searchText: String = ""
    @Published var activeFilter: NotesFilter = .all
    @Published var showMicPermissionAlert = false
    @Published var showSpeechPermissionAlert = false
    @Published var isSpeechTranscriptionAvailable = true
    @Published var showNearLimitWarning = false
    /// VSL-C: after leading intent parse, host should dismiss sheet then open Antifake.
    @Published var pendingAntifakeFromVoice: AntifakeSharePayload?
    /// VSL-C: optional status navigation after «статус».
    @Published var pendingStatusNavigation = false

    private static let routerEnabledKey = "voiceIntentRouterEnabled"
    private static let presetConsentKey = "voice_notes_preset_network_allowed"

    private let recorderService = VoiceNotesRecorderService()
    private let transcriptionService = VoiceNotesTranscriptionService()
    private let summaryService = VoiceNotesSummaryService()
    private let store = VoiceNotesStore()
    private var startTappedAt: Date?
    private var feedbackLogged = false
    private var timer: Timer?
    private var recordingStartedAt: Date?
    private var pendingDeleteNote: VoiceNoteItem?
    private var pendingDeleteTimer: Timer?
    private var recordingURL: URL?

    init() {
        recorderService.onInterruptedAndAutoSaved = { [weak self] in
            guard let self else { return }
            Task { @MainActor in
                self.autosaveAfterInterruption()
            }
        }
        recorderService.onAudioLevel = { [weak self] level in
            guard let self else { return }
            Task { @MainActor in
                let normalized = AudioLevelMeter.normalizedLevel(fromAveragePower: level)
                self.noiseLevel = normalized.isFinite ? normalized : 0
            }
        }
        loadNotes()
        dictionaryPhrases = VoiceNotesDictionary.load()
        speechUsesAppleCloud = false
    }

    deinit {
        timer?.invalidate()
        pendingDeleteTimer?.invalidate()
    }

    var groupedNotes: [(titleKey: String, items: [VoiceNoteItem])] {
        let calendar = Calendar.current
        let now = Date()
        let filteredBase = notes.filter { note in
            guard !searchText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return true }
            let q = searchText.lowercased()
            return note.title.lowercased().contains(q)
                || note.transcriptPreview.lowercased().contains(q)
                || note.summary.lowercased().contains(q)
                || note.tags.joined(separator: " ").lowercased().contains(q)
        }
        let today = filteredBase.filter { calendar.isDate($0.createdAt, inSameDayAs: now) }
        let yesterday = filteredBase.filter {
            guard let day = calendar.date(byAdding: .day, value: -1, to: now) else { return false }
            return calendar.isDate($0.createdAt, inSameDayAs: day)
        }
        let older = filteredBase.filter { note in
            !today.contains(where: { $0.id == note.id }) && !yesterday.contains(where: { $0.id == note.id })
        }

        var result: [(String, [VoiceNoteItem])] = []
        switch activeFilter {
        case .all:
            if !today.isEmpty { result.append(("voice_notes_section_today", today)) }
            if !yesterday.isEmpty { result.append(("voice_notes_section_yesterday", yesterday)) }
            if !older.isEmpty { result.append(("voice_notes_section_projects", older)) }
        case .today:
            if !today.isEmpty { result.append(("voice_notes_section_today", today)) }
        case .yesterday:
            if !yesterday.isEmpty { result.append(("voice_notes_section_yesterday", yesterday)) }
        case .projects:
            if !older.isEmpty { result.append(("voice_notes_section_projects", older)) }
        case .ideas:
            let ideas = filteredBase.filter { $0.tags.contains("intent_idea") }
            if !ideas.isEmpty { result.append(("voice_notes_section_ideas", ideas)) }
        case .reminds:
            let reminds = filteredBase.filter { $0.tags.contains("intent_remind") }
            if !reminds.isEmpty { result.append(("voice_notes_section_reminds", reminds)) }
        }
        return result
    }

    func startRecording() {
        guard recordingState != .recording else { return }
        showNearLimitWarning = false

        let session = AVAudioSession.sharedInstance()
        switch session.recordPermission {
        case .granted:
            beginRecordingAfterPermission()
        case .denied:
            showMicPermissionAlert = true
            recordingState = .failed
            currentStatusText = "voice_notes_mic_permission_denied"
        case .undetermined:
            session.requestRecordPermission { [weak self] granted in
                Task { @MainActor in
                    guard let self else { return }
                    if granted {
                        self.beginRecordingAfterPermission()
                    } else {
                        self.showMicPermissionAlert = true
                        self.recordingState = .failed
                        self.currentStatusText = "voice_notes_mic_permission_denied"
                    }
                }
            }
        @unknown default:
            showMicPermissionAlert = true
        }
    }

    private func beginRecordingAfterPermission() {
        MasterLogger.shared.business("🎙️ VoiceNotes: Recording started")
        speechSiteLink = false
        recordingState = .recording
        currentStatusText = "voice_notes_status_listening"
        feedbackLogged = false
        startTappedAt = Date()
        do {
            recorderService.onBuffer = { [weak self] buffer in
                self?.liveTranscriber?.append(buffer)
            }
            let url = try recorderService.start()
            recordingURL = url
            recordingStartedAt = Date()
            liveTranscript = ""
            startLiveTranscription()
        } catch {
            recordingState = .failed
            currentStatusText = "voice_notes_session_busy"
            return
        }
        track(action: "voice_record_start_success_rate")
        HapticFeedback.impact(.medium)
        startTimer()
        logTimeToFirstFeedbackIfNeeded()
    }

    func pauseRecording() {
        guard recordingState == .recording else { return }
        recordingState = .paused
        currentStatusText = "voice_notes_status_paused"
        recorderService.pause()
        liveTranscriber?.pause()
        stopTimer()
    }

    func resumeRecording() {
        guard recordingState == .paused else { return }
        recordingState = .recording
        currentStatusText = "voice_notes_status_listening"
        recorderService.resume()
        liveTranscriber?.resume()
        startTimer()
    }

    func stopAndSaveRecording() {
        guard recordingState == .recording || recordingState == .paused else { return }
        MasterLogger.shared.business("🎙️ VoiceNotes: Stop & save (elapsed \(elapsedSec)s)")
        recordingState = .processing
        currentStatusText = "voice_notes_status_processing"
        stopTimer()
        recorderService.onBuffer = nil
        let finishedURL = recorderService.stop() ?? recordingURL
        let elapsedFromService = Int((recordingStartedAt.map { Date().timeIntervalSince($0) } ?? 0).rounded())
        let duration = max(max(elapsedSec, elapsedFromService), 1)
        let noteId = UUID()
        let transcriber = liveTranscriber
        liveTranscriber = nil
        recordingStartedAt = nil
        recordingURL = nil
        elapsedSec = 0
        noiseLevel = 0.0

        func save(transcript: VoiceNotesTranscript) {
            let text = transcript.text.trimmingCharacters(in: .whitespacesAndNewlines)
            let preview = text.isEmpty ? "voice_notes_transcript_pending" : text
            let newNote = VoiceNoteItem(
                id: noteId,
                title: generatedTitle(for: Date()),
                createdAt: Date(),
                durationSec: duration,
                transcriptPreview: preview,
                summary: "",
                summaryConfidence: 0.0,
                summaryVersion: 0,
                tags: [],
                audioPath: finishedURL?.path ?? "",
                segments: transcript.segments,
                sourceTranscript: text,
                keptFirstMinuteOnly: transcript.keptFirstMinuteOnly
            )
            notes.insert(newNote, at: 0)
            persistNotes()
            showRecordingSavedToast(path: finishedURL?.path ?? "")
            HapticFeedback.impact(.light)
            recordingState = .saved
            currentStatusText = "voice_notes_status_saved"
            liveTranscript = ""
            let sendToApple = sendCurrentRecordingToApple
            sendCurrentRecordingToApple = false
            if text.isEmpty {
                runFileTranscription(noteId: noteId, localURL: finishedURL, allowCloud: sendToApple)
            }
        }

        if let transcriber {
            transcriber.finish { transcript in
                Task { @MainActor in
                    save(transcript: transcript)
                }
            }
        } else {
            save(transcript: VoiceNotesTranscript(text: liveTranscript, segments: [], staysOnDevice: true, keptFirstMinuteOnly: false))
        }
    }

    func markInterruption() {
        track(action: "voice_record_interruption_rate")
    }

    func markTranscriptionResult(success: Bool, empty: Bool) {
        if success { track(action: "transcription_success_rate") }
        if empty { track(action: "empty_result_rate") }
    }

    func markSummaryGeneration(success: Bool) {
        if success { track(action: "summary_generation_success_rate") }
    }

    func markVoiceSessionStable() {
        track(action: "crash_free_sessions_voice")
        refreshSpeechAvailability()
        ensureSpeechAuthorizationForTranscription()
    }

    func refreshSpeechAvailability() {
        let locale = LocalizationManager.shared.speechRecognitionLocale
        isSpeechTranscriptionAvailable = SpeechRecognizerFactory.isSpeechInputAvailable(preferred: locale)
    }

    func ensureSpeechAuthorizationForTranscription() {
        switch SFSpeechRecognizer.authorizationStatus() {
        case .authorized:
            break
        case .denied, .restricted:
            showSpeechPermissionAlert = true
        case .notDetermined:
            SFSpeechRecognizer.requestAuthorization { [weak self] status in
                Task { @MainActor in
                    guard let self else { return }
                    if status != .authorized {
                        self.showSpeechPermissionAlert = true
                    }
                    self.refreshSpeechAvailability()
                }
            }
        @unknown default:
            showSpeechPermissionAlert = true
        }
    }

    func requestDelete(note: VoiceNoteItem) {
        notes.removeAll { $0.id == note.id }
        persistNotes()
        pendingDeleteNote = note
        canUndoDelete = true
        pendingDeleteTimer?.invalidate()
        pendingDeleteTimer = Timer.scheduledTimer(withTimeInterval: 5.0, repeats: false) { [weak self] _ in
            guard let self else { return }
            Task { @MainActor in
                self.finalizeDelete()
            }
        }
    }

    func undoDelete() {
        guard let note = pendingDeleteNote else { return }
        notes.insert(note, at: 0)
        persistNotes()
        pendingDeleteNote = nil
        canUndoDelete = false
        pendingDeleteTimer?.invalidate()
    }
    
    func renameNote(noteId: UUID, to newTitle: String) {
        let trimmed = newTitle.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty, let idx = notes.firstIndex(where: { $0.id == noteId }) else { return }
        notes[idx].title = trimmed
        persistNotes()
    }

    func generateSummary(noteId: UUID, forceRegenerate: Bool = false) {
        guard let idx = notes.firstIndex(where: { $0.id == noteId }) else { return }
        if !forceRegenerate && !notes[idx].summary.isEmpty { return }
        let result = summaryService.summarize(
            transcript: notes[idx].transcriptPreview,
            title: notes[idx].title,
            previousVersion: notes[idx].summaryVersion
        )
        notes[idx].summary = result.text
        notes[idx].summaryConfidence = result.confidence
        notes[idx].summaryVersion = result.version
        if !result.suggestedTags.isEmpty {
            let intentTags = notes[idx].tags.filter { $0.hasPrefix("intent_") }
            let merged = Array(Set(notes[idx].tags + result.suggestedTags)).sorted()
            // A12: never drop intent_* tags when summary suggests others.
            notes[idx].tags = Array(Set(merged + intentTags)).sorted()
        }
        persistNotes()
        markSummaryGeneration(success: true)
    }

    /// VSL-C: leading-word router after STT. Keeps full transcript; merges intent tag.
    private func applyVoiceIntentRouting(noteIndex idx: Int, transcript: String) {
        let enabled = UserDefaults.standard.object(forKey: Self.routerEnabledKey) as? Bool ?? true
        guard enabled else { return }

        let parsed = VoiceIntentRouter.parse(transcript)
        notes[idx].tags = Array(Set(notes[idx].tags + [parsed.intentTag])).sorted()
        VoiceSafetyNowStore.save(
            intentTag: parsed.intentTag,
            detail: parsed.remainder.isEmpty ? parsed.fullTranscript : parsed.remainder
        )

        switch parsed.intent {
        case .antifakeURL, .securityCheck:
            pendingAntifakeFromVoice = Self.makeAntifakePayload(from: parsed)
        case .status:
            pendingStatusNavigation = true
        case .remind:
            VoiceRemindScheduler.schedule(
                fromRemainder: parsed.remainder.isEmpty ? parsed.fullTranscript : parsed.remainder,
                noteId: notes[idx].id
            )
        case .incident, .idea, .breakSegment, .note:
            break
        }
    }

    /// VSL-C P2 — weekly digest from local notes (last 7 days).
    func makeWeeklyDigest() -> VoiceWeeklyDigestResult {
        let stored = notes.map {
            VoiceNotesStore.StoredVoiceNote(
                id: $0.id,
                title: $0.title,
                createdAt: $0.createdAt,
                durationSec: $0.durationSec,
                transcriptPreview: $0.transcriptPreview,
                summary: $0.summary,
                summaryConfidence: $0.summaryConfidence,
                summaryVersion: $0.summaryVersion,
                tags: $0.tags,
                audioPath: $0.audioPath
            )
        }
        return VoiceWeeklyDigestService.build(notes: stored)
    }

    /// Real users say «ссылка» / «проверка», not «https://…».
    /// Prefer spoken URL/text; if none — take **copied** link/text from clipboard (on-demand).
    private static func makeAntifakePayload(from parsed: VoiceIntentRouter.Result) -> AntifakeSharePayload {
        let spoken = parsed.antifakePrefill
        if let url = AntifakeTextInputClassifier.extractURL(from: spoken) {
            return AntifakeSharePayload(mode: .url, value: url, createdAt: Date())
        }
        if !spoken.isEmpty, parsed.intent == .securityCheck {
            return AntifakeSharePayload(mode: .text, value: spoken, createdAt: Date())
        }

        // Clipboard fallback (user already copied a suspicious link)
        if let clip = UIPasteboard.general.string?
            .trimmingCharacters(in: .whitespacesAndNewlines),
           !clip.isEmpty {
            switch ClipboardSafetyService.process(clip) {
            case .ok(let cleaned) where !cleaned.isEmpty:
                if AntifakeTextInputClassifier.extractURL(from: cleaned) != nil
                    || AntifakeTextInputClassifier.looksLikeURL(cleaned) {
                    return AntifakeSharePayload(mode: .url, value: cleaned, createdAt: Date())
                }
                return AntifakeSharePayload(mode: .text, value: cleaned, createdAt: Date())
            case .blockedSecret, .ok:
                break
            }
        }

        // Open Antifake empty — user can paste manually
        return AntifakeSharePayload(mode: .url, value: "", createdAt: Date())
    }

    func consumePendingAntifakeFromVoice() -> AntifakeSharePayload? {
        let payload = pendingAntifakeFromVoice
        pendingAntifakeFromVoice = nil
        return payload
    }

    func consumePendingStatusNavigation() -> Bool {
        let flag = pendingStatusNavigation
        pendingStatusNavigation = false
        return flag
    }

    func updateSummary(noteId: UUID, summary: String, confidence: Double?) {
        guard let idx = notes.firstIndex(where: { $0.id == noteId }) else { return }
        let trimmed = summary.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        notes[idx].summary = trimmed
        notes[idx].summaryVersion = max(1, notes[idx].summaryVersion + 1)
        if let confidence {
            notes[idx].summaryConfidence = min(max(confidence, 0), 1)
        }
        persistNotes()
    }

    func createCallAssistantNote(goal: String, postCallNote: String, outcomes: String) {
        let goalText = goal.trimmingCharacters(in: .whitespacesAndNewlines)
        let postText = postCallNote.trimmingCharacters(in: .whitespacesAndNewlines)
        let outcomeText = outcomes.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !goalText.isEmpty || !postText.isEmpty || !outcomeText.isEmpty else { return }

        let transcript = [
            "Goal: \(goalText.isEmpty ? "-" : goalText)",
            "Post-call note: \(postText.isEmpty ? "-" : postText)",
            "Outcome: \(outcomeText.isEmpty ? "-" : outcomeText)"
        ].joined(separator: "\n")
        let result = summaryService.summarize(transcript: transcript, title: "Call Assistant", previousVersion: 0)

        let note = VoiceNoteItem(
            id: UUID(),
            title: "Call Assistant • \(generatedTitle(for: Date()))",
            createdAt: Date(),
            durationSec: 0,
            transcriptPreview: transcript,
            summary: result.text,
            summaryConfidence: result.confidence,
            summaryVersion: result.version,
            tags: Array(Set(["call_assistant"] + result.suggestedTags)).sorted(),
            audioPath: ""
        )
        notes.insert(note, at: 0)
        persistNotes()
        ToastManager.shared.showSuccess(
            LocalizationManager.shared.localized("call_assistant_toast_saved")
        )
    }

    private func showRecordingSavedToast(path: String) {
        guard !path.isEmpty else { return }
        let fileName = URL(fileURLWithPath: path).lastPathComponent
        let message = LocalizationManager.shared.localized("voice_notes_toast_saved", fileName)
        ToastManager.shared.showSuccess(message)
    }

    private func finalizeDelete() {
        guard let note = pendingDeleteNote else { return }
        store.deleteAudioIfExists(path: note.audioPath)
        pendingDeleteNote = nil
        canUndoDelete = false
    }

    private func startTimer() {
        timer?.invalidate()
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            guard let self else { return }
            Task { @MainActor in
                self.elapsedSec += 1
                let remaining = Self.maxRecordingDurationSec - self.elapsedSec
                if remaining == Self.recordingWarningBeforeEndSec {
                    self.showNearLimitWarning = true
                    self.currentStatusText = "voice_notes_limit_warning"
                }
                if self.elapsedSec >= Self.maxRecordingDurationSec {
                    self.stopAndSaveRecording()
                }
            }
        }
    }

    private func stopTimer() {
        timer?.invalidate()
        timer = nil
    }

    private func logTimeToFirstFeedbackIfNeeded() {
        guard !feedbackLogged, let startedAt = startTappedAt else { return }
        feedbackLogged = true
        _ = Int(Date().timeIntervalSince(startedAt) * 1000)
        // Local-only privacy: do not send timing metrics to backend.
    }

    private func track(action: String) {
        // Local-only privacy: no outbound metric events from Voice Notes.
        _ = action
    }

    private func loadNotes() {
        let stored = store.load()
        notes = stored.map {
            VoiceNoteItem(
                id: $0.id,
                title: $0.title,
                createdAt: $0.createdAt,
                durationSec: $0.durationSec,
                transcriptPreview: $0.transcriptPreview,
                summary: $0.summary,
                summaryConfidence: $0.summaryConfidence,
                summaryVersion: $0.summaryVersion,
                tags: $0.tags,
                audioPath: $0.audioPath,
                segments: $0.segments,
                sourceTranscript: $0.sourceTranscript,
                keptFirstMinuteOnly: $0.keptFirstMinuteOnly
            )
        }
    }

    private func persistNotes() {
        let payload = notes.map {
            VoiceNotesStore.StoredVoiceNote(
                id: $0.id,
                title: $0.title,
                createdAt: $0.createdAt,
                durationSec: $0.durationSec,
                transcriptPreview: $0.transcriptPreview,
                summary: $0.summary,
                summaryConfidence: $0.summaryConfidence,
                summaryVersion: $0.summaryVersion,
                tags: $0.tags,
                audioPath: $0.audioPath,
                segments: $0.segments,
                sourceTranscript: $0.sourceTranscript,
                keptFirstMinuteOnly: $0.keptFirstMinuteOnly
            )
        }
        store.save(payload)
    }

    private func generatedTitle(for date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd HH:mm"
        return "Voice Note • \(formatter.string(from: date))"
    }

    var allowsCloudPresets: Bool { !CompanionUserContext.isChildProfile }
    var presetNetworkAllowed: Bool {
        UserDefaults.standard.bool(forKey: Self.presetConsentKey)
    }

    var speechBannerKey: String {
        speechUsesAppleCloud ? "voice_notes_banner_cloud" : "voice_notes_banner_on_device"
    }

    func addDictionaryPhrase(_ phrase: String) {
        dictionaryPhrases.append(phrase)
        VoiceNotesDictionary.save(dictionaryPhrases)
        dictionaryPhrases = VoiceNotesDictionary.load()
    }

    func removeDictionaryPhrase(at index: Int) {
        guard dictionaryPhrases.indices.contains(index) else { return }
        dictionaryPhrases.remove(at: index)
        VoiceNotesDictionary.save(dictionaryPhrases)
    }

    func applyCleaner(noteId: UUID) {
        guard let idx = notes.firstIndex(where: { $0.id == noteId }) else { return }
        rememberSource(at: idx)
        notes[idx].transcriptPreview = VoiceNotesTextCleanup.cleaner(notes[idx].sourceTranscript)
        persistNotes()
    }

    func applyClear(noteId: UUID) {
        guard let idx = notes.firstIndex(where: { $0.id == noteId }) else { return }
        rememberSource(at: idx)
        notes[idx].transcriptPreview = VoiceNotesTextCleanup.makeClear(notes[idx].sourceTranscript)
        persistNotes()
    }

    func requestFamily(noteId: UUID) {
        requestNetworkPreset(.family(noteId))
    }

    func requestMinutes(noteId: UUID) {
        requestNetworkPreset(.minutes(noteId))
    }

    func confirmPresetNetwork() {
        UserDefaults.standard.set(true, forKey: Self.presetConsentKey)
        showPresetConsent = false
        let continuation = presetContinuation
        presetContinuation = nil
        if let pending = pendingPreset {
            pendingPreset = nil
            switch pending {
            case .family(let id):
                runPreset(noteId: id, showPolite: true)
            case .minutes(let id):
                runPreset(noteId: id, showPolite: false)
            }
        }
        continuation?()
    }

    func performIfPresetAllowed(_ action: @escaping () -> Void) {
        guard allowsCloudPresets else { return }
        if UserDefaults.standard.bool(forKey: Self.presetConsentKey) {
            action()
            return
        }
        presetContinuation = action
        showPresetConsent = true
    }

    func restoreSource(noteId: UUID) {
        guard let idx = notes.firstIndex(where: { $0.id == noteId }) else { return }
        let source = notes[idx].sourceTranscript
        guard !source.isEmpty else { return }
        notes[idx].transcriptPreview = source
        persistNotes()
    }

    func speak(noteId: UUID) {
        guard let note = notes.first(where: { $0.id == noteId }) else { return }
        let text = readableText(note)
        guard !text.isEmpty else { return }
        speaker.stopSpeaking(at: .immediate)
        let locale = LocalizationManager.shared.speechRecognitionLocale.identifier
        for sentence in VoiceNotesTextCleanup.splitSentences(text) {
            let utterance = AVSpeechUtterance(string: sentence)
            utterance.voice = AVSpeechSynthesisVoice(language: locale)
            speaker.speak(utterance)
        }
    }

    func allowAppleCloudAndRetry() {
        speechUsesAppleCloud = true
        showCloudConsent = false
        if let id = pendingCloudNoteId,
           let note = notes.first(where: { $0.id == id }),
           !note.audioPath.isEmpty {
            pendingCloudNoteId = nil
            runFileTranscription(noteId: id, localURL: URL(fileURLWithPath: note.audioPath), allowCloud: true)
            return
        }
        sendCurrentRecordingToApple = true
    }

    func importRecording(url: URL) {
        let ext = url.pathExtension.lowercased()
        if ext == "mkv" {
            longFileNotice = false
            speechSiteLink = allowsCloudPresets
            currentStatusText = allowsCloudPresets ? "voice_notes_mkv_wait" : "voice_notes_mkv_phone"
            return
        }
        speechSiteLink = false
        let allowed: Set<String> = ["mp3", "m4a", "wav", "flac", "mp4", "mov"]
        guard allowed.contains(ext) else {
            currentStatusText = "voice_notes_import_unsupported"
            return
        }
        let accessed = url.startAccessingSecurityScopedResource()
        defer { if accessed { url.stopAccessingSecurityScopedResource() } }
        let dir = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let dest = dir.appendingPathComponent("voice_note_\(UUID().uuidString).\(ext)")
        do {
            if FileManager.default.fileExists(atPath: dest.path) {
                try FileManager.default.removeItem(at: dest)
            }
            try FileManager.default.copyItem(at: url, to: dest)
        } catch {
            currentStatusText = "voice_notes_import_unsupported"
            return
        }
        let note = VoiceNoteItem(
            id: UUID(),
            title: generatedTitle(for: Date()),
            createdAt: Date(),
            durationSec: 1,
            transcriptPreview: "voice_notes_transcript_pending",
            summary: "",
            summaryConfidence: 0,
            summaryVersion: 0,
            tags: ["imported"],
            audioPath: dest.path
        )
        notes.insert(note, at: 0)
        persistNotes()
        runFileTranscription(noteId: note.id, localURL: dest, allowCloud: false)
    }

    private func startLiveTranscription() {
        let live = VoiceNotesLiveTranscriber(
            dictionary: dictionaryPhrases,
            onUpdate: { [weak self] text in
                Task { @MainActor in
                    self?.liveTranscript = text
                }
            },
            onNeedsCloud: { [weak self] partial in
                Task { @MainActor in
                    guard let self else { return }
                    if !partial.isEmpty { self.liveTranscript = partial }
                    if self.allowsCloudPresets {
                        self.showCloudConsent = true
                    } else {
                        self.currentStatusText = "voice_notes_language_missing"
                    }
                }
            }
        )
        liveTranscriber = live
        if SFSpeechRecognizer.authorizationStatus() == .authorized {
            live.start()
            return
        }
        SFSpeechRecognizer.requestAuthorization { [weak self] status in
            Task { @MainActor in
                guard let self else { return }
                if status == .authorized {
                    self.liveTranscriber?.start()
                } else {
                    self.showSpeechPermissionAlert = true
                }
            }
        }
    }

    private func requestNetworkPreset(_ preset: PendingPreset) {
        guard allowsCloudPresets else { return }
        if UserDefaults.standard.bool(forKey: Self.presetConsentKey) {
            pendingPreset = preset
            confirmPresetNetwork()
            return
        }
        pendingPreset = preset
        showPresetConsent = true
    }

    private func runPreset(noteId: UUID, showPolite: Bool) {
        guard let note = notes.first(where: { $0.id == noteId }) else { return }
        let text = readableText(note)
        guard !text.isEmpty else { return }
        Task { @MainActor in
            do {
                let result = try await VoiceNotesStructureService.structure(transcript: text)
                guard let idx = self.notes.firstIndex(where: { $0.id == noteId }) else { return }
                self.rememberSource(at: idx)
                if showPolite, !result.polite.isEmpty {
                    self.notes[idx].transcriptPreview = result.polite
                }
                self.presetStructure = result
                self.persistNotes()
            } catch {
                self.currentStatusText = "voice_structure_soft_fail"
            }
        }
    }

    private func rememberSource(at index: Int) {
        if notes[index].sourceTranscript.isEmpty {
            let current = notes[index].transcriptPreview
            if !current.hasPrefix("voice_notes_"), !current.hasPrefix("ai_assistant_") {
                notes[index].sourceTranscript = current
            }
        }
    }

    private func readableText(_ note: VoiceNoteItem) -> String {
        let raw = note.transcriptPreview
        if raw.hasPrefix("voice_notes_") || raw.hasPrefix("ai_assistant_") || raw.isEmpty {
            return note.sourceTranscript
        }
        return raw
    }

    private func runFileTranscription(noteId: UUID, localURL: URL?, allowCloud: Bool) {
        guard let localURL else { return }
        if allowCloud { speechUsesAppleCloud = true }
        transcriptionService.transcribeFile(
            url: localURL,
            allowCloud: allowCloud,
            dictionary: dictionaryPhrases
        ) { [weak self] result in
            guard let self else { return }
            Task { @MainActor in
                self.applyFileResult(noteId: noteId, result: result, url: localURL)
            }
        }
    }

    private func applyFileResult(noteId: UUID, result: Result<VoiceNotesTranscript, Error>, url: URL) {
        guard let idx = notes.firstIndex(where: { $0.id == noteId }) else { return }
        switch result {
        case .success(let transcript):
            let text = transcript.text.trimmingCharacters(in: .whitespacesAndNewlines)
            notes[idx].transcriptPreview = text.isEmpty ? "ai_assistant_voice_empty_result" : text
            notes[idx].sourceTranscript = text
            notes[idx].segments = transcript.segments
            notes[idx].keptFirstMinuteOnly = transcript.keptFirstMinuteOnly
            longFileNotice = transcript.keptFirstMinuteOnly
            speechSiteLink = false
            speechUsesAppleCloud = !transcript.staysOnDevice
            if !text.isEmpty {
                applyVoiceIntentRouting(noteIndex: idx, transcript: text)
            }
            markTranscriptionResult(success: !text.isEmpty, empty: text.isEmpty)
        case .failure(let error):
            if case VoiceNotesTranscriptionError.needsCloudConsent(let partial) = error {
                if !partial.isEmpty {
                    notes[idx].transcriptPreview = partial
                    notes[idx].sourceTranscript = partial
                } else {
                    notes[idx].transcriptPreview = "voice_notes_language_missing"
                }
                if allowsCloudPresets {
                    pendingCloudNoteId = noteId
                    showCloudConsent = true
                }
            } else if let e = error as? VoiceNotesTranscriptionError {
                switch e {
                case .permissionDenied:
                    notes[idx].transcriptPreview = "voice_notes_transcript_permission_denied"
                    showSpeechPermissionAlert = true
                case .recognizerUnavailable:
                    notes[idx].transcriptPreview = "voice_notes_transcript_local_unavailable"
                case .timedOut:
                    notes[idx].transcriptPreview = "voice_notes_transcript_timeout"
                case .failed:
                    notes[idx].transcriptPreview = "voice_notes_transcript_error"
                case .needsCloudConsent:
                    break
                }
            } else {
                notes[idx].transcriptPreview = "voice_notes_transcript_error"
            }
            markTranscriptionResult(success: false, empty: true)
        }
        persistNotes()
    }

    private func runLocalTranscriptionIfPossible(noteId: UUID, localURL: URL?) {
        runFileTranscription(noteId: noteId, localURL: localURL, allowCloud: false)
    }
    
    private func autosaveAfterInterruption() {
        guard recordingState == .recording || recordingState == .paused else { return }
        stopTimer()
        recorderService.onBuffer = nil
        let finishedURL = recorderService.stop() ?? recordingURL
        let elapsedFromService = Int((recordingStartedAt.map { Date().timeIntervalSince($0) } ?? 0).rounded())
        let noteId = UUID()
        let draft = VoiceNoteItem(
            id: noteId,
            title: generatedTitle(for: Date()),
            createdAt: Date(),
            durationSec: max(max(elapsedSec, elapsedFromService), 1),
            transcriptPreview: liveTranscript.isEmpty ? "voice_notes_transcript_pending" : liveTranscript,
            summary: "",
            summaryConfidence: 0.0,
            summaryVersion: 0,
            tags: ["autosaved"],
            audioPath: finishedURL?.path ?? "",
            sourceTranscript: liveTranscript
        )
        let transcriber = liveTranscriber
        liveTranscriber = nil
        notes.insert(draft, at: 0)
        persistNotes()
        showRecordingSavedToast(path: finishedURL?.path ?? "")
        recordingState = .saved
        currentStatusText = "voice_notes_status_autosaved"
        recordingStartedAt = nil
        recordingURL = nil
        elapsedSec = 0
        noiseLevel = 0.0
        liveTranscript = ""
        markInterruption()
        ToastManager.shared.showWarning(
            LocalizationManager.shared.localized("voice_recording_interrupted")
        )
        if let transcriber {
            transcriber.finish { [weak self] transcript in
                Task { @MainActor in
                    guard let self, let idx = self.notes.firstIndex(where: { $0.id == noteId }) else { return }
                    let text = transcript.text.trimmingCharacters(in: .whitespacesAndNewlines)
                    if text.isEmpty {
                        self.runFileTranscription(noteId: noteId, localURL: finishedURL, allowCloud: false)
                        return
                    }
                    self.notes[idx].transcriptPreview = text
                    self.notes[idx].sourceTranscript = text
                    self.notes[idx].segments = transcript.segments
                    self.persistNotes()
                }
            }
        } else {
            runFileTranscription(noteId: noteId, localURL: finishedURL, allowCloud: false)
        }
    }
}

private struct VoiceNotesSummaryService {
    struct Output {
        let text: String
        let confidence: Double
        let version: Int
        let suggestedTags: [String]
    }

    func summarize(transcript: String, title: String, previousVersion: Int) -> Output {
        let cleaned = transcript
            .replacingOccurrences(of: "\n", with: " ")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let lower = cleaned.lowercased()
        let tokens = cleaned.split(separator: " ").map(String.init)
        let preview = tokens.prefix(28).joined(separator: " ")
        let hasPlaceholder = lower.hasPrefix("voice_notes_") || lower.hasPrefix("ai_assistant_")
        let summaryText: String
        let confidence: Double

        if hasPlaceholder || cleaned.isEmpty {
            summaryText = LocalizationManager.shared.localized("voice_notes_summary_need_transcript")
            confidence = 0.35
        } else {
            summaryText = preview + (tokens.count > 28 ? "..." : "")
            confidence = min(0.95, max(0.6, Double(min(tokens.count, 60)) / 100.0 + 0.45))
        }

        var tags: [String] = []
        if lower.contains("release") || lower.contains("релиз") { tags.append("release") }
        if lower.contains("звон") || lower.contains("call") { tags.append("call") }
        if lower.contains("family") || lower.contains("сем") { tags.append("family") }
        if lower.contains("bug") || lower.contains("ошиб") { tags.append("bugfix") }
        if tags.isEmpty, !title.isEmpty { tags.append("notes") }

        return Output(
            text: summaryText,
            confidence: confidence,
            version: max(1, previousVersion + 1),
            suggestedTags: tags
        )
    }
}
