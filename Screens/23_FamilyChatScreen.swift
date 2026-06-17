import SwiftUI
import AVFoundation
import UserNotifications
import UIKit
import UniformTypeIdentifiers
import Contacts
import ContactsUI
import CoreLocation
import Combine

/**
 * 💬 Family Chat Screen
 * Семейный чат
 * 17_family_chat_screen из HTML
 * 
 * ✅ PRODUCTION READY:
 * - Получение familyId из UserDefaults
 * - Динамическое количество участников
 * - Автообновление сообщений (polling)
 * - Улучшенная обработка ошибок
 * - Индикатор отправки сообщения
 * - Автопрокрутка к новым сообщениям
 */

struct FamilyChatScreen: View {
    
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var messageText: String = ""
    @State private var messages: [FamilyChatMessage] = []
    @State private var isLoading: Bool = false
    @State private var isSending: Bool = false
    /// Текст алерта ошибки (без `alert(item:)` с `Identifiable`, чтобы снизить риск циклов AttributeGraph).
    @State private var chatErrorMessage: String? = nil
    /// После `GET /members` / заголовков сервера: нет семьи — не слать typing/send с устаревшим `family_id`.
    @State private var chatFamilyContextInvalid: Bool = false
    /// Поколение silent-запроса списка: устаревшие ответы не перезаписывают `messages` (гонки polling + после send).
    @State private var silentMessagesFetchGeneration: UInt64 = 0
    @State private var onlineMembersCount: Int = 0
    @State private var onlineUsers: Set<String> = []
    
    // Extended features state
    @StateObject private var voiceRecorder = VoiceMessageRecorder()
    /// Синглтоны: `@ObservedObject`, не `@StateObject` (иначе конфликт владения и риск реентрантности с Combine).
    @ObservedObject private var offlineManager = FamilyChatOfflineManager.shared
    @ObservedObject private var mediaUploadManager = MediaUploadManager.shared
    @ObservedObject private var pushService = PushNotificationService.shared
    @ObservedObject private var e2eeManager = FamilyE2EEManager.shared
    @State private var webSocket: FamilyChatWebSocket?
    @State private var isRecordingVoice: Bool = false
    @State private var recordingURL: URL? = nil
    @State private var isSearching: Bool = false
    @State private var searchText: String = ""
    @State private var filteredMessages: [FamilyChatMessage] = []
    @State private var typingUsers: [String] = []
    @State private var selectedMessage: FamilyChatMessage? = nil
    @State private var showMessageActions: Bool = false
    @State private var replyToMessage: FamilyChatMessage? = nil
    @State private var editingMessage: FamilyChatMessage? = nil
    @State private var editText: String = ""
    @State private var showMediaPicker: Bool = false
    @State private var selectedMedia: UIImage? = nil
    @State private var showThemeSettings: Bool = false
    @State private var chatTheme: ChatTheme = .light
    @State private var showCamera: Bool = false
    @State private var showComposerActions: Bool = false
    @State private var showQuickReactionPicker: Bool = false
    @State private var showFileImporter: Bool = false
    @State private var showContactPicker: Bool = false
    @State private var isResolvingLocation: Bool = false
    @State private var showFeedbackSheet: Bool = false
    @State private var typingStopWorkItem: DispatchWorkItem? = nil
    /// Debounce typing: `Task` на MainActor, чтобы не дергать сеть синхронно из `onChange` и не захватывать устаревший `struct View`.
    @State private var typingTextDebounceTask: Task<Void, Never>?
    @State private var lastTypingSignalAt: Date = .distantPast
    @State private var typingExpiryByUser: [String: Date] = [:]
    @State private var wsRealtimeUnavailable: Bool = false
    /// После успешной отправки (текст/медиа/голос): защита silent-poll от пустого GET, пока бэкенд не отдал сообщения в ленту.
    @State private var lastOutboundChatCompletedAt: Date?

    private let familyMembersKey = "family_members_list"
    
    private let apiService = APIService.shared
    private let homeChatLastFamilyActivityKey = "home_chat_last_family_activity_at"
    @StateObject private var locationShareManager = LocationShareManager()
    
    enum ChatTheme: String, CaseIterable {
        case light = "light"
        case dark = "dark"
        case auto = "auto"
    }
    
    
    var body: some View {
        familyChatRootDecorated
    }

    /// Основная колонка: навбар, баннеры, список сообщений (без модификаторов жизненного цикла).
    private var familyChatMainColumn: some View {
        VStack(spacing: 0) {
            ALADDINNavigationBar(
                title: localizationManager.localized("family_chat_title"),
                subtitle: presenceSubtitle,
                showBackButton: true,
                showProfileButton: false,
                showListButton: false,
                onBack: {
                    dismiss()

                    DispatchQueue.main.async {
                        if navigationManager.canGoBack {
                            navigationManager.goBack()
                        }
                    }
                }
            )
            .accessibilityElement(children: .combine)
            .accessibilityLabel(localizationManager.localized("family_chat_nav_accessibility"))

            if wsRealtimeUnavailable {
                familyChatWebSocketBanner
            }

            if AppConfig.isFamilyChatE2EEEnabled && !e2eeManager.isReady {
                familyChatE2EEBanner
            }

            if familyChatHasLegacyMessages {
                familyChatLegacyThreadBanner
            }

            if !onlineUsers.isEmpty {
                familyChatOnlineMembersStrip
            }

            if isSearching {
                ChatSearchBar(
                    searchText: $searchText,
                    isSearching: $isSearching,
                    onClear: {
                        searchText = ""
                        filteredMessages = messages
                    }
                )
                .padding(Spacing.screenPadding)
            }

            if !normalizedTypingUsers.isEmpty {
                TypingIndicatorView(typingUsers: normalizedTypingUsers)
            }

            familyChatMessagesScrollArea
        }
    }

    private var familyChatHasLegacyMessages: Bool {
        AppConfig.isFamilyChatE2EEEnabled && messages.contains { $0.isLegacyPlaintext }
    }

    private var familyChatLegacyThreadBanner: some View {
        HStack(spacing: Spacing.s) {
            Image(systemName: "exclamationmark.shield.fill")
                .foregroundColor(.orange)
            Text(localizationManager.localized("family_chat_legacy_thread_hint"))
                .font(.caption)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
            Spacer(minLength: 0)
        }
        .padding(.horizontal, Spacing.screenPadding)
        .padding(.vertical, Spacing.s)
    }

    private var familyChatE2EEBanner: some View {
        HStack(spacing: Spacing.s) {
            Image(systemName: "lock.fill")
                .foregroundColor(.secondaryGold)
            Text(localizationManager.localized("family_chat_e2ee_setup"))
                .font(.caption)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
            Spacer(minLength: 0)
        }
        .padding(.horizontal, Spacing.screenPadding)
        .padding(.vertical, Spacing.s)
    }

