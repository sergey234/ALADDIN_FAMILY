import SwiftUI

struct VoiceNotesScreen: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @Environment(\.dismiss) private var dismiss
    @StateObject private var viewModel = VoiceNotesViewModel()
    @StateObject private var playback = VoiceNotePlaybackController()
    @State private var showRenameAlert = false
    @State private var renameText = ""
    @State private var renameTargetId: UUID?
    @State private var callGoalText = ""
    @State private var callPostText = ""
    @State private var callOutcomeText = ""
    @State private var isCallAssistantExpanded = false
    @State private var structureResult: VoiceNotesStructureResult?
    @State private var isStructuring = false
    @State private var structureErrorKey: String?
    @State private var dayRecapResult: VoiceDayRecapResult?
    @State private var isDayRecapping = false
    @State private var dayRecapErrorKey: String?
    @State private var showDayRecapHint = false

    var body: some View {
        NavigationView {
            ZStack {
                StormMeshBackground(variant: .neutral)
                    .ignoresSafeArea()

                ScrollView(.vertical, showsIndicators: true) {
                    LazyVStack(alignment: .leading, spacing: 12) {
                        QuickRecorderBar(viewModel: viewModel)
                            .environmentObject(localizationManager)
                            .padding(.horizontal)

                        privacyBanner

                        notesContent

                        callAssistantSection
                    }
                    .padding(.bottom, 8)
                }
            }
            .foregroundColor(.white)
            .searchable(text: $viewModel.searchText, prompt: localizationManager.localized("voice_notes_search_placeholder"))
            .safeAreaInset(edge: .bottom) {
                if viewModel.canUndoDelete {
                    HStack {
                        Text(localizationManager.localized("voice_notes_deleted_undo_hint"))
                            .font(.subheadline)
                        Spacer()
                        Button(localizationManager.localized("voice_notes_undo")) {
                            viewModel.undoDelete()
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    .padding()
                    .background(.ultraThinMaterial)
                }
            }
            .navigationTitle(localizationManager.localized("voice_notes_title"))
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("common_close")) {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    EmptyView()
                }
            }
        }
        .onAppear {
            viewModel.markVoiceSessionStable()
            if VoiceDayRecapService.consumePendingOpen() {
                showDayRecapHint = true
                if let note = viewModel.groupedNotes.flatMap(\.items).first {
                    let text = note.summary.isEmpty ? note.transcriptPreview : note.summary
                    runDayRecap(transcript: text)
                }
            }
        }
        .onDisappear {
            playback.stop()
        }
        .alert(localizationManager.localized("voice_notes_mic_permission_title"), isPresented: $viewModel.showMicPermissionAlert) {
            Button(localizationManager.localized("common_cancel"), role: .cancel) {}
            Button(localizationManager.localized("voice_open_settings")) { openSettings() }
        } message: {
            Text(localizationManager.localized("voice_notes_mic_permission_message"))
        }
        .alert(localizationManager.localized("voice_notes_speech_permission_title"), isPresented: $viewModel.showSpeechPermissionAlert) {
            Button(localizationManager.localized("common_cancel"), role: .cancel) {}
            Button(localizationManager.localized("voice_open_settings")) { openSettings() }
        } message: {
            Text(localizationManager.localized("voice_notes_speech_permission_message"))
        }
        .alert(localizationManager.localized("voice_notes_rename"), isPresented: $showRenameAlert) {
            TextField(localizationManager.localized("voice_notes_rename_placeholder"), text: $renameText)
            Button(localizationManager.localized("common_cancel"), role: .cancel) {}
            Button(localizationManager.localized("common_save")) {
                if let id = renameTargetId {
                    viewModel.renameNote(noteId: id, to: renameText)
                }
            }
        } message: {
            Text(localizationManager.localized("voice_notes_rename_prompt"))
        }
        .sheet(item: $structureResult) { result in
            VoiceNotesStructureSheet(result: result)
                .environmentObject(localizationManager)
                .environmentObject(navigationManager)
        }
        .sheet(item: $dayRecapResult) { result in
            VoiceDayRecapSheet(result: result)
                .environmentObject(localizationManager)
                .environmentObject(navigationManager)
        }
        .alert(
            localizationManager.localized("voice_structure_error_title"),
            isPresented: Binding(
                get: { structureErrorKey != nil },
                set: { if !$0 { structureErrorKey = nil } }
            )
        ) {
            Button(localizationManager.localized("common_ok"), role: .cancel) {
                structureErrorKey = nil
            }
        } message: {
            Text(localizationManager.localized(structureErrorKey ?? "voice_structure_error"))
        }
        .alert(
            localizationManager.localized("voice_day_recap_error_title"),
            isPresented: Binding(
                get: { dayRecapErrorKey != nil },
                set: { if !$0 { dayRecapErrorKey = nil } }
            )
        ) {
            Button(localizationManager.localized("common_ok"), role: .cancel) {
                dayRecapErrorKey = nil
            }
        } message: {
            Text(localizationManager.localized(dayRecapErrorKey ?? "voice_day_recap_error"))
        }
        .overlay(alignment: .top) {
            if showDayRecapHint {
                Text(localizationManager.localized("voice_day_recap_hint"))
                    .font(.caption)
                    .padding(8)
                    .background(.ultraThinMaterial)
                    .cornerRadius(8)
                    .padding(.top, 8)
                    .onAppear {
                        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
                            showDayRecapHint = false
                        }
                    }
            }
        }
    }

    private func runStructure(transcript: String) {
        guard !isStructuring else { return }
        isStructuring = true
        structureErrorKey = nil
        Task { @MainActor in
            defer { isStructuring = false }
            do {
                structureResult = try await VoiceNotesStructureService.structure(transcript: transcript)
            } catch {
                structureErrorKey = "voice_structure_error"
            }
        }
    }

    private func runDayRecap(transcript: String) {
        guard !isDayRecapping else { return }
        let cleaned = transcript.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !cleaned.isEmpty,
              !cleaned.hasPrefix("voice_notes_") else {
            dayRecapErrorKey = "voice_day_recap_need_transcript"
            return
        }
        isDayRecapping = true
        dayRecapErrorKey = nil
        Task { @MainActor in
            defer { isDayRecapping = false }
            do {
                dayRecapResult = try await VoiceDayRecapService.recap(transcript: cleaned)
            } catch {
                dayRecapErrorKey = "voice_day_recap_error"
            }
        }
    }
}

