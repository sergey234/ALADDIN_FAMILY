import SwiftUI
import Combine

// Master Logger for AI assistant logging
private let logger = MasterLogger.shared

/// 🤖 AI Assistant Screen
/// Экран AI помощника - чат с искусственным интеллектом
/// Источник дизайна: /mobile/wireframes/08_ai_assistant.html
struct AIAssistantScreen: View {

    // MARK: - State

    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss
    @State private var messageText: String = ""
    @State private var messages: [ChatMessage] = []
    @State private var isLoading = false
    @State private var showError = false
    @State private var errorMessage = ""
    @State private var showMicrophonePermissionAlert = false
    @State private var showSpeechPermissionAlert = false
    @State private var showVoiceServiceUnavailableAlert = false
    @State private var isHoldRecording = false
    @State private var holdRecordingDidStart = false
    @State private var holdDragTranslation: CGFloat = 0
    @State private var holdWillCancel = false
    @State private var showFeedbackSheet = false
    @State private var showDemoServerBanner = false
    @State private var showWellnessReferralSheet = false
    /// Снимок SyncEngine — не читаем @Published singleton в body (watchdog / layout deadlock).
    @State private var aiSyncStateDisplay: SyncState = .idle

    // Сервисы
    @StateObject private var speechManager = SpeechManager()

    private let hasReceivedWelcomeKey = "ai_assistant_welcome_sent"
    
    struct ChatSuggestedAction: Identifiable, Codable, Equatable {
        let id: String
        let title: String
    }

    struct ChatMessage: Identifiable, Codable {
        let id: UUID
        let text: String
        let isUser: Bool
        let time: String
        /// E2.4: UTC anchor for 90-day local retention (hybrid D).
        let storedAt: Date
        var grounded: Bool?
        var sources: [String]?
        var suggestedActions: [ChatSuggestedAction]?

        init(
            id: UUID = UUID(),
            text: String,
            isUser: Bool,
            time: String,
            storedAt: Date = Date(),
            grounded: Bool? = nil,
            sources: [String]? = nil,
            suggestedActions: [ChatSuggestedAction]? = nil
        ) {
            self.id = id
            self.text = text
            self.isUser = isUser
            self.time = time
            self.storedAt = storedAt
            self.grounded = grounded
            self.sources = sources
            self.suggestedActions = suggestedActions
        }

        init(from decoder: Decoder) throws {
            let c = try decoder.container(keyedBy: CodingKeys.self)
            id = try c.decode(UUID.self, forKey: .id)
            text = try c.decode(String.self, forKey: .text)
            isUser = try c.decode(Bool.self, forKey: .isUser)
            time = try c.decode(String.self, forKey: .time)
            if let interval = try c.decodeIfPresent(TimeInterval.self, forKey: .storedAt) {
                storedAt = Date(timeIntervalSince1970: interval)
            } else {
                storedAt = Date()
            }
            grounded = try c.decodeIfPresent(Bool.self, forKey: .grounded)
            sources = try c.decodeIfPresent([String].self, forKey: .sources)
            suggestedActions = try c.decodeIfPresent([ChatSuggestedAction].self, forKey: .suggestedActions)
        }

        func encode(to encoder: Encoder) throws {
            var c = encoder.container(keyedBy: CodingKeys.self)
            try c.encode(id, forKey: .id)
            try c.encode(text, forKey: .text)
            try c.encode(isUser, forKey: .isUser)
            try c.encode(time, forKey: .time)
            try c.encode(storedAt.timeIntervalSince1970, forKey: .storedAt)
            try c.encodeIfPresent(grounded, forKey: .grounded)
            try c.encodeIfPresent(sources, forKey: .sources)
            try c.encodeIfPresent(suggestedActions, forKey: .suggestedActions)
        }

        private enum CodingKeys: String, CodingKey {
            case id, text, isUser, time, storedAt, grounded, sources, suggestedActions
        }
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон — Storm Mesh AI light (Batch 2, режим C)
            StormMeshBackground(variant: .ai)
                .accessibilityElement()
                .accessibilityLabel(localizationManager.localized("ai_assistant_background"))
            
            VStack(spacing: 0) {
                // Заголовок с кнопкой назад
                HStack(spacing: 16) {
                    Button(action: {
                        // ✅ ГИБРИДНЫЙ ПОДХОД: dismiss() как основной механизм + синхронизация NavigationManager
                        // dismiss() - использует встроенный механизм SwiftUI, работает надёжно
                        dismiss()
                        
                        // Дополнительно синхронизируем NavigationManager для корректной работы стека
                        DispatchQueue.main.async {
                            if navigationManager.canGoBack {
                                navigationManager.goBack()
                            }
                        }
                    }) {
                        Image(systemName: "chevron.left")
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.white)
                            .frame(width: 44, height: 44)
                            .background(
                                Circle()
                                    .fill(Color.white.opacity(0.2))
                            )
                    }
                    .accessibilityLabel(localizationManager.localized("ai_assistant_back"))
                    .accessibilityIdentifier("ai_assistant_nav_back")
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text(localizationManager.localized("ai_assistant_title"))
                            .font(.system(size: 24, weight: .bold))
                            .foregroundColor(.white)
                        Text(localizationManager.localized("ai_assistant_subtitle"))
                            .font(.system(size: 14, weight: .regular))
                            .foregroundColor(.white.opacity(0.8))
                        Text(aiSyncStatusTitle)
                            .font(.system(size: 11, weight: .semibold))
                            .foregroundColor(aiSyncStatusColor)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(aiSyncStatusColor.opacity(0.2))
                            .clipShape(Capsule())
                    }
                    
                    Spacer()
                }
                .padding(.horizontal, 20)
                .padding(.top, 16)
                .padding(.bottom, 12)

                if !isAIDataSharingEnabled {
                    aiConsentBanner
                        .padding(.horizontal, 20)
                        .padding(.bottom, 8)
                }

                if showDemoServerBanner {
                    aiDemoServerBanner
                        .padding(.horizontal, 20)
                        .padding(.bottom, 8)
                }