    private var familyChatWebSocketBanner: some View {
        HStack(spacing: Spacing.s) {
            Image(systemName: "antenna.radiowaves.left.and.right.slash")
                .foregroundColor(.orange)
            Text(localizationManager.localized("family_chat_ws_offline_hint"))
                .font(.caption)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)
            Spacer(minLength: 0)
            Button(localizationManager.localized("family_chat_reconnect")) {
                webSocket?.reconnectNow()
            }
            .font(.caption.weight(.semibold))
        }
        .padding(.horizontal, Spacing.screenPadding)
        .padding(.vertical, Spacing.s)
        .background(Color.orange.opacity(0.12))
    }

    private var familyChatOnlineMembersStrip: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 6) {
                ForEach(Array(onlineUsers).sorted(), id: \.self) { user in
                    Text(user)
                        .font(.caption2)
                        .foregroundColor(.white.opacity(0.9))
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.green.opacity(0.22))
                        .clipShape(Capsule())
                }
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
        .padding(.top, 6)
    }

    private var familyChatMessagesScrollArea: some View {
        ScrollViewReader { proxy in
            ScrollView {
                VStack(spacing: Spacing.m) {
                    if let replyTo = replyToMessage {
                        ReplyBubbleView(replyTo: replyTo) {
                            replyToMessage = nil
                        }
                        .padding(.horizontal, Spacing.screenPadding)
                    }

                    ForEach(displayMessages) { message in
                        familyChatMessageRow(message)
                    }
                }
                .padding(Spacing.screenPadding)
            }
            .onAppear {
                DispatchQueue.main.async {
                    if let lastMessage = messages.last {
                        scrollToMessage(lastMessage.id, proxy: proxy)
                    }
                }
            }
            .onChange(of: messages.count) { _ in
                guard let lastMessage = messages.last else { return }
                let messageId = lastMessage.id
                DispatchQueue.main.async {
                    scrollToMessage(messageId, proxy: proxy)
                }
            }
            .accessibilityElement(children: .contain)
            .accessibilityLabel(localizationManager.localized("family_chat_messages_list"))
        }
    }

    @ViewBuilder
    private func familyChatMessageRow(_ message: FamilyChatMessage) -> some View {
        if message.mediaType != nil || message.messageType == .image || message.messageType == .video || message.messageType == .voice {
            MediaMessageBubble(
                message: message,
                isCurrentUser: message.isCurrentUser,
                uploadProgress: message.uploadProgress
            )
            .id(message.id)
            .contextMenu {
                MessageContextMenu(
                    message: message,
                    onDelete: { deleteMessage(message) },
                    onEdit: { startEditing(message) },
                    onReply: { replyToMessage = message },
                    onCopy: { copyMessage(message) },
                    onForward: { forwardMessage(message) },
                    onAddReaction: { showReactionPicker(for: message) }
                )
            }
        } else {
            MessageBubbleView(
                message: message,
                replyPreview: replyPreview(for: message),
                allMessages: [],
                onLongPress: {
                    selectedMessage = message
                    showMessageActions = true
                },
                onReaction: { emoji in
                    addReaction(to: message, emoji: emoji)
                }
            )
            .id(message.id)
            .contextMenu {
                MessageContextMenu(
                    message: message,
                    onDelete: { deleteMessage(message) },
                    onEdit: { startEditing(message) },
                    onReply: { replyToMessage = message },
                    onCopy: { copyMessage(message) },
                    onForward: { forwardMessage(message) },
                    onAddReaction: { showReactionPicker(for: message) }
                )
            }
        }
    }

    private var familyChatCoreChrome: some View {
        familyChatMainColumn
            .background(StormMeshBackground(variant: .family))
            .onReceive(Timer.publish(every: 8.0, on: .main, in: .common).autoconnect()) { _ in
                if !isLoading && !isSending {
                    loadMessages(silent: true)
                }
            }
            .onReceive(Timer.publish(every: 1.0, on: .main, in: .common).autoconnect()) { _ in
                pruneStaleTypingIndicators()
            }
            .accessibilityElement(children: .contain)
            .accessibilityLabel(localizationManager.localized("family_chat_accessibility"))
            .navigationBarHidden(true)
            .safeAreaInset(edge: .top) {
                Color.clear.frame(height: Spacing.m)
            }
            .safeAreaInset(edge: .bottom) {
                composerBar
            }
    }

    private var familyChatLifecycleAttached: some View {
        familyChatCoreChrome
            .task {
                print("🚨 FamilyChatScreen загружен!")
                markFamilyActivity()
                await refreshFamilyContextFromMembersAPI()
                updateOnlineMembersCount()
                loadCachedMessages()
                let hadCachedSnapshot = !messages.isEmpty
                loadMessages(silent: hadCachedSnapshot)
                if AppConfig.isFamilyChatE2EEEnabled, let fid = getFamilyId(), !fid.isEmpty {
                    await e2eeManager.bootstrap(familyId: fid)
                }
                setupWebSocket()
                setupPushNotifications()
            }
            .onReceive(NotificationCenter.default.publisher(for: UIApplication.didBecomeActiveNotification)) { _ in
                if let ws = webSocket, !ws.isConnected, ws.connectionStatus != .connecting {
                    ws.connect()
                }
            }
            .onDisappear {
                typingTextDebounceTask?.cancel()
                typingStopWorkItem?.cancel()
                webSocket?.sendStopTyping()
                webSocket?.disconnect()
            }
    }

    private var familyChatSheetsLayer: some View {
        familyChatLifecycleAttached
            .sheet(isPresented: $showMediaPicker) {
                ImagePickerView(sourceType: .photoLibrary) { image in
                    selectedMedia = image
                    sendMediaMessage(image: image)
                }
                .aladdinSheetPresentation()
            }
            .sheet(isPresented: $showCamera) {
                ImagePickerView(sourceType: .camera) { image in
                    selectedMedia = image
                    sendMediaMessage(image: image)
                }
                .aladdinSheetPresentation()
            }
            .sheet(isPresented: $showMessageActions) {
                Group {
                    if let message = selectedMessage {
                        MessageActionsMenu(
                            message: message,
                            onDelete: { deleteMessage(message) },
                            onEdit: { startEditing(message) },
                            onReply: { replyToMessage = message },
                            onCopy: { copyMessage(message) },
                            onForward: { forwardMessage(message) },
                            onAddReaction: { showReactionPicker(for: message) }
                        )
                    }
                }
                .aladdinSheetPresentation()
            }
            .sheet(isPresented: $showFeedbackSheet) {
                AIFeedbackSheet(
                    isPresented: $showFeedbackSheet,
                    apiService: apiService,
                    resolvedBy: "family_chat_feedback_sheet"
                )
                .environmentObject(localizationManager)
            }
    }

    private var familyChatDialogsLayer: some View {
        familyChatSheetsLayer
            .confirmationDialog(
                localizationManager.localized("family_chat_title"),
                isPresented: $showComposerActions
            ) {
                Button(localizationManager.localized("family_chat_action_emoji")) {
                    showQuickReactionPicker = true
                }
                Button(localizationManager.localized("family_chat_action_quick_reply")) {
                    applyQuickReplyFromMenu()
                }
                Button(localizationManager.localized("family_chat_voice_button")) {
                    if isRecordingVoice {
                        if let url = voiceRecorder.stopRecording() {
                            recordingURL = url
                            sendVoiceMessage(url: url)
                        }
                        isRecordingVoice = false
                    } else if voiceRecorder.startRecording() != nil {
                        isRecordingVoice = true
                    }
                }
                Button(localizationManager.localized("family_chat_action_camera")) {
                    showCamera = true
                }
                Button(localizationManager.localized("family_chat_action_gallery")) {
                    showMediaPicker = true
                }
                Button(localizationManager.localized("family_chat_action_file")) {
                    showFileImporter = true
                }
                Button(localizationManager.localized("family_chat_action_location")) {
                    shareCurrentLocation()
                }
                Button(localizationManager.localized("family_chat_action_contact")) {
                    showContactPicker = true
                }
                Button(localizationManager.localized("family_chat_action_feedback")) {
                    showFeedbackSheet = true
                }
                Button(localizationManager.localized(isSearching ? "family_chat_action_hide_search" : "family_chat_action_search")) {
                    isSearching.toggle()
                    if !isSearching {
                        searchText = ""
                        filteredMessages = messages
                    }
                }
                Button(localizationManager.localized("family_chat_voice_cancel"), role: .cancel) {}
            }
            .confirmationDialog(
                localizationManager.localized("family_chat_action_choose_reaction"),
                isPresented: $showQuickReactionPicker
            ) {
                ForEach(["👍", "❤️", "🔥", "😂", "👏", "🙏", "😮", "🎉"], id: \.self) { emoji in
                    Button(emoji) {
                        applyQuickReactionFromMenu(emoji: emoji)
                    }
                }
                Button(localizationManager.localized("family_chat_voice_cancel"), role: .cancel) {}
            }
            .fileImporter(
                isPresented: $showFileImporter,
                allowedContentTypes: [.data, .content],
                allowsMultipleSelection: false
            ) { result in
                switch result {
                case .success(let urls):
                    guard let url = urls.first else { return }
                    let text = String(
                        format: localizationManager.localized("family_chat_action_file_attached_format"),
                        url.lastPathComponent
                    )
                    messageText = text
                    sendMessage()
                case .failure(let error):
                    presentChatError(error.localizedDescription, context: "fileImporter", underlying: error)
                }
            }
            .sheet(isPresented: $showContactPicker) {
                ContactPickerView(
                    onSelect: { contact in
                        sendContactCard(contact)
                    },
                    onCancel: {
                        showContactPicker = false
                    }
                )
                .aladdinSheetPresentation()
            }
    }

    private var familyChatInteractionOverlays: some View {
        familyChatDialogsLayer
            .overlay {
                Group {
                    if isRecordingVoice {
                        VoiceRecordingView(
                            recorder: voiceRecorder,
                            onSend: { url in
                                recordingURL = url
                                sendVoiceMessage(url: url)
                                isRecordingVoice = false
                            },
                            onCancel: {
                                voiceRecorder.cancelRecording()
                                isRecordingVoice = false
                            }
                        )
                        .padding()
                    }
                    if isResolvingLocation {
                        ProgressView(localizationManager.localized("family_chat_action_location_fetching"))
                            .padding()
                            .background(Color.black.opacity(0.75))
                            .foregroundColor(.white)
                            .cornerRadius(12)
                    }
                }
            }
            .onChange(of: messageText) { newValue in
                scheduleTypingSideEffects(for: newValue)
            }
            .onChange(of: searchText) { newValue in
                filterMessages(newValue)
            }
            .overlay {
                if isLoading {
                    ProgressView()
                        .scaleEffect(1.5)
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                        .background(Color.black.opacity(0.3))
                }
            }
    }

    private var familyChatRootDecorated: some View {
        familyChatInteractionOverlays
            .alert(
                localizationManager.localized("family_chat_error_title"),
                isPresented: Binding(
                    get: { chatErrorMessage != nil },
                    set: { if !$0 { chatErrorMessage = nil } }
                ),
                actions: {
                    Button(localizationManager.localized("family_chat_error_ok")) {
                        chatErrorMessage = nil
                    }
                },
                message: {
                    Text(chatErrorMessage ?? "")
                }
            )
    }
    
    // MARK: - Helper Methods

    private var presenceSubtitle: String {
        if onlineUsers.isEmpty {
            return String(format: localizationManager.localized("family_chat_subtitle"), onlineMembersCount)
        }
        let sorted = Array(onlineUsers).sorted()
        let preview = sorted.prefix(2).joined(separator: ", ")
        if sorted.count > 2 {
            let more = sorted.count - 2
            return "\(preview) +\(more)"
        }
        return preview
    }

    private var normalizedTypingUsers: [String] {
        Array(Set(typingUsers.map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }))
            .filter { !$0.isEmpty }
            .sorted()
    }

    /// Единый источник с APIService: Keychain + legacy UserDefaults (`FamilyLocalStore.loadPersistedFamilyId`).
    private func getFamilyId() -> String? {
        let raw = FamilyLocalStore.loadPersistedFamilyId()
            .trimmingCharacters(in: .whitespacesAndNewlines)
        guard !raw.isEmpty else { return nil }
        return raw
    }

    /// Отличить ошибку декодирования/контракта от реальной сетевой недоступности (разный текст для пользователя).
    private static func isSendDecodingOrPayloadMismatch(_ error: Error) -> Bool {
        if let ne = error as? NetworkError {
            if case .decodingError = ne { return true }
        }
        let s = error.localizedDescription.lowercased()
        // Не считать «offline fallback» и прочие сетевые тексты несоответствием контракта (иначе ложный алерт при 404 send).
        if s.contains("mock") || s.contains("mock_fallback") || s.contains("sfm_mock") || s.contains("sfm_") { return true }
        return s.contains("couldn't be read")
            || s.contains("could not be read")
            || (s.contains("missing") && s.contains("key"))
    }

    private func dismissChatError() {
        chatErrorMessage = nil
    }

    /// Сервер должен вернуть `success: true` и непустой `messageId`; иначе декодирование могло «проглотить» пустой контракт.
    private func isSuccessfulSendResponse(_ r: SendFamilyChatMessageResponse) -> Bool {
        let sid = r.messageId.trimmingCharacters(in: .whitespacesAndNewlines)
        return r.success && !sid.isEmpty
    }

    /// Диагностика в консоль при показе алерта (endpoint HTTP сюда не передаём — его нет в колбэке APIService без доработки сетевого слоя).
    private func presentChatError(_ message: String, context: String, underlying: Error? = nil, silent: Bool? = nil) {
        let u = underlying.map { "\(Swift.type(of: $0)): \($0.localizedDescription)" } ?? "—"
        let s = silent.map { $0 ? "да" : "нет" } ?? "—"
        print("🔎 Семейный чат [\(context)] алерт: «\(message.prefix(160))» | underlying=\(u) | silentPoll=\(s)")
        chatErrorMessage = message
    }

    /// 404 после выравнивания семьи на сервере: нет членства / нет primary — не путать с декодированием.
    private func isFamilyNotFoundForChat(_ error: Error) -> Bool {
        guard let ne = error as? NetworkError else { return false }
        if case .notFound(let msg) = ne {
            let m = (msg ?? "").lowercased()
            return m.contains("family not found")
                || m.contains("family context")
                || m.contains("no family context")
        }
        return false
    }

    /// Текст для пользователя при ошибке загрузки ленты (не вешаем всё на «интернет»).
    private func localizedLoadFailureMessage(for error: Error) -> String {
        guard let ne = error as? NetworkError else {
            let d = error.localizedDescription.lowercased()
            if d.contains("network") || d.contains("internet") || d.contains("connection") || d.contains("timed out") || d.contains("could not connect") {
                return localizationManager.localized("family_chat_error_network")
            }
            return localizationManager.localized("family_chat_error_data")
        }
        switch ne {
        case .noConnection, .timeout, .dnsResolutionFailed, .serverUnavailable,
             .sslPinningFailed, .invalidCertificate, .encryptionError:
            return localizationManager.localized("family_chat_error_network")
        case .forbidden(let msg):
            let m = (msg ?? "").lowercased()
            if m.contains("not a member") {
                return localizationManager.localized("family_chat_error_upload_not_member")
            }
            return localizationManager.localized("family_chat_error_auth")
        case .unauthorized, .tokenExpired, .invalidToken, .reauthenticationRequired:
            return localizationManager.localized("family_chat_error_auth")
        case .notFound(let msg):
            let m = (msg ?? "").lowercased()
            if m.contains("family not found") || m.contains("family context") || m.contains("no family context") {
                return localizationManager.localized("family_chat_error_no_server_family")
            }
            return localizationManager.localized("family_chat_error_not_found")
        default:
            return localizationManager.localized("family_chat_error_data")
        }
    }

    private func isSecureRemoteMediaURL(_ raw: String) -> Bool {
        guard let parsed = URL(string: raw), let scheme = parsed.scheme?.lowercased() else { return false }
        if scheme == "https" { return true }
        // Local preview URLs are allowed for pending/offline UI.
        if scheme == "file" { return true }
        return false
    }

    /// `GET /api/family/members` подтягивает `X-Resolved-Family-Id` / `X-Family-Context` до ленты и синхронизирует чипы с сервером.
    private func refreshFamilyContextFromMembersAPI() async {
        let loc = localizationManager
        await withCheckedContinuation { (continuation: CheckedContinuation<Void, Never>) in
            apiService.getFamilyMembersWithSyncContext { result in
                Task { @MainActor in
                    defer { continuation.resume() }
                    switch result {
                    case .success(let ctx):
                        if ctx.members.isEmpty {
                            chatFamilyContextInvalid = true
                            updateOnlineMembersCount()
                            return
                        }
                        chatFamilyContextInvalid = false
                        if let data = Self.encodeFamilyMembersListData(from: ctx.members, localizationManager: loc) {
                            UserDefaults.standard.set(data, forKey: familyMembersKey)
                            let fid = FamilyLocalStore.loadPersistedFamilyId().trimmingCharacters(in: .whitespacesAndNewlines)
                            FamilyLocalStore.persistRosterSnapshotFamilyId(fid)
                            UserDefaults.standard.synchronize()
                        }
                        updateOnlineMembersCount()
                    case .failure:
                        chatFamilyContextInvalid = true
                        updateOnlineMembersCount()
                    }
                }
            }
        }
    }

    /// Сохраняем ростер из API в `family_members_list`, чтобы чипы совпадали с сервером.
    private static func encodeFamilyMembersListData(from members: [FamilyMemberResponse], localizationManager: LocalizationManager) -> Data? {
        let converted: [FamilyMemberData] = members.map { member in
            let normalizedRole = member.role.lowercased()
            let role: FamilyMemberCard.FamilyRole
            let parentLabels = Set(["parent", localizationManager.localized("family_role_parent_label").lowercased()])
            let childLabels = Set(["child", localizationManager.localized("family_role_child_label").lowercased()])
            let teenLabels = Set(["teenager", "teen", localizationManager.localized("family_role_teen_label").lowercased()])
            let elderlyLabels = Set(["elderly", "grandparent", localizationManager.localized("family_role_elderly_label").lowercased()])
            switch normalizedRole {
            case _ where parentLabels.contains(normalizedRole): role = .parent
            case _ where childLabels.contains(normalizedRole): role = .child
            case _ where teenLabels.contains(normalizedRole): role = .teenager
            case _ where elderlyLabels.contains(normalizedRole): role = .elderly
            default: role = .parent
            }
            let avatar: String
            switch role {
            case .parent: avatar = "👨"
            case .child: avatar = "👧"
            case .teenager: avatar = "🧒"
            case .elderly: avatar = "👵"
            }
            let protectionStatus: FamilyMemberCard.ProtectionStatus
            switch (member.status ?? "protected").lowercased() {
            case "protected": protectionStatus = .protected
            case "warning": protectionStatus = .warning
            case "danger": protectionStatus = .danger
            case "offline": protectionStatus = .offline
            default: protectionStatus = .protected
            }
            return FamilyMemberData(
                id: member.id,
                serverMemberId: member.id,
                localOnly: false,
                name: member.name,
                role: role,
                avatar: avatar,
                status: protectionStatus,
                threatsBlocked: member.threatsBlocked ?? 0,
                lastActive: member.lastActive ?? ""
            )
        }
        return try? JSONEncoder().encode(converted)
    }

    private func replyPreview(for message: FamilyChatMessage) -> FamilyChatMessage? {
        guard let rid = message.replyToMessageId?.trimmingCharacters(in: .whitespacesAndNewlines), !rid.isEmpty else { return nil }
        return messages.first(where: { $0.id == rid })
    }

    /// Не вызывать REST/WS typing синхронно из тела `onChange` — debounce через Task на MainActor.
    private func scheduleTypingSideEffects(for newValue: String) {
        typingTextDebounceTask?.cancel()
        let trimmed = newValue.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty {
            typingStopWorkItem?.cancel()
            webSocket?.sendStopTyping()
            return
        }
        typingTextDebounceTask = Task { @MainActor in
            try? await Task.sleep(nanoseconds: 350_000_000)
            guard !Task.isCancelled else { return }
            let current = messageText.trimmingCharacters(in: .whitespacesAndNewlines)
            guard !current.isEmpty else {
                webSocket?.sendStopTyping()
                return
            }
            sendTypingIndicator()
        }
    }
    
    /// Обновляет количество участников онлайн
    private func updateOnlineMembersCount() {
        guard let savedData = UserDefaults.standard.data(forKey: familyMembersKey),
              let members = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) else {
            onlineMembersCount = 0
            onlineUsers = []
            return
        }
        onlineUsers = Set(members.map(\.name))
        onlineMembersCount = onlineUsers.count
        print("✅ FamilyChatScreen: Обновлено количество участников: \(onlineMembersCount)")
    }
    
    // MARK: - Actions
    
    /// Загружает сообщения из API. Для `silent` отбрасываются устаревшие ответы при гонках с polling/после отправки.
    private func loadMessages(silent: Bool = false) {
        if !silent {
            // Любой полноэкранный запрос устаревает уже ушедшие silent — иначе старый polling перезапишет свежую ленту.
            silentMessagesFetchGeneration += 1
            isLoading = true
            dismissChatError()
        }
        // Не сбрасываем алерт при silent-опросе: иначе гонка с таймером/после failed send
        // затирает алерт до завершения запроса и даёт ложное «сбросилось само».

        let silentToken: UInt64?
        if silent {
            silentMessagesFetchGeneration += 1
            silentToken = silentMessagesFetchGeneration
        } else {
            silentToken = nil
        }

        apiService.getFamilyChatMessages { [self] result in
            DispatchQueue.main.async {
                if let token = silentToken, token != silentMessagesFetchGeneration {
                    print("ℹ️ FamilyChatScreen: отброшен устаревший silent-ответ загрузки сообщений (token=\(token))")
                    return
                }
                if !silent {
                    isLoading = false
                }

                switch result {
                case .success(let responses):
                    if let fid = getFamilyId(), !fid.isEmpty {
                        offlineManager.cacheMessages(responses, familyId: fid)
                    }
                    let serverList = responses.map { convertToMessage($0) }
                    if silent {
                        // Пустой ответ после отправки часто затирал оптимистичные пузыри (сервер ещё не отдал запись в GET).
                        if serverList.isEmpty, !messages.isEmpty {
                            let hasPending = messages.contains { $0.id.hasPrefix("pending-") }
                            let recentOutbound = lastOutboundChatCompletedAt.map { Date().timeIntervalSince($0) < 45 } ?? false
                            if hasPending || recentOutbound {
                                print("ℹ️ FamilyChatScreen: silent GET messages=[] — сохраняем ленту (\(messages.count)) pending=\(hasPending) recentOutbound=\(recentOutbound)")
                                return
                            }
                        }
                        let serverIds = Set(serverList.map(\.id))
                        let pendingExtras = messages.filter { $0.id.hasPrefix("pending-") && !serverIds.contains($0.id) }
                        messages = serverList + pendingExtras
                    } else {
                        messages = serverList
                    }
                    if !messages.isEmpty {
                        markFamilyActivity()
                    }
                    dismissChatError()

                    print("✅ FamilyChatScreen: Сообщения загружены успешно (\(messages.count) сообщений)")

                case .failure(let error):
                    print("❌ FamilyChatScreen: Ошибка загрузки сообщений: \(error.localizedDescription)")

                    if isFamilyNotFoundForChat(error) {
                        chatFamilyContextInvalid = true
                        FamilyLocalStore.clearPersistedFamilyContextWhenServerReportsNoFamily()
                    }

                    #if DEBUG
                    if messages.isEmpty && !silent && !chatFamilyContextInvalid {
                        print("ℹ️ FamilyChatScreen: Используем mock данные для отображения (DEBUG)")
                        messages = getMockMessages()
                    }
                    #endif

                    if !silent && messages.isEmpty {
                        let errorDesc = error.localizedDescription
                        if isFamilyNotFoundForChat(error) {
                            presentChatError(
                                localizationManager.localized("family_chat_error_no_server_family"),
                                context: "loadMessages.noFamilyContext",
                                underlying: error,
                                silent: silent
                            )
                        } else if errorDesc.contains("404") || errorDesc.contains("not found") || errorDesc.contains("ресурс не найден") {
                            presentChatError(
                                localizationManager.localized("family_chat_error_not_found"),
                                context: "loadMessages.notFound",
                                underlying: error,
                                silent: silent
                            )
                        } else {
                            presentChatError(
                                localizedLoadFailureMessage(for: error),
                                context: "loadMessages",
                                underlying: error,
                                silent: silent
                            )
                        }
                    } else if silent {
                        print("🔎 FamilyChatScreen: silent loadMessages завершился ошибкой (алерт не показываем): \(error.localizedDescription)")
                    }
                }
            }
        }
    }
    
    
    /// Прокручивает к указанному сообщению
    private func scrollToMessage(_ messageId: String, proxy: ScrollViewProxy) {
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            withAnimation(.easeInOut(duration: 0.3)) {
                proxy.scrollTo(messageId, anchor: .bottom)
            }
        }
    }
    
    // MARK: - Mock Data (для тестирования)
    
    private func getMockMessages() -> [FamilyChatMessage] {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        
        let now = Date()
        return [
            FamilyChatMessage(
                id: "mock_1",
                sender: "Сергей",
                text: "Всем привет! Как дела?",
                time: formatter.string(from: now.addingTimeInterval(-3600)),
                isCurrentUser: true
            ),
            FamilyChatMessage(
                id: "mock_2",
                sender: "Мария",
                text: "Привет! У нас всё хорошо 😊",
                time: formatter.string(from: now.addingTimeInterval(-3540)),
                isCurrentUser: false
            ),
            FamilyChatMessage(
                id: "mock_3",
                sender: "Маша",
                text: "Папа, можно мне ещё 30 минут?",
                time: formatter.string(from: now.addingTimeInterval(-3480)),
                isCurrentUser: false
            ),
            FamilyChatMessage(
                id: "mock_4",
                sender: "Сергей",
                text: "Конечно, дочка!",
                time: formatter.string(from: now.addingTimeInterval(-3420)),
                isCurrentUser: true
            ),
            FamilyChatMessage(
                id: "mock_5",
                sender: "Бабушка",
                text: "Как мне настроить VPN?",
                time: formatter.string(from: now.addingTimeInterval(-3300)),
                isCurrentUser: false
            ),
            FamilyChatMessage(
                id: "mock_6",
                sender: "Сергей",
                text: "Сейчас помогу! Открой настройки...",
                time: formatter.string(from: now.addingTimeInterval(-3240)),
                isCurrentUser: true
            )
        ]
    }
    
    // MARK: - Data Conversion
    
    private func convertToMessage(_ response: FamilyChatMessageResponse) -> FamilyChatMessage {
        let familyId = getFamilyId() ?? ""
        let decoded: FamilyChatMessageResponse
        if AppConfig.isFamilyChatE2EEEnabled, !familyId.isEmpty {
            decoded = FamilyE2EEManager.shared.decryptIncoming(response, familyId: familyId)
        } else {
            decoded = response
        }
        let timeString = formatTimestamp(decoded.timestamp)
        let msgType = MessageType(rawValue: decoded.messageType ?? "text") ?? .text
        var mediaKind: MediaType? = decoded.mediaType.flatMap { MediaType(rawValue: $0) }
        if mediaKind == nil, msgType == .voice || msgType == .audio {
            mediaKind = msgType == .audio ? .audio : .voice
        }
        let legacy = FamilyChatE2EULegacyPolicy.isLegacyMessage(response: decoded)
        let e2ee = FamilyChatE2EULegacyPolicy.isE2EEMessage(response: decoded)
        let decryptFailed = FamilyChatE2EULegacyPolicy.decryptionFailed(response: decoded, afterDecrypt: decoded.text)
        let redacted = legacy && FamilyChatE2EULegacyPolicy.shouldRedactLegacyPlaintext(timestamp: decoded.timestamp)
        let visibleText = FamilyChatE2EULegacyPolicy.displayText(
            raw: decoded.text,
            timestamp: decoded.timestamp,
            isLegacy: legacy,
            decryptionFailed: decryptFailed
        )

        var encryptedMedia = FamilyE2EEManager.encryptedMedia(from: decoded, familyId: familyId)
        if encryptedMedia == nil,
           e2ee,
           let b64 = decoded.ciphertext?.trimmingCharacters(in: .whitespacesAndNewlines),
           !b64.isEmpty,
           let inner = try? FamilyE2EECryptoEngine.decrypt(ciphertextBase64: b64, familyId: familyId),
           let m = inner.media {
            encryptedMedia = FamilyChatEncryptedMedia(
                ciphertextUrl: m.url,
                contentHash: m.hash,
                keyBase64: m.key,
                duration: m.duration,
                mimeType: m.mime,
                messageType: inner.t
            )
        }

        return FamilyChatMessage(
            id: decoded.id.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                ? UUID().uuidString
                : decoded.id,
            sender: decoded.sender,
            text: visibleText,
            time: timeString,
            isCurrentUser: decoded.isCurrentUser,
            messageType: msgType,
            voiceUrl: legacy ? decoded.voiceUrl : nil,
            voiceDuration: decoded.voiceDuration,
            mediaUrl: legacy ? decoded.mediaUrl : nil,
            mediaThumbnailUrl: legacy ? decoded.mediaThumbnailUrl : nil,
            mediaType: mediaKind,
            replyToMessageId: decoded.replyToMessageId,
            reactions: decoded.reactions ?? [],
            readStatus: decoded.readStatus,
            readAt: decoded.readAt,
            editedAt: decoded.editedAt,
            envelopeVersion: FamilyChatE2EULegacyPolicy.envelopeVersion(from: decoded),
            isLegacyPlaintext: legacy,
            isE2EEMessage: e2ee,
            decryptionFailed: decryptFailed,
            rawTimestamp: decoded.timestamp,
            isRedactedLegacy: redacted,
            encryptedMedia: encryptedMedia
        )
    }

    /// После upload: v2 ciphertext + blob URL или legacy plaintext URLs.
    private func submitMediaChatMessage(
        familyId: String,
        messageId: String,
        messageType: String,
        uploadType: UploadMediaType,
        uploadedUrl: String,
        voiceDuration: Double?,
        replyToMessageId: String?
    ) {
        guard requireE2EEReady(context: "submitMedia.e2ee") else { return }

        let useE2EE = AppConfig.isFamilyChatE2EEEnabled && e2eeManager.isReady
        if useE2EE, let meta = mediaUploadManager.lastE2EEUpload(forMessageId: messageId) {
            do {
                let mime = uploadMimeType(uploadType)
                let enc = try e2eeManager.encryptOutgoingMedia(
                    familyId: familyId,
                    messageType: messageType,
                    ciphertextUrl: meta.url,
                    contentHash: meta.hash,
                    keyBase64: meta.keyBase64,
                    duration: voiceDuration,
                    mimeType: mime
                )
                apiService.sendFamilyChatMessage(
                    message: nil,
                    familyId: familyId,
                    messageType: messageType,
                    voiceUrl: nil,
                    voiceDuration: voiceDuration,
                    mediaUrl: nil,
                    mediaType: uploadType.rawValue,
                    replyToMessageId: replyToMessageId,
                    envelopeVersion: 2,
                    senderDeviceId: enc.senderDeviceId,
                    ciphertext: enc.ciphertext,
                    mediaCiphertextUrl: meta.url,
                    mediaCiphertextHash: meta.hash
                ) { [self] sendResult in
                    handleMediaSendResult(sendResult, familyId: familyId, messageId: messageId, messageType: messageType, uploadedUrl: uploadedUrl, voiceDuration: voiceDuration, replyToMessageId: replyToMessageId)
                }
            } catch {
                presentChatError(
                    localizationManager.localized("family_chat_error_send_response"),
                    context: "submitMedia.e2ee",
                    underlying: error
                )
            }
            return
        }

        presentChatError(
            localizationManager.localized("family_chat_e2ee_not_ready"),
            context: "submitMedia.e2eeMissingMeta"
        )
    }

    private func handleMediaSendResult(
        _ sendResult: Result<SendFamilyChatMessageResponse, Error>,
        familyId: String,
        messageId: String,
        messageType: String,
        uploadedUrl: String,
        voiceDuration: Double?,
        replyToMessageId: String?
    ) {
        DispatchQueue.main.async {
            switch sendResult {
            case .success(let r):
                guard self.isSuccessfulSendResponse(r) else {
                    self.presentChatError(
                        self.localizationManager.localized("family_chat_error_send_response"),
                        context: "submitMedia.contract",
                        underlying: nil
                    )
                    return
                }
                self.replyToMessage = nil
                self.lastOutboundChatCompletedAt = Date()
                self.loadMessages(silent: true)
            case .failure(let err):
                if self.isFamilyNotFoundForChat(err) {
                    self.chatFamilyContextInvalid = true
                    self.presentChatError(
                        self.localizationManager.localized("family_chat_error_no_server_family"),
                        context: "submitMedia.familyNotResolved",
                        underlying: err
                    )
                } else {
                    self.presentChatError(
                        self.localizedLoadFailureMessage(for: err),
                        context: "submitMedia",
                        underlying: err
                    )
                }
                self.offlineManager.addPendingMessage(PendingChatMessage(
                    id: UUID(uuidString: messageId) ?? UUID(),
                    text: nil,
                    familyId: familyId,
                    messageType: messageType,
                    voiceUrl: uploadedUrl,
                    voiceDuration: voiceDuration,
                    mediaUrl: uploadedUrl,
                    mediaType: messageType,
                    replyToMessageId: replyToMessageId
                ))
            }
        }
    }

    private func uploadMimeType(_ type: UploadMediaType) -> String {
        switch type {
        case .image: return "image/jpeg"
        case .video: return "video/mp4"
        case .audio, .voice: return "audio/m4a"
        }
    }
    
    // ✅ ИСПРАВЛЕНИЕ BUILD 90: Статические форматтеры для предотвращения рекурсии
    private static let timestampFormatters: [DateFormatter] = {
        let formats = [
            "yyyy-MM-dd'T'HH:mm:ss",
            "yyyy-MM-dd'T'HH:mm:ss.SSS",
            "yyyy-MM-dd'T'HH:mm:ssZ",
            "yyyy-MM-dd HH:mm:ss"
        ]
        return formats.map { format in
            let formatter = DateFormatter()
            formatter.dateFormat = format
            formatter.locale = Locale(identifier: "ru_RU") // Статический locale
            return formatter
        }
    }()
    
    private static let timeFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        formatter.locale = Locale(identifier: "ru_RU") // Статический locale
        return formatter
    }()
    
    private func formatTimestamp(_ timestamp: String) -> String {
        // ✅ Используем статические форматтеры вместо создания новых каждый раз
        for formatter in Self.timestampFormatters {
            if let date = formatter.date(from: timestamp) {
                return Self.timeFormatter.string(from: date)
            }
        }
        
        return getCurrentTime()
    }
    
    private func getCurrentTime() -> String {
        // ✅ Используем статический formatter вместо создания нового каждый раз
        return Self.timeFormatter.string(from: Date())
    }
    
    // MARK: - Extended Features
    
    /// Отображаемые сообщения (с учетом поиска)
    private var displayMessages: [FamilyChatMessage] {
        if isSearching && !searchText.isEmpty {
            return filteredMessages
        }
        return messages
    }

    private var composerBar: some View {
        VStack(spacing: 8) {
            if chatFamilyContextInvalid {
                Text(localizationManager.localized("family_chat_banner_no_family"))
                    .font(.footnote)
                    .foregroundColor(Color(UIColor.secondaryLabel))
                    .multilineTextAlignment(.center)
                    .frame(maxWidth: .infinity)
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.vertical, 6)
                    .background(Color.orange.opacity(0.15))
                    .cornerRadius(10)
            }
            HStack(alignment: .bottom, spacing: 10) {
                Button(action: {
                    showComposerActions = true
                }) {
                    Image(systemName: isRecordingVoice ? "stop.circle.fill" : "plus.circle.fill")
                        .font(.system(size: 20, weight: .semibold))
                        .foregroundColor(isRecordingVoice ? .red : .textPrimary)
                        .frame(width: 42, height: 42)
                        .background(Color.surfaceDark.opacity(0.55))
                        .cornerRadius(12)
                }
                .disabled(chatFamilyContextInvalid)
                .accessibilityLabel(localizationManager.localized("family_chat_voice_button"))
                .accessibilityHint(localizationManager.localized("family_chat_action_open_menu"))

                ZStack(alignment: .topLeading) {
                    if messageText.isEmpty {
                        Text(localizationManager.localized("family_chat_input_placeholder"))
                            .foregroundColor(Color(UIColor.secondaryLabel))
                            .padding(.horizontal, 14)
                            .padding(.vertical, 12)
                            .allowsHitTesting(false)
                    }

                    TextEditor(text: $messageText)
                        .font(.system(size: 16))
                        .foregroundColor(Color(UIColor.label))
                        .padding(.horizontal, 10)
                        .padding(.vertical, 8)
                        .frame(minHeight: 44, maxHeight: composerHeight(for: messageText))
                        .background(Color.clear)
                        .disabled(isSending || chatFamilyContextInvalid)
                        .accessibilityLabel(localizationManager.localized("family_chat_input_accessibility"))
                        .accessibilityHint(localizationManager.localized("family_chat_input_hint"))
                }
                .background(Color(UIColor.secondarySystemGroupedBackground))
                .overlay(
                    RoundedRectangle(cornerRadius: 14)
                        .stroke(Color(UIColor.separator), lineWidth: 1)
                )
                .cornerRadius(14)

                Button(action: {
                    sendMessage()
                }) {
                    if isSending {
                        ProgressView()
                            .scaleEffect(0.85)
                            .frame(width: 42, height: 42)
                    } else {
                        Image(systemName: "paperplane.fill")
                            .font(.system(size: 17, weight: .semibold))
                            .foregroundColor(.backgroundDark)
                            .frame(width: 42, height: 42)
                            .background(messageText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? Color.surfaceDark.opacity(0.5) : Color.secondaryGold)
                            .cornerRadius(12)
                    }
                }
                .disabled(chatFamilyContextInvalid || messageText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isSending)
                .accessibilityLabel(localizationManager.localized("family_chat_send_button"))
                .accessibilityHint(localizationManager.localized("family_chat_send_hint"))
            }
            .padding(Spacing.m)
            .stormGlassCard(cornerRadius: 16)
            .padding(.horizontal, Spacing.screenPadding)
            .padding(.top, 8)
            .padding(.bottom, 8)
        }
    }

    private func composerHeight(for text: String) -> CGFloat {
        let lineBreakCount = text.components(separatedBy: .newlines).count
        let estimatedWrappedLines = max(1, Int(ceil(Double(text.count) / 34.0)))
        let lineCount = max(lineBreakCount, estimatedWrappedLines)
        let clampedLines = min(max(lineCount, 1), 5)
        return CGFloat(clampedLines * 24 + 20)
    }
    
    /// Фильтрация сообщений по поисковому запросу
    private func filterMessages(_ query: String) {
        if query.isEmpty {
            filteredMessages = messages
        } else {
            filteredMessages = messages.filter { message in
                message.text?.localizedCaseInsensitiveContains(query) ?? false
            }
        }
    }
    
    /// Настройка WebSocket
    private func setupWebSocket() {
        let familyId = getFamilyId()
        webSocket = FamilyChatWebSocket(familyId: familyId)
        
        webSocket?.onNewMessage = { [self] response in
            let newMessage = convertToMessage(response)
            if !messages.contains(where: { $0.id == newMessage.id }) {
                messages.append(newMessage)
                scrollToLastMessage()
            }
        }
        
        webSocket?.onTyping = { [self] userName, isTyping in
            if isTyping {
                if !typingUsers.contains(userName) {
                    typingUsers.append(userName)
                }
                typingExpiryByUser[userName] = Date().addingTimeInterval(6.0)
            } else {
                typingUsers.removeAll { $0 == userName }
                typingExpiryByUser.removeValue(forKey: userName)
            }
        }

        webSocket?.onPresence = { [self] userName, isOnline in
            if isOnline {
                onlineUsers.insert(userName)
            } else {
                onlineUsers.remove(userName)
                typingUsers.removeAll { $0 == userName }
                typingExpiryByUser.removeValue(forKey: userName)
            }
            onlineMembersCount = onlineUsers.count
        }

        webSocket?.onConnectionStatus = { [self] status in
            switch status {
            case .connected:
                wsRealtimeUnavailable = false
            case .connecting:
                wsRealtimeUnavailable = false
                typingUsers.removeAll()
                typingExpiryByUser.removeAll()
            case .reconnecting, .disconnected, .error:
                wsRealtimeUnavailable = true
                typingUsers.removeAll()
                typingExpiryByUser.removeAll()
                onlineUsers.removeAll()
                onlineMembersCount = 0
            }
        }
        
        webSocket?.onMessageDeleted = { [self] messageId in
            messages.removeAll { $0.id == messageId }
        }
        
        webSocket?.onMessageEdited = { [self] messageId, newText in
            if let index = messages.firstIndex(where: { $0.id == messageId }) {
                messages[index] = messages[index].withUpdatedText(newText, editedAt: getCurrentTime())
            }
        }
        
        webSocket?.connect()
    }
    
    /// Настройка push-уведомлений
    private func setupPushNotifications() {
        pushService.requestAuthorization()
    }
    
    /// E2EE обязателен — без silent plaintext fallback.
    private func requireE2EEReady(context: String) -> Bool {
        guard !AppConfig.isFamilyChatE2EEEnabled || e2eeManager.isReady else {
            presentChatError(
                localizationManager.localized("family_chat_e2ee_not_ready"),
                context: context
            )
            return false
        }
        return true
    }

    /// Загрузка кэшированных сообщений
    private func loadCachedMessages() {
        let cached = offlineManager.loadCachedMessages(familyId: getFamilyId())
        if messages.isEmpty && !cached.isEmpty {
            messages = cached.map { convertToMessage($0) }
        }
    }
    
    /// Отправка голосового: загрузка через MediaUploadManager, затем регистрация сообщения на сервере
    private func sendVoiceMessage(url: URL) {
        guard !chatFamilyContextInvalid else {
            presentChatError(localizationManager.localized("family_chat_error_no_server_family"), context: "sendVoiceMessage.contextInvalid")
            return
        }
        guard let familyId = getFamilyId(), !familyId.isEmpty else {
            presentChatError(localizationManager.localized("family_chat_error_family_missing"), context: "sendVoiceMessage.noFamilyId")
            return
        }
        guard let data = try? Data(contentsOf: url), !data.isEmpty else {
            presentChatError(localizationManager.localized("family_chat_error_data"), context: "sendVoiceMessage.emptyFile")
            return
        }
        
        let duration = voiceRecorder.recordingDuration
        let messageId = UUID().uuidString
        let localPreviewUrl = url.absoluteString
        
        let newMessage = FamilyChatMessage(
            id: messageId,
            sender: localizationManager.localized("family_chat_you"),
            text: nil,
            time: getCurrentTime(),
            isCurrentUser: true,
            messageType: .voice,
            voiceUrl: localPreviewUrl,
            voiceDuration: duration,
            mediaUrl: nil,
            mediaType: .voice,
            uploadProgress: 0.0
        )
        messages.append(newMessage)
        
        mediaUploadManager.uploadMedia(
            data: data,
            type: .voice,
            forMessageId: messageId,
            familyId: familyId
        ) { [self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let uploadedUrl):
                    guard isSecureRemoteMediaURL(uploadedUrl) else {
                        presentChatError(
                            localizationManager.localized("family_chat_error_upload_insecure_url"),
                            context: "sendVoiceMessage.upload.insecureURL"
                        )
                        return
                    }
                    if let idx = messages.firstIndex(where: { $0.id == messageId }) {
                        var m = messages[idx]
                        m = FamilyChatMessage(
                            id: m.id,
                            sender: m.sender,
                            text: m.text,
                            time: m.time,
                            isCurrentUser: m.isCurrentUser,
                            messageType: .voice,
                            voiceUrl: uploadedUrl,
                            voiceDuration: duration,
                            mediaUrl: uploadedUrl,
                            mediaThumbnailUrl: m.mediaThumbnailUrl,
                            mediaType: .voice,
                            replyToMessageId: m.replyToMessageId,
                            reactions: m.reactions,
                            readStatus: m.readStatus,
                            readAt: m.readAt,
                            editedAt: m.editedAt,
                            uploadProgress: 1.0
                        )
                        messages[idx] = m
                    }
                    
                    self.submitMediaChatMessage(
                        familyId: familyId,
                        messageId: messageId,
                        messageType: "voice",
                        uploadType: .voice,
                        uploadedUrl: uploadedUrl,
                        voiceDuration: duration,
                        replyToMessageId: self.replyToMessage?.id
                    )

                case .failure(let error):
                    presentChatError(
                        localizedLoadFailureMessage(for: error),
                        context: "sendVoiceMessage.upload",
                        underlying: error
                    )
                    offlineManager.addPendingMessage(PendingChatMessage(
                        id: UUID(uuidString: messageId)!,
                        text: nil,
                        familyId: familyId,
                        messageType: "voice",
                        voiceUrl: localPreviewUrl,
                        voiceDuration: duration,
                        mediaUrl: nil,
                        mediaType: "voice",
                        replyToMessageId: replyToMessage?.id
                    ))
                }
            }
        }
    }
    
    /// ✅ Отправка изображения: upload → регистрация сообщения на сервере
    private func sendMediaMessage(image: UIImage) {
        guard let imageData = image.jpegData(compressionQuality: 0.8) else { return }
        guard !chatFamilyContextInvalid else {
            presentChatError(localizationManager.localized("family_chat_error_no_server_family"), context: "sendMediaMessage.contextInvalid")
            return
        }
        guard let familyId = getFamilyId(), !familyId.isEmpty else {
            presentChatError(localizationManager.localized("family_chat_error_family_missing"), context: "sendMediaMessage.noFamilyId")
            return
        }
        
        let messageId = UUID().uuidString
        
        let newMessage = FamilyChatMessage(
            id: messageId,
            sender: localizationManager.localized("family_chat_you"),
            text: nil,
            time: getCurrentTime(),
            isCurrentUser: true,
            messageType: .image,
            mediaUrl: nil,
            mediaType: .image,
            uploadProgress: 0.0
        )
        
        messages.append(newMessage)
        
        mediaUploadManager.uploadMedia(
            data: imageData,
            type: .image,
            forMessageId: messageId,
            familyId: familyId
        ) { [self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let mediaUrl):
                    guard isSecureRemoteMediaURL(mediaUrl) else {
                        presentChatError(
                            localizationManager.localized("family_chat_error_upload_insecure_url"),
                            context: "sendMediaMessage.upload.insecureURL"
                        )
                        return
                    }
                    if let index = messages.firstIndex(where: { $0.id == messageId }) {
                        let prev = messages[index]
                        messages[index] = FamilyChatMessage(
                            id: prev.id,
                            sender: prev.sender,
                            text: prev.text,
                            time: prev.time,
                            isCurrentUser: prev.isCurrentUser,
                            messageType: .image,
                            voiceUrl: prev.voiceUrl,
                            voiceDuration: prev.voiceDuration,
                            mediaUrl: mediaUrl,
                            mediaThumbnailUrl: prev.mediaThumbnailUrl,
                            mediaType: .image,
                            replyToMessageId: prev.replyToMessageId,
                            reactions: prev.reactions,
                            readStatus: prev.readStatus,
                            readAt: prev.readAt,
                            editedAt: prev.editedAt,
                            uploadProgress: 1.0
                        )
                    }
                    
                    self.submitMediaChatMessage(
                        familyId: familyId,
                        messageId: messageId,
                        messageType: "image",
                        uploadType: .image,
                        uploadedUrl: mediaUrl,
                        voiceDuration: nil,
                        replyToMessageId: self.replyToMessage?.id
                    )

                case .failure(let error):
                    presentChatError(
                        localizedLoadFailureMessage(for: error),
                        context: "sendMediaMessage.upload",
                        underlying: error
                    )
                    offlineManager.addPendingMessage(PendingChatMessage(
                        id: UUID(uuidString: messageId)!,
                        text: nil,
                        familyId: familyId,
                        messageType: "image",
                        mediaUrl: nil,
                        mediaType: "image",
                        replyToMessageId: replyToMessage?.id
                    ))
                }
            }
        }
    }
    
    /// Отправка индикатора "печатает..."
    private func sendTypingIndicator() {
        guard !chatFamilyContextInvalid else { return }
        let trimmed = messageText.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty {
            typingStopWorkItem?.cancel()
            webSocket?.sendStopTyping()
            return
        }

        let now = Date()
        if now.timeIntervalSince(lastTypingSignalAt) >= 1.2 {
            webSocket?.sendTyping()
            apiService.sendTypingIndicator(familyId: getFamilyId()) { _ in }
            lastTypingSignalAt = now
        }

        typingStopWorkItem?.cancel()
        let stopTask = DispatchWorkItem {
            webSocket?.sendStopTyping()
        }
        typingStopWorkItem = stopTask
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0, execute: stopTask)
    }

    private func pruneStaleTypingIndicators() {
        let now = Date()
        let staleUsers = typingExpiryByUser.compactMap { user, expiresAt in
            expiresAt < now ? user : nil
        }
        guard !staleUsers.isEmpty else { return }
        staleUsers.forEach { user in
            typingExpiryByUser.removeValue(forKey: user)
            typingUsers.removeAll { $0 == user }
        }
    }
    
    /// Удаление сообщения
    private func deleteMessage(_ message: FamilyChatMessage) {
        apiService.deleteFamilyChatMessage(messageId: message.id) { [self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(_):
                    messages.removeAll { $0.id == message.id }
                case .failure(let error):
                    let description = error.localizedDescription.lowercased()
                    if description.contains("invalid user_id") || description.contains("invalid user id") {
                        presentChatError(
                            localizationManager.localized("family_chat_error_auth"),
                            context: "deleteMessage.invalidUser",
                            underlying: error
                        )
                    } else {
                        presentChatError(
                            localizedLoadFailureMessage(for: error),
                            context: "deleteMessage",
                            underlying: error
                        )
                    }
                }
            }
        }
    }
    
    /// Начало редактирования сообщения
    private func startEditing(_ message: FamilyChatMessage) {
        guard FamilyChatE2EULegacyPolicy.canEdit(message: message) else {
            presentChatError(
                localizationManager.localized("family_chat_error_edit_not_allowed"),
                context: "startEditing.e2eeOrLegacy"
            )
            return
        }
        editingMessage = message
        editText = message.text ?? ""
        showMessageActions = false
    }
    
    /// Сохранение редактирования
    private func saveEdit() {
        guard let message = editingMessage else { return }
        
        apiService.editFamilyChatMessage(messageId: message.id, newText: editText) { [self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(_):
                    if let index = messages.firstIndex(where: { $0.id == message.id }) {
                        messages[index] = messages[index].withUpdatedText(editText, editedAt: getCurrentTime())
                    }
                    editingMessage = nil
                    editText = ""
                case .failure(let error):
                    presentChatError(
                        localizedLoadFailureMessage(for: error),
                        context: "saveEdit",
                        underlying: error
                    )
                }
            }
        }
    }
    
    /// Копирование сообщения
    private func copyMessage(_ message: FamilyChatMessage) {
        if let text = message.text {
            UIPasteboard.general.string = text
        }
    }
    
    /// Пересылка сообщения
    private func forwardMessage(_ message: FamilyChatMessage) {
        // TODO: Реализовать пересылку
        print("📤 Пересылка сообщения: \(message.text ?? "")")
    }
    
    /// Добавление реакции
    private func addReaction(to message: FamilyChatMessage, emoji: String) {
        apiService.addReaction(messageId: message.id, emoji: emoji) { [self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(_):
                    // Обновляем сообщение с новой реакцией
                    if let index = messages.firstIndex(where: { $0.id == message.id }) {
                        let updated = messages[index]
                        var reactions = updated.reactions
                        reactions.append(MessageReaction(emoji: emoji, userId: "current_user", userName: "You"))
                        messages[index] = FamilyChatMessage(
                            id: updated.id,
                            sender: updated.sender,
                            text: updated.text,
                            time: updated.time,
                            isCurrentUser: updated.isCurrentUser,
                            messageType: updated.messageType,
                            voiceUrl: updated.voiceUrl,
                            voiceDuration: updated.voiceDuration,
                            mediaUrl: updated.mediaUrl,
                            mediaThumbnailUrl: updated.mediaThumbnailUrl,
                            mediaType: updated.mediaType,
                            replyToMessageId: updated.replyToMessageId,
                            reactions: reactions,
                            readStatus: updated.readStatus,
                            readAt: updated.readAt,
                            editedAt: updated.editedAt
                        )
                    }
                case .failure(let error):
                    presentChatError(
                        localizedLoadFailureMessage(for: error),
                        context: "addReaction",
                        underlying: error
                    )
                }
            }
        }
    }
    
    /// Показ пикера реакций
    private func showReactionPicker(for message: FamilyChatMessage) {
        // TODO: Показать модальное окно с выбором реакции
        selectedMessage = message
    }
    
    /// Прокрутка к последнему сообщению
    private func scrollToLastMessage() {
        // Выполняется через onChange в ScrollViewReader
    }
    
    /// Обновление отправки сообщения для поддержки ответов
    private func sendMessage() {
        guard !messageText.isEmpty && !isSending else { return }

        guard !chatFamilyContextInvalid else {
            presentChatError(
                localizationManager.localized("family_chat_error_no_server_family"),
                context: "sendMessage.contextInvalid"
            )
            return
        }
        
        let messageToSend = messageText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !messageToSend.isEmpty else {
            messageText = ""
            return
        }
        
        guard let familyId = getFamilyId(), !familyId.isEmpty else {
            presentChatError(localizationManager.localized("family_chat_error_family_missing"), context: "sendMessage.noFamilyId")
            return
        }
        guard requireE2EEReady(context: "sendMessage.e2ee") else { return }

        isSending = true
        markFamilyActivity()
        typingTextDebounceTask?.cancel()
        messageText = ""
        typingStopWorkItem?.cancel()
        webSocket?.sendStopTyping()
        
        let impactFeedback = UIImpactFeedbackGenerator(style: .light)
        impactFeedback.impactOccurred()
        
        var envelopeVersion: Int? = nil
        var senderDeviceId: String? = nil
        var ciphertext: String? = nil
        var plaintextForSend: String? = nil

        if AppConfig.isFamilyChatE2EEEnabled {
            do {
                let enc = try e2eeManager.encryptOutgoing(
                    plaintext: messageToSend,
                    messageType: "text",
                    familyId: familyId
                )
                envelopeVersion = 2
                senderDeviceId = enc.senderDeviceId
                ciphertext = enc.ciphertext
            } catch {
                isSending = false
                messageText = messageToSend
                presentChatError(
                    localizationManager.localized("family_chat_error_send_response"),
                    context: "sendMessage.e2ee",
                    underlying: error
                )
                return
            }
        } else {
            plaintextForSend = messageToSend
        }

        apiService.sendFamilyChatMessage(
            message: plaintextForSend,
            familyId: familyId,
            messageType: "text",
            voiceUrl: nil,
            voiceDuration: nil,
            mediaUrl: nil,
            mediaType: nil,
            replyToMessageId: replyToMessage?.id,
            envelopeVersion: envelopeVersion,
            senderDeviceId: senderDeviceId,
            ciphertext: ciphertext
        ) { [self] result in
            DispatchQueue.main.async {
                isSending = false
                
                switch result {
                case .success(let sendResponse):
                    guard isSuccessfulSendResponse(sendResponse) else {
                        messageText = messageToSend
                        presentChatError(
                            localizationManager.localized("family_chat_error_send_response"),
                            context: "sendMessage.contract",
                            underlying: nil
                        )
                        return
                    }
                    let capturedReplyId = replyToMessage?.id
                    replyToMessage = nil
                    dismissChatError()
                    // Оптимистичное отображение сразу на девайсе, даже если следующий silent-poll задержится.
                    let sid = sendResponse.messageId.trimmingCharacters(in: .whitespacesAndNewlines)
                    let optimisticId = sid.isEmpty ? "pending-\(UUID().uuidString)" : sid
                    let optimistic = FamilyChatMessage(
                        id: optimisticId,
                        sender: localizationManager.localized("family_chat_you"),
                        text: messageToSend,
                        time: getCurrentTime(),
                        isCurrentUser: true,
                        messageType: .text,
                        voiceUrl: nil,
                        voiceDuration: nil,
                        mediaUrl: nil,
                        mediaThumbnailUrl: nil,
                        mediaType: nil,
                        replyToMessageId: capturedReplyId,
                        reactions: [],
                        readStatus: nil,
                        readAt: nil,
                        editedAt: nil,
                        uploadProgress: nil,
                        envelopeVersion: envelopeVersion ?? 1,
                        isLegacyPlaintext: false,
                        isE2EEMessage: envelopeVersion == 2,
                        decryptionFailed: false,
                        rawTimestamp: nil,
                        isRedactedLegacy: false
                    )
                    if !messages.contains(where: { $0.id == optimisticId }) {
                        messages.append(optimistic)
                    }
                    lastOutboundChatCompletedAt = Date()
                    loadMessages(silent: true)

                    pushService.sendChatNotification(
                        message: messageToSend,
                        sender: "You", // TODO: Получить реальное имя
                        familyId: familyId
                    )

                case .failure(let error):
                    messageText = messageToSend

                    if offlineManager.isOffline, AppConfig.isFamilyChatE2EEEnabled, let cipher = ciphertext {
                        offlineManager.addPendingMessage(PendingChatMessage(
                            text: nil,
                            familyId: familyId,
                            replyToMessageId: replyToMessage?.id,
                            envelopeVersion: 2,
                            senderDeviceId: senderDeviceId,
                            ciphertext: cipher
                        ))
                    }

                    if isFamilyNotFoundForChat(error) {
                        chatFamilyContextInvalid = true
                        presentChatError(
                            localizationManager.localized("family_chat_error_no_server_family"),
                            context: "sendMessage.familyNotResolved",
                            underlying: error
                        )
                    } else if Self.isSendDecodingOrPayloadMismatch(error) {
                        presentChatError(
                            localizationManager.localized("family_chat_error_send_response"),
                            context: "sendMessage.decodeOrContract",
                            underlying: error
                        )
                    } else {
                        presentChatError(
                            localizedLoadFailureMessage(for: error),
                            context: "sendMessage",
                            underlying: error
                        )
                    }
                }
            }
        }
    }

    private func markFamilyActivity() {
        UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: homeChatLastFamilyActivityKey)
    }

    private func quickActionTargetMessage() -> FamilyChatMessage? {
        if let selectedMessage {
            return selectedMessage
        }
        return messages.last
    }

    private func applyQuickReplyFromMenu() {
        guard let target = quickActionTargetMessage() else { return }
        replyToMessage = target
    }

    private func applyQuickReactionFromMenu(emoji: String) {
        if messageText.isEmpty {
            messageText = emoji
        } else {
            messageText.append(emoji)
        }
    }

    private func shareCurrentLocation() {
        isResolvingLocation = true
        locationShareManager.requestCurrentLocation { result in
            DispatchQueue.main.async {
                isResolvingLocation = false
                switch result {
                case .success(let location):
                    let coordinates = String(format: "%.5f, %.5f", location.coordinate.latitude, location.coordinate.longitude)
                    let mapURL = "https://maps.apple.com/?ll=\(location.coordinate.latitude),\(location.coordinate.longitude)"
                    messageText = String(
                        format: localizationManager.localized("family_chat_action_location_card_format"),
                        coordinates,
                        mapURL
                    )
                    sendMessage()
                case .failure:
                    presentChatError(
                        localizationManager.localized("family_chat_action_location_error"),
                        context: "shareCurrentLocation"
                    )
                }
            }
        }
    }

    private func sendContactCard(_ contact: CNContact) {
        let formatter = CNContactFormatter()
        formatter.style = .fullName
        let fullName = formatter.string(from: contact)?.trimmingCharacters(in: .whitespacesAndNewlines)
        let displayName = (fullName?.isEmpty == false ? fullName! : localizationManager.localized("family_chat_you"))
        let phone = contact.phoneNumbers.first?.value.stringValue ?? localizationManager.localized("family_chat_action_contact_no_phone")
        messageText = String(
            format: localizationManager.localized("family_chat_action_contact_card_format"),
            displayName,
            phone
        )
        sendMessage()
    }
}