private extension VoiceNotesScreen {
    var privacyBanner: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 8) {
                Image(systemName: "lock.shield")
                    .foregroundColor(.green)
                Text(localizationManager.localized("voice_notes_local_only_disclaimer"))
                    .font(.footnote)
                    .foregroundColor(.secondary)
            }
            Text(localizationManager.localized("voice_notes_privacy_stt_disclaimer"))
                .font(.caption)
                .foregroundColor(.secondary)
            Text(localizationManager.localized("voice_structure_privacy"))
                .font(.caption)
                .foregroundColor(.secondary)
            if !viewModel.isSpeechTranscriptionAvailable {
                Text(localizationManager.localized("voice_notes_speech_unavailable_hint"))
                    .font(.caption)
                    .foregroundColor(.orange)
            }
        }
        .padding(.horizontal)
    }

    var notesFilterPicker: some View {
        Picker(localizationManager.localized("voice_notes_filter_title"), selection: $viewModel.activeFilter) {
            ForEach(VoiceNotesViewModel.NotesFilter.allCases, id: \.rawValue) { filter in
                Text(localizationManager.localized(filter.titleKey)).tag(filter)
            }
        }
        .pickerStyle(.segmented)
        .padding(.horizontal)
    }

    var notesContent: some View {
        VStack(spacing: 0) {
            notesFilterPicker

            if viewModel.groupedNotes.isEmpty {
                emptyState
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 32)
            } else {
                notesSectionsInScroll
            }
        }
    }

    /// Секции заметок вне `List`, чтобы общий экран прокручивался одним `ScrollView`.
    private var notesSectionsInScroll: some View {
        ForEach(viewModel.groupedNotes, id: \.titleKey) { section in
            VStack(alignment: .leading, spacing: 10) {
                Text(localizationManager.localized(section.titleKey))
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.secondary)
                    .padding(.horizontal)
                ForEach(section.items) { note in
                    noteRow(note)
                }
            }
        }
    }

    var emptyState: some View {
        VStack(spacing: 10) {
            Image(systemName: SFSymbolCompat.voiceNotes)
                .font(.system(size: 28))
                .foregroundColor(.secondary)
            Text(localizationManager.localized(emptyTitleKey))
                .font(.headline)
            Text(localizationManager.localized(emptySubtitleKey))
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .padding(.horizontal, 20)
        .frame(maxWidth: .infinity)
    }

    func noteRow(_ note: VoiceNotesViewModel.VoiceNoteItem) -> some View {
        VoiceNoteCard(
            note: note,
            playback: playback,
            onRegenerateSummary: {
                viewModel.generateSummary(noteId: note.id, forceRegenerate: true)
            },
            onSendToAI: { text in
                UserDefaults.standard.set(text, forKey: AppConfig.UserDefaultsKeys.pendingAIAssistantDraftMessage)
                playback.stop()
                dismiss()
                navigationManager.navigateTo(.aiAssistant)
            },
            onStructure: { text in
                runStructure(transcript: text)
            },
            isStructuring: isStructuring
        )
            .environmentObject(localizationManager)
            .padding(.horizontal, 12)
            .contextMenu {
                Button(localizationManager.localized("voice_notes_rename")) {
                    renameTargetId = note.id
                    renameText = note.title
                    showRenameAlert = true
                }
                Button(localizationManager.localized("voice_notes_summarize")) {
                    viewModel.generateSummary(noteId: note.id, forceRegenerate: true)
                }
                Button(localizationManager.localized("voice_day_recap_button")) {
                    let text = note.summary.isEmpty ? note.transcriptPreview : "\(note.summary)\n\(note.transcriptPreview)"
                    runDayRecap(transcript: text)
                }
                Button(role: .destructive) {
                    viewModel.requestDelete(note: note)
                } label: {
                    Label(localizationManager.localized("notification_delete"), systemImage: "trash")
                }
            }
    }

    var callAssistantSection: some View {
        DisclosureGroup(
            isExpanded: $isCallAssistantExpanded,
            content: {
                VStack(alignment: .leading, spacing: 8) {
                    Text(localizationManager.localized("call_assistant_section_subtitle"))
                        .font(.caption)
                        .foregroundColor(.secondary)

                    TextField(localizationManager.localized("call_assistant_goal_placeholder"), text: $callGoalText)
                        .textFieldStyle(.roundedBorder)
                    TextField(localizationManager.localized("call_assistant_postcall_placeholder"), text: $callPostText)
                        .textFieldStyle(.roundedBorder)
                    TextField(localizationManager.localized("call_assistant_outcome_placeholder"), text: $callOutcomeText)
                        .textFieldStyle(.roundedBorder)

                    Button(localizationManager.localized("call_assistant_save_note")) {
                        viewModel.createCallAssistantNote(
                            goal: callGoalText,
                            postCallNote: callPostText,
                            outcomes: callOutcomeText
                        )
                        callGoalText = ""
                        callPostText = ""
                        callOutcomeText = ""
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(
                        callGoalText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
                        callPostText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
                        callOutcomeText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                    )
                }
                .padding(.top, 6)
            },
            label: {
                Text(localizationManager.localized("call_assistant_section_title"))
                    .font(.headline)
            }
        )
        .padding(.horizontal)
    }

    var emptyTitleKey: String {
        viewModel.searchText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            ? "voice_notes_empty_title"
            : "voice_notes_empty_search_title"
    }

    private func openSettings() {
        if let url = URL(string: UIApplication.openSettingsURLString) {
            UIApplication.shared.open(url)
        }
    }

    var emptySubtitleKey: String {
        viewModel.searchText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            ? "voice_notes_empty_subtitle"
            : "voice_notes_empty_search_subtitle"
    }
}