                // Чат
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: 12) {
                        if messages.isEmpty {
                            // Пустое состояние с приветственным сообщением
                            VStack(spacing: Spacing.m) {
                                EmptyStateView(
                                    icon: "🤖",
                                    title: localizationManager.localized("ai_assistant_empty_title"),
                                    description: localizationManager.localized("ai_assistant_empty_description"),
                                    actionTitle: nil,
                                    action: nil
                                )
                                
                                if !UserDefaults.standard.bool(forKey: hasReceivedWelcomeKey) {
                                    chatBubble(message: ChatMessage(
                                        text: localizationManager.localized("ai_assistant_welcome"),
                                        isUser: false,
                                        time: currentTime()
                                    ))
                                }
                            }
                            .padding(.top, 40)
                        } else {
                            ForEach(messages) { message in
                                chatBubble(message: message)
                            }
                        }

                        // Индикатор загрузки
                        if isLoading {
                    TypingIndicatorView(typingUsers: [localizationManager.localized("ai_assistant_title")])
                        }

                        // Spacer для клавиатуры
                        Spacer()
                            .frame(height: 16)
                    }
                    .padding(.top, 12)
                    .padding(.horizontal, 20)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel(localizationManager.localized("ai_assistant_chat"))
                
                // Быстрые действия
                if !isLoading {
                    QuickActionsView(onActionSelected: handleQuickAction)
                        .padding(.horizontal, 20)
                        .padding(.bottom, 10)
                }

                // Поле ввода
                messageInputBar
            }
        }
        .task {
            logger.business("🤖 AI Assistant: Screen appeared, loading messages")
            aiSyncStateDisplay = SyncEngine.shared.latestStateByDomain[.aiStreaming] ?? .idle
            speechManager.warmUpPermissionsIfNeeded()
            loadMessages()
            seedWelcomeMessageIfNeeded()
            applyPendingDraftFromVoiceNotes()
            setupNotifications()
        }
        .onChange(of: localizationManager.currentLanguage) { _ in
            speechManager.refreshAvailability()
        }
        .onChange(of: speechManager.livePartialTranscript) { transcript in
            guard speechManager.isRecording, !transcript.isEmpty else { return }
            messageText = transcript
        }
        .onReceive(
            SyncEngine.shared.events
                .filter { $0.domain == .aiStreaming }
                .debounce(for: .milliseconds(200), scheduler: RunLoop.main)
        ) { event in
            aiSyncStateDisplay = event.state
            if case .error(let message) = event.state {
                showError = true
                errorMessage = message
            }
        }
        .onDisappear {
            if speechManager.isRecording {
                speechManager.stopRecording()
            }
            removeNotifications()
        }
        .navigationBarHidden(true)
        .id("ai_assistant_lang_\(localizationManager.currentLanguage.rawValue)")
        .sheet(isPresented: $showFeedbackSheet) {
            AIFeedbackSheet(isPresented: $showFeedbackSheet, apiService: APIService.shared, resolvedBy: "ai_assistant_feedback_sheet")
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showWellnessReferralSheet) {
            WellnessReferralSheet(level: "L2")
                .environmentObject(localizationManager)
        }
        .alert(localizationManager.localized("common_error"), isPresented: $showError) {
            Button(localizationManager.localized("common_ok"), role: .cancel) {}
        } message: {
            Text(errorMessage)
        }
        .alert(localizationManager.localized("voice_notes_mic_permission_title"), isPresented: $showMicrophonePermissionAlert) {
            Button(localizationManager.localized("common_cancel"), role: .cancel) {}
            Button(localizationManager.localized("voice_open_settings")) { openSettings() }
        } message: {
            Text(localizationManager.localized("ai_assistant_mic_permission_denied"))
        }
        .alert(localizationManager.localized("ai_assistant_speech_permission_title"), isPresented: $showSpeechPermissionAlert) {
            Button(localizationManager.localized("common_cancel"), role: .cancel) {}
            Button(localizationManager.localized("voice_open_settings")) { openSettings() }
        } message: {
            Text(localizationManager.localized("ai_assistant_speech_permission_denied"))
        }
        .alert(localizationManager.localized("common_error"), isPresented: $showVoiceServiceUnavailableAlert) {
            Button(localizationManager.localized("common_cancel"), role: .cancel) {}
            Button(localizationManager.localized("voice_open_settings")) {
                openSettings()
            }
        } message: {
            Text(localizationManager.localized("ai_assistant_voice_service_unavailable"))
        }
    }

    private var aiSyncStatusTitle: String {
        aiSyncStateDisplay.localizedTitle(using: localizationManager)
    }

    private var aiSyncStatusColor: Color {
        switch aiSyncStateDisplay {
        case .idle:
            return .gray
        case .local, .pending:
            return .orange
        case .syncing:
            return .blue
        case .synced:
            return .green
        case .conflict, .error:
            return .red
        }
    }

    private var isAIDataSharingEnabled: Bool {
        UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.aiDataSharingEnabled)
    }

    private var aiDemoServerBanner: some View {
        HStack(spacing: 12) {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundColor(.yellow)
            Text(localizationManager.localized("ai_assistant_demo_server_banner"))
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.white)
            Spacer(minLength: 0)
        }
        .padding(12)
        .stormGlassCard(cornerRadius: 12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.red.opacity(0.22))
        )
    }

    private var aiConsentBanner: some View {
        HStack(spacing: 12) {
            Text(localizationManager.localized("ai_consent_banner_title"))
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(.white)
            Spacer()
            Button(localizationManager.localized("ai_consent_banner_action")) {
                navigationManager.navigateTo(.settings)
            }
            .font(.system(size: 13, weight: .semibold))
            .foregroundColor(.yellow)
        }
        .padding(12)
        .stormGlassCard(cornerRadius: 12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.orange.opacity(0.25))
        )
    }
    
    // MARK: - Chat Bubble
    
    private func chatBubble(message: ChatMessage) -> some View {
        HStack {
            if message.isUser {
                Spacer()
            }
            
            VStack(alignment: message.isUser ? .trailing : .leading, spacing: 6) {
                if !message.isUser, message.grounded == true {
                    Text(localizationManager.localized("ai_grounded_badge"))
                        .font(.caption2.weight(.semibold))
                        .foregroundColor(.green)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.green.opacity(0.15))
                        .clipShape(Capsule())
                    if let kbSources = message.sources, !kbSources.isEmpty {
                        Text(kbSourcesLabel(kbSources))
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                } else if !message.isUser, message.grounded == false {
                    Text(localizationManager.localized("ai_ungrounded_banner"))
                        .font(.caption2.weight(.semibold))
                        .foregroundColor(.orange)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.orange.opacity(0.15))
                        .clipShape(Capsule())
                }

                Text(message.text)
                    .font(.body)
                    .foregroundColor(message.isUser ? .white : Color(UIColor.label))
                    .padding(12)
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(
                                message.isUser
                                    ? AnyShapeStyle(
                                        LinearGradient(
                                            colors: [Color.blue, Color.blue.opacity(0.85)],
                                            startPoint: .topLeading,
                                            endPoint: .bottomTrailing
                                        )
                                    )
                                    : AnyShapeStyle(Color(UIColor.secondarySystemGroupedBackground))
                            )
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(message.isUser ? Color.clear : Color(UIColor.separator), lineWidth: 1)
                    )

                if !message.isUser, let actions = message.suggestedActions, !actions.isEmpty {
                    aiActionButtons(actions)
                }
                
                Text(message.time)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .padding(.horizontal, 8)
            }
            .frame(maxWidth: 280, alignment: message.isUser ? .trailing : .leading)
            
            if !message.isUser {
                Spacer()
            }
        }
    }
    
    @ViewBuilder
    private func aiActionButtons(_ actions: [ChatSuggestedAction]) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            ForEach(actions) { action in
                Button {
                    if let url = AIActionCardMapper.phoneURL(for: action.id) {
                        UIApplication.shared.open(url)
                        return
                    }
                    if AIActionCardMapper.opensReferralSheet(action.id) {
                        showWellnessReferralSheet = true
                        return
                    }
                    guard let screen = AIActionCardMapper.screen(for: action.id) else { return }
                    logger.business("🤖 AI action card: \(action.id) → \(screen.rawValue)")
                    navigationManager.navigateTo(screen)
                } label: {
                    Text(action.title)
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.white)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                        .background(Color.blue.opacity(0.85))
                        .clipShape(Capsule())
                }
                .accessibilityIdentifier("ai_action_\(action.id)")
            }
        }
        .frame(maxWidth: 280, alignment: .leading)
    }

    // MARK: - Message Input Bar (как в семейном чате — читаемый TextEditor + контраст)

    private var messageInputBar: some View {
        VStack(spacing: 6) {
            HStack(alignment: .bottom, spacing: 10) {
                Image(systemName: speechManager.isRecording || isHoldRecording ? "mic.fill" : "mic")
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundColor(speechManager.isRecording || isHoldRecording ? .red : (speechManager.isSpeechInputAvailable ? .white : .gray))
                    .frame(width: 42, height: 42)
                    .background(Color.white.opacity(speechManager.isSpeechInputAvailable ? 0.18 : 0.08))
                    .cornerRadius(12)
                    .contentShape(Rectangle())
                    .onTapGesture {
                        guard !isHoldRecording else { return }
                        toggleVoiceRecording()
                    }
                    .highPriorityGesture(
                        DragGesture(minimumDistance: 0)
                            .onChanged { value in
                                holdDragTranslation = value.translation.width
                                holdWillCancel = value.translation.width < -72
                                guard speechManager.isSpeechInputAvailable, !holdRecordingDidStart else { return }
                                holdRecordingDidStart = true
                                isHoldRecording = true
                                startHoldVoiceRecording()
                            }
                            .onEnded { value in
                                let cancel = holdWillCancel || value.translation.width < -80
                                holdRecordingDidStart = false
                                isHoldRecording = false
                                holdDragTranslation = 0
                                holdWillCancel = false
                                if speechManager.isRecording {
                                    if cancel {
                                        speechManager.cancelRecording()
                                    } else {
                                        speechManager.stopRecording()
                                    }
                                }
                            }
                    )
                    .disabled(!speechManager.isSpeechInputAvailable && !speechManager.isRecording)
                    .accessibilityLabel(localizationManager.localized("ai_assistant_voice_input_label"))
                    .accessibilityHint(localizationManager.localized("ai_assistant_voice_hold_hint"))

                ZStack(alignment: .topLeading) {
                    if messageText.isEmpty {
                        Text(localizationManager.localized("ai_assistant_placeholder"))
                            .foregroundColor(Color(UIColor.secondaryLabel))
                            .padding(.horizontal, 14)
                            .padding(.vertical, 12)
                            .allowsHitTesting(false)
                    }

                    TextEditor(text: $messageText)
                        .font(.system(size: 16))
                        .foregroundColor(Color(UIColor.label))
                        .modifier(AIComposerHideScrollBackground())
                        .padding(.horizontal, 10)
                        .padding(.vertical, 8)
                        .frame(minHeight: 44, maxHeight: aiComposerHeight(for: messageText))
                        .background(Color.clear)
                        .disabled(isLoading || speechManager.isRecording)
                        .accessibilityLabel(localizationManager.localized("ai_assistant_placeholder"))
                }
                .background(Color(UIColor.secondarySystemGroupedBackground))
                .overlay(
                    RoundedRectangle(cornerRadius: 14)
                        .stroke(Color(UIColor.separator), lineWidth: 1)
                )
                .cornerRadius(14)

                Button(action: sendMessage) {
                    if isLoading {
                        ProgressView()
                            .tint(.backgroundDark)
                            .scaleEffect(0.85)
                            .frame(width: 42, height: 42)
                    } else {
                        Image(systemName: "paperplane.fill")
                            .font(.system(size: 17, weight: .semibold))
                            .foregroundColor(.backgroundDark)
                            .frame(width: 42, height: 42)
                            .background(
                                messageText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                                    ? Color.surfaceDark.opacity(0.5)
                                    : Color.secondaryGold
                            )
                            .cornerRadius(12)
                    }
                }
                .disabled(messageText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isLoading)

                Button(action: { showFeedbackSheet = true }) {
                    Image(systemName: "star.fill")
                        .font(.system(size: 17, weight: .semibold))
                        .foregroundColor(.orange)
                        .frame(width: 42, height: 42)
                        .background(Color.white.opacity(0.18))
                        .cornerRadius(12)
                }
                .accessibilityLabel(localizationManager.localized("app_feedback_star_accessibility"))
            }
            .padding(Spacing.m)
            .stormGlassCard(cornerRadius: 16)
            .padding(.horizontal, Spacing.screenPadding)
            .padding(.top, 8)
            .padding(.bottom, 8)

            VStack(alignment: .leading, spacing: 4) {
                HStack(spacing: 6) {
                    Text(localizationManager.localized(voiceInputStatusKey))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.75))
                    if speechManager.isRecording && speechManager.usesCloudRecognition {
                        Text(localizationManager.localized("ai_assistant_voice_via_siri"))
                            .font(.caption2)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(Color.orange.opacity(0.35))
                            .clipShape(Capsule())
                    }
                    if !speechManager.isSpeechInputAvailable {
                        Text(localizationManager.localized("ai_assistant_voice_unavailable_chip"))
                            .font(.caption2)
                            .foregroundColor(.orange)
                    }
                }
                if speechManager.isRecording || speechManager.isPreparingRecording {
                    VoiceLevelBarsView(level: speechManager.audioLevel, activeColor: .red)
                        .padding(.top, 2)
                }
                if isHoldRecording && holdWillCancel {
                    Text(localizationManager.localized("ai_assistant_voice_slide_cancel"))
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.orange)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(.horizontal, Spacing.screenPadding)
            .padding(.bottom, 4)
        }
        .background(LinearGradient.cardGradient.appGlassmorphism())
    }

    private func aiComposerHeight(for text: String) -> CGFloat {
        let lineBreakCount = text.components(separatedBy: .newlines).count
        let estimatedWrappedLines = max(1, Int(ceil(Double(text.count) / 34.0)))
        let lineCount = max(lineBreakCount, estimatedWrappedLines)
        let clampedLines = min(max(lineCount, 1), 5)
        return CGFloat(clampedLines * 24 + 20)
    }
    
    private func sendMessage() {
        guard !messageText.isEmpty else {
            logger.warn("AI Assistant: Attempted to send empty message")
            return
        }

        guard isAIDataSharingEnabled else {
            AIAssistantResponseDiagnostics.logDelivery(
                source: .cloudDisabled,
                context: "consent_off",
                responseLength: 0,
                grounded: nil,
                toolsUsed: nil,
                preview: ""
            )
            errorMessage = AIOutboundTextGate.GateError.optInRequired.errorDescription
                ?? localizationManager.localized("ai_error_consent_required")
            showError = true
            return
        }

        logger.business("🤖 AI Assistant: Sending message (length: \(messageText.count) chars)")

        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()

        let rawMessage = messageText
        messageText = ""

        let context = determineMessageContext(rawMessage)
        logger.business("🤖 AI Assistant: Message context determined: \(context)")

        if context == "feedback" {
            messages.append(ChatMessage(text: rawMessage, isUser: true, time: currentTime()))
            saveMessages()
            isLoading = true
            logger.business("🤖 AI Assistant: Detected feedback message, sending to feedback system")
            sendFeedbackMessage(rawMessage)
            return
        }

        do {
            let prepared = try AIOutboundTextGate.prepareUserMessage(rawMessage)
            messages.append(ChatMessage(text: prepared.displayText, isUser: true, time: currentTime()))
            saveMessages()
            isLoading = true
            logger.business("🤖 AI Assistant: Sending regular message to AI (redactions=\(prepared.redactionCount))")
            sendRegularMessage(prepared.cloudText, displayMessage: prepared.displayText, context: context)
        } catch let error as InputSanitizer.SanitizationError {
            errorMessage = LocalizationManager.shared.localized("ai_assistant_error_sanitization", error.localizedDescription)
            showError = true
        } catch let error as AIOutboundTextGate.GateError {
            errorMessage = error.localizedDescription
            showError = true
        } catch {
            errorMessage = localizationManager.localized("ai_assistant_error_unknown_processing")
            showError = true
        }
    }

    private func sendFeedbackMessage(_ message: String) {
        logger.business("🤖 AI Assistant: Processing feedback message")

        // Определяем тип feedback для персонализированного ответа
        let feedbackType = determineFeedbackType(message)
        logger.business("🤖 AI Assistant: Feedback type determined: \(feedbackType)")

        // Отправляем как обратную связь
        logger.network("🤖 AI Assistant: Sending feedback to server")
        APIService.shared.sendAIFeedback(
            rating: 5,
            comment: message,
            messageId: nil,
            queryText: message,
            resolvedBy: "ai_chat_feedback",
            faqId: nil,
            confidence: nil,
            sessionId: currentFeedbackSessionId()
        ) { [self] result in
            DispatchQueue.main.async {
                isLoading = false

                switch result {
                case .success:
                    logger.business("✅ AI Assistant: Feedback sent successfully")
                    let feedbackResponse = ChatMessage(
                        text: getPersonalizedFeedbackResponse(feedbackType, message),
                        isUser: false,
                        time: currentTime()
                    )
                    messages.append(feedbackResponse)
                    saveMessages()

                case .failure(let error):
                    logger.error("❌ AI Assistant: Failed to send feedback", error: error)
                    showError = true
                    errorMessage = String(
                        format: localizationManager.localized("ai_assistant_error_feedback_failed"),
                        error.localizedDescription
                    )

                    let errorResponse = ChatMessage(
                        text: localizationManager.localized("ai_assistant_error_feedback_retry"),
                        isUser: false,
                        time: currentTime()
                    )
                    messages.append(errorResponse)
                    saveMessages()
                }
            }
        }
    }

    private func currentFeedbackSessionId() -> String {
        if let existing = UserDefaults.standard.string(forKey: "jwt_session_id"), !existing.isEmpty {
            return existing
        }
        let generated = UUID().uuidString
        UserDefaults.standard.set(generated, forKey: "jwt_session_id")
        return generated
    }

    private func getPersonalizedFeedbackResponse(_ feedbackType: String, _ originalMessage: String) -> String {
        let baseResponse: String

        switch feedbackType {
        case "FEATURE_REQUEST":
            baseResponse = """
            Спасибо за ваше предложение! 🚀
            ALADDIN стремится стать лучше и мы обязательно рассмотрим
            добавление этой функции в следующих обновлениях.

            Ваша обратная связь очень важна для нас! 💡

            Расскажите подробнее:
            • На каких экранах вы хотели бы видеть эту функцию?
            • Как вы представляете её работу?
            • Есть ли похожие функции в других приложениях?

            Хотите поделиться еще какими-то идеями?
            """

        case "IMPROVEMENT":
            baseResponse = """
            Спасибо за замечание! 💡 Ваше предложение поможет сделать
            приложение еще лучше и удобнее.

            Мы проанализируем возможность этого улучшения и
            рассмотрим его реализацию в ближайших обновлениях.

            Что именно неудобно в текущей реализации?
            Есть ли другие аспекты, которые можно улучшить?

            Ваши идеи помогают развивать ALADDIN! 🙏
            """

        case "BUG_REPORT":
            baseResponse = """
            Спасибо за информацию о проблеме! 🐛
            Мы сожалеем о неудобствах и передадим эту информацию
            нашей команде разработчиков для скорейшего исправления.

            Для быстрого решения проблемы:
            • Какая версия приложения у вас установлена?
            • В какой момент происходит ошибка?
            • Можете ли вы описать последовательность действий?

            Ваша помощь в решении проблем очень ценна! 💪
            """

        case "UX_IMPROVEMENT":
            baseResponse = """
            Спасибо за отзыв об интерфейсе! 🎨 Ваше мнение поможет нам
            сделать приложение более удобным и красивым.

            Мы внимательно изучим ваше предложение и учтем его
            при следующей итерации дизайна.

            Как бы вы хотели видеть этот элемент интерфейса?
            Есть ли другие аспекты дизайна, которые можно улучшить?

            Спасибо за вашу заботу о UX ALADDIN! ✨
            """

        default: // GENERAL_FEEDBACK
            baseResponse = """
            Спасибо за вашу обратную связь! 💝 Мы ценим ваше время и
            внимание к деталям. Ваши идеи помогают развивать ALADDIN.

            Мы внимательно изучим ваше предложение и обязательно
            учтем его при планировании будущих обновлений.

            Хотите поделиться еще чем-то или у вас есть другие вопросы?
            Мы всегда открыты к диалогу! 🙏
            """
        }

        return baseResponse
    }

    private func determineFeedbackType(_ message: String) -> String {
        let lowerMessage = message.lowercased()

        // FEATURE_REQUEST - запросы на новые функции
        if lowerMessage.contains("добавить") || lowerMessage.contains("создать") ||
           lowerMessage.contains("новая функция") || lowerMessage.contains("хотел бы видеть") ||
           lowerMessage.contains("add") || lowerMessage.contains("new feature") ||
           lowerMessage.contains("would like to see") || lowerMessage.contains("implement") {
            return "FEATURE_REQUEST"
        }

        // IMPROVEMENT - улучшения существующих функций
        if lowerMessage.contains("улучшить") || lowerMessage.contains("оптимизировать") ||
           lowerMessage.contains("ускорить") || lowerMessage.contains("сделать лучше") ||
           lowerMessage.contains("improve") || lowerMessage.contains("optimize") ||
           lowerMessage.contains("faster") || lowerMessage.contains("better") {
            return "IMPROVEMENT"
        }

        // BUG_REPORT - сообщения об ошибках
        if lowerMessage.contains("не работает") || lowerMessage.contains("ошибка") ||
           lowerMessage.contains("глюк") || lowerMessage.contains("вылетает") ||
           lowerMessage.contains("тормозит") || lowerMessage.contains("зависает") ||
           lowerMessage.contains("bug") || lowerMessage.contains("error") ||
           lowerMessage.contains("crash") || lowerMessage.contains("slow") ||
           lowerMessage.contains("freeze") {
            return "BUG_REPORT"
        }

        // UX_IMPROVEMENT - улучшения интерфейса
        if lowerMessage.contains("интерфейс") || lowerMessage.contains("дизайн") ||
           lowerMessage.contains("удобнее") || lowerMessage.contains("красивее") ||
           lowerMessage.contains("понятнее") || lowerMessage.contains("ui") ||
           lowerMessage.contains("ux") || lowerMessage.contains("design") ||
           lowerMessage.contains("easier") || lowerMessage.contains("clearer") {
            return "UX_IMPROVEMENT"
        }

        // GENERAL_FEEDBACK - общая обратная связь
        return "GENERAL_FEEDBACK"
    }

    private func sendRegularMessage(_ message: String, displayMessage: String, context: String) {
        logger.business("🤖 AI Assistant: Sending message to AI service (context: \(context))")

        // Hybrid FAQ+AI: локальный матч по тексту пользователя (до redact на сервере).
        if let faqMatch = UnifiedFAQCatalog.bestMatch(for: displayMessage, localize: localizationManager.localized) {
            logger.business("📚 AI Assistant: FAQ match found id=\(faqMatch.id)")
            showDemoServerBanner = false
            AIAssistantResponseDiagnostics.logDelivery(
                source: .faqLocal,
                context: context,
                responseLength: faqMatch.answer.count,
                grounded: true,
                toolsUsed: ["faq:\(faqMatch.id)"],
                preview: faqMatch.answer
            )
            isLoading = false
            let faqResponse = ChatMessage(
                text: localizationManager.localized("ai_assistant_faq_footer", faqMatch.answer, faqMatch.id),
                isUser: false,
                time: currentTime()
            )
            messages.append(faqResponse)
            saveMessages()
            return
        }

        // Отправляем обычное сообщение AI
        logger.network("🤖 AI Assistant: Making API call to AI service")
        let responseLanguage = localizationManager.aiResponseLanguageCode
        APIService.shared.sendMessageToAI(message: message, context: context, responseLanguage: responseLanguage) { [self] result in
            DispatchQueue.main.async {
                isLoading = false

                switch result {
                case .success(let response):
                    logger.business("✅ AI Assistant: Received AI response (length: \(response.response.count) chars)")

                    // Проверяем, является ли ответ стандартным mock ответом сервера
                    let finalResponse = userFacingAIReply(from: response.response)
                    let source = AIAssistantResponseDiagnostics.classifyServerResponse(
                        finalResponse,
                        grounded: response.grounded
                    )
                    showDemoServerBanner = (source == .cloudAPIProbableMock || source == .cloudRuleBasedOffTopic)
                    AIAssistantResponseDiagnostics.logDelivery(
                        source: source,
                        context: context,
                        responseLength: finalResponse.count,
                        grounded: response.grounded,
                        toolsUsed: response.toolsUsed,
                        preview: finalResponse
                    )
                    logger.business("🤖 AI Assistant: Server response source=\(source.rawValue)")

                    let actions = (response.suggestedActions ?? []).map {
                        ChatSuggestedAction(id: $0.id, title: $0.title)
                    }
                    let aiResponse = ChatMessage(
                        text: finalResponse,
                        isUser: false,
                        time: currentTime(),
                        grounded: response.grounded,
                        sources: response.sources,
                        suggestedActions: actions.isEmpty ? nil : actions
                    )
                    
                    // ✅ BUILD 115: Детальное логирование для подтверждения добавления сообщения
                    logger.business("✅ AI Assistant: Adding message to UI - text: '\(finalResponse.prefix(50))...', isUser: false")
                    messages.append(aiResponse)
                    logger.business("✅ AI Assistant: Message added successfully. Total messages: \(messages.count)")
                    saveMessages()
                    logger.business("✅ AI Assistant: Messages saved to storage")

                case .failure(let error):
                    logger.error("❌ AI Assistant: Failed to get AI response", error: error)
                    logger.error("❌ AI Assistant: Error details - \(error.localizedDescription)")
                    let errLower = error.localizedDescription.lowercased()
                    
                    // ✅ BUILD 115: Детальное логирование для диагностики на реальном устройстве
                    if let networkError = error as? NetworkError {
                        logger.error("❌ AI Assistant: NetworkError type - \(networkError)")
                    }
                    
                    #if DEBUG
                    print("❌ AI Assistant: Full error: \(error)")
                    if let decodingError = error as? DecodingError {
                        print("❌ AI Assistant: DecodingError details: \(decodingError)")
                    }
                    #endif
                    
                    showError = true
                    if errLower.contains("502") || errLower.contains("bad gateway") || errLower.contains("ошибка шлюза") {
                        errorMessage = localizationManager.localized("ai_error_gateway_retry")
                    } else if errLower.contains("503") || errLower.contains("unavailable") {
                        errorMessage = localizationManager.localized("ai_error_service_unavailable")
                    } else if errLower.contains("422") || errLower.contains("pii") {
                        errorMessage = localizationManager.localized("ai_error_pii_blocked")
                    } else if errLower.contains("429") || errLower.contains("rate limit") {
                        errorMessage = localizationManager.localized("ai_error_rate_limit")
                    } else {
                        errorMessage = String(
                            format: localizationManager.localized("ai_assistant_error_response_failed"),
                            error.localizedDescription
                        )
                    }

                    let errorResponse = ChatMessage(
                        text: (errLower.contains("502") || errLower.contains("bad gateway") || errLower.contains("ошибка шлюза"))
                            ? localizationManager.localized("ai_error_gateway_retry")
                            : (errLower.contains("503") || errLower.contains("unavailable")
                            ? localizationManager.localized("ai_error_service_unavailable")
                            : localizationManager.localized("ai_assistant_error_generic_retry")),
                        isUser: false,
                        time: currentTime()
                    )
                    messages.append(errorResponse)
                    saveMessages()
                }
            }
        }
    }

    private func determineMessageContext(_ message: String) -> String {
        let lowerMessage = message.lowercased()

        // Проверяем на предложения и пожелания
        if isFeedbackMessage(message) {
            return "feedback"
        }

        // Расширенные проверки для определения контекста
        let protectionKeywords = ["защит", "protection", "security", "безопасност", "safe", "guard", "shield",
                                  "статус", "status", "работа", "работает", "активн", "active", "включен",
                                  "вкл", "on", "работает ли", "запущен", "running", "функционирует"]

        let threatKeywords = ["угроз", "threat", "attack", "атака", "вирус", "virus", "троян", "trojan",
                              "фишинг", "phishing", "мошенни", "fraud", "взлом", "hack", "вредонос",
                              "malware", "спам", "spam", "риск", "risk", "опасност", "danger"]

        let recommendationKeywords = ["рекоменд", "совет", "tip", "advice", "подскаж", "help", "помощ",
                                      "как", "how", "что делать", "what to do", "улучшить", "improve",
                                      "лучше", "better", "оптимизир", "optimize", "настроить", "configure"]

        let helpKeywords = ["помощ", "help", "справк", "инструкц", "guide", "руководств", "документац",
                            "как пользоваться", "how to use", "информация", "info", "объясни", "explain"]

        let statsKeywords = ["статистик", "stats", "данные", "data", "отчет", "report", "покажи", "show",
                             "числа", "numbers", "график", "chart", "анализ", "analysis", "мониторинг", "monitoring"]

        // Проверяем наличие ключевых слов в сообщении
        for keyword in protectionKeywords {
            if lowerMessage.contains(keyword) {
                return "protection_status"
            }
        }

        for keyword in threatKeywords {
            if lowerMessage.contains(keyword) {
                return "threat_analysis"
            }
        }

        for keyword in recommendationKeywords {
            if lowerMessage.contains(keyword) {
                return "recommendations"
            }
        }

        for keyword in helpKeywords {
            if lowerMessage.contains(keyword) {
                return "help"
            }
        }

        for keyword in statsKeywords {
            if lowerMessage.contains(keyword) {
                return "stats"
            }
        }

        // Приветственные сообщения и общие вопросы
        let greetingKeywords = ["привет", "здравствуй", "добр", "hi", "hello", "hey", "хай"]
        for keyword in greetingKeywords {
            if lowerMessage.contains(keyword) {
                return "greeting"
            }
        }

        return "general"
    }

    private func isFeedbackMessage(_ message: String) -> Bool {
        let lowerMessage = message.lowercased()

        // Ключевые слова для предложений и пожеланий
        let feedbackKeywords = [
            "предложение", "пожелание", "улучшить", "улучшение", "предлагаю",
            "хотелось бы", "было бы хорошо", "можно добавить", "нужно исправить",
            "suggestion", "wish", "improve", "enhancement", "would like",
            "it would be good", "can add", "need to fix", "feedback",
            "отзыв", "замечание", "идея", "мысль"
        ]

        // Проверяем наличие ключевых слов
        for keyword in feedbackKeywords {
            if lowerMessage.contains(keyword) {
                return true
            }
        }

        // Проверяем специальные префиксы
        if lowerMessage.hasPrefix("предложение:") ||
           lowerMessage.hasPrefix("пожелание:") ||
           lowerMessage.hasPrefix("идея:") ||
           lowerMessage.hasPrefix("suggestion:") ||
           lowerMessage.hasPrefix("feedback:") {
            return true
        }

        return false
    }

    // Локальная обработка ответов AI (fallback если сервер не работает)
    // MARK: - Data Loading and Saving

    /// Убирает служебный stderr Hermes; не дописывает подсказки к ответу модели.
    private func userFacingAIReply(from raw: String) -> String {
        let text = AIAssistantResponseSanitizer.userFacingText(from: raw)
            .trimmingCharacters(in: .whitespacesAndNewlines)
        return text.isEmpty
            ? localizationManager.localized("ai_error_service_unavailable")
            : text
    }

    private func seedWelcomeMessageIfNeeded() {
        guard !UserDefaults.standard.bool(forKey: hasReceivedWelcomeKey) else { return }
        let welcome = ChatMessage(
            text: localizationManager.localized("ai_assistant_welcome"),
            isUser: false,
            time: currentTime()
        )
        if !messages.contains(where: { $0.text == welcome.text && !$0.isUser }) {
            messages.append(welcome)
            saveMessages()
        }
        UserDefaults.standard.set(true, forKey: hasReceivedWelcomeKey)
        logger.business("🤖 AI Assistant: Welcome message seeded for new user")
    }

    private func loadMessages() {
        guard let decoded = AIAssistantHistoryMigration.load([ChatMessage].self) else {
            logger.business("🤖 AI Assistant: No saved messages (v2), starting fresh")
            messages = []
            return
        }
        let filtered = decoded.filter {
            AIAssistantLocalHistoryPolicy.purgeIfNeeded(storedAt: $0.storedAt)
                && !AIAssistantHistoryMigration.isDemoOrSeedMessage($0.text)
        }
        messages = filtered
        if filtered.count != decoded.count {
            AIAssistantHistoryMigration.save(filtered)
            logger.business("🤖 AI Assistant: Pruned \(decoded.count - filtered.count) stale messages on load")
        }
        logger.business("✅ AI Assistant: Loaded \(messages.count) messages (schema v\(AIAssistantHistoryMigration.currentSchemaVersion))")
    }

    private func saveMessages() {
        AIAssistantHistoryMigration.save(messages)
        logger.business("✅ AI Assistant: Saved \(messages.count) messages to storage")
    }
    
    private func currentTime() -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        formatter.locale = localizationManager.locale
        return formatter.string(from: Date())
    }

    private func kbSourcesLabel(_ sources: [String]) -> String {
        let display = sources.prefix(3).map { id in
            id.hasPrefix("faq_") ? String(id.dropFirst(4)) : id
        }.joined(separator: ", ")
        let template = localizationManager.localized("ai_kb_sources")
        return String(format: template, display)
    }

    private func handleQuickAction(_ action: QuickActionType) {
        logger.business("🤖 AI Assistant: Quick action selected: \(action)")

        let message: String
        switch action {
        case .protectionStatus:
            message = localizationManager.localized("ai_assistant_quick_prompt_protection_status")
        case .analyzeThreats:
            message = localizationManager.localized("ai_assistant_quick_prompt_analyze_threats")
        case .securityTips:
            message = localizationManager.localized("ai_assistant_quick_prompt_security_tips")
        case .help:
            message = localizationManager.localized("ai_assistant_quick_prompt_help")
        case .familySetup:
            message = localizationManager.localized("ai_assistant_quick_prompt_family_setup")
        case .reportIncident:
            message = localizationManager.localized("ai_assistant_quick_prompt_report_incident")
        }

        messageText = message
        logger.business("🤖 AI Assistant: Quick action message set: '\(message)'")
        sendMessage()
    }

    private func applyPendingDraftFromVoiceNotes() {
        let key = AppConfig.UserDefaultsKeys.pendingAIAssistantDraftMessage
        guard let draft = UserDefaults.standard.string(forKey: key)?
            .trimmingCharacters(in: .whitespacesAndNewlines),
              !draft.isEmpty else { return }
        UserDefaults.standard.removeObject(forKey: key)
        messageText = draft
    }

    private func setupNotifications() {
        NotificationCenter.default.addObserver(forName: .microphonePermissionDenied, object: nil, queue: .main) { _ in
            showMicrophonePermissionAlert = true
        }
        NotificationCenter.default.addObserver(forName: .speechRecognitionPermissionDenied, object: nil, queue: .main) { _ in
            showSpeechPermissionAlert = true
        }
        NotificationCenter.default.addObserver(forName: .speechPermissionDenied, object: nil, queue: .main) { _ in
            showSpeechPermissionAlert = true
        }
        NotificationCenter.default.addObserver(forName: .speechServiceUnavailable, object: nil, queue: .main) { _ in
            showVoiceServiceUnavailableAlert = true
        }
        NotificationCenter.default.addObserver(forName: .voiceNoteSendToAI, object: nil, queue: .main) { notification in
            if let text = notification.userInfo?["text"] as? String, !text.isEmpty {
                messageText = text
            }
        }
        NotificationCenter.default.addObserver(forName: .voiceRecordingInterrupted, object: nil, queue: .main) { _ in
            ToastManager.shared.showWarning(
                localizationManager.localized("voice_recording_interrupted")
            )
        }
    }

    private func removeNotifications() {
        let center = NotificationCenter.default
        center.removeObserver(self, name: .microphonePermissionDenied, object: nil)
        center.removeObserver(self, name: .speechRecognitionPermissionDenied, object: nil)
        center.removeObserver(self, name: .speechPermissionDenied, object: nil)
        center.removeObserver(self, name: .speechServiceUnavailable, object: nil)
        center.removeObserver(self, name: .voiceNoteSendToAI, object: nil)
        center.removeObserver(self, name: .voiceRecordingInterrupted, object: nil)
    }

    private func startHoldVoiceRecording() {
        guard speechManager.isSpeechInputAvailable, !speechManager.isRecording, !speechManager.isPreparingRecording else { return }
        holdWillCancel = false
        holdDragTranslation = 0
        speechManager.startRecording { recognizedText in
            handleVoiceRecognitionResult(recognizedText, autoSend: true)
        }
    }

    private func toggleVoiceRecording() {
        guard speechManager.isSpeechInputAvailable || speechManager.isRecording || speechManager.isPreparingRecording else {
            showVoiceServiceUnavailableAlert = true
            return
        }
        if speechManager.isRecording {
            logger.business("🎤 AI Assistant: Stopping voice recording")
            HapticFeedback.impact(.light)
            speechManager.stopRecording()
        } else if speechManager.isPreparingRecording {
            return
        } else {
            logger.business("🎤 AI Assistant: Starting voice recording")
            HapticFeedback.impact(.medium)
            speechManager.startRecording { recognizedText in
                handleVoiceRecognitionResult(recognizedText, autoSend: true)
            }
        }
    }

    /// После STT: текст в поле; отправка только при включённом «Облачный AI-помощник».
    private func handleVoiceRecognitionResult(_ recognizedText: String?, autoSend: Bool) {
        guard let text = recognizedText?.trimmingCharacters(in: .whitespacesAndNewlines), !text.isEmpty else {
            logger.warn("🎤 AI Assistant: Voice recognition returned empty text")
            switch speechManager.lastRecognitionFailure {
            case .serviceUnavailable:
                errorMessage = localizationManager.localized("ai_assistant_voice_service_unavailable")
            case .recordingTooShort:
                errorMessage = localizationManager.localized("companion_voice_hold_too_short")
            case .emptyTranscript, .none:
                errorMessage = localizationManager.localized("ai_assistant_voice_empty_result")
            }
            showError = true
            return
        }
        logger.business("🎤 AI Assistant: Voice recognized: '\(text.prefix(50))...' (length: \(text.count))")
        messageText = text
        guard autoSend else { return }
        guard isAIDataSharingEnabled else {
            // Распознавание прошло; блокируем только отправку на сервер ALADDIN.
            return
        }
        sendMessage()
    }

    private var voiceInputStatusKey: String {
        if speechManager.isPreparingRecording {
            return "ai_assistant_voice_status_preparing"
        }
        if speechManager.isRecording {
            return "ai_assistant_voice_status_listening"
        }
        if isLoading {
            return "ai_assistant_voice_status_processing"
        }
        return "ai_assistant_voice_status_idle"
    }

    private func openSettings() {
        if let url = URL(string: UIApplication.openSettingsURLString) {
            UIApplication.shared.open(url)
        }
    }
}