private final class LocationShareManager: NSObject, ObservableObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    private var completion: ((Result<CLLocation, Error>) -> Void)?

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyHundredMeters
    }

    func requestCurrentLocation(completion: @escaping (Result<CLLocation, Error>) -> Void) {
        self.completion = completion
        guard CLLocationManager.locationServicesEnabled() else {
            completion(.failure(NSError(domain: "Location", code: 1, userInfo: nil)))
            return
        }
        switch manager.authorizationStatus {
        case .authorizedWhenInUse, .authorizedAlways:
            manager.requestLocation()
        case .notDetermined:
            manager.requestWhenInUseAuthorization()
        case .restricted, .denied:
            completion(.failure(NSError(domain: "Location", code: 2, userInfo: nil)))
        @unknown default:
            completion(.failure(NSError(domain: "Location", code: 3, userInfo: nil)))
        }
    }

    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        switch manager.authorizationStatus {
        case .authorizedWhenInUse, .authorizedAlways:
            manager.requestLocation()
        case .restricted, .denied:
            completion?(.failure(NSError(domain: "Location", code: 2, userInfo: nil)))
            completion = nil
        default:
            break
        }
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.first else {
            completion?(.failure(NSError(domain: "Location", code: 4, userInfo: nil)))
            completion = nil
            return
        }
        completion?(.success(location))
        completion = nil
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        completion?(.failure(error))
        completion = nil
    }
}

