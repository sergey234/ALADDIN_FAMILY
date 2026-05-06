import SwiftUI

struct VoiceNotesScreen: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss
    @StateObject private var viewModel = VoiceNotesViewModel()
    @State private var showRenameAlert = false
    @State private var renameText = ""
    @State private var renameTargetId: UUID?
    @State private var callGoalText = ""
    @State private var callPostText = ""
    @State private var callOutcomeText = ""

    var body: some View {
        NavigationView {
            VStack(spacing: 12) {
                QuickRecorderBar(viewModel: viewModel)
                    .environmentObject(localizationManager)
                    .padding(.horizontal)

                privacyBanner

                callAssistantSection

                notesContent
                    .searchable(text: $viewModel.searchText, prompt: localizationManager.localized("voice_notes_search_placeholder"))
            }
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
        HStack(spacing: 8) {
            Image(systemName: "lock.shield")
                .foregroundColor(.green)
            Text(localizationManager.localized("voice_notes_local_only_disclaimer"))
                .font(.footnote)
                .foregroundColor(.secondary)
            Spacer()
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
            } else {
                notesList
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
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    var notesList: some View {
        List {
            ForEach(viewModel.groupedNotes, id: \.titleKey) { section in
                Section(localizationManager.localized(section.titleKey)) {
                    ForEach(section.items) { note in
                        noteRow(note)
                    }
                }
            }
        }
        .listStyle(.insetGrouped)
    }

    func noteRow(_ note: VoiceNotesViewModel.VoiceNoteItem) -> some View {
        VoiceNoteCard(note: note)
            .environmentObject(localizationManager)
            .listRowInsets(EdgeInsets(top: 6, leading: 12, bottom: 6, trailing: 12))
            .listRowBackground(Color.clear)
            .contextMenu {
                Button(localizationManager.localized("voice_notes_rename")) {
                    renameTargetId = note.id
                    renameText = note.title
                    showRenameAlert = true
                }
                Button(localizationManager.localized("voice_notes_summarize")) {
                    viewModel.generateSummary(noteId: note.id, forceRegenerate: true)
                }
            }
            .swipeActions(edge: .trailing, allowsFullSwipe: false) {
                Button {
                    viewModel.generateSummary(noteId: note.id, forceRegenerate: true)
                } label: {
                    Label(localizationManager.localized("voice_notes_summary_retry"), systemImage: "arrow.clockwise")
                }
                .tint(.orange)

                Button(role: .destructive) {
                    viewModel.requestDelete(note: note)
                } label: {
                    Label(localizationManager.localized("notification_delete"), systemImage: "trash")
                }
            }
    }

    var callAssistantSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("call_assistant_section_title"))
                .font(.headline)
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
        .padding(.horizontal)
    }

    var emptyTitleKey: String {
        viewModel.searchText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            ? "voice_notes_empty_title"
            : "voice_notes_empty_search_title"
    }

    var emptySubtitleKey: String {
        viewModel.searchText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            ? "voice_notes_empty_subtitle"
            : "voice_notes_empty_search_subtitle"
    }
}

