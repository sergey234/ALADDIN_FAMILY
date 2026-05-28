import SwiftUI

/// Разговор с выбранным героем (текст + голос MVP).
struct CompanionConversationScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @StateObject private var caps = CompanionCapabilitiesService.shared
    @StateObject private var voiceSession = CompanionVoiceSession()
    @StateObject private var speechManager = SpeechManager()
    @StateObject private var speechOutput = CompanionSpeechOutput()
    @StateObject private var streamService = CompanionStreamingService.shared

    @AppStorage("companion_selected_character_id") private var characterId: String = "unicorn"
    @AppStorage("companion_active_thread_id") private var activeThreadId: String = ""
    @AppStorage("companion_security_expert_mode") private var securityExpertMode = false
    @AppStorage("companion_equipped_cosmetic_id") private var equippedCosmeticId: String = ""
    @AppStorage("companion_legal_ack_version") private var legalAckVersion: String = ""
    /// P1-13c: озвучка текстовых ответов (Моё → можно выключить).
    @AppStorage("companion_response_tts_enabled") private var responseTTSEnabled = true
    @State private var personalityPreset: String = "friendly"
    @State private var trustScore: Int = 10
    @State private var showCosmetics = false
    @State private var usageSnapshot: CompanionUsageSnapshot?
    @State private var showLegal = false
    @State private var messages: [CompanionChatBubble] = []
    @State private var input = ""
    @State private var sessionId: String = ""
    @State private var heroEmotion: CompanionHeroEmotion = .idle
    @State private var isSending = false
    @State private var lipSyncPhase: CGFloat = 0
    @State private var errorText: String?
    @State private var feedbackBusyId: UUID?
    @State private var streamingHeroIndex: Int?
    @State private var showResumeStream = false
    @State private var streamEmotionDebouncer = CompanionStreamEmotionDebouncer()
    @State private var contentEmotionAfterSpeaking: CompanionHeroEmotion = .happy
    /// HERO-3-23: последняя emotion из SSE (fallback), на UI не вешаем до `done`.
    @State private var pendingStreamContentEmotion: CompanionHeroEmotion?
    @State private var textSpeakingDismissTask: Task<Void, Never>?
    @State private var showFullChatHistory = false
    @FocusState private var isInputFocused: Bool
    @State private var showMicrophonePermissionAlert = false
    @State private var showSpeechPermissionAlert = false
    @State private var showVoiceServiceUnavailableAlert = false
    @State private var isHoldRecording = false
    @State private var holdWillCancel = false
    @State private var holdRecordingDidStart = false
    @State private var holdRecordingBeganAt: Date?
    var embeddedInHome: Bool = false
    var availableCharacters: [CompanionCharacterDTO] = []
    var onSelectCharacter: ((String) -> Void)? = nil
    var onOpenMineTab: (() -> Void)? = nil

    private var isCloudAIEnabled: Bool {
        AppConfig.isAIDataSharingEnabled
    }

    var body: some View {
        VStack(spacing: 0) {
            GeometryReader { geo in
                let layout = CompanionHeroLayout.conversationMetrics(contentSize: geo.size)
                VStack(spacing: 0) {
                    heroStage(layout: layout)
                        .contentShape(Rectangle())
                        .onTapGesture { isInputFocused = false }
                    if usageSnapshot != nil {
                        CompanionUsageBanner(usage: usageSnapshot)
                            .padding(.horizontal, 12)
                            .padding(.vertical, 4)
                    }
                    Divider().opacity(0.15)
                    companionDialogueStrip
                        .frame(height: layout.chatZoneHeight)
                        .contentShape(Rectangle())
                        .onTapGesture { isInputFocused = false }
                }
            }
            if !isCloudAIEnabled {
                cloudAIConsentBanner
            }
            if let errorText, !errorText.isEmpty {
                Text(errorText)
                    .font(.caption)
                    .foregroundStyle(.orange)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 6)
            }
            inputBar
        }
        .background(Color(.systemGroupedBackground))
        .navigationBarTitleDisplayMode(.inline)
        .toolbar(content: conversationToolbarContent)
        .sheet(isPresented: $showLegal, onDismiss: {
            if legalAckVersion.isEmpty {
                legalAckVersion = "2026-05-26"
            }
        }) {
            NavigationView {
                CompanionLegalScreen(onAcknowledge: {
                    legalAckVersion = "2026-05-26"
                    showLegal = false
                })
                .environmentObject(navigationManager)
                .environmentObject(localizationManager)
            }
            .navigationViewStyle(.stack)
        }
        .sheet(isPresented: $showCosmetics) {
            NavigationView {
                ScrollView {
                    CompanionCosmeticsSection(
                        characterId: characterId,
                        trustScore: trustScore,
                        equippedCosmeticId: $equippedCosmeticId
                    )
                    .padding()
                }
                .navigationTitle("Наряды")
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .confirmationAction) {
                        Button("Готово") { showCosmetics = false }
                    }
                }
            }
            .navigationViewStyle(.stack)
            .modifier(CompanionSheetDetentsModifier())
        }
        .task { await loadState() }
        .onAppear {
            speechManager.audioSessionConsumer = .companion
            speechManager.warmUpPermissionsIfNeeded()
            voiceSession.onAssistantReply = { line, emo in
                handleVoiceAssistantReply(line: line, emotion: emo)
            }
            if legalAckVersion.isEmpty {
                showLegal = true
            }
            CompanionAnalytics.track(.open, characterId: characterId, sessionId: sessionId)
            if !embeddedInHome {
                Task { await caps.refresh() }
            }
        }
        .onReceive(NotificationCenter.default.publisher(for: .microphonePermissionDenied)) { _ in
            showMicrophonePermissionAlert = true
            heroEmotion = .alert
        }
        .onReceive(NotificationCenter.default.publisher(for: .speechRecognitionPermissionDenied)) { _ in
            showSpeechPermissionAlert = true
            heroEmotion = .alert
        }
        .onReceive(NotificationCenter.default.publisher(for: .speechServiceUnavailable)) { _ in
            showVoiceServiceUnavailableAlert = true
            heroEmotion = .alert
        }
        .onReceive(NotificationCenter.default.publisher(for: .voiceAudioSessionBusy)) { _ in
            errorText = "Микрофон занят другим режимом. Закройте AI-помощник или диктофон."
            heroEmotion = .alert
        }
        .onDisappear {
            if speechManager.isRecording {
                speechManager.stopRecording()
            }
            speechOutput.stop()
            voiceSession.disconnect()
        }
        .onChange(of: speechManager.livePartialTranscript) { partial in
            guard speechManager.isRecording || speechManager.isPreparingRecording else { return }
            if !partial.isEmpty {
                input = partial
            }
        }
        .alert("Нужен доступ к микрофону", isPresented: $showMicrophonePermissionAlert) {
            Button("OK", role: .cancel) {}
        } message: {
            Text("Разрешите микрофон в Настройках iPhone → ALADDIN Family.")
        }
        .alert("Нужно распознавание речи", isPresented: $showSpeechPermissionAlert) {
            Button("OK", role: .cancel) {}
        } message: {
            Text("Разрешите «Распознавание речи» в Настройках iPhone → ALADDIN Family.")
        }
        .alert("Голосовой ввод недоступен", isPresented: $showVoiceServiceUnavailableAlert) {
            Button("OK", role: .cancel) {}
        } message: {
            Text("Проверьте интернет и разрешения микрофона, затем попробуйте снова.")
        }
        .onChange(of: voiceSession.emotion) { newValue in
            applyVoiceSessionEmotion(newValue)
        }
        .onChange(of: speechOutput.isSpeaking) { speaking in
            if speaking {
                heroEmotion = .speaking
                lipSyncPhase = 1
            } else {
                finishSpeakingPhase()
            }
        }
        .sheet(isPresented: $showFullChatHistory) {
            NavigationView {
                fullChatHistoryScroll
                    .navigationTitle("История")
                    .navigationBarTitleDisplayMode(.inline)
                    .toolbar {
                        ToolbarItem(placement: .confirmationAction) {
                            Button("Готово") { showFullChatHistory = false }
                        }
                    }
            }
            .navigationViewStyle(.stack)
        }
    }

    /// Сцена виртуального друга (~56% высоты), GROK §6.2 — не мини-аватар в шапке чата.
    private func heroStage(layout: CompanionHeroLayout.ConversationMetrics) -> some View {
        ZStack(alignment: .bottom) {
            Color(.systemGroupedBackground).opacity(0.3)
            CompanionHeroAvatarView(
                characterId: characterId,
                emotion: heroEmotion,
                lipSyncPhase: lipSyncPhase,
                equippedCosmeticId: activeEquippedCosmetic,
                stageStyle: .conversationFullBody,
                stageSize: layout.stageSize
            )
            .padding(.horizontal, CompanionHeroLayout.stageHorizontalPadding)
            .padding(.top, 6)
            .padding(.bottom, CompanionHeroLayout.heroStatusOverlayHeight)
            .accessibilityIdentifier("companion_hero_stage")
            heroStatusOverlay
        }
        .frame(height: layout.heroZoneHeight)
        .frame(maxWidth: .infinity)
        .clipped()
    }

    private var companionDialogueStrip: some View {
        CompanionDialogueStrip(
            messages: messages,
            showResumeStream: showResumeStream,
            isSending: isSending,
            feedbackBusyId: feedbackBusyId,
            onResume: { Task { await resumeStream() } },
            onShowHistory: { showFullChatHistory = true },
            onFeedback: { index, vote in
                Task { await sendFeedback(messageIndex: index, vote: vote) }
            }
        )
    }

    private var heroStatusOverlay: some View {
        VStack(spacing: 6) {
            if embeddedInHome && availableCharacters.count > 1 {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(availableCharacters) { hero in
                            let isSelected = hero.id == characterId
                            Button {
                                characterId = hero.id
                                activeThreadId = ""
                                sessionId = ""
                                messages = []
                                onSelectCharacter?(hero.id)
                                Task { await loadState() }
                            } label: {
                                Text("\(CompanionHeroRiveMapping.heroBaseEmoji(characterId: hero.id)) \(hero.displayName)")
                                    .font(.caption.weight(.semibold))
                                    .padding(.horizontal, 10)
                                    .padding(.vertical, 6)
                                    .background(isSelected ? Color.purple.opacity(0.22) : Color.clear)
                                    .clipShape(Capsule())
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(.horizontal, 8)
                }
            }
            if speechManager.isRecording || speechManager.isPreparingRecording || voiceSession.isAwaitingReply || speechOutput.isSpeaking {
                Text(voiceStatusLabel)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.purple)
            }
            HStack {
                Text(emotionLabel)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.primary)
                Spacer()
                Label("Доверие \(trustScore)", systemImage: "heart.fill")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .frame(maxWidth: .infinity)
        .background(.ultraThinMaterial)
    }

    private var activeEquippedCosmetic: String {
        guard !equippedCosmeticId.isEmpty else { return "" }
        return equippedCosmeticId
    }

    private var voiceStatusLabel: String {
        if speechManager.isPreparingRecording { return "Подключаю микрофон…" }
        if speechManager.isRecording { return "Слушаю тебя…" }
        if voiceSession.isAwaitingReply { return "Думаю…" }
        if speechOutput.isSpeaking { return "Говорю…" }
        return ""
    }

    private var emotionLabel: String {
        switch heroEmotion {
        case .listening: return "Слушаю…"
        case .speaking: return "Говорю…"
        case .thinking: return "Думаю…"
        case .alert: return "Осторожно"
        case .playful: return "Весело!"
        case .sad: return "Сочувствую…"
        case .comfort: return "Рядом с тобой"
        case .nostalgic: return "Тепло и спокойно"
        case .curious: return "Интересно!"
        case .excited: return "Ура!"
        case .celebrate: return "Ура, круто!"
        default: return "Привет!"
        }
    }

    private var fullChatHistoryScroll: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 12) {
                    if showResumeStream {
                        Button {
                            Task { await resumeStream() }
                        } label: {
                            Label("Продолжить загрузку", systemImage: "arrow.clockwise.circle.fill")
                                .font(.subheadline.bold())
                                .foregroundStyle(.purple)
                        }
                        .disabled(isSending)
                        .frame(maxWidth: .infinity, alignment: .center)
                        .padding(.vertical, 4)
                    }
                    ForEach(Array(messages.enumerated()), id: \.element.id) { idx, msg in
                        VStack(alignment: msg.isUser ? .trailing : .leading, spacing: 4) {
                            HStack {
                                if msg.isUser { Spacer() }
                                Text(msg.text)
                                    .padding(10)
                                    .background(msg.isUser ? Color.blue.opacity(0.15) : Color.gray.opacity(0.12))
                                    .clipShape(RoundedRectangle(cornerRadius: 12))
                                if !msg.isUser { Spacer() }
                            }
                            if !msg.isUser {
                                feedbackBar(for: msg, at: idx)
                            }
                        }
                        .id(msg.id)
                    }
                }
                .padding()
            }
            .onChange(of: messages.count) { _ in
                if let last = messages.last?.id {
                    withAnimation { proxy.scrollTo(last, anchor: .bottom) }
                }
            }
        }
    }

    @ToolbarContentBuilder
    private func conversationToolbarContent() -> some ToolbarContent {
        ToolbarItem(placement: .navigationBarLeading) {
            if embeddedInHome {
                EmptyView()
            } else {
                Menu {
                    Toggle(isOn: $securityExpertMode) {
                        Label("Режим эксперта безопасности", systemImage: "shield.lefthalf.filled")
                    }
                } label: {
                    Image(systemName: securityExpertMode ? "shield.lefthalf.filled" : "shield")
                }
                .accessibilityLabel("Настройки безопасности")
            }
        }
        ToolbarItem(placement: .navigationBarTrailing) {
            HStack(spacing: 16) {
                if embeddedInHome {
                    Button {
                        onOpenMineTab?()
                    } label: {
                        Image(systemName: "slider.horizontal.3")
                    }
                    .accessibilityLabel("Открыть вкладку Моё")
                } else {
                    Button {
                        showLegal = true
                    } label: {
                        Image(systemName: "doc.text")
                    }
                    .accessibilityLabel("Правила")
                    Button {
                        showCosmetics = true
                    } label: {
                        Image(systemName: "sparkles")
                    }
                    .accessibilityLabel("Наряды героя")
                }
            }
        }
    }

    @ViewBuilder
    private func feedbackBar(for msg: CompanionChatBubble, at index: Int) -> some View {
        HStack(spacing: 20) {
            feedbackButton(
                systemName: msg.feedbackVote == "up" ? "hand.thumbsup.fill" : "hand.thumbsup",
                tint: .green,
                disabled: feedbackBusyId == msg.id || msg.feedbackVote != nil
            ) {
                Task { await sendFeedback(messageIndex: index, vote: "up") }
            }
            feedbackButton(
                systemName: msg.feedbackVote == "down" ? "hand.thumbsdown.fill" : "hand.thumbsdown",
                tint: .orange,
                disabled: feedbackBusyId == msg.id || msg.feedbackVote != nil
            ) {
                Task { await sendFeedback(messageIndex: index, vote: "down") }
            }
        }
        .font(.caption)
        .padding(.leading, 4)
    }

    private func feedbackButton(
        systemName: String,
        tint: Color,
        disabled: Bool,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: action) {
            Image(systemName: systemName)
                .foregroundStyle(tint)
        }
        .disabled(disabled)
        .buttonStyle(.plain)
    }

    private var cloudAIConsentBanner: some View {
        HStack(spacing: 12) {
            Text(localizationManager.localized("ai_consent_banner_title"))
                .font(.caption.weight(.medium))
                .foregroundStyle(.primary)
            Spacer(minLength: 8)
            Button(localizationManager.localized("ai_consent_banner_action")) {
                navigationManager.navigateTo(.settings)
            }
            .font(.caption.weight(.semibold))
            .foregroundStyle(.purple)
        }
        .padding(10)
        .background(Color.orange.opacity(0.2))
    }

    private var voiceHintText: String {
        if speechManager.isPreparingRecording { return "Подключаю микрофон…" }
        if speechManager.isStoppingRecording { return "Завершаю запись…" }
        if speechManager.isMicrophoneCoolingDown { return "Подожди секунду и говори снова" }
        if speechManager.isRecording && isHoldRecording { return "Держи 1–2 сек, отпусти — герой ответит" }
        if speechManager.isRecording { return "Нажми ещё раз, чтобы остановить и отправить" }
        return "Микрофон: нажми (tap) или зажми (hold)"
    }

    private var inputBar: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 10) {
                TextField("Сообщение…", text: $input)
                    .textFieldStyle(.roundedBorder)
                    .focused($isInputFocused)
                    .submitLabel(.send)
                    .onSubmit {
                        Task { await sendText() }
                    }
                if caps.voiceRealtimeEnabled {
                    Image(systemName: voiceMicSymbol)
                        .font(.title2)
                        .foregroundStyle(voiceMicTint)
                        .frame(width: 36, height: 36)
                        .contentShape(Rectangle())
                        .onTapGesture {
                            guard !isHoldRecording else { return }
                            Task { await toggleVoice() }
                        }
                        .highPriorityGesture(
                            DragGesture(minimumDistance: 0)
                                .onChanged { value in
                                    holdWillCancel = value.translation.width < -72
                                    guard speechManager.isSpeechInputAvailable, !holdRecordingDidStart else { return }
                                    holdRecordingDidStart = true
                                    holdRecordingBeganAt = Date()
                                    isHoldRecording = true
                                    Task { await startHoldVoiceRecording() }
                                }
                                .onEnded { value in
                                    let cancel = holdWillCancel || value.translation.width < -80
                                    holdRecordingDidStart = false
                                    isHoldRecording = false
                                    holdWillCancel = false
                                    let heldSec = Date().timeIntervalSince(holdRecordingBeganAt ?? Date())
                                    holdRecordingBeganAt = nil
                                    if speechManager.isRecording {
                                        if cancel {
                                            speechManager.cancelRecording()
                                        } else if heldSec < 0.55 {
                                            speechManager.cancelRecording()
                                            errorText = "Подержи микрофон чуть дольше (около секунды) и отпусти."
                                            heroEmotion = .alert
                                        } else {
                                            speechManager.stopRecording()
                                        }
                                    }
                                }
                        )
                        .accessibilityLabel("Голосовой ввод")
                        .accessibilityHint("Нажми для старта/стопа, либо удерживай и отпусти для отправки")
                        .opacity((speechManager.isPreparingRecording || voiceSession.isAwaitingReply) ? 0.5 : 1.0)
                        .allowsHitTesting(!(speechManager.isPreparingRecording || speechManager.isStoppingRecording || speechManager.isMicrophoneCoolingDown || voiceSession.isAwaitingReply))
                }
                Button {
                    Task { await sendText() }
                } label: {
                    Image(systemName: "paperplane.fill")
                }
                .disabled(input.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isSending)
            }
            if caps.voiceRealtimeEnabled {
                Text(voiceHintText)
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
        }
        .padding()
        .background(.bar)
        .toolbar {
            ToolbarItemGroup(placement: .keyboard) {
                Spacer()
                Button("Готово") { isInputFocused = false }
            }
        }
    }

    private var voiceMicSymbol: String {
        if speechManager.isRecording || voiceSession.isConnected { return "stop.circle.fill" }
        return "mic.circle.fill"
    }

    private var voiceMicTint: Color {
        if speechManager.isRecording || voiceSession.isConnected { return .red }
        return .purple
    }

    private func loadState() async {
        if !activeThreadId.isEmpty {
            sessionId = activeThreadId
            await loadThreadHistory(threadId: activeThreadId)
        }
        do {
            async let stateTask = CompanionAPIService.shared.fetchState(characterId: characterId)
            async let profileTask = CompanionAPIService.shared.fetchProfile()
            let state = try await stateTask
            trustScore = state.trustScore
            usageSnapshot = state.usage
            heroEmotion = CompanionHeroEmotion(rawValue: state.emotionDefault) ?? .idle
            if let profile = try? await profileTask {
                let ageBand = characterId == "unicorn" ? "child" : "parent"
                personalityPreset = CompanionPersonalityPresets.effective(
                    stored: profile.personalityPreset,
                    characterId: characterId,
                    ageBand: ageBand
                )
                if let remoteEquipped = profile.equippedCosmeticId,
                   profile.equippedCosmeticCharacterId == characterId {
                    equippedCosmeticId = remoteEquipped
                }
            }
        } catch {
            errorText = error.localizedDescription
        }
        restorePendingStreamIfNeeded()
    }

    private func loadThreadHistory(threadId: String) async {
        do {
            let rows = try await CompanionAPIService.shared.fetchThreadMessages(threadId: threadId)
            messages = rows.map { CompanionChatBubble(text: $0.text, isUser: $0.role == "user") }
        } catch {
            errorText = error.localizedDescription
        }
    }

    private func resolveThreadId() -> String {
        if !activeThreadId.isEmpty { return activeThreadId }
        if !sessionId.isEmpty { return sessionId }
        let newId = "companion-\(UUID().uuidString.lowercased().replacingOccurrences(of: "-", with: "").prefix(16))"
        sessionId = newId
        return newId
    }

    private func userQuery(before index: Int) -> String? {
        guard index > 0 else { return nil }
        for i in stride(from: index - 1, through: 0, by: -1) where messages[i].isUser {
            return messages[i].text
        }
        return nil
    }

    private func sendFeedback(messageIndex: Int, vote: String) async {
        guard messages.indices.contains(messageIndex) else { return }
        let msg = messages[messageIndex]
        guard !msg.isUser else { return }

        feedbackBusyId = msg.id
        defer { feedbackBusyId = nil }

        let threadId = resolveThreadId()
        do {
            let resp = try await CompanionAPIService.shared.submitFeedback(
                vote: vote,
                characterId: characterId,
                threadId: threadId,
                messageId: msg.id.uuidString,
                assistantText: msg.text,
                userQueryText: userQuery(before: messageIndex)
            )
            if let idx = messages.firstIndex(where: { $0.id == msg.id }) {
                var updated = messages[idx]
                updated.feedbackVote = vote
                messages[idx] = updated
            }
            trustScore = resp.trustScore
            HapticFeedback.impact(.light)
        } catch {
            errorText = error.localizedDescription
        }
    }

    private func restorePendingStreamIfNeeded() {
        guard let partial = streamService.syncPendingFromDisk() else {
            showResumeStream = false
            return
        }
        showResumeStream = true
        if streamingHeroIndex == nil {
            messages.append(CompanionChatBubble(text: partial, isUser: false))
            streamingHeroIndex = messages.count - 1
        }
        heroEmotion = .thinking
    }

    private func appendStreamingHeroBubble() -> Int {
        messages.append(CompanionChatBubble(text: "", isUser: false))
        let idx = messages.count - 1
        streamingHeroIndex = idx
        return idx
    }

    private func updateStreamingBubble(at index: Int, append token: String) {
        guard messages.indices.contains(index) else { return }
        let prev = messages[index]
        messages[index] = CompanionChatBubble(
            id: prev.id,
            text: prev.text + token,
            isUser: false,
            feedbackVote: prev.feedbackVote
        )
    }

    private func finishStreamSuccess(at index: Int, meta: CompanionStreamDonePayload?) {
        streamingHeroIndex = nil
        showResumeStream = false
        streamEmotionDebouncer.cancel()
        if let meta, let score = meta.trustScore {
            trustScore = score
        }
        let content = meta?.emotion.flatMap { CompanionHeroEmotion(rawValue: $0) }
            ?? pendingStreamContentEmotion
            ?? .happy
        pendingStreamContentEmotion = nil
        let line = messages.indices.contains(index) ? messages[index].text : ""
        presentAssistantReply(line: line, contentEmotion: content)
        CompanionAnalytics.track(
            .message,
            characterId: characterId,
            sessionId: sessionId,
            extra: ["emotion": content.rawValue]
        )
        Task { await refreshUsage() }
        if messages.indices.contains(index), messages[index].text.isEmpty {
            messages[index] = CompanionChatBubble(
                id: messages[index].id,
                text: "…",
                isUser: false
            )
        }
    }

    private func handleStreamFailure(at index: Int) {
        if streamService.canResume {
            showResumeStream = true
            heroEmotion = .thinking
            return
        }
        streamingHeroIndex = nil
        showResumeStream = false
        if messages.indices.contains(index) {
            messages[index] = CompanionChatBubble(
                id: messages[index].id,
                text: "Не удалось отправить. Попробуй ещё раз.",
                isUser: false
            )
        } else {
            messages.append(CompanionChatBubble(text: "Не удалось отправить. Попробуй ещё раз.", isUser: false))
        }
        heroEmotion = .alert
    }

    private func sendText() async {
        isInputFocused = false
        let text = input.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }
        guard isCloudAIEnabled else {
            errorText = AIOutboundTextGate.GateError.optInRequired.errorDescription
            heroEmotion = .alert
            return
        }
        input = ""
        errorText = nil
        messages.append(CompanionChatBubble(text: text, isUser: true))
        isSending = true
        showResumeStream = false
        streamEmotionDebouncer.cancel()
        pendingStreamContentEmotion = nil
        heroEmotion = .thinking
        defer { isSending = false }

        let threadId = resolveThreadId()
        activeThreadId = threadId
        sessionId = threadId
        let heroIdx = appendStreamingHeroBubble()

        await streamService.streamMessage(
            message: text,
            characterId: characterId,
            sessionId: threadId,
            securityExpertMode: securityExpertMode,
            onEmotion: { name in
                applyStreamEmotion(name)
            },
            onToken: { token in
                updateStreamingBubble(at: heroIdx, append: token)
            },
            onComplete: { _, meta in
                finishStreamSuccess(at: heroIdx, meta: meta)
            },
            onError: { error in
                if let gate = error as? AIOutboundTextGate.GateError {
                    errorText = gate.errorDescription
                } else {
                    errorText = error.localizedDescription
                }
                handleStreamFailure(at: heroIdx)
            }
        )
    }

    private func resumeStream() async {
        guard let heroIdx = streamingHeroIndex else {
            let idx = appendStreamingHeroBubble()
            streamingHeroIndex = idx
            await resumeStreamAt(index: idx)
            return
        }
        await resumeStreamAt(index: heroIdx)
    }

    private func resumeStreamAt(index heroIdx: Int) async {
        isSending = true
        showResumeStream = false
        streamEmotionDebouncer.cancel()
        pendingStreamContentEmotion = nil
        heroEmotion = .thinking
        defer { isSending = false }

        await streamService.resumeInterruptedStream(
            onToken: { token in
                updateStreamingBubble(at: heroIdx, append: token)
            },
            onComplete: { _, meta in
                finishStreamSuccess(at: heroIdx, meta: meta)
            },
            onError: { error in
                if let gate = error as? AIOutboundTextGate.GateError {
                    errorText = gate.errorDescription
                } else {
                    errorText = error.localizedDescription
                }
                handleStreamFailure(at: heroIdx)
            }
        )
    }

    private func toggleVoice() async {
        isInputFocused = false
        guard !speechManager.isPreparingRecording,
              !speechManager.isStoppingRecording,
              !speechManager.isMicrophoneCoolingDown,
              !voiceSession.isAwaitingReply else { return }
        if speechManager.isRecording {
            speechManager.stopRecording()
            return
        }
        guard isCloudAIEnabled else {
            errorText = AIOutboundTextGate.GateError.optInRequired.errorDescription
            heroEmotion = .alert
            return
        }
        if voiceSession.isConnected {
            CompanionAnalytics.track(.voiceEnd, characterId: characterId, sessionId: sessionId)
            voiceSession.disconnect()
            speechOutput.stop()
            return
        }
        guard speechManager.isSpeechInputAvailable else {
            errorText = "Голосовой ввод недоступен. Проверь разрешения микрофона и распознавания речи."
            heroEmotion = .alert
            showVoiceServiceUnavailableAlert = true
            return
        }
        errorText = nil
        heroEmotion = .listening
        input = ""
        speechManager.startRecording { recognized in
            Task { await handleVoiceTranscript(recognized) }
        }
    }

    private func startHoldVoiceRecording() async {
        guard isCloudAIEnabled else {
            errorText = AIOutboundTextGate.GateError.optInRequired.errorDescription
            heroEmotion = .alert
            return
        }
        guard !speechManager.isRecording,
              !speechManager.isPreparingRecording,
              !speechManager.isStoppingRecording,
              !speechManager.isMicrophoneCoolingDown else { return }
        guard !voiceSession.isAwaitingReply else { return }
        guard speechManager.isSpeechInputAvailable else {
            errorText = "Голосовой ввод недоступен. Проверь разрешения микрофона и распознавания речи."
            heroEmotion = .alert
            showVoiceServiceUnavailableAlert = true
            return
        }
        errorText = nil
        heroEmotion = .listening
        input = ""
        speechManager.startRecording { recognized in
            Task { await handleVoiceTranscript(recognized) }
        }
    }

    private func handleVoiceTranscript(_ recognized: String?) async {
        guard let text = recognized?.trimmingCharacters(in: .whitespacesAndNewlines), !text.isEmpty else {
            heroEmotion = .alert
            errorText = "Не удалось распознать речь. Зажми микрофон на 1–2 сек, говори чётко. Проверь: Настройки → Siri и Диктовка (русский) и доступ в интернет."
            return
        }
        messages.append(CompanionChatBubble(text: text, isUser: true))
        heroEmotion = .thinking
        isSending = true
        defer { isSending = false }

        if caps.voiceRealtimeEnabled {
            do {
                let token = try await CompanionAPIService.shared.fetchEphemeralVoiceToken()
                try await voiceSession.connect(ephemeralToken: token.token)
                CompanionAnalytics.track(.voiceStart, characterId: characterId, sessionId: sessionId)
                let fid = FamilyLocalStore.loadPersistedFamilyId()
                voiceSession.sendConfig(
                    characterId: characterId,
                    securityExpertMode: securityExpertMode,
                    responseLanguage: LocalizationManager.shared.aiResponseLanguageCode,
                    familyId: fid.isEmpty ? nil : fid
                )
                voiceSession.sendAudioStop(
                    transcript: text,
                    characterId: characterId,
                    sessionId: resolveThreadId(),
                    securityExpertMode: securityExpertMode
                )
                return
            } catch {
                voiceSession.disconnect()
            }
        }

        await sendVoiceAsChat(text)
    }

    private func sendVoiceAsChat(_ text: String) async {
        do {
            let resp = try await CompanionAPIService.shared.sendChat(
                message: text,
                characterId: characterId,
                sessionId: resolveThreadId(),
                inputMode: "voice",
                securityExpertMode: securityExpertMode
            )
            handleVoiceAssistantReply(line: resp.response, emotion: CompanionHeroEmotion(rawValue: resp.emotion) ?? .happy)
            trustScore = resp.trustScore
            await refreshUsage()
            if let unlocked = resp.cosmeticUnlocked, !unlocked.isEmpty {
                equippedCosmeticId = unlocked
            }
        } catch {
            heroEmotion = .alert
            errorText = error.localizedDescription
        }
    }

    private func refreshUsage() async {
        if let state = try? await CompanionAPIService.shared.fetchState(characterId: characterId) {
            usageSnapshot = state.usage
        }
    }

    private func handleVoiceAssistantReply(line: String, emotion: CompanionHeroEmotion) {
        guard !line.isEmpty else { return }
        messages.append(CompanionChatBubble(text: line, isUser: false))
        contentEmotionAfterSpeaking = emotion
        heroEmotion = .speaking
        lipSyncPhase = 1
        speechOutput.speak(line, personalityPreset: personalityPreset, characterId: characterId)
        if voiceSession.isConnected {
            Task {
                try? await Task.sleep(nanoseconds: 1_200_000_000)
                await MainActor.run {
                    if voiceSession.isConnected {
                        voiceSession.disconnect()
                    }
                }
            }
        }
    }

    // MARK: - HERO-3-18 / HERO-3-19 — таймлайн §2.2

    /// HERO-3-23: во время `thinking`/stream лица не дёргаем — emotion только из `done` meta (+ fallback stash).
    private func applyStreamEmotion(_ name: String) {
        guard let emo = CompanionHeroEmotion(rawValue: name), emo.isStreamContentEmotion else { return }
        pendingStreamContentEmotion = emo
        guard heroEmotion != .thinking, heroEmotion != .speaking, !speechOutput.isSpeaking else { return }
        streamEmotionDebouncer.submit(emo) { heroEmotion = $0 }
    }

    /// Текстовый ответ: TTS (если включён) или `speaking` минимум 1.2 s без звука.
    private func presentAssistantReply(line: String, contentEmotion: CompanionHeroEmotion) {
        contentEmotionAfterSpeaking = contentEmotion
        let trimmed = line.trimmingCharacters(in: .whitespacesAndNewlines)
        textSpeakingDismissTask?.cancel()

        if responseTTSEnabled, !trimmed.isEmpty {
            heroEmotion = .speaking
            lipSyncPhase = 1
            speechOutput.speak(trimmed, personalityPreset: personalityPreset, characterId: characterId)
            return
        }
        applyTextOnlySpeakingVisual(contentEmotion)
    }

    private func applyTextOnlySpeakingVisual(_ content: CompanionHeroEmotion) {
        contentEmotionAfterSpeaking = content
        heroEmotion = .speaking
        lipSyncPhase = 1
        textSpeakingDismissTask = Task {
            try? await Task.sleep(nanoseconds: 1_200_000_000)
            await MainActor.run {
                guard heroEmotion == .speaking, !speechOutput.isSpeaking else { return }
                finishSpeakingPhase()
            }
        }
    }

    private func finishSpeakingPhase() {
        textSpeakingDismissTask?.cancel()
        textSpeakingDismissTask = nil
        lipSyncPhase = 0
        guard heroEmotion == .speaking else { return }
        heroEmotion = contentEmotionAfterSpeaking
    }

    private func applyVoiceSessionEmotion(_ newValue: CompanionHeroEmotion) {
        if newValue == .speaking {
            lipSyncPhase = 1
            heroEmotion = .speaking
        } else if newValue.isStreamContentEmotion {
            contentEmotionAfterSpeaking = newValue
            if !speechOutput.isSpeaking {
                heroEmotion = newValue
            }
        } else {
            heroEmotion = newValue
            if newValue != .speaking {
                lipSyncPhase = 0
            }
        }
    }
}

/// `presentationDetents` только iOS 16+; deployment target 15.2.
private struct CompanionSheetDetentsModifier: ViewModifier {
    func body(content: Content) -> some View {
        if #available(iOS 16.0, *) {
            content.presentationDetents([.medium, .large])
        } else {
            content
        }
    }
}