private struct ContactPickerView: UIViewControllerRepresentable {
    let onSelect: (CNContact) -> Void
    let onCancel: () -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(onSelect: onSelect, onCancel: onCancel)
    }

    func makeUIViewController(context: Context) -> CNContactPickerViewController {
        let picker = CNContactPickerViewController()
        picker.delegate = context.coordinator
        picker.displayedPropertyKeys = [CNContactGivenNameKey, CNContactFamilyNameKey, CNContactPhoneNumbersKey]
        return picker
    }

    func updateUIViewController(_ uiViewController: CNContactPickerViewController, context: Context) {}

    final class Coordinator: NSObject, CNContactPickerDelegate {
        let onSelect: (CNContact) -> Void
        let onCancel: () -> Void

        init(onSelect: @escaping (CNContact) -> Void, onCancel: @escaping () -> Void) {
            self.onSelect = onSelect
            self.onCancel = onCancel
        }

        func contactPicker(_ picker: CNContactPickerViewController, didSelect contact: CNContact) {
            onSelect(contact)
            onCancel()
        }

        func contactPickerDidCancel(_ picker: CNContactPickerViewController) {
            onCancel()
        }
    }
}

// MARK: - Family Chat Message (обновлено для полноценной медиа-поддержки)

/// ✅ Обновлённая модель с чёткой типизацией медиа (Phase 2026)
struct FamilyChatMessage: Identifiable {
    /// Серверный идентификатор (`MSG_…`), не случайный UUID — нужен для реакций/удаления/ответов.
    let id: String
    let sender: String
    let text: String?
    let time: String
    let isCurrentUser: Bool
    