/// Скрывает системный фон TextEditor (iOS 16+) для контраста как в Family Chat.
private struct AIComposerHideScrollBackground: ViewModifier {
    func body(content: Content) -> some View {
        if #available(iOS 16.0, *) {
            content.scrollContentBackground(.hidden)
        } else {
            content
        }
    }
}

// MARK: - Quick Actions

enum QuickActionType {
    case protectionStatus
    case analyzeThreats
    case securityTips
    case help
    case familySetup
    case reportIncident
}

struct QuickAction: Identifiable {
    let id = UUID()
    let type: QuickActionType
    let icon: String
    let title: String
}

struct QuickActionsView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let onActionSelected: (QuickActionType) -> Void

    private var actions: [QuickAction] {
        [
            QuickAction(type: .protectionStatus, icon: "🛡️", title: localizationManager.localized("ai_assistant_quick_action_protection_status")),
            QuickAction(type: .analyzeThreats, icon: "🔍", title: localizationManager.localized("ai_assistant_quick_action_analyze_threats")),
            QuickAction(type: .securityTips, icon: "💡", title: localizationManager.localized("ai_assistant_quick_action_security_tips")),
            QuickAction(type: .help, icon: "❓", title: localizationManager.localized("ai_assistant_quick_action_help")),
            QuickAction(type: .familySetup, icon: "👨‍👩‍👧‍👦", title: localizationManager.localized("ai_assistant_quick_action_family")),
            QuickAction(type: .reportIncident, icon: "🚨", title: localizationManager.localized("ai_assistant_quick_action_incident"))
        ]
    }

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(actions) { action in
                    Button(action: {
                        onActionSelected(action.type)
                    }) {
                        VStack(spacing: 4) {
                            Text(action.icon)
                                .font(.system(size: 20))
                            Text(action.title)
                                .font(.system(size: 10, weight: .medium))
                                .multilineTextAlignment(.center)
                                .lineLimit(2)
                        }
                        .frame(width: 60, height: 60)
                        .background(Color.blue.opacity(0.1))
                        .foregroundColor(.blue)
                        .cornerRadius(12)
                    }
                }
            }
            .padding(.horizontal, 4)
        }
    }
}

// MARK: - Preview

#if DEBUG
struct AIAssistantScreen_Previews: PreviewProvider {
    static var previews: some View {
        AIAssistantScreen()
    }
}
#endif




