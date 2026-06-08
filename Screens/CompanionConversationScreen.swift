import SwiftUI
import UIKit
import AVFoundation
import UniformTypeIdentifiers

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
    @AppStorage("companion_mic_coach_seen") private var micCoachSeen = false
    @AppStorage(CompanionSettings.heroPresencePinStorageKey) private var heroPresencePinRaw: String = CompanionSettings.HeroPresencePinMode.auto.rawValue
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
    @State private var showVoiceReconnect = false
    private struct VoiceTurnRetryContext: Equatable {
        let transcript: String
        let characterId: String
        let threadId: String
    }
    @State private var voiceRetryContext: VoiceTurnRetryContext?
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
    /// Отделяем «тап» от «удержания» — иначе DragGesture(minimumDistance: 0) + onTap дают 2× STT и 2× ответ.
    @State private var micTouchBeganAt: Date?
    @State private var micHoldArmTask: Task<Void, Never>?
    @State private var voiceCaptureActive = false
    @State private var lastVoiceSentText: String?
    @State private var lastVoiceSentAt: Date?
    @State private var lastServerSTTFallbackFailed = false
    @State private var lastServerSTTFailureDetail: String?
    @State private var showMicCoach = false
    @State private var showAssistantBusyHint = false
    @State private var showingOfflineCache = false
    @State private var lifeDomains: [CompanionLifeDomainDTO] = []
    @State private var showSocialBridgeBanner = false
    @State private var showWellnessReferralSheet = false
    @State private var companionEntryBanner: String?
    @State private var wellnessRecapLine: String?
    @State private var memoryChips: [CompanionMemoryItemDTO] = []
    @State private var memoryChipsEnabled = false
    @State private var highlightMicPulse = false
    @State private var chatMode: String = "fast"
    @State private var pendingAttachments: [CompanionAttachmentPayload] = []
    @AppStorage("companion_active_workspace_id") private var activeWorkspaceId: String = ""
    @State private var trustStreakDays: Int = 0
    @State private var lastTrustDelta: Int?
    @State private var showPhotoPicker = false
    @State private var showPdfImporter = false
    var embeddedInHome: Bool = false
    var availableCharacters: [CompanionCharacterDTO] = []
    var onSelectCharacter: ((String) -> Void)? = nil
    var onOpenMineTab: (() -> Void)? = nil
    /// AIL §6.2b: уведомляет `CompanionHomeScreen` о смене chrome (tab bar / header).
    var onPresenceChange: ((CompanionHeroLayout.ConversationPresence) -> Void)? = nil

    @State private var conversationPresence: CompanionHeroLayout.ConversationPresence = .standard
    @State private var userPinnedChrome = false
    @State private var voiceIdleExitTask: Task<Void, Never>?

    private var isCloudAIEnabled: Bool {
        AppConfig.isAIDataSharingEnabled
    }

    private var isChildProfile: Bool {
        CompanionUserContext.isChildProfile
    }

    /// Задержка перед стартом hold-to-talk у взрослого UI (короткий тап = toggle).
    private let micHoldArmDelaySec: TimeInterval = 0.35
    private let micHoldMinSec: TimeInterval = 0.55
    private let voiceSendDedupSec: TimeInterval = 3.0
    private let serverSTTCooldownSec: TimeInterval = 10.0
    @State private var lastServerSTTFallbackAt: Date?

    var body: some View {
        conversationWithLifecycle(conversationWithSheets(conversationStyledCore))
    }

    private var conversationStyledCore: some View {
        conversationBodyCore
            .background {
                if embeddedInHome {
                    Color.clear
                } else {
                    StormMeshBackground(variant: .warm)
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar(content: conversationToolbarContent)
    }

    @ViewBuilder
    private var conversationBodyCore: some View {
        VStack(spacing: 0) {
            GeometryReader { geo in
                let layout = CompanionHeroLayout.conversationMetrics(
                    contentSize: geo.size,
                    presence: conversationPresence
                )
                let bannerMode: CompanionConversationBannersSection.DisplayMode =
                    layout.presence == .immersive ? .chips : .full
                let activeWellnessPillar = WellnessSessionStore.activePillar.flatMap { WellnessPillar(rawValue: $0) }
                let wellnessMoodEmoji = WellnessSessionStore.loadCheckin().map { moodEmoji($0.mood) }
                VStack(spacing: 0) {
                    heroStage(layout: layout)
                        .contentShape(Rectangle())
                        .onTapGesture { isInputFocused = false }
                    CompanionConversationBannersSection(
                        mode: bannerMode,
                        usage: usageSnapshot,
                        wellnessPillar: activeWellnessPillar,
                        wellnessMoodEmoji: wellnessMoodEmoji,
                        companionEntryBanner: companionEntryBanner,
                        onDismissEntryBanner: {
                            WellnessSessionStore.setCompanionEntryBanner(nil)
                            companionEntryBanner = nil
                        },
                        wellnessRecapLine: wellnessRecapLine,
                        memoryChipsEnabled: memoryChipsEnabled,
                        memoryChipCount: memoryChips.count,
                        onMemoryChipTap: { showFullChatHistory = true }
                    )
                    if bannerMode == .full, memoryChipsEnabled, !memoryChips.isEmpty {
                        companionMemoryChipsRow
                    }
                    Divider().opacity(layout.presence == .immersive ? 0.05 : 0.15)
                    Group {
                        if layout.presence == .immersive {
                            companionDialogueStrip
                                .frame(height: layout.chatZoneHeight)
                                .stormGlassCard(cornerRadius: 16)
                        } else {
                            companionDialogueStrip
                                .frame(height: layout.chatZoneHeight)
                        }
                    }
                        .contentShape(Rectangle())
                        .onTapGesture { isInputFocused = false }
                }
            }
            if !isCloudAIEnabled {
                cloudAIConsentBanner
            }
            if showingOfflineCache {
                Text(localizationManager.localized("companion_offline_cached_hint"))
                    .font(.caption2)
                    .foregroundStyle(.orange)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 16)
            }
            conversationErrorBanner
            inputBar
        }
    }

    @ViewBuilder
    private var conversationErrorBanner: some View {
        if let errorText, !errorText.isEmpty {
            if showAssistantBusyHint {
                VStack(alignment: .leading, spacing: 6) {
                    Text(localizationManager.localized("companion_mic_assistant_busy"))
                        .font(.caption)
                        .foregroundStyle(.orange)
                    Button(localizationManager.localized("companion_mic_assistant_busy_action")) {
                        navigationManager.navigateTo(.aiAssistant)
                    }
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.purple)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal, 16)
                .padding(.vertical, 6)
            } else {
                Text(errorText)
                    .font(.caption)
                    .foregroundStyle(.orange)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 6)
            }
        }
    }

    @ViewBuilder
    private func conversationWithSheets<Content: View>(_ content: Content) -> some View {
        content
        .sheet(isPresented: $showLegal, onDismiss: {
            if legalAckVersion.isEmpty {
                legalAckVersion = "2026-05-30"
            }
        }) {
            NavigationView {
                CompanionLegalScreen(onAcknowledge: {
                    legalAckVersion = "2026-05-30"
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
                .navigationTitle(localizationManager.localized("companion_conversation_cosmetics"))
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .confirmationAction) {
                        Button(localizationManager.localized("companion_conversation_done")) { showCosmetics = false }
                    }
                }
            }
            .navigationViewStyle(.stack)
            .modifier(CompanionSheetDetentsModifier())
        }
        .fileImporter(
            isPresented: $showPdfImporter,
            allowedContentTypes: [.pdf],
            allowsMultipleSelection: false
        ) { result in
            Task { await ingestPdfImport(result) }
        }
        .sheet(isPresented: $showPhotoPicker) {
            ImagePickerView(sourceType: .photoLibrary) { image in
                ingestPickedImage(image)
            }
        }
        .sheet(isPresented: $showFullChatHistory) {
            NavigationView {
                fullChatHistoryScroll
                    .navigationTitle(localizationManager.localized("companion_conversation_history"))
                    .navigationBarTitleDisplayMode(.inline)
                    .toolbar {
                        ToolbarItem(placement: .confirmationAction) {
                            Button(localizationManager.localized("companion_conversation_done")) { showFullChatHistory = false }
                        }
                    }
            }
            .navigationViewStyle(.stack)
        }
        .sheet(isPresented: $showMicCoach) {
            micCoachSheet
        }
        .sheet(isPresented: $showWellnessReferralSheet) {
            WellnessReferralSheet(level: "L2")
                .environmentObject(localizationManager)
        }
    }

    @ViewBuilder
    private func conversationWithLifecycle<Content: View>(_ content: Content) -> some View {
        content
        .task { await loadState() }
        .onAppear(perform: handleConversationAppear)
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
            showAssistantBusyHint = true
            errorText = localizationManager.localized("companion_mic_assistant_busy")
            heroEmotion = .alert
        }
        .onDisappear(perform: handleConversationDisappear)
        .onChange(of: speechManager.livePartialTranscript) { partial in
            guard speechManager.isRecording || speechManager.isPreparingRecording else { return }
            if !partial.isEmpty {
                input = partial
            }
        }
        .alert(localizationManager.localized("companion_alert_mic_title"), isPresented: $showMicrophonePermissionAlert) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(localizationManager.localized("companion_alert_mic_body"))
        }
        .alert(localizationManager.localized("companion_alert_speech_title"), isPresented: $showSpeechPermissionAlert) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(localizationManager.localized("companion_alert_speech_body"))
        }
        .alert(localizationManager.localized("companion_alert_voice_title"), isPresented: $showVoiceServiceUnavailableAlert) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(localizationManager.localized("companion_alert_voice_body"))
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
            syncConversationPresence()
        }
        .onChange(of: input) { newValue in
            CompanionOfflineStore.saveDraft(characterId: characterId, text: newValue)
        }
        .onChange(of: messages.count) { _ in
            persistConversationCache()
            syncConversationPresence()
        }
        .onChange(of: characterId) { newId in
            input = CompanionOfflineStore.loadDraft(characterId: newId)
        }
        .onChange(of: speechManager.isRecording) { _ in syncConversationPresence() }
        .onChange(of: speechManager.isPreparingRecording) { _ in syncConversationPresence() }
        .onChange(of: voiceSession.isAwaitingReply) { _ in syncConversationPresence() }
        .onChange(of: heroPresencePinRaw) { _ in syncConversationPresence() }
    }

    private func handleConversationAppear() {
        companionEntryBanner = WellnessSessionStore.companionEntryBanner
        if WellnessSessionStore.consumeMicHighlight() {
            highlightMicPulse = true
            Task {
                try? await Task.sleep(nanoseconds: 8_000_000_000)
                await MainActor.run { highlightMicPulse = false }
            }
        }
        speechManager.audioSessionConsumer = .companion
        speechManager.warmUpPermissionsIfNeeded()
        voiceSession.onAssistantReply = { line, emo in
            handleVoiceAssistantReply(line: line, emotion: emo)
            if let trust = voiceSession.lastTrustScore {
                trustScore = trust
            }
        }
        voiceSession.onError = { code in
            if code == "connection_lost", voiceRetryContext != nil {
                showVoiceReconnect = true
                isSending = false
            }
            errorText = CompanionDisplayNames.voiceErrorMessage(code: code, localizationManager: localizationManager)
            heroEmotion = .alert
        }
        if input.isEmpty {
            input = CompanionOfflineStore.loadDraft(characterId: characterId)
        }
        if legalAckVersion.isEmpty {
            showLegal = true
        }
        speechOutput.onPlaybackEnded = {
            deactivateSharedAudioSessionForMic()
        }
        if !embeddedInHome {
            Task { await caps.refresh() }
        }
        if caps.voiceRealtimeEnabled && !micCoachSeen {
            showMicCoach = true
        }
        syncConversationPresence()
    }

    private func handleConversationDisappear() {
        voiceIdleExitTask?.cancel()
        voiceIdleExitTask = nil
        userPinnedChrome = false
        conversationPresence = .standard
        onPresenceChange?(.standard)
        if speechManager.isRecording {
            speechManager.stopRecording()
        }
        speechOutput.stop()
        voiceSession.disconnect()
    }

    private func deactivateSharedAudioSessionForMic() {
        VoiceAudioSessionCoordinator.shared.forceReleaseAll()
        try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
    }

    private func persistConversationCache() {
        CompanionOfflineStore.saveMessages(threadId: resolveThreadId(), messages: messages)
    }

    private var isVoiceActive: Bool {
        speechManager.isRecording
            || speechManager.isPreparingRecording
            || voiceSession.isAwaitingReply
            || speechOutput.isSpeaking
    }

    private func syncConversationPresence() {
        guard AppConfig.heroImmersiveLayoutEnabled else {
            voiceIdleExitTask?.cancel()
            voiceIdleExitTask = nil
            applyConversationPresence(.standard)
            return
        }

        if isVoiceActive {
            voiceIdleExitTask?.cancel()
            voiceIdleExitTask = nil
            if userPinnedChrome { userPinnedChrome = false }
            applyConversationPresence(.immersive)
            return
        }

        let target = CompanionHeroLayout.resolvePresence(
            messagesEmpty: messages.isEmpty,
            isVoiceActive: false,
            userPinnedChrome: userPinnedChrome,
            immersiveEnabled: true,
            pinMode: heroPresencePinMode
        )

        if conversationPresence == .immersive, target != .immersive {
            voiceIdleExitTask?.cancel()
            voiceIdleExitTask = Task { @MainActor in
                try? await Task.sleep(
                    nanoseconds: UInt64(CompanionHeroLayout.immersiveVoiceIdleDebounceSec * 1_000_000_000)
                )
                guard !Task.isCancelled else { return }
                applyConversationPresence(target)
            }
            return
        }

        voiceIdleExitTask?.cancel()
        voiceIdleExitTask = nil
        applyConversationPresence(target)
    }

    private func applyConversationPresence(_ next: CompanionHeroLayout.ConversationPresence) {
        guard next != conversationPresence else { return }
        withAnimation(.easeInOut(duration: 0.25)) {
            conversationPresence = next
        }
        onPresenceChange?(next)
    }

    private func pinChromeFromImmersive() {
        userPinnedChrome = true
        voiceIdleExitTask?.cancel()
        voiceIdleExitTask = nil
        let next = CompanionHeroLayout.resolvePresence(
            messagesEmpty: messages.isEmpty,
            isVoiceActive: false,
            userPinnedChrome: true,
            immersiveEnabled: AppConfig.heroImmersiveLayoutEnabled,
            pinMode: heroPresencePinMode
        )
        applyConversationPresence(next)
    }

    private var heroPresencePinMode: CompanionSettings.HeroPresencePinMode {
        CompanionSettings.HeroPresencePinMode(rawValue: heroPresencePinRaw) ?? .auto
    }

    /// Сцена виртуального друга — AIL §6.2b (standard / focused / immersive).
    private func heroStage(layout: CompanionHeroLayout.ConversationMetrics) -> some View {
        ZStack(alignment: layout.statusOverlayAtTop ? .top : .bottom) {
            if layout.presence != .immersive {
                Color(.systemGroupedBackground).opacity(0.3)
            }
            CompanionHeroAvatarView(
                characterId: characterId,
                emotion: heroEmotion,
                lipSyncPhase: lipSyncPhase,
                equippedCosmeticId: activeEquippedCosmetic,
                stageStyle: .conversationFullBody,
                stageContentMode: layout.contentMode,
                stageSize: layout.stageSize
            )
            .padding(.horizontal, CompanionHeroLayout.stageHorizontalPadding)
            .padding(.top, layout.statusOverlayAtTop ? CompanionHeroLayout.heroStatusOverlayHeight + 4 : 6)
            .padding(.bottom, layout.stageBottomInset)
            .accessibilityIdentifier("companion_hero_stage")
            if isChildProfile && caps.voiceRealtimeEnabled && embeddedInHome {
                VStack {
                    Spacer()
                    childSceneSpeakButton
                        .padding(.bottom, layout.stageBottomInset + 12)
                }
            }
            heroStatusOverlay
        }
        .overlay(alignment: .top) {
            if layout.presence == .immersive {
                Button(action: pinChromeFromImmersive) {
                    Color.clear
                        .frame(maxWidth: .infinity)
                        .frame(height: 48)
                        .contentShape(Rectangle())
                }
                .buttonStyle(.plain)
                .accessibilityLabel(localizationManager.localized("companion_immersive_show_chrome"))
                .accessibilityIdentifier("companion_immersive_chrome_exit")
            }
        }
        .frame(height: layout.heroZoneHeight)
        .frame(maxWidth: .infinity)
        .clipped()
        .animation(.easeInOut(duration: 0.25), value: layout.presence)
    }

    private var companionDialogueStrip: some View {
        CompanionDialogueStrip(
            messages: messages,
            showResumeStream: showResumeStream,
            showVoiceReconnect: showVoiceReconnect,
            isSending: isSending,
            feedbackBusyId: feedbackBusyId,
            onResume: { Task { await resumeStream() } },
            onVoiceReconnect: { Task { await retryVoiceRealtime() } },
            onShowHistory: { showFullChatHistory = true },
            onFeedback: { index, vote in
                Task { await sendFeedback(messageIndex: index, vote: vote) }
            },
            onActionTap: { action in
                handleWellnessAction(action)
            }
        )
    }

    private func handleWellnessAction(_ action: CompanionSuggestedActionDTO) {
        if let url = AIActionCardMapper.phoneURL(for: action.id) {
            UIApplication.shared.open(url)
            return
        }
        if AIActionCardMapper.opensReferralSheet(action.id) {
            showWellnessReferralSheet = true
            return
        }
        if let screen = AIActionCardMapper.screen(for: action.id) {
            navigationManager.navigateTo(screen)
        }
    }

    private func attachSuggestedActions(at index: Int, actions: [CompanionSuggestedActionDTO]?) {
        guard messages.indices.contains(index), let actions, !actions.isEmpty else { return }
        var bubble = messages[index]
        bubble.suggestedActions = actions
        messages[index] = bubble
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
            if isChildProfile {
                HStack {
                    Spacer()
                    Button {
                        onOpenMineTab?()
                    } label: {
                        Label("\(trustScore)", systemImage: "heart.fill")
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(.secondary)
                    }
                    .buttonStyle(.plain)
                    .accessibilityLabel("Trust \(trustScore)")
                }
            } else {
                HStack {
                    Text(emotionLabel)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(.primary)
                    Spacer()
                    Label(String(format: localizationManager.localized("companion_conversation_trust"), trustScore), systemImage: "heart.fill")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    if let lastTrustDelta, lastTrustDelta > 0 {
                        Text(
                            String(
                                format: localizationManager.localized("companion_trust_delta_gain"),
                                lastTrustDelta
                            )
                        )
                        .font(.caption2.weight(.semibold))
                        .foregroundStyle(.green)
                    }
                }
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .frame(maxWidth: .infinity)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
    }

    private var activeEquippedCosmetic: String {
        guard !equippedCosmeticId.isEmpty else { return "" }
        return equippedCosmeticId
    }

    private var voiceStatusLabel: String {
        if speechManager.isPreparingRecording { return localizationManager.localized("companion_voice_preparing") }
        if speechManager.isRecording { return localizationManager.localized("companion_voice_listening") }
        if voiceSession.isAwaitingReply { return localizationManager.localized("companion_voice_thinking") }
        if speechOutput.isSpeaking { return localizationManager.localized("companion_voice_speaking") }
        return ""
    }

    private var emotionLabel: String {
        switch heroEmotion {
        case .listening: return localizationManager.localized("companion_emotion_listening")
        case .speaking: return localizationManager.localized("companion_emotion_speaking")
        case .thinking: return localizationManager.localized("companion_emotion_thinking")
        case .alert: return localizationManager.localized("companion_emotion_alert")
        case .playful: return localizationManager.localized("companion_emotion_playful")
        case .sad: return localizationManager.localized("companion_emotion_sad")
        case .comfort: return localizationManager.localized("companion_emotion_comfort")
        case .nostalgic: return localizationManager.localized("companion_emotion_nostalgic")
        case .curious: return localizationManager.localized("companion_emotion_curious")
        case .excited: return localizationManager.localized("companion_emotion_excited")
        case .celebrate: return localizationManager.localized("companion_emotion_celebrate")
        default: return localizationManager.localized("companion_emotion_happy")
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
                            Label(localizationManager.localized("companion_conversation_resume_stream"), systemImage: "arrow.clockwise.circle.fill")
                                .font(.subheadline.bold())
                                .foregroundStyle(.purple)
                        }
                        .disabled(isSending)
                        .frame(maxWidth: .infinity, alignment: .center)
                        .padding(.vertical, 4)
                    }
                    if showVoiceReconnect {
                        Button {
                            Task { await retryVoiceRealtime() }
                        } label: {
                            Label(localizationManager.localized("companion_conversation_resume_voice"), systemImage: "mic.circle.fill")
                                .font(.subheadline.bold())
                                .foregroundStyle(.orange)
                        }
                        .disabled(isSending)
                        .frame(maxWidth: .infinity, alignment: .center)
                        .padding(.vertical, 4)
                        .accessibilityIdentifier("companion_resume_voice_button_history")
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
                        Label(localizationManager.localized("companion_conversation_security_expert"), systemImage: "shield.lefthalf.filled")
                    }
                } label: {
                    Image(systemName: securityExpertMode ? "shield.lefthalf.filled" : "shield")
                }
                .accessibilityLabel(localizationManager.localized("companion_conversation_security_expert"))
            }
        }
        ToolbarItem(placement: .navigationBarTrailing) {
            HStack(spacing: 16) {
                if !isChildProfile {
                    Menu {
                        Button { chatMode = "fast" } label: {
                            Label(localizationManager.localized("companion_mode_fast"), systemImage: chatMode == "fast" ? "checkmark" : "bolt")
                        }
                        Button { chatMode = "reasoning" } label: {
                            Label(localizationManager.localized("companion_mode_reasoning"), systemImage: chatMode == "reasoning" ? "checkmark" : "brain")
                        }
                        Button { chatMode = "think" } label: {
                            Label(localizationManager.localized("companion_mode_think"), systemImage: chatMode == "think" ? "checkmark" : "sparkles")
                        }
                    } label: {
                        Image(systemName: "slider.horizontal.2.square")
                    }
                    .accessibilityLabel(localizationManager.localized("companion_mode_picker"))
                }
                if embeddedInHome {
                    Button {
                        onOpenMineTab?()
                    } label: {
                        Image(systemName: "slider.horizontal.3")
                    }
                    .accessibilityLabel(localizationManager.localized("companion_conversation_mine_tab"))
                } else {
                    Button {
                        showLegal = true
                    } label: {
                        Image(systemName: "doc.text")
                    }
                    .accessibilityLabel(localizationManager.localized("companion_conversation_rules"))
                    Button {
                        showCosmetics = true
                    } label: {
                        Image(systemName: "sparkles")
                    }
                    .accessibilityLabel(localizationManager.localized("companion_conversation_cosmetics"))
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
                label: localizationManager.localized("companion_feedback_up"),
                disabled: feedbackBusyId == msg.id || msg.feedbackVote != nil
            ) {
                Task { await sendFeedback(messageIndex: index, vote: "up") }
            }
            feedbackButton(
                systemName: msg.feedbackVote == "down" ? "hand.thumbsdown.fill" : "hand.thumbsdown",
                tint: .orange,
                label: localizationManager.localized("companion_feedback_down"),
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
        label: String,
        disabled: Bool,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: action) {
            Image(systemName: systemName)
                .foregroundStyle(tint)
        }
        .disabled(disabled)
        .buttonStyle(.plain)
        .accessibilityLabel(label)
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
        if isChildProfile {
            if speechManager.isPreparingRecording { return localizationManager.localized("companion_mic_coach_step1") }
            if speechManager.isRecording && isHoldRecording { return localizationManager.localized("companion_mic_coach_step3") }
            if speechManager.isRecording { return localizationManager.localized("companion_mic_hold_hint_child") }
            return localizationManager.localized("companion_mic_hold_hint_child")
        }
        if speechManager.isPreparingRecording { return localizationManager.localized("companion_voice_preparing") }
        if speechManager.isStoppingRecording { return localizationManager.localized("companion_voice_stopping") }
        if speechManager.isMicrophoneCoolingDown { return localizationManager.localized("companion_voice_cooldown") }
        if speechManager.isRecording && isHoldRecording { return localizationManager.localized("companion_voice_hold_hint") }
        if speechManager.isRecording { return localizationManager.localized("companion_voice_tap_stop") }
        return localizationManager.localized("companion_voice_mic_modes")
    }

    private var childSceneSpeakButton: some View {
        Text(localizationManager.localized("companion_mic_speak_button"))
            .font(.title3.bold())
            .foregroundStyle(.white)
            .padding(.horizontal, 28)
            .padding(.vertical, 14)
            .background(
                Capsule()
                    .fill(speechManager.isRecording ? Color.red : Color.purple)
            )
            .scaleEffect(isHoldRecording ? 1.06 : (highlightMicPulse ? 1.08 : 1.0))
            .animation(.easeInOut(duration: 0.15), value: isHoldRecording)
            .animation(highlightMicPulse ? .easeInOut(duration: 0.8).repeatForever(autoreverses: true) : .default, value: highlightMicPulse)
            .overlay {
                if highlightMicPulse {
                    Capsule()
                        .stroke(Color.mint, lineWidth: 3)
                        .scaleEffect(1.12)
                        .opacity(0.85)
                }
            }
            .accessibilityIdentifier("companion_child_speak_button")
            .accessibilityLabel(localizationManager.localized("companion_mic_speak_button"))
            .accessibilityHint(localizationManager.localized("companion_mic_hold_hint_child"))
            .highPriorityGesture(companionMicDragGesture(childImmediateHold: true))
            .opacity((speechManager.isPreparingRecording || voiceSession.isAwaitingReply || speechOutput.isSpeaking) ? 0.5 : 1.0)
            .allowsHitTesting(!(speechManager.isPreparingRecording || speechManager.isStoppingRecording || speechManager.isMicrophoneCoolingDown || voiceSession.isAwaitingReply || speechOutput.isSpeaking))
    }

    private var micCoachSheet: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: 20) {
                Text("🎤")
                    .font(.system(size: 56))
                    .frame(maxWidth: .infinity)
                Text(localizationManager.localized("companion_mic_coach_title"))
                    .font(.title2.bold())
                VStack(alignment: .leading, spacing: 12) {
                    Text(localizationManager.localized("companion_mic_coach_step1"))
                    Text(localizationManager.localized("companion_mic_coach_step2"))
                    Text(localizationManager.localized("companion_mic_coach_step3"))
                }
                .font(.body)
                Spacer()
                Button {
                    micCoachSeen = true
                    showMicCoach = false
                } label: {
                    Text(localizationManager.localized("companion_mic_coach_done"))
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.purple)
                        .foregroundColor(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 14))
                }
                .accessibilityIdentifier("companion_mic_coach_done_button")
            }
            .padding(24)
            .navigationBarTitleDisplayMode(.inline)
        }
        .navigationViewStyle(.stack)
        .modifier(CompanionSheetDetentsModifier())
    }

    private var domainTopicChips: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(localizationManager.localized("companion_domains_title"))
                .font(.caption.weight(.semibold))
                .foregroundStyle(.secondary)
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(lifeDomains) { domain in
                        Button {
                            input = domain.starterPrompt
                            isInputFocused = true
                        } label: {
                            Text(domain.label)
                                .font(.caption.weight(.medium))
                                .padding(.horizontal, 12)
                                .padding(.vertical, 8)
                                .background(Color.purple.opacity(0.12))
                                .clipShape(Capsule())
                        }
                        .accessibilityLabel(domain.label)
                        .accessibilityHint(domain.starterPrompt)
                    }
                }
            }
        }
    }

    private var socialBridgeBanner: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(localizationManager.localized("companion_social_bridge_title"))
                .font(.caption.weight(.semibold))
            Text(localizationManager.localized("companion_social_bridge_body"))
                .font(.caption2)
                .foregroundStyle(.secondary)
            Button {
                showSocialBridgeBanner = false
            } label: {
                Text(localizationManager.localized("companion_social_bridge_dismiss"))
                    .font(.caption.weight(.semibold))
            }
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.blue.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 10))
        .accessibilityElement(children: .combine)
    }

    private var inputBar: some View {
        VStack(alignment: .leading, spacing: 6) {
            if showSocialBridgeBanner {
                socialBridgeBanner
            }
            if !lifeDomains.isEmpty && messages.isEmpty {
                domainTopicChips
            }
            if trustStreakDays >= 3 {
                Text(localizationManager.localized("companion_trust_streak", trustStreakDays))
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
            if !pendingAttachments.isEmpty {
                Text(
                    String(
                        format: localizationManager.localized("companion_attach_pending"),
                        pendingAttachments.count
                    )
                )
                .font(.caption2)
                .foregroundStyle(.secondary)
            }
            HStack(spacing: 10) {
                if !isChildProfile {
                    attachmentPickerMenu
                }
                TextField(localizationManager.localized("companion_conversation_message_placeholder"), text: $input)
                    .textFieldStyle(.roundedBorder)
                    .focused($isInputFocused)
                    .submitLabel(.send)
                    .accessibilityIdentifier("companion_message_input")
                    .onSubmit {
                        Task { await sendText() }
                    }
                if caps.voiceRealtimeEnabled {
                    Image(systemName: voiceMicSymbol)
                        .font(.title2)
                        .foregroundStyle(voiceMicTint)
                        .frame(width: 36, height: 36)
                        .contentShape(Rectangle())
                        .highPriorityGesture(companionMicDragGesture(childImmediateHold: false))
                        .accessibilityLabel(isChildProfile
                            ? localizationManager.localized("companion_mic_speak_button")
                            : localizationManager.localized("companion_voice_input_label"))
                        .accessibilityHint(isChildProfile
                            ? localizationManager.localized("companion_mic_hold_hint_child")
                            : localizationManager.localized("companion_voice_input_hint"))
                        .opacity((speechManager.isPreparingRecording || voiceSession.isAwaitingReply || speechOutput.isSpeaking) ? 0.5 : 1.0)
                        .allowsHitTesting(!(speechManager.isPreparingRecording || speechManager.isStoppingRecording || speechManager.isMicrophoneCoolingDown || voiceSession.isAwaitingReply || speechOutput.isSpeaking))
                }
                Button {
                    Task { await sendText() }
                } label: {
                    Image(systemName: "paperplane.fill")
                }
                .disabled(input.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isSending)
                .accessibilityIdentifier("companion_send_button")
                .accessibilityLabel(localizationManager.localized("companion_conversation_send"))
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
                Button(localizationManager.localized("companion_conversation_done")) { isInputFocused = false }
            }
        }
    }

    private var attachmentPickerMenu: some View {
        Menu {
            Button {
                showPhotoPicker = true
            } label: {
                Label(
                    localizationManager.localized("companion_attach_photo"),
                    systemImage: "photo"
                )
            }
            Button {
                showPdfImporter = true
            } label: {
                Label(
                    localizationManager.localized("companion_attach_pdf"),
                    systemImage: "doc"
                )
            }
            if !pendingAttachments.isEmpty {
                Button(role: .destructive) {
                    pendingAttachments = []
                } label: {
                    Label(
                        localizationManager.localized("companion_attach_clear"),
                        systemImage: "xmark.circle"
                    )
                }
            }
        } label: {
            Image(systemName: "paperclip")
        }
        .accessibilityLabel(localizationManager.localized("companion_attach_menu"))
    }

    private static let attachmentMaxBytes = 300_000

    private func ingestPickedImage(_ image: UIImage) {
        guard let data = image.jpegData(compressionQuality: 0.85) else {
            errorText = localizationManager.localized("companion_attach_error")
            return
        }
        guard data.count <= Self.attachmentMaxBytes else {
            errorText = localizationManager.localized("companion_attach_too_large")
            return
        }
        pendingAttachments = [
            CompanionAttachmentPayload(
                kind: "image",
                filename: "photo.jpg",
                mimeType: "image/jpeg",
                contentB64: data.base64EncodedString()
            )
        ]
    }

    private func ingestPdfImport(_ result: Result<[URL], Error>) async {
        switch result {
        case .failure(let error):
            errorText = error.localizedDescription
        case .success(let urls):
            guard let url = urls.first else { return }
            guard url.startAccessingSecurityScopedResource() else {
                errorText = localizationManager.localized("companion_attach_error")
                return
            }
            defer { url.stopAccessingSecurityScopedResource() }
            do {
                let data = try Data(contentsOf: url)
                guard data.count <= Self.attachmentMaxBytes else {
                    errorText = localizationManager.localized("companion_attach_too_large")
                    return
                }
                pendingAttachments = [
                    CompanionAttachmentPayload(
                        kind: "pdf",
                        filename: url.lastPathComponent,
                        mimeType: "application/pdf",
                        contentB64: data.base64EncodedString()
                    )
                ]
            } catch {
                errorText = error.localizedDescription
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
            async let domainsTask = CompanionAPIService.shared.fetchLifeDomains(
                locale: LocalizationManager.shared.aiResponseLanguageCode,
                securityExpertMode: securityExpertMode
            )
            let state = try await stateTask
            lifeDomains = (try? await domainsTask) ?? []
            trustScore = state.trustScore
            usageSnapshot = state.usage
            heroEmotion = CompanionHeroEmotion(rawValue: state.emotionDefault) ?? .idle
            if let profile = try? await profileTask {
                let ageBand = CompanionUserContext.companionAgeBand
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
            errorText = CompanionErrorMapper.message(for: error, localizationManager: localizationManager)
        }
        await loadWellnessRecapIfNeeded()
        await loadCompanionMemoryChipsIfNeeded()
        restorePendingStreamIfNeeded()
        await MainActor.run { syncConversationPresence() }
    }

    private var companionMemoryChipsRow: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(localizationManager.localized("companion_memory_chips_label"))
                .font(.caption2.weight(.semibold))
                .foregroundStyle(.secondary)
                .padding(.horizontal, 14)
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(memoryChips.prefix(6)) { item in
                        Text(item.summary)
                            .font(.caption2)
                            .lineLimit(2)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 6)
                            .background(Color(hex: "6366F1").opacity(0.12))
                            .clipShape(Capsule())
                            .accessibilityIdentifier("companion_memory_chip")
                    }
                }
                .padding(.horizontal, 14)
            }
        }
        .padding(.vertical, 4)
        .accessibilityIdentifier("companion_memory_chips_row")
    }

    private func loadCompanionMemoryChipsIfNeeded() async {
        guard !isChildProfile else {
            memoryChipsEnabled = false
            memoryChips = []
            return
        }
        do {
            let resp = try await CompanionAPIService.shared.fetchMemory()
            memoryChipsEnabled = resp.memoryEnabled
            memoryChips = resp.items
        } catch {
            memoryChipsEnabled = false
            memoryChips = []
        }
    }

    private func loadWellnessRecapIfNeeded() async {
        guard WellnessSessionStore.hasAcceptedConsent else {
            wellnessRecapLine = nil
            return
        }
        if let cached = WellnessOfflineStore.loadRecap() {
            wellnessRecapLine = companionRecapDisplayLine(from: cached)
        }
        do {
            let recap = try await WellnessAPIService.shared.fetchSessionRecap()
            WellnessOfflineStore.saveRecap(recap)
            wellnessRecapLine = companionRecapDisplayLine(from: recap)
        } catch {
            // keep cached line if any
        }
    }

    private func companionRecapDisplayLine(from recap: WellnessSessionRecapResponse) -> String? {
        let raw: String?
        if let cont = recap.continuityMessage, !cont.isEmpty {
            raw = cont
        } else if let msg = recap.message, !msg.isEmpty {
            raw = msg
        } else {
            return nil
        }
        guard let raw else { return nil }
        return String(format: localizationManager.localized("wellness_recap_prefix"), raw)
    }

    private func loadThreadHistory(threadId: String) async {
        do {
            let rows = try await CompanionAPIService.shared.fetchThreadMessages(threadId: threadId)
            messages = rows.map { CompanionChatBubble(text: $0.text, isUser: $0.role == "user") }
            showingOfflineCache = false
            persistConversationCache()
        } catch {
            let cached = CompanionOfflineStore.loadMessages(threadId: threadId)
            if !cached.isEmpty {
                messages = cached
                showingOfflineCache = true
            } else {
                errorText = CompanionErrorMapper.message(for: error, localizationManager: localizationManager)
            }
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
            errorText = CompanionErrorMapper.message(for: error, localizationManager: localizationManager)
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

    private func moodEmoji(_ mood: String) -> String {
        switch mood {
        case "great": return "😊"
        case "sad": return "😢"
        case "anxious": return "😰"
        case "tired": return "😴"
        default: return "🙂"
        }
    }

    private func applySocialBridge(from meta: CompanionStreamDonePayload?) {
        if meta?.showSocialBridge == true {
            showSocialBridgeBanner = true
        }
    }

    private func applySocialBridge(from response: CompanionChatResponse) {
        if response.showSocialBridge == true {
            showSocialBridgeBanner = true
        }
    }

    private func finishStreamSuccess(at index: Int, meta: CompanionStreamDonePayload?) {
        streamingHeroIndex = nil
        showResumeStream = false
        streamEmotionDebouncer.cancel()
        applySocialBridge(from: meta)
        attachSuggestedActions(at: index, actions: meta?.suggestedActions)
        if let meta, let score = meta.trustScore {
            trustScore = score
        }
        if let meta, let streak = meta.trustStreakDays {
            trustStreakDays = streak
        }
        if let meta, let delta = meta.trustDelta, delta > 0 {
            lastTrustDelta = delta
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
                text: localizationManager.localized("companion_conversation_send_failed"),
                isUser: false
            )
        } else {
            messages.append(CompanionChatBubble(text: localizationManager.localized("companion_conversation_send_failed"), isUser: false))
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

        let attachmentsForSend = pendingAttachments
        pendingAttachments = []
        await streamService.streamMessage(
            message: text,
            characterId: characterId,
            sessionId: threadId,
            securityExpertMode: securityExpertMode,
            chatMode: chatMode,
            workspaceId: activeWorkspaceId.isEmpty ? nil : activeWorkspaceId,
            attachments: attachmentsForSend,
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
                    errorText = CompanionErrorMapper.message(for: error, localizationManager: localizationManager)
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
                    errorText = CompanionErrorMapper.message(for: error, localizationManager: localizationManager)
                }
                handleStreamFailure(at: heroIdx)
            }
        )
    }

    private func companionMicDragGesture(childImmediateHold: Bool) -> some Gesture {
        DragGesture(minimumDistance: 0)
            .onChanged { value in
                if !childImmediateHold {
                    holdWillCancel = value.translation.width < -72
                }
                if micTouchBeganAt == nil {
                    micTouchBeganAt = Date()
                }
                scheduleMicHoldRecordingStart(immediate: childImmediateHold)
            }
            .onEnded { value in
                let cancel = !childImmediateHold && (holdWillCancel || value.translation.width < -80)
                Task { await finishMicPress(cancelSlide: cancel, childImmediateHold: childImmediateHold) }
            }
    }

    private func cancelMicHoldArmTask() {
        micHoldArmTask?.cancel()
        micHoldArmTask = nil
    }

    private func scheduleMicHoldRecordingStart(immediate: Bool) {
        guard speechManager.isSpeechInputAvailable,
              !holdRecordingDidStart,
              !voiceCaptureActive,
              !speechManager.isRecording,
              !speechManager.isPreparingRecording,
              !speechManager.isStoppingRecording,
              !speechManager.isMicrophoneCoolingDown,
              !speechOutput.isSpeaking,
              !voiceSession.isAwaitingReply else { return }

        if immediate {
            holdRecordingDidStart = true
            holdRecordingBeganAt = micTouchBeganAt ?? Date()
            isHoldRecording = true
            Task { await startHoldVoiceRecording() }
            return
        }

        guard micHoldArmTask == nil else { return }
        micHoldArmTask = Task {
            defer { Task { @MainActor in micHoldArmTask = nil } }
            try? await Task.sleep(nanoseconds: UInt64(micHoldArmDelaySec * 1_000_000_000))
            guard !Task.isCancelled else { return }
            await MainActor.run {
                guard micTouchBeganAt != nil, !holdRecordingDidStart, !voiceCaptureActive else { return }
                holdRecordingDidStart = true
                holdRecordingBeganAt = micTouchBeganAt ?? Date()
                isHoldRecording = true
            }
            await startHoldVoiceRecording()
        }
    }

    private func finishMicPress(cancelSlide: Bool, childImmediateHold: Bool) async {
        cancelMicHoldArmTask()
        let pressBegan = micTouchBeganAt
        micTouchBeganAt = nil
        let heldSec = Date().timeIntervalSince(pressBegan ?? holdRecordingBeganAt ?? Date())
        let wasCapturing = holdRecordingDidStart || speechManager.isRecording || speechManager.isPreparingRecording

        defer {
            holdRecordingDidStart = false
            isHoldRecording = false
            holdWillCancel = false
            holdRecordingBeganAt = nil
        }

        if wasCapturing || speechManager.isRecording {
            if cancelSlide {
                speechManager.cancelRecording()
                return
            }
            if heldSec < micHoldMinSec {
                speechManager.cancelRecording()
                errorText = childImmediateHold
                    ? localizationManager.localized("companion_mic_hold_hint_child")
                    : localizationManager.localized("companion_voice_hold_too_short")
                heroEmotion = .alert
                return
            }
            speechManager.stopRecording()
            return
        }

        // Короткий тап без hold — режим toggle (только взрослый UI).
        if !childImmediateHold, heldSec < micHoldArmDelaySec + 0.08 {
            await toggleVoice()
        }
    }

    private func toggleVoice() async {
        isInputFocused = false
        guard !speechManager.isPreparingRecording,
              !speechManager.isStoppingRecording,
              !speechManager.isMicrophoneCoolingDown,
              !voiceSession.isAwaitingReply,
              !speechOutput.isSpeaking,
              !voiceCaptureActive else { return }
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
            errorText = localizationManager.localized("companion_voice_unavailable")
            heroEmotion = .alert
            showVoiceServiceUnavailableAlert = true
            return
        }
        await beginVoiceCapture()
    }

    private func startHoldVoiceRecording() async {
        guard isCloudAIEnabled else {
            errorText = AIOutboundTextGate.GateError.optInRequired.errorDescription
            heroEmotion = .alert
            return
        }
        guard !voiceCaptureActive,
              !speechManager.isRecording,
              !speechManager.isPreparingRecording,
              !speechManager.isStoppingRecording,
              !speechManager.isMicrophoneCoolingDown,
              !speechOutput.isSpeaking else { return }
        guard !voiceSession.isAwaitingReply else { return }
        guard speechManager.isSpeechInputAvailable else {
            errorText = localizationManager.localized("companion_voice_unavailable")
            heroEmotion = .alert
            showVoiceServiceUnavailableAlert = true
            return
        }
        await beginVoiceCapture()
    }

    private func beginVoiceCapture() async {
        guard !voiceCaptureActive else { return }
        voiceCaptureActive = true
        errorText = nil
        lastServerSTTFallbackFailed = false
        lastServerSTTFailureDetail = nil
        heroEmotion = .listening
        input = ""
        prepareMicForRecording()
        speechManager.startRecording { recognized in
            Task {
                defer { voiceCaptureActive = false }
                await handleVoiceTranscript(recognized)
            }
        }
    }

    private func prepareMicForRecording() {
        speechOutput.stop()
        if voiceSession.isConnected {
            voiceSession.disconnect()
        }
        deactivateSharedAudioSessionForMic()
    }

    private func handleVoiceTranscript(_ recognized: String?) async {
        var text = recognized?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        if text.isEmpty {
            text = await tryServerSTTFallbackIfEligible() ?? ""
        }
        guard !text.isEmpty else {
            heroEmotion = .alert
            if !speechManager.hadAudioSignalDuringLastSession {
                errorText = localizationManager.localized("companion_voice_no_audio_signal")
            } else if speechManager.lastRecognitionFailure == .serviceUnavailable {
                errorText = localizationManager.localized("ai_assistant_voice_service_unavailable")
            } else if speechManager.lastRecognitionFailure == .recordingTooShort {
                errorText = localizationManager.localized("companion_voice_hold_too_short")
            } else if lastServerSTTFallbackFailed {
                if lastServerSTTFailureDetail == "server_stt_geo_blocked" {
                    errorText = localizationManager.localized("companion_voice_server_stt_geo_blocked")
                } else {
                    errorText = localizationManager.localized("companion_voice_server_stt_unavailable")
                }
            } else if !isCloudAIEnabled {
                errorText = AIOutboundTextGate.GateError.optInRequired.errorDescription
            } else {
                errorText = localizationManager.localized("companion_voice_recognition_failed")
            }
            return
        }
        if let last = lastVoiceSentText,
           let sentAt = lastVoiceSentAt,
           last == text,
           Date().timeIntervalSince(sentAt) < voiceSendDedupSec {
            return
        }
        guard !isSending else { return }
        lastVoiceSentText = text
        lastVoiceSentAt = Date()
        messages.append(CompanionChatBubble(text: text, isUser: true))
        heroEmotion = .thinking
        isSending = true
        defer { isSending = false }

        let threadId = resolveThreadId()
        voiceRetryContext = VoiceTurnRetryContext(
            transcript: text,
            characterId: characterId,
            threadId: threadId
        )
        showVoiceReconnect = false

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
                    sessionId: threadId,
                    securityExpertMode: securityExpertMode
                )
                return
            } catch {
                voiceSession.disconnect()
                await sendVoiceAsChat(text)
                return
            }
        }

        await sendVoiceAsChat(text)
    }

    /// r100-5-voice — повтор WS-хода или fallback в текстовый чат.
    private func retryVoiceRealtime() async {
        guard let ctx = voiceRetryContext else {
            showVoiceReconnect = false
            return
        }
        showVoiceReconnect = false
        isSending = true
        heroEmotion = .thinking
        errorText = nil
        defer { isSending = false }

        if caps.voiceRealtimeEnabled {
            do {
                let token = try await CompanionAPIService.shared.fetchEphemeralVoiceToken()
                try await voiceSession.connect(ephemeralToken: token.token)
                let fid = FamilyLocalStore.loadPersistedFamilyId()
                voiceSession.sendConfig(
                    characterId: ctx.characterId,
                    securityExpertMode: securityExpertMode,
                    responseLanguage: LocalizationManager.shared.aiResponseLanguageCode,
                    familyId: fid.isEmpty ? nil : fid
                )
                if voiceSession.resendPendingStopIfAny() {
                    return
                }
                voiceSession.sendAudioStop(
                    transcript: ctx.transcript,
                    characterId: ctx.characterId,
                    sessionId: ctx.threadId,
                    securityExpertMode: securityExpertMode
                )
                return
            } catch {
                voiceSession.disconnect()
            }
        }
        await sendVoiceAsChat(ctx.transcript)
    }

    /// Apple STT failed — one server fallback attempt (Whisper on ALADDIN VPS, audio not retained server-side).
    private func tryServerSTTFallbackIfEligible() async -> String? {
        guard isCloudAIEnabled else { return nil }
        guard caps.serverSttFallbackEnabled else { return nil }
        guard speechManager.hadAudioSignalDuringLastSession else { return nil }
        if let last = lastServerSTTFallbackAt,
           Date().timeIntervalSince(last) < serverSTTCooldownSec {
            return nil
        }
        guard let wav = speechManager.takeFallbackWAVData(), wav.count > 44 else { return nil }

        lastServerSTTFallbackAt = Date()
        heroEmotion = .thinking
        errorText = localizationManager.localized("companion_voice_server_stt_processing")

        do {
            let response = try await CompanionAPIService.shared.transcribeVoiceFallback(
                audioWAV: wav,
                characterId: characterId,
                sessionId: resolveThreadId()
            )
            let trimmed = response.text.trimmingCharacters(in: .whitespacesAndNewlines)
            guard !trimmed.isEmpty else { return nil }
            if let prepared = try? AIOutboundTextGate.prepareUserMessage(trimmed) {
                return prepared.displayText
            }
            return trimmed
        } catch {
            lastServerSTTFallbackFailed = true
            let detail = error.localizedDescription.lowercased()
            if detail.contains("server_stt_geo_blocked") || detail.contains("geo_blocked") {
                lastServerSTTFailureDetail = "server_stt_geo_blocked"
            } else {
                lastServerSTTFailureDetail = nil
            }
            MasterLogger.shared.warn("Companion server STT fallback failed: \(error.localizedDescription)")
            return nil
        }
    }

    private func sendVoiceAsChat(_ text: String) async {
        do {
            let resp = try await CompanionAPIService.shared.sendChat(
                message: text,
                characterId: characterId,
                sessionId: resolveThreadId(),
                inputMode: "voice",
                securityExpertMode: securityExpertMode,
                chatMode: chatMode,
                attachments: pendingAttachments
            )
            pendingAttachments = []
            if let streak = resp.trustStreakDays {
                trustStreakDays = streak
            }
            handleVoiceAssistantReply(line: resp.response, emotion: CompanionHeroEmotion(rawValue: resp.emotion) ?? .happy)
            trustScore = resp.trustScore
            if resp.trustDelta > 0 {
                lastTrustDelta = resp.trustDelta
            }
            applySocialBridge(from: resp)
            if let actions = resp.suggestedActions, !actions.isEmpty,
               let idx = messages.lastIndex(where: { !$0.isUser }) {
                attachSuggestedActions(at: idx, actions: actions)
            }
            CompanionLastToolsStore.save(resp.toolsUsed)
            await refreshUsage()
            if let unlocked = resp.cosmeticUnlocked, !unlocked.isEmpty {
                equippedCosmeticId = unlocked
            }
        } catch {
            heroEmotion = .alert
            errorText = CompanionErrorMapper.message(for: error, localizationManager: localizationManager)
        }
    }

    private func refreshUsage() async {
        if let state = try? await CompanionAPIService.shared.fetchState(characterId: characterId) {
            usageSnapshot = state.usage
        }
    }

    private func handleVoiceAssistantReply(line: String, emotion: CompanionHeroEmotion) {
        showVoiceReconnect = false
        voiceRetryContext = nil
        let trimmed = line.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        if let last = messages.last, !last.isUser, last.text == trimmed { return }
        messages.append(CompanionChatBubble(text: trimmed, isUser: false))
        contentEmotionAfterSpeaking = emotion
        heroEmotion = .speaking
        lipSyncPhase = 1
        speechOutput.speak(trimmed, personalityPreset: personalityPreset, characterId: characterId)
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