    // Тип сообщения
    let messageType: MessageType
    
    // Медиа контент
    let voiceUrl: String?
    let voiceDuration: Double?
    let mediaUrl: String?
    /// Превью кадра (видео / лёгкий URL для списка), если сервер прислал отдельно от `mediaUrl`
    let mediaThumbnailUrl: String?
    let mediaType: MediaType?
    
    let replyToMessageId: String?
    let reactions: [MessageReaction]
    let readStatus: String?
    let readAt: String?
    let editedAt: String?
    
    // Локальное состояние для UI
    var uploadProgress: Double? = nil // 0.0...1.0 для отображения прогресса

    // E1.5 E2EE / legacy
    let envelopeVersion: Int?
    let isLegacyPlaintext: Bool
    let isE2EEMessage: Bool
    let decryptionFailed: Bool
    let rawTimestamp: String?
    /// Текст скрыт по политике 90 дней (legacy на сервере).
    let isRedactedLegacy: Bool
    let encryptedMedia: FamilyChatEncryptedMedia?

    var showsLegacyBanner: Bool { isLegacyPlaintext && !decryptionFailed }
    var showsE2EELock: Bool { isE2EEMessage && !decryptionFailed && !isLegacyPlaintext }
    
    init(id: String = UUID().uuidString, 
         sender: String, 
         text: String? = nil, 
         time: String, 
         isCurrentUser: Bool,
         messageType: MessageType = .text,
         voiceUrl: String? = nil,
         voiceDuration: Double? = nil,
         mediaUrl: String? = nil,
         mediaThumbnailUrl: String? = nil,
         mediaType: MediaType? = nil,
         replyToMessageId: String? = nil,
         reactions: [MessageReaction] = [],
         readStatus: String? = nil,
         readAt: String? = nil,
         editedAt: String? = nil,
         uploadProgress: Double? = nil,
         envelopeVersion: Int? = nil,
         isLegacyPlaintext: Bool = false,
         isE2EEMessage: Bool = false,
         decryptionFailed: Bool = false,
         rawTimestamp: String? = nil,
         isRedactedLegacy: Bool = false,
         encryptedMedia: FamilyChatEncryptedMedia? = nil) {
        
        self.id = id
        self.sender = sender
        self.text = text
        self.time = time
        self.isCurrentUser = isCurrentUser
        self.messageType = messageType
        self.voiceUrl = voiceUrl
        self.voiceDuration = voiceDuration
        self.mediaUrl = mediaUrl
        self.mediaThumbnailUrl = mediaThumbnailUrl
        self.mediaType = mediaType
        self.replyToMessageId = replyToMessageId
        self.reactions = reactions
        self.readStatus = readStatus
        self.readAt = readAt
        self.editedAt = editedAt
        self.uploadProgress = uploadProgress
        self.envelopeVersion = envelopeVersion
        self.isLegacyPlaintext = isLegacyPlaintext
        self.isE2EEMessage = isE2EEMessage
        self.decryptionFailed = decryptionFailed
        self.rawTimestamp = rawTimestamp
        self.isRedactedLegacy = isRedactedLegacy
        self.encryptedMedia = encryptedMedia
    }

