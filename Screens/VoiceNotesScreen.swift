import SwiftUI
import UniformTypeIdentifiers

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
    @State private var lastStructureTranscript: String = ""
    @State private var dayRecapResult: VoiceDayRecapResult?
    @State private var isDayRecapping = false
    @State private var dayRecapErrorKey: String?
    @State private var showDayRecapHint = false
    @State private var weeklyDigestResult: VoiceWeeklyDigestResult?
    @State private var dictionaryDraft = ""
    @AppStorage("voice_safety_log_coach_tip_dismissed") private var coachTipDismissed = false

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

                        if !coachTipDismissed {
                            coachTipBanner
                        }

                        privacyBanner

                        dictionarySection

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
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text(localizationManager.localized("voice_notes_title"))
                        .font(.headline.weight(.bold))
                        .foregroundColor(.white)
                }
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("common_close")) {
                        dismiss()
                    }
                    .foregroundColor(.secondaryGold)
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("voice_weekly_digest_button")) {
                        weeklyDigestResult = viewModel.makeWeeklyDigest()
                    }
                    .foregroundColor(.secondaryGold)
                    .accessibilityIdentifier("voice_weekly_digest_button")
                }
            }
            .compatibleToolbarColorScheme(.dark)
        }
        .onAppear {
            viewModel.markVoiceSessionStable()
            VoiceWeeklyDigestService.ensureSundaySchedule()
            if VoiceWeeklyDigestService.consumePendingOpen() {
                weeklyDigestResult = viewModel.makeWeeklyDigest()
            }
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
        .onChange(of: viewModel.pendingAntifakeFromVoice) { payload in
            guard payload != nil else { return }
            routePendingAntifakeAfterDismiss()
        }
        .onChange(of: viewModel.pendingStatusNavigation) { pending in
            guard pending else { return }
            routePendingStatusAfterDismiss()
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
        .alert(localizationManager.localized("voice_notes_cloud_title"), isPresented: $viewModel.showCloudConsent) {
            Button(localizationManager.localized("common_cancel"), role: .cancel) {}
            Button(localizationManager.localized("voice_notes_cloud_yes")) {
                viewModel.allowAppleCloudAndRetry()
            }
        } message: {
            Text(localizationManager.localized("voice_notes_cloud_body"))
        }
        .alert(localizationManager.localized("voice_notes_preset_title"), isPresented: $viewModel.showPresetConsent) {
            Button(localizationManager.localized("common_cancel"), role: .cancel) {
                viewModel.showPresetConsent = false
            }
            Button(localizationManager.localized("voice_notes_preset_yes")) {
                viewModel.confirmPresetNetwork()
            }
        } message: {
            Text(localizationManager.localized("voice_notes_preset_body"))
        }
        .fileImporter(
            isPresented: $viewModel.showImporter,
            allowedContentTypes: [.audio, .movie, .mpeg4Movie],
            allowsMultipleSelection: false
        ) { result in
            if case .success(let urls) = result, let url = urls.first {
                viewModel.importRecording(url: url)
            }
        }
        .onChange(of: viewModel.presetStructure?.id) { _ in
            if let result = viewModel.presetStructure {
                structureResult = result
            }
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
        .sheet(item: $weeklyDigestResult) { result in
            VoiceWeeklyDigestSheet(result: result)
                .environmentObject(localizationManager)
        }
        .alert(
            localizationManager.localized("voice_structure_error_title"),
            isPresented: Binding(
                get: { structureErrorKey != nil },
                set: { if !$0 { structureErrorKey = nil } }
            )
        ) {
            Button(localizationManager.localized("common_cancel"), role: .cancel) {
                structureErrorKey = nil
            }
            Button(localizationManager.localized("voice_structure_retry")) {
                let retry = lastStructureTranscript
                structureErrorKey = nil
                if !retry.isEmpty {
                    runStructure(transcript: retry)
                }
            }
        } message: {
            Text(localizationManager.localized(structureErrorKey ?? "voice_structure_soft_fail"))
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
        guard viewModel.allowsCloudPresets, viewModel.presetNetworkAllowed else { return }
        guard !isStructuring else { return }
        isStructuring = true
        structureErrorKey = nil
        lastStructureTranscript = transcript
        Task { @MainActor in
            defer { isStructuring = false }
            do {
                structureResult = try await VoiceNotesStructureService.structure(transcript: transcript)
            } catch {
                ToastManager.shared.showWarning(
                    localizationManager.localized("voice_structure_soft_fail")
                )
                structureErrorKey = "voice_structure_soft_fail"
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
    /// VN-UI-01: readable on StormMesh — avoid `.secondary` (too dim on dark).
    private var privacyReadableForeground: Color {
        Color.white.opacity(0.78)
    }

    var privacyBanner: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 8) {
                Image(systemName: "lock.shield")
                    .foregroundColor(.green)
                Text(localizationManager.localized(viewModel.speechBannerKey))
                    .font(.footnote)
                    .foregroundColor(privacyReadableForeground)
            }
            if viewModel.longFileNotice {
                Text(localizationManager.localized("voice_notes_long_file"))
                    .font(.caption)
                    .foregroundColor(.orange)
            }
            if viewModel.allowsCloudPresets && (viewModel.longFileNotice || viewModel.speechSiteLink),
               let site = URL(string: "https://aladdin-ai.ru/speech.html") {
                Link(localizationManager.localized("voice_notes_long_file_site"), destination: site)
                    .font(.caption)
            }
            Text(localizationManager.localized("voice_notes_privacy_stt_disclaimer"))
                .font(.caption)
                .foregroundColor(privacyReadableForeground)
            Text(localizationManager.localized("voice_safety_local_vs_antifake"))
                .font(.caption)
                .foregroundColor(privacyReadableForeground)
            Text(localizationManager.localized("voice_structure_privacy"))
                .font(.caption)
                .foregroundColor(privacyReadableForeground)
            if !viewModel.isSpeechTranscriptionAvailable {
                Text(localizationManager.localized("voice_notes_speech_unavailable_hint"))
                    .font(.caption)
                    .foregroundColor(.orange)
            }
        }
        .padding(.horizontal)
    }

    private var dictionarySection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("voice_notes_dictionary"))
                .font(.body.weight(.semibold))
            Text(localizationManager.localized("voice_notes_dictionary_note"))
                .font(.caption)
                .foregroundColor(privacyReadableForeground)
            HStack {
                TextField(localizationManager.localized("voice_notes_dictionary_placeholder"), text: $dictionaryDraft)
                    .textFieldStyle(.roundedBorder)
                    .accessibilityLabel(localizationManager.localized("voice_notes_dictionary_placeholder"))
                Button(localizationManager.localized("voice_notes_dictionary_add")) {
                    viewModel.addDictionaryPhrase(dictionaryDraft)
                    dictionaryDraft = ""
                }
                .disabled(dictionaryDraft.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || viewModel.dictionaryPhrases.count >= 100)
                .accessibilityLabel(localizationManager.localized("voice_notes_dictionary_add"))
            }
            ForEach(Array(viewModel.dictionaryPhrases.enumerated()), id: \.offset) { index, phrase in
                HStack {
                    Text(phrase).font(.body)
                    Spacer()
                    Button(localizationManager.localized("voice_notes_dictionary_remove")) {
                        viewModel.removeDictionaryPhrase(at: index)
                    }
                    .accessibilityLabel(localizationManager.localized("voice_notes_dictionary_remove") + " " + phrase)
                }
            }
        }
        .padding(.horizontal)
    }

    private var coachTipBanner: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(localizationManager.localized("voice_safety_coach_tip"))
                .font(.footnote)
                .foregroundColor(.white.opacity(0.9))
            Button(localizationManager.localized("voice_safety_coach_tip_dismiss")) {
                coachTipDismissed = true
            }
            .font(.caption.weight(.semibold))
            .foregroundColor(Color(hex: "F5C542"))
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.08))
        .cornerRadius(12)
        .padding(.horizontal)
        .accessibilityIdentifier("voice_safety_coach_tip")
    }

    /// A9: dismiss VoiceNotes sheet first, then open Antifake (not under the modal).
    private func routePendingAntifakeAfterDismiss() {
        guard let payload = viewModel.consumePendingAntifakeFromVoice() else { return }
        ToastManager.shared.showInfo(localizationManager.localized("voice_safety_opening_antifake"))
        dismiss()
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) {
            navigationManager.navigateToAntifakeShareCheck(payload: payload)
        }
    }

    private func routePendingStatusAfterDismiss() {
        guard viewModel.consumePendingStatusNavigation() else { return }
        dismiss()
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) {
            navigationManager.navigateTo(.networkProtection)
        }
    }

    var notesFilterPicker: some View {
        Picker(localizationManager.localized("voice_notes_filter_title"), selection: $viewModel.activeFilter) {
            ForEach(VoiceNotesViewModel.NotesFilter.allCases, id: \.rawValue) { filter in
                Text(localizationManager.localized(filter.titleKey)).tag(filter)
            }
        }
        .pickerStyle(.menu)
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
            onSendToAI: viewModel.allowsCloudPresets ? { text in
                UserDefaults.standard.set(text, forKey: AppConfig.UserDefaultsKeys.pendingAIAssistantDraftMessage)
                playback.stop()
                dismiss()
                navigationManager.navigateTo(.aiAssistant)
            } : nil,
            onStructure: { _ in
                viewModel.requestMinutes(noteId: note.id)
            },
            onFamily: {
                viewModel.requestFamily(noteId: note.id)
            },
            onCleaner: { viewModel.applyCleaner(noteId: note.id) },
            onClear: { viewModel.applyClear(noteId: note.id) },
            onRead: { viewModel.speak(noteId: note.id) },
            onCheck: {
                let text = note.transcriptPreview
                guard !text.hasPrefix("voice_notes_"), !text.isEmpty else { return }
                navigationManager.navigateToAntifakeShareCheck(
                    payload: AntifakeSharePayload(mode: .text, value: text, createdAt: Date())
                )
            },
            onRestore: { viewModel.restoreSource(noteId: note.id) },
            allowsCloudActions: viewModel.allowsCloudPresets,
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
        VStack(alignment: .leading, spacing: Spacing.s) {
            Button {
                withAnimation(.easeInOut(duration: 0.2)) {
                    isCallAssistantExpanded.toggle()
                }
            } label: {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(localizationManager.localized("call_assistant_section_title"))
                            .font(.headline.weight(.bold))
                            .foregroundColor(.textPrimary)
                        Text(localizationManager.localized("call_assistant_section_subtitle"))
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.9))
                            .multilineTextAlignment(.leading)
                    }
                    Spacer()
                    Image(systemName: isCallAssistantExpanded ? "chevron.up" : "chevron.down")
                        .foregroundColor(.secondaryGold)
                }
            }
            .buttonStyle(.plain)

            if isCallAssistantExpanded {
                VStack(alignment: .leading, spacing: Spacing.m) {
                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        Text(localizationManager.localized("call_assistant_before_label"))
                            .font(.caption.weight(.semibold))
                            .foregroundColor(.secondaryGold)
                        ZStack(alignment: .leading) {
                            if callGoalText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                                Text(localizationManager.localized("call_assistant_goal_placeholder"))
                                    .font(.body)
                                    .foregroundColor(.white.opacity(0.72))
                                    .padding(.horizontal, Spacing.s)
                            }
                            TextField("", text: $callGoalText)
                                .font(.body)
                                .foregroundColor(.white)
                                .padding(Spacing.s)
                        }
                        .background(Color.white.opacity(0.14))
                        .overlay(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .stroke(Color.white.opacity(0.35), lineWidth: 1)
                        )
                        .cornerRadius(CornerRadius.medium)
                    }

                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        Text(localizationManager.localized("call_assistant_after_label"))
                            .font(.caption.weight(.semibold))
                            .foregroundColor(.secondaryGold)
                        ZStack(alignment: .leading) {
                            if callPostText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                                Text(localizationManager.localized("call_assistant_postcall_placeholder"))
                                    .font(.body)
                                    .foregroundColor(.white.opacity(0.72))
                                    .padding(.horizontal, Spacing.s)
                            }
                            TextField("", text: $callPostText)
                                .font(.body)
                                .foregroundColor(.white)
                                .padding(Spacing.s)
                        }
                        .background(Color.white.opacity(0.14))
                        .overlay(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .stroke(Color.white.opacity(0.35), lineWidth: 1)
                        )
                        .cornerRadius(CornerRadius.medium)
                        ZStack(alignment: .leading) {
                            if callOutcomeText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                                Text(localizationManager.localized("call_assistant_outcome_placeholder"))
                                    .font(.body)
                                    .foregroundColor(.white.opacity(0.72))
                                    .padding(.horizontal, Spacing.s)
                            }
                            TextField("", text: $callOutcomeText)
                                .font(.body)
                                .foregroundColor(.white)
                                .padding(Spacing.s)
                        }
                        .background(Color.white.opacity(0.14))
                        .overlay(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .stroke(Color.white.opacity(0.35), lineWidth: 1)
                        )
                        .cornerRadius(CornerRadius.medium)
                    }

                    Button {
                        viewModel.createCallAssistantNote(
                            goal: callGoalText,
                            postCallNote: callPostText,
                            outcomes: callOutcomeText
                        )
                        callGoalText = ""
                        callPostText = ""
                        callOutcomeText = ""
                    } label: {
                        Text(localizationManager.localized("call_assistant_save_note"))
                            .font(.bodyBold)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.s)
                            .background(Color.secondaryGold)
                            .cornerRadius(CornerRadius.medium)
                    }
                    .disabled(
                        callGoalText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
                        callPostText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
                        callOutcomeText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                    )
                }
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .secondaryGold)
        .padding(.horizontal)
        .withToast()
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

