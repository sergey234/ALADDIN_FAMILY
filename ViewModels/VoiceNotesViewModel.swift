import Foundation
import SwiftUI
import AVFoundation

@MainActor
final class VoiceNotesViewModel: ObservableObject {
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
    }
    
    enum NotesFilter: String, CaseIterable {
        case all
        case today
        case yesterday
        case projects
        
        var titleKey: String {
            switch self {
            case .all: return "voice_notes_filter_all"
            case .today: return "voice_notes_section_today"
            case .yesterday: return "voice_notes_section_yesterday"
            case .projects: return "voice_notes_section_projects"
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
    @Published var searchText: String = ""
    @Published var activeFilter: NotesFilter = .all

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
        loadNotes()
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
        }
        return result
    }

    func startRecording() {
        guard recordingState != .recording else { return }
        recordingState = .recording
        currentStatusText = "voice_notes_status_listening"
        feedbackLogged = false
        startTappedAt = Date()
        if let url = try? recorderService.start() {
            recordingURL = url
            recordingStartedAt = Date()
        } else {
            recordingState = .failed
            currentStatusText = "ai_assistant_voice_service_unavailable"
            return
        }
        track(action: "voice_record_start_success_rate")
        startTimer()
        logTimeToFirstFeedbackIfNeeded()
    }

    func pauseRecording() {
        guard recordingState == .recording else { return }
        recordingState = .paused
        currentStatusText = "voice_notes_status_paused"
        recorderService.pause()
        stopTimer()
    }

    func resumeRecording() {
        guard recordingState == .paused else { return }
        recordingState = .recording
        currentStatusText = "voice_notes_status_listening"
        recorderService.resume()
        startTimer()
    }

    func stopAndSaveRecording() {
        guard recordingState == .recording || recordingState == .paused else { return }
        recordingState = .processing
        currentStatusText = "voice_notes_status_processing"
        stopTimer()

        let finishedURL = recorderService.stop() ?? recordingURL
        let elapsedFromService = Int((recordingStartedAt.map { Date().timeIntervalSince($0) } ?? 0).rounded())
        let newNote = VoiceNoteItem(
            id: UUID(),
            title: generatedTitle(for: Date()),
            createdAt: Date(),
            durationSec: max(max(elapsedSec, elapsedFromService), 1),
            transcriptPreview: "voice_notes_transcript_pending",
            summary: "",
            summaryConfidence: 0.0,
            summaryVersion: 0,
            tags: [],
            audioPath: finishedURL?.path ?? ""
        )
        notes.insert(newNote, at: 0)
        persistNotes()
        showRecordingSavedToast(path: finishedURL?.path ?? "")
        recordingState = .saved
        currentStatusText = "voice_notes_status_saved"
        recordingStartedAt = nil
        recordingURL = nil
        elapsedSec = 0
        noiseLevel = 0.0
        runLocalTranscriptionIfPossible(noteId: newNote.id, localURL: finishedURL)
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
            notes[idx].tags = Array(Set(notes[idx].tags + result.suggestedTags)).sorted()
        }
        persistNotes()
        markSummaryGeneration(success: true)
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
                self.noiseLevel = min(1.0, self.noiseLevel + 0.07)
                if self.noiseLevel > 0.92 {
                    self.noiseLevel = 0.18
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
        if stored.isEmpty {
            seedDemoData()
            return
        }
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
                audioPath: $0.audioPath
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
                audioPath: $0.audioPath
            )
        }
        store.save(payload)
    }

    private func generatedTitle(for date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd HH:mm"
        return "Voice Note • \(formatter.string(from: date))"
    }

    private func seedDemoData() {
        let now = Date()
        notes = [
            VoiceNoteItem(
                id: UUID(),
                title: generatedTitle(for: now),
                createdAt: now,
                durationSec: 94,
                transcriptPreview: "Нужно согласовать релиз и проверить smoke по family API.",
                summary: "Согласовать релиз и выполнить смоук-проверки API семейного чата.",
                summaryConfidence: 0.88,
                summaryVersion: 1,
                tags: ["release", "api"],
                audioPath: ""
            ),
            VoiceNoteItem(
                id: UUID(),
                title: generatedTitle(for: Calendar.current.date(byAdding: .day, value: -1, to: now) ?? now),
                createdAt: Calendar.current.date(byAdding: .day, value: -1, to: now) ?? now,
                durationSec: 56,
                transcriptPreview: "Подготовить сценарий UX-тестов для voice-notes dashboard.",
                summary: "Собрать UX-тест-кейсы для диктофона и статусов ошибок.",
                summaryConfidence: 0.81,
                summaryVersion: 1,
                tags: ["ux", "qa"],
                audioPath: ""
            )
        ]
        persistNotes()
    }
    
    private func runLocalTranscriptionIfPossible(noteId: UUID, localURL: URL?) {
        guard localOnlyModeEnabled, let localURL else { return }
        transcriptionService.transcribeOnDevice(url: localURL) { [weak self] result in
            guard let self else { return }
            Task { @MainActor in
                switch result {
                case .success(let text):
                    if let idx = self.notes.firstIndex(where: { $0.id == noteId }) {
                        self.notes[idx].transcriptPreview = text.isEmpty
                            ? "ai_assistant_voice_empty_result"
                            : text
                        self.persistNotes()
                        self.markTranscriptionResult(success: !text.isEmpty, empty: text.isEmpty)
                    }
                case .failure(let error):
                    if let idx = self.notes.firstIndex(where: { $0.id == noteId }) {
                        if let e = error as? VoiceNotesTranscriptionError {
                            switch e {
                            case .permissionDenied:
                                self.notes[idx].transcriptPreview = "voice_notes_transcript_permission_denied"
                            case .recognizerUnavailable:
                                self.notes[idx].transcriptPreview = "voice_notes_transcript_local_unavailable"
                            case .timedOut:
                                self.notes[idx].transcriptPreview = "voice_notes_transcript_timeout"
                            case .failed:
                                self.notes[idx].transcriptPreview = "voice_notes_transcript_error"
                            }
                        } else {
                            self.notes[idx].transcriptPreview = "voice_notes_transcript_error"
                        }
                        self.persistNotes()
                        self.markTranscriptionResult(success: false, empty: true)
                    }
                }
            }
        }
    }
    
    private func autosaveAfterInterruption() {
        guard recordingState == .recording || recordingState == .paused else { return }
        stopTimer()
        let finishedURL = recorderService.stop() ?? recordingURL
        let elapsedFromService = Int((recordingStartedAt.map { Date().timeIntervalSince($0) } ?? 0).rounded())
        let draft = VoiceNoteItem(
            id: UUID(),
            title: generatedTitle(for: Date()),
            createdAt: Date(),
            durationSec: max(max(elapsedSec, elapsedFromService), 1),
            transcriptPreview: "voice_notes_transcript_pending",
            summary: "",
            summaryConfidence: 0.0,
            summaryVersion: 0,
            tags: ["autosaved"],
            audioPath: finishedURL?.path ?? ""
        )
        notes.insert(draft, at: 0)
        persistNotes()
        showRecordingSavedToast(path: finishedURL?.path ?? "")
        recordingState = .saved
        currentStatusText = "voice_notes_status_autosaved"
        recordingStartedAt = nil
        recordingURL = nil
        elapsedSec = 0
        noiseLevel = 0.0
        markInterruption()
        runLocalTranscriptionIfPossible(noteId: draft.id, localURL: finishedURL)
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
            summaryText = "Локальное резюме недоступно: сначала завершите транскрипцию."
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