    func withUpdatedText(_ newText: String, editedAt: String?) -> FamilyChatMessage {
        FamilyChatMessage(
            id: id,
            sender: sender,
            text: newText,
            time: time,
            isCurrentUser: isCurrentUser,
            messageType: messageType,
            voiceUrl: voiceUrl,
            voiceDuration: voiceDuration,
            mediaUrl: mediaUrl,
            mediaThumbnailUrl: mediaThumbnailUrl,
            mediaType: mediaType,
            replyToMessageId: replyToMessageId,
            reactions: reactions,
            readStatus: readStatus,
            readAt: readAt,
            editedAt: editedAt,
            uploadProgress: uploadProgress,
            envelopeVersion: envelopeVersion,
            isLegacyPlaintext: isLegacyPlaintext,
            isE2EEMessage: isE2EEMessage,
            decryptionFailed: decryptionFailed,
            rawTimestamp: rawTimestamp,
            isRedactedLegacy: isRedactedLegacy,
            encryptedMedia: encryptedMedia
        )
    }
}

enum MessageType: String {
    case text = "text"
    case image = "image"
    case video = "video"
    case voice = "voice"
    case audio = "audio"
    case file = "file"
}

enum MediaType: String {
    case image = "image"
    case video = "video"
    case voice = "voice"
    case audio = "audio"
}

