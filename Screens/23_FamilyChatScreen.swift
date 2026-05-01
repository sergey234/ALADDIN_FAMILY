import SwiftUI
import AVFoundation
import UserNotifications
import UIKit
import UniformTypeIdentifiers
import Contacts
import ContactsUI
import CoreLocation

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
    @State private var errorMessage: String? = nil
    @State private var refreshTimer: Timer? = nil
    @State private var onlineMembersCount: Int = 0
    @State private var onlineUsers: Set<String> = []
    
    // Extended features state
    @StateObject private var voiceRecorder = VoiceMessageRecorder()
    /// Синглтоны: `@ObservedObject`, не `@StateObject` (иначе конфликт владения и риск реентрантности с Combine).
    @ObservedObject private var offlineManager = FamilyChatOfflineManager.shared
    @ObservedObject private var mediaUploadManager = MediaUploadManager.shared
    @ObservedObject private var pushService = PushNotificationService.shared
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
    @State private var chatTheme: ChatTheme = .auto
    @State private var showCamera: Bool = false
    @State private var showComposerActions: Bool = false
    @State private var showQuickReactionPicker: Bool = false
    @State private var showFileImporter: Bool = false
    @State private var showContactPicker: Bool = false
    @State private var isResolvingLocation: Bool = false
    @State private var typingStopWorkItem: DispatchWorkItem? = nil
    @State private var lastTypingSignalAt: Date = .distantPast
    @State private var typingExpiryByUser: [String: Date] = [:]
    @State private var presencePruneTimer: Timer? = nil
    
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
        VStack(spacing: 0) {
            ALADDINNavigationBar(
                title: localizationManager.localized("family_chat_title"),
                subtitle: presenceSubtitle,
                showBackButton: true,
                showProfileButton: false,
                showListButton: false,
                onBack: {
                    stopAutoRefresh()
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

            if !onlineUsers.isEmpty {
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
            
            // Search Bar
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
            
            // Typing Indicator
            if !normalizedTypingUsers.isEmpty {
                TypingIndicatorView(typingUsers: normalizedTypingUsers)
            }
            
            // Messages List with ScrollViewReader
            ScrollViewReader { proxy in
                ScrollView {
                    VStack(spacing: Spacing.m) {
                        // Reply Preview
                        if let replyTo = replyToMessage {
                            ReplyBubbleView(replyTo: replyTo) {
                                replyToMessage = nil
                            }
                            .padding(.horizontal, Spacing.screenPadding)
                        }
                        
                        // Messages
                        ForEach(displayMessages) { message in
                            if message.mediaType != nil || message.messageType == .image || message.messageType == .video || message.messageType == .voice {
                                // Используем специализированный MediaMessageBubble для всех медиа
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
                                    allMessages: messages,
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
                    }
                    .padding(Spacing.screenPadding)
                }
                .onAppear {
                    // Сохраняем proxy для использования в методах
                    DispatchQueue.main.async {
                        if let lastMessage = messages.last {
                            scrollToMessage(lastMessage.id, proxy: proxy)
                        }
                    }
                }
                .onChange(of: messages.count) { _ in
                    // Автопрокрутка при появлении новых сообщений
                    if let lastMessage = messages.last {
                        scrollToMessage(lastMessage.id, proxy: proxy)
                    }
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel(localizationManager.localized("family_chat_messages_list"))
            }
            
        }
        .background(LinearGradient.backgroundGradient.ignoresSafeArea())
        .accessibilityElement(children: .contain)
        .accessibilityLabel(localizationManager.localized("family_chat_accessibility"))
        .navigationBarHidden(true)
        .safeAreaInset(edge: .top) {
            Color.clear.frame(height: Spacing.m)
        }
        .safeAreaInset(edge: .bottom) {
            composerBar
        }
        .task {
            print("🚨 FamilyChatScreen загружен!")
            markFamilyActivity()
            updateOnlineMembersCount()
            loadCachedMessages()
            let hadCachedSnapshot = !messages.isEmpty
            loadMessages(silent: hadCachedSnapshot)
            startAutoRefresh()
            setupWebSocket()
            setupPushNotifications()
            startPresencePruneTimer()
        }
        .onDisappear {
            stopAutoRefresh()
            stopPresencePruneTimer()
            typingStopWorkItem?.cancel()
            webSocket?.sendStopTyping()
            webSocket?.disconnect()
        }
        .sheet(isPresented: $showMediaPicker) {
            ImagePickerView(sourceType: .photoLibrary) { image in
                selectedMedia = image
                sendMediaMessage(image: image)
            }
        }
        .sheet(isPresented: $showCamera) {
            ImagePickerView(sourceType: .camera) { image in
                selectedMedia = image
                sendMediaMessage(image: image)
            }
        }
        .sheet(isPresented: $showMessageActions) {
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
                errorMessage = error.localizedDescription
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
        }
        .overlay {
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
        .onChange(of: messageText) { _ in
            sendTypingIndicator()
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
        .alert(localizationManager.localized("family_chat_error_title"), isPresented: .constant(errorMessage != nil)) {
            Button(localizationManager.localized("family_chat_error_ok")) {
                errorMessage = nil
            }
        } message: {
            if let error = errorMessage {
                Text(error)
            }
        }
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

    /// Получает familyId из UserDefaults (канонический ключ — `FamilyLocalStore.familyIdKey`).
    private func getFamilyId() -> String? {
        let raw = UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey)?
            .trimmingCharacters(in: .whitespacesAndNewlines)
        guard let raw, !raw.isEmpty else { return nil }
        return raw
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
    
    // MARK: - Auto Refresh
    
    /// Запускает автоматическое обновление сообщений
    private func startAutoRefresh() {
        stopAutoRefresh() // Останавливаем предыдущий таймер, если есть
        
        refreshTimer = Timer.scheduledTimer(withTimeInterval: 8.0, repeats: true) { [self] _ in
            // Обновляем только если экран активен и нет активной загрузки
            if !isLoading && !isSending {
                loadMessages(silent: true)
            }
        }
        
        // Добавляем таймер в RunLoop для работы в фоне
        if let timer = refreshTimer {
            RunLoop.current.add(timer, forMode: .common)
        }
        
        print("✅ FamilyChatScreen: Автообновление запущено (интервал: 8 секунд)")
    }
    
    /// Останавливает автоматическое обновление
    private func stopAutoRefresh() {
        refreshTimer?.invalidate()
        refreshTimer = nil
        print("✅ FamilyChatScreen: Автообновление остановлено")
    }
    
    // MARK: - Actions
    
    /// Загружает сообщения из API
    private func loadMessages(silent: Bool = false) {
        if !silent {
            isLoading = true
        }
        errorMessage = nil
        
        apiService.getFamilyChatMessages { [self] result in
            DispatchQueue.main.async {
                if !silent {
                    isLoading = false
                }
                
                switch result {
                case .success(let responses):
                    messages = responses.map { response in
                        convertToMessage(response)
                    }
                    if !messages.isEmpty {
                        markFamilyActivity()
                    }
                    errorMessage = nil
                    
                    // Автопрокрутка будет выполнена через onChange
                    
                    print("✅ FamilyChatScreen: Сообщения загружены успешно (\(messages.count) сообщений)")
                    
                case .failure(let error):
                    print("❌ FamilyChatScreen: Ошибка загрузки сообщений: \(error.localizedDescription)")
                    
                    // Mock только в DEBUG: в Release при ошибке не подставляем русскоязычный фейковый чат.
                    #if DEBUG
                    if messages.isEmpty && !silent {
                        print("ℹ️ FamilyChatScreen: Используем mock данные для отображения (DEBUG)")
                        messages = getMockMessages()
                    }
                    #endif
                    
                    // Показываем ошибку только если это не silent обновление и нет данных
                    if !silent && messages.isEmpty {
                        let errorDesc = error.localizedDescription
                        if errorDesc.contains("404") || errorDesc.contains("not found") || errorDesc.contains("ресурс не найден") {
                            errorMessage = localizationManager.localized("family_chat_error_not_found")
                        } else if errorDesc.contains("network") || errorDesc.contains("connection") {
                            errorMessage = localizationManager.localized("family_chat_error_loading")
                        } else {
                            errorMessage = localizationManager.localized("family_chat_error_loading")
                        }
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
        let timeString = formatTimestamp(response.timestamp)
        let msgType = MessageType(rawValue: response.messageType ?? "text") ?? .text
        var mediaKind: MediaType? = response.mediaType.flatMap { MediaType(rawValue: $0) }
        if mediaKind == nil, msgType == .voice || msgType == .audio {
            mediaKind = msgType == .audio ? .audio : .voice
        }
        
        return FamilyChatMessage(
            id: response.id.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                ? UUID().uuidString
                : response.id,
            sender: response.sender,
            text: response.text,
            time: timeString,
            isCurrentUser: response.isCurrentUser,
            messageType: msgType,
            voiceUrl: response.voiceUrl,
            voiceDuration: response.voiceDuration,
            mediaUrl: response.mediaUrl,
            mediaThumbnailUrl: response.mediaThumbnailUrl,
            mediaType: mediaKind,
            replyToMessageId: response.replyToMessageId,
            reactions: response.reactions ?? [],
            readStatus: response.readStatus,
            readAt: response.readAt,
            editedAt: response.editedAt
        )
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
                .accessibilityLabel(localizationManager.localized("family_chat_voice_button"))
                .accessibilityHint(localizationManager.localized("family_chat_action_open_menu"))

                ZStack(alignment: .topLeading) {
                    if messageText.isEmpty {
                        Text(localizationManager.localized("family_chat_input_placeholder"))
                            .foregroundColor(Color.black.opacity(0.55))
                            .padding(.horizontal, 14)
                            .padding(.vertical, 12)
                            .allowsHitTesting(false)
                    }

                    TextEditor(text: $messageText)
                        .font(.system(size: 16))
                        .foregroundColor(.black)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 8)
                        .frame(minHeight: 44, maxHeight: composerHeight(for: messageText))
                        .background(Color.clear)
                        .disabled(isSending)
                        .accessibilityLabel(localizationManager.localized("family_chat_input_accessibility"))
                        .accessibilityHint(localizationManager.localized("family_chat_input_hint"))
                }
                .background(Color.white.opacity(0.96))
                .overlay(
                    RoundedRectangle(cornerRadius: 14)
                        .stroke(Color.black.opacity(0.18), lineWidth: 1)
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
                .disabled(messageText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isSending)
                .accessibilityLabel(localizationManager.localized("family_chat_send_button"))
                .accessibilityHint(localizationManager.localized("family_chat_send_hint"))
            }
            .padding(.horizontal, Spacing.screenPadding)
            .padding(.top, 8)
            .padding(.bottom, 8)
        }
        .background(LinearGradient.cardGradient.appGlassmorphism())
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
                break
            case .connecting, .reconnecting:
                typingUsers.removeAll()
                typingExpiryByUser.removeAll()
            case .disconnected, .error:
                // Не держим stale presence во время разрыва канала.
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
                let updatedMessage = messages[index]
                // Обновляем текст сообщения
                messages[index] = FamilyChatMessage(
                    id: updatedMessage.id,
                    sender: updatedMessage.sender,
                    text: newText,
                    time: updatedMessage.time,
                    isCurrentUser: updatedMessage.isCurrentUser,
                    messageType: updatedMessage.messageType,
                    voiceUrl: updatedMessage.voiceUrl,
                    voiceDuration: updatedMessage.voiceDuration,
                    mediaUrl: updatedMessage.mediaUrl,
                    mediaThumbnailUrl: updatedMessage.mediaThumbnailUrl,
                    mediaType: updatedMessage.mediaType,
                    replyToMessageId: updatedMessage.replyToMessageId,
                    reactions: updatedMessage.reactions,
                    readStatus: updatedMessage.readStatus,
                    readAt: updatedMessage.readAt,
                    editedAt: getCurrentTime()
                )
            }
        }
        
        webSocket?.connect()
    }
    
    /// Настройка push-уведомлений
    private func setupPushNotifications() {
        pushService.requestAuthorization()
    }
    
    /// Загрузка кэшированных сообщений
    private func loadCachedMessages() {
        let cached = offlineManager.loadCachedMessages()
        if messages.isEmpty && !cached.isEmpty {
            messages = cached.map { convertToMessage($0) }
        }
    }
    
    /// Отправка голосового: загрузка через MediaUploadManager, затем регистрация сообщения на сервере
    private func sendVoiceMessage(url: URL) {
        guard let familyId = getFamilyId(), !familyId.isEmpty else {
            errorMessage = localizationManager.localized("family_chat_error_loading")
            return
        }
        guard let data = try? Data(contentsOf: url), !data.isEmpty else {
            errorMessage = localizationManager.localized("family_chat_error_loading")
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
                    
                    self.apiService.sendFamilyChatMessage(
                        message: nil,
                        familyId: familyId,
                        messageType: "voice",
                        voiceUrl: uploadedUrl,
                        voiceDuration: duration,
                        mediaUrl: uploadedUrl,
                        mediaType: "voice",
                        replyToMessageId: self.replyToMessage?.id
                    ) { sendResult in
                        DispatchQueue.main.async {
                            switch sendResult {
                            case .success:
                                self.replyToMessage = nil
                                self.loadMessages(silent: true)
                            case .failure(let err):
                                self.errorMessage = err.localizedDescription
                                self.offlineManager.addPendingMessage(PendingChatMessage(
                                    id: UUID(uuidString: messageId)!,
                                    text: nil,
                                    familyId: familyId,
                                    messageType: "voice",
                                    voiceUrl: uploadedUrl,
                                    voiceDuration: duration,
                                    mediaUrl: uploadedUrl,
                                    mediaType: "voice",
                                    replyToMessageId: self.replyToMessage?.id
                                ))
                            }
                        }
                    }
                    
                case .failure(let error):
                    errorMessage = error.localizedDescription
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
        guard let familyId = getFamilyId(), !familyId.isEmpty else {
            errorMessage = localizationManager.localized("family_chat_error_loading")
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
                    
                    self.apiService.sendFamilyChatMessage(
                        message: nil,
                        familyId: familyId,
                        messageType: "image",
                        voiceUrl: nil,
                        voiceDuration: nil,
                        mediaUrl: mediaUrl,
                        mediaType: "image",
                        replyToMessageId: self.replyToMessage?.id
                    ) { sendResult in
                        DispatchQueue.main.async {
                            switch sendResult {
                            case .success:
                                self.replyToMessage = nil
                                self.loadMessages(silent: true)
                            case .failure(let err):
                                self.errorMessage = err.localizedDescription
                                self.offlineManager.addPendingMessage(PendingChatMessage(
                                    id: UUID(uuidString: messageId)!,
                                    text: nil,
                                    familyId: familyId,
                                    messageType: "image",
                                    mediaUrl: mediaUrl,
                                    mediaType: "image",
                                    replyToMessageId: self.replyToMessage?.id
                                ))
                            }
                        }
                    }
                    
                case .failure(let error):
                    errorMessage = error.localizedDescription
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
        let trimmed = messageText.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty {
            typingStopWorkItem?.cancel()
            webSocket?.sendStopTyping()
            return
        }

        let now = Date()
        if now.timeIntervalSince(lastTypingSignalAt) >= 1.2 {
            webSocket?.sendTyping()
            lastTypingSignalAt = now
        }
        apiService.sendTypingIndicator(familyId: getFamilyId()) { _ in }

        typingStopWorkItem?.cancel()
        let stopTask = DispatchWorkItem {
            webSocket?.sendStopTyping()
        }
        typingStopWorkItem = stopTask
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0, execute: stopTask)
    }

    private func startPresencePruneTimer() {
        stopPresencePruneTimer()
        presencePruneTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [self] _ in
            pruneStaleTypingIndicators()
        }
        if let timer = presencePruneTimer {
            RunLoop.current.add(timer, forMode: .common)
        }
    }

    private func stopPresencePruneTimer() {
        presencePruneTimer?.invalidate()
        presencePruneTimer = nil
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
                        errorMessage = "Не удалось подтвердить профиль по токену. Выйдите из аккаунта и войдите снова."
                    } else {
                        errorMessage = error.localizedDescription
                    }
                }
            }
        }
    }
    
    /// Начало редактирования сообщения
    private func startEditing(_ message: FamilyChatMessage) {
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
                        let updated = messages[index]
                        messages[index] = FamilyChatMessage(
                            id: updated.id,
                            sender: updated.sender,
                            text: editText,
                            time: updated.time,
                            isCurrentUser: updated.isCurrentUser,
                            messageType: updated.messageType,
                            voiceUrl: updated.voiceUrl,
                            voiceDuration: updated.voiceDuration,
                            mediaUrl: updated.mediaUrl,
                            mediaThumbnailUrl: updated.mediaThumbnailUrl,
                            mediaType: updated.mediaType,
                            replyToMessageId: updated.replyToMessageId,
                            reactions: updated.reactions,
                            readStatus: updated.readStatus,
                            readAt: updated.readAt,
                            editedAt: getCurrentTime()
                        )
                    }
                    editingMessage = nil
                    editText = ""
                case .failure(let error):
                    errorMessage = error.localizedDescription
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
                    errorMessage = error.localizedDescription
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
        
        let messageToSend = messageText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !messageToSend.isEmpty else {
            messageText = ""
            return
        }
        
        guard let familyId = getFamilyId(), !familyId.isEmpty else {
            errorMessage = localizationManager.localized("family_chat_error_loading")
            return
        }
        isSending = true
        markFamilyActivity()
        messageText = ""
        typingStopWorkItem?.cancel()
        webSocket?.sendStopTyping()
        
        let impactFeedback = UIImpactFeedbackGenerator(style: .light)
        impactFeedback.impactOccurred()
        
        apiService.sendFamilyChatMessage(
            message: messageToSend,
            familyId: familyId,
            messageType: "text",
            voiceUrl: nil,
            voiceDuration: nil,
            mediaUrl: nil,
            mediaType: nil,
            replyToMessageId: replyToMessage?.id
        ) { [self] result in
            DispatchQueue.main.async {
                isSending = false
                
                switch result {
                case .success(_):
                    replyToMessage = nil
                    // ✅ ИСПРАВЛЕНО: Используем silent: true, чтобы не показывать ошибку при неудачной загрузке
                    // Сообщение уже отправлено успешно, оно появится при следующем автообновлении
                    loadMessages(silent: true)
                    
                    // Отправляем push-уведомление другим участникам
                    pushService.sendChatNotification(
                        message: messageToSend,
                        sender: "You", // TODO: Получить реальное имя
                        familyId: familyId
                    )
                    
                case .failure(let error):
                    messageText = messageToSend
                    
                    // Добавляем в очередь офлайн
                    if offlineManager.isOffline {
                        offlineManager.addPendingMessage(PendingChatMessage(
                            text: messageToSend,
                            familyId: familyId,
                            replyToMessageId: replyToMessage?.id
                        ))
                    }
                    
                    let errorDesc = error.localizedDescription
                    if errorDesc.contains("network") || errorDesc.contains("connection") {
                        errorMessage = localizationManager.localized("family_chat_error_loading")
                    } else {
                        errorMessage = localizationManager.localized("family_chat_error_loading")
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
                    errorMessage = localizationManager.localized("family_chat_action_location_error")
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
         uploadProgress: Double? = nil) {
        
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
    let allMessages: [FamilyChatMessage]
    let onLongPress: () -> Void
    let onReaction: (String) -> Void
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    init(message: FamilyChatMessage, allMessages: [FamilyChatMessage] = [], onLongPress: @escaping () -> Void, onReaction: @escaping (String) -> Void) {
        self.message = message
        self.allMessages = allMessages
        self.onLongPress = onLongPress
        self.onReaction = onReaction
    }
    
    var body: some View {
        VStack(alignment: message.isCurrentUser ? .trailing : .leading, spacing: Spacing.xxs) {
            // Reply Preview
            if let replyToId = message.replyToMessageId,
               let replyTo = allMessages.first(where: { $0.id == replyToId }) {
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
                            
                            if let text = message.text {
                                Text(text)
                                    .font(.body)
                                    .foregroundColor(.textPrimary)
                                    .padding(Spacing.m)
                                    .background(
                                        message.isCurrentUser
                                            ? Color.primaryBlue
                                            : Color.surfaceDark
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
            
            if message.isCurrentUser && message.messageType == .text {
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
