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

    var body: some View {
        NavigationView {
            ZStack {
                StormMeshBackground(variant: .neutral)
                    .ignoresSafeArea()

                ScrollView {
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
            Image(systemName: "waveform.badge.mic")
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
            }
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