// MARK: - Message Bubble View (Extended)

struct MessageBubbleView: View {
    let message: FamilyChatMessage
    /// Если задан — показываем цитату ответа без зависимости от всего массива `messages` (меньше перерисовок / циклов SwiftUI).
    let replyPreview: FamilyChatMessage?
    let allMessages: [FamilyChatMessage]
    let onLongPress: () -> Void
    let onReaction: (String) -> Void
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    init(
        message: FamilyChatMessage,
        replyPreview: FamilyChatMessage? = nil,
        allMessages: [FamilyChatMessage] = [],
        onLongPress: @escaping () -> Void,
        onReaction: @escaping (String) -> Void
    ) {
        self.message = message
        self.replyPreview = replyPreview
        self.allMessages = allMessages
        self.onLongPress = onLongPress
        self.onReaction = onReaction
    }

    private var resolvedReplyTo: FamilyChatMessage? {
        if let replyPreview, !replyPreview.id.isEmpty { return replyPreview }
        guard let replyToId = message.replyToMessageId?.trimmingCharacters(in: .whitespacesAndNewlines), !replyToId.isEmpty else { return nil }
        return allMessages.first(where: { $0.id == replyToId })
    }
    
    var body: some View {
        VStack(alignment: message.isCurrentUser ? .trailing : .leading, spacing: Spacing.xxs) {
            // Reply Preview
            if let replyTo = resolvedReplyTo {
                ReplyBubbleView(replyTo: replyTo) {}
                    .padding(.bottom, Spacing.xxs)
            }
            
            // Message Content
            Group {
                switch message.messageType {
                case .voice, .audio:
                    VoiceMessageBubble(message: message)
                case .image, .video:
                    MediaMessageBubble(
                        message: message,
                        isCurrentUser: message.isCurrentUser,
                        uploadProgress: message.uploadProgress
                    )
                default:
                    // Text message
                    HStack {
                        if message.isCurrentUser {
                            Spacer()
                        }
                        
                        VStack(alignment: message.isCurrentUser ? .trailing : .leading, spacing: Spacing.xxs) {
                            if !message.isCurrentUser {
                                Text(message.sender)
                                    .font(.captionBold)
                                    .foregroundColor(.secondaryGold)
                            }

                            if message.showsLegacyBanner {
                                familyChatSecurityCaption(
                                    icon: "exclamationmark.shield",
                                    text: localizationManager.localized("family_chat_legacy_not_e2ee")
                                )
                            } else if message.decryptionFailed {
                                familyChatSecurityCaption(
                                    icon: "lock.slash",
                                    text: localizationManager.localized("family_chat_e2ee_decrypt_failed")
                                )
                            } else if message.isRedactedLegacy {
                                familyChatSecurityCaption(
                                    icon: "clock.badge.exclamationmark",
                                    text: localizationManager.localized("family_chat_legacy_redacted")
                                )
                            }
                            
                            if let text = message.text, !text.isEmpty {
                                HStack(alignment: .top, spacing: 6) {
                                    if message.showsE2EELock {
                                        Image(systemName: "lock.fill")
                                            .font(.caption)
                                            .foregroundColor(message.isCurrentUser ? Color.white.opacity(0.85) : .secondaryGold)
                                            .padding(.top, 2)
                                    }
                                    Text(text)
                                        .font(.body)
                                        .foregroundColor(message.isCurrentUser ? Color.white : Color(UIColor.label))
                                }
                                .padding(Spacing.m)
                                .background(
                                    message.isCurrentUser
                                        ? Color.primaryBlue
                                        : Color(UIColor.secondarySystemBackground)
                                )
                                .cornerRadius(CornerRadius.medium)
                            }
                            
                            HStack(spacing: Spacing.xs) {
                                Text(message.time)
                                    .font(.captionSmall)
                                    .foregroundColor(.textTertiary)
                                
                                if message.editedAt != nil {
                                    Text(localizationManager.localized("family_chat_message_edited"))
                                        .font(.captionSmall)
                                        .foregroundColor(.textTertiary)
                                }
                                
                                if message.isCurrentUser {
                                    Image(systemName: statusIcon)
                                        .font(.captionSmall)
                                        .foregroundColor(statusColor)
                                }
                            }
                        }
                        .frame(maxWidth: UIScreen.main.bounds.width * 0.7, alignment: message.isCurrentUser ? .trailing : .leading)
                        
                        if !message.isCurrentUser {
                            Spacer()
                        }
                    }
                }
            }
            .onLongPressGesture {
                onLongPress()
            }
            
            // Reactions
            if !message.reactions.isEmpty {
                MessageReactionsView(
                    message: message,
                    onAddReaction: onReaction,
                    onRemoveReaction: { emoji in
                        onReaction(emoji) // Переключаем реакцию
                    }
                )
            }
        }
    }
    
    @ViewBuilder
    private func familyChatSecurityCaption(icon: String, text: String) -> some View {
        HStack(spacing: 6) {
            Image(systemName: icon)
                .font(.caption2)
            Text(text)
                .font(.caption2)
                .fixedSize(horizontal: false, vertical: true)
        }
        .foregroundColor(.textTertiary)
        .padding(.horizontal, Spacing.s)
        .padding(.vertical, 4)
        .background(Color(UIColor.tertiarySystemFill))
        .cornerRadius(CornerRadius.small)
    }

    private var statusIcon: String {
        switch message.readStatus {
        case "read":
            return "checkmark.circle.fill"
        case "delivered":
            return "checkmark.circle"
        default:
            return "circle"
        }
    }
    
    private var statusColor: Color {
        switch message.readStatus {
        case "read":
            return .secondaryGold
        case "delivered":
            return .textTertiary
        default:
            return .textTertiary.opacity(0.5)
        }
    }
}

// MARK: - Chat Bubble View (Legacy)

struct ChatBubbleView: View {
    let message: FamilyChatMessage
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        MessageBubbleView(
            message: message,
            replyPreview: nil,
            allMessages: [],
            onLongPress: {},
            onReaction: { _ in }
        )
    }
}

// MARK: - Message Context Menu

struct MessageContextMenu: View {
    let message: FamilyChatMessage
    let onDelete: () -> Void
    let onEdit: () -> Void
    let onReply: () -> Void
    let onCopy: () -> Void
    let onForward: () -> Void
    let onAddReaction: () -> Void
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        Group {
            Button(action: onReply) {
                Label(localizationManager.localized("family_chat_message_reply"), systemImage: "arrowshape.turn.up.left")
            }
            
            if message.text != nil {
                Button(action: onCopy) {
                    Label(localizationManager.localized("family_chat_message_copy"), systemImage: "doc.on.doc")
                }
            }
            
            Button(action: onAddReaction) {
                Label(localizationManager.localized("family_chat_reaction_add"), systemImage: "face.smiling")
            }
            
            if FamilyChatE2EULegacyPolicy.canEdit(message: message) {
                Button(action: onEdit) {
                    Label(localizationManager.localized("family_chat_message_edit"), systemImage: "pencil")
                }
            }
            
            if message.isCurrentUser {
                Button(role: .destructive, action: onDelete) {
                    Label(localizationManager.localized("family_chat_message_delete"), systemImage: "trash")
                }
            }
        }
    }
}

// MARK: - Image Picker (gallery / camera)

struct ImagePickerView: UIViewControllerRepresentable {
    let sourceType: UIImagePickerController.SourceType
    let onSelect: (UIImage) -> Void
    @Environment(\.dismiss) private var dismiss
    
    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        picker.sourceType = resolvedSourceType()
        picker.allowsEditing = true
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    private func resolvedSourceType() -> UIImagePickerController.SourceType {
        if UIImagePickerController.isSourceTypeAvailable(sourceType) {
            return sourceType
        }

        let fallbackCandidates: [UIImagePickerController.SourceType] = [.photoLibrary, .savedPhotosAlbum]
        for candidate in fallbackCandidates where UIImagePickerController.isSourceTypeAvailable(candidate) {
            return candidate
        }

        // Last-resort safe default; avoids crashing on unavailable camera in simulator.
        return .photoLibrary
    }
    
    final class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: ImagePickerView
        
        init(_ parent: ImagePickerView) {
            self.parent = parent
        }
        
        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
            if let image = info[.editedImage] as? UIImage ?? info[.originalImage] as? UIImage {
                parent.onSelect(image)
            }
            parent.dismiss()
        }
        
        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            parent.dismiss()
        }
    }
}

// MARK: - Preview

struct FamilyChatScreen_Previews: PreviewProvider {
    static var previews: some View {
        FamilyChatScreen()
            .environmentObject(NavigationManager())
            .environmentObject(LocalizationManager())
    }
}
