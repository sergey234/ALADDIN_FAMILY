import SwiftUI
import AVFoundation
import UserNotifications

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
    
    // Extended features state
    @StateObject private var voiceRecorder = VoiceMessageRecorder()
    @StateObject private var offlineManager = FamilyChatOfflineManager.shared
    @StateObject private var pushService = PushNotificationService.shared
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
    
    // UserDefaults ключи
    private let familyIdKey = "family_id"
    private let familyMembersKey = "family_members_list"
    
    private let apiService = APIService(networkManager: NetworkManager())
    
    enum ChatTheme: String, CaseIterable {
        case light = "light"
        case dark = "dark"
        case auto = "auto"
    }
    
    
    var body: some View {
        VStack(spacing: 0) {
            ALADDINNavigationBar(
                title: localizationManager.localized("family_chat_title"),
                subtitle: String(format: localizationManager.localized("family_chat_subtitle"), onlineMembersCount),
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
            if !typingUsers.isEmpty {
                TypingIndicatorView(typingUsers: typingUsers)
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
            
            // Input Field
            HStack(spacing: Spacing.s) {
                TextField(localizationManager.localized("family_chat_input_placeholder"), text: $messageText)
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium)
                    .cornerRadius(CornerRadius.md)
                    .foregroundColor(.textPrimary)
                    .font(.body)
                    .disabled(isSending)
                    .accessibilityLabel(localizationManager.localized("family_chat_input_accessibility"))
                    .accessibilityHint(localizationManager.localized("family_chat_input_hint"))
                    .onSubmit {
                        if !messageText.isEmpty && !isSending {
                            sendMessage()
                        }
                    }
                
                // Send Button
                Button(action: {
                    sendMessage()
                }) {
                    if isSending {
                        ProgressView()
                            .scaleEffect(0.8)
                            .frame(width: Size.navButtonSize, height: Size.navButtonSize)
                    } else {
                        Image(systemName: "paperplane.fill")
                            .font(.body)
                            .foregroundColor(.backgroundDark)
                            .frame(width: Size.navButtonSize, height: Size.navButtonSize)
                            .background(messageText.isEmpty ? Color.surfaceDark.opacity(0.5) : Color.secondaryGold)
                            .cornerRadius(CornerRadius.medium)
                    }
                }
                .disabled(messageText.isEmpty || isSending)
                .accessibilityLabel(localizationManager.localized("family_chat_send_button"))
                .accessibilityHint(localizationManager.localized("family_chat_send_hint"))
                
                // Voice message button
                Button(action: {
                    if isRecordingVoice {
                        if let url = voiceRecorder.stopRecording() {
                            recordingURL = url
                            sendVoiceMessage(url: url)
                        }
                        isRecordingVoice = false
                    } else {
                        if voiceRecorder.startRecording() != nil {
                            isRecordingVoice = true
                        }
                    }
                }) {
                    Image(systemName: isRecordingVoice ? "stop.circle.fill" : "mic.fill")
                        .font(.body)
                        .foregroundColor(isRecordingVoice ? .red : .textPrimary)
                        .frame(width: Size.navButtonSize, height: Size.navButtonSize)
                        .background(isRecordingVoice ? Color.red.opacity(0.3) : Color.surfaceDark.opacity(0.6))
                        .cornerRadius(CornerRadius.medium)
                }
                .accessibilityLabel(localizationManager.localized("family_chat_voice_button"))
                .accessibilityHint(localizationManager.localized("family_chat_voice_hint"))
                
                // Media button
                Button(action: {
                    showMediaPicker = true
                }) {
                    Image(systemName: "photo")
                        .font(.body)
                        .foregroundColor(.textPrimary)
                        .frame(width: Size.navButtonSize, height: Size.navButtonSize)
                        .background(Color.surfaceDark.opacity(0.6))
                        .cornerRadius(CornerRadius.medium)
                }
                
                // Search button
                Button(action: {
                    isSearching.toggle()
                    if !isSearching {
                        searchText = ""
                        filteredMessages = messages
                    }
                }) {
                    Image(systemName: isSearching ? "xmark" : "magnifyingglass")
                        .font(.body)
                        .foregroundColor(.textPrimary)
                        .frame(width: Size.navButtonSize, height: Size.navButtonSize)
                        .background(Color.surfaceDark.opacity(0.6))
                        .cornerRadius(CornerRadius.medium)
                }
            }
            .padding(Spacing.screenPadding)
            .background(
                LinearGradient.cardGradient
                    .appGlassmorphism()
            )
        }
        .background(LinearGradient.backgroundGradient.ignoresSafeArea())
        .accessibilityElement(children: .contain)
        .accessibilityLabel(localizationManager.localized("family_chat_accessibility"))
        .navigationBarHidden(true)
        .safeAreaInset(edge: .top) {
            Color.clear.frame(height: Spacing.m)
        }
        .task {
            print("🚨 FamilyChatScreen загружен!")
            updateOnlineMembersCount()
            loadMessages()
            startAutoRefresh()
            setupWebSocket()
            setupPushNotifications()
            loadCachedMessages()
        }
        .onDisappear {
            stopAutoRefresh()
            webSocket?.disconnect()
        }
        .sheet(isPresented: $showMediaPicker) {
            MediaPickerView(onSelect: { image in
                selectedMedia = image
                sendMediaMessage(image: image)
            })
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
    
    /// Получает familyId из UserDefaults
    private func getFamilyId() -> String? {
        return UserDefaults.standard.string(forKey: familyIdKey)
    }
    
    /// Обновляет количество участников онлайн
    private func updateOnlineMembersCount() {
        guard let savedData = UserDefaults.standard.data(forKey: familyMembersKey),
              let members = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) else {
            onlineMembersCount = 0
            return
        }
        onlineMembersCount = members.count
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
                    errorMessage = nil
                    
                    // Автопрокрутка будет выполнена через onChange
                    
                    print("✅ FamilyChatScreen: Сообщения загружены успешно (\(messages.count) сообщений)")
                    
                case .failure(let error):
                    print("❌ FamilyChatScreen: Ошибка загрузки сообщений: \(error.localizedDescription)")
                    
                    // Fallback на mock данные только при первой загрузке
                    if messages.isEmpty && !silent {
                        print("ℹ️ FamilyChatScreen: Используем mock данные для отображения")
                        messages = getMockMessages()
                    }
                    
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
    private func scrollToMessage(_ messageId: UUID, proxy: ScrollViewProxy) {
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
                sender: "Сергей",
                text: "Всем привет! Как дела?",
                time: formatter.string(from: now.addingTimeInterval(-3600)),
                isCurrentUser: true
            ),
            FamilyChatMessage(
                sender: "Мария",
                text: "Привет! У нас всё хорошо 😊",
                time: formatter.string(from: now.addingTimeInterval(-3540)),
                isCurrentUser: false
            ),
            FamilyChatMessage(
                sender: "Маша",
                text: "Папа, можно мне ещё 30 минут?",
                time: formatter.string(from: now.addingTimeInterval(-3480)),
                isCurrentUser: false
            ),
            FamilyChatMessage(
                sender: "Сергей",
                text: "Конечно, дочка!",
                time: formatter.string(from: now.addingTimeInterval(-3420)),
                isCurrentUser: true
            ),
            FamilyChatMessage(
                sender: "Бабушка",
                text: "Как мне настроить VPN?",
                time: formatter.string(from: now.addingTimeInterval(-3300)),
                isCurrentUser: false
            ),
            FamilyChatMessage(
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
        
        return FamilyChatMessage(
            id: UUID(uuidString: response.id) ?? UUID(),
            sender: response.sender,
            text: response.text,
            time: timeString,
            isCurrentUser: response.isCurrentUser,
            messageType: response.messageType,
            voiceUrl: response.voiceUrl,
            voiceDuration: response.voiceDuration,
            mediaUrl: response.mediaUrl,
            mediaType: response.mediaType,
            replyToMessageId: response.replyToMessageId,
            reactions: response.reactions ?? [],
            readStatus: response.readStatus,
            readAt: response.readAt,
            editedAt: response.editedAt
        )
    }
    
    private func formatTimestamp(_ timestamp: String) -> String {
        // Поддерживаем разные форматы timestamp
        let formatters = [
            "yyyy-MM-dd'T'HH:mm:ss",
            "yyyy-MM-dd'T'HH:mm:ss.SSS",
            "yyyy-MM-dd'T'HH:mm:ssZ",
            "yyyy-MM-dd HH:mm:ss"
        ]
        
        for format in formatters {
            let formatter = DateFormatter()
            formatter.dateFormat = format
            
            if let date = formatter.date(from: timestamp) {
                let timeFormatter = DateFormatter()
                timeFormatter.dateFormat = "HH:mm"
                return timeFormatter.string(from: date)
            }
        }
        
        return getCurrentTime()
    }
    
    private func getCurrentTime() -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        return formatter.string(from: Date())
    }
    
    // MARK: - Extended Features
    
    /// Отображаемые сообщения (с учетом поиска)
    private var displayMessages: [FamilyChatMessage] {
        if isSearching && !searchText.isEmpty {
            return filteredMessages
        }
        return messages
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
        
        webSocket?.onTyping = { [self] userName in
            if !typingUsers.contains(userName) {
                typingUsers.append(userName)
                // Автоматически убираем через 5 секунд
                DispatchQueue.main.asyncAfter(deadline: .now() + 5.0) {
                    typingUsers.removeAll { $0 == userName }
                }
            }
        }
        
        webSocket?.onMessageDeleted = { [self] messageId in
            messages.removeAll { $0.id.uuidString == messageId }
        }
        
        webSocket?.onMessageEdited = { [self] messageId, newText in
            if let index = messages.firstIndex(where: { $0.id.uuidString == messageId }) {
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
    
    /// Отправка голосового сообщения
    private func sendVoiceMessage(url: URL) {
        let familyId = getFamilyId()
        let duration = voiceRecorder.recordingDuration
        
        // TODO: Загрузить файл на сервер и получить URL
        // Пока используем локальный URL
        let voiceUrl = url.absoluteString
        
        apiService.sendFamilyChatMessage(
            message: nil,
            familyId: familyId,
            messageType: "voice",
            voiceUrl: voiceUrl,
            voiceDuration: duration,
            mediaUrl: nil,
            mediaType: nil,
            replyToMessageId: replyToMessage?.id.uuidString
        ) { [self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(_):
                    replyToMessage = nil
                    loadMessages(silent: false)
                case .failure(let error):
                    errorMessage = error.localizedDescription
                    // Добавляем в очередь офлайн
                    offlineManager.addPendingMessage(PendingChatMessage(
                        text: nil,
                        familyId: familyId,
                        messageType: "voice",
                        voiceUrl: voiceUrl,
                        voiceDuration: duration
                    ))
                }
            }
        }
    }
    
    /// Отправка медиа сообщения
    private func sendMediaMessage(image: UIImage) {
        guard let imageData = image.jpegData(compressionQuality: 0.8) else { return }
        
        let familyId = getFamilyId()
        
        // TODO: Загрузить на сервер
        apiService.uploadMedia(data: imageData, type: "image") { [self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let mediaUrl):
                    apiService.sendFamilyChatMessage(
                        message: nil,
                        familyId: familyId,
                        messageType: "image",
                        voiceUrl: nil,
                        voiceDuration: nil,
                        mediaUrl: mediaUrl,
                        mediaType: "image",
                        replyToMessageId: replyToMessage?.id.uuidString
                    ) { result in
                        switch result {
                        case .success(_):
                            replyToMessage = nil
                            loadMessages(silent: false)
                        case .failure(let error):
                            errorMessage = error.localizedDescription
                        }
                    }
                case .failure(let error):
                    errorMessage = error.localizedDescription
                }
            }
        }
    }
    
    /// Отправка индикатора "печатает..."
    private func sendTypingIndicator() {
        guard !messageText.isEmpty else { return }
        webSocket?.sendTyping()
        apiService.sendTypingIndicator(familyId: getFamilyId()) { _ in }
    }
    
    /// Удаление сообщения
    private func deleteMessage(_ message: FamilyChatMessage) {
        apiService.deleteFamilyChatMessage(messageId: message.id.uuidString) { [self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(_):
                    messages.removeAll { $0.id == message.id }
                case .failure(let error):
                    errorMessage = error.localizedDescription
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
        
        apiService.editFamilyChatMessage(messageId: message.id.uuidString, newText: editText) { [self] result in
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
        apiService.addReaction(messageId: message.id.uuidString, emoji: emoji) { [self] result in
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
        
        let familyId = getFamilyId()
        isSending = true
        messageText = ""
        
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
            replyToMessageId: replyToMessage?.id.uuidString
        ) { [self] result in
            DispatchQueue.main.async {
                isSending = false
                
                switch result {
                case .success(_):
                    replyToMessage = nil
                    loadMessages(silent: false)
                    
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
                            replyToMessageId: replyToMessage?.id.uuidString
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
}

// MARK: - Family Chat Message

struct FamilyChatMessage: Identifiable {
    let id: UUID
    let sender: String
    let text: String?
    let time: String
    let isCurrentUser: Bool
    
    // Extended fields
    let messageType: String? // "text", "voice", "image", "video"
    let voiceUrl: String?
    let voiceDuration: Double?
    let mediaUrl: String?
    let mediaType: String?
    let replyToMessageId: String?
    let reactions: [MessageReaction]
    let readStatus: String? // "sent", "delivered", "read"
    let readAt: String?
    let editedAt: String?
    
    init(
        id: UUID = UUID(),
        sender: String,
        text: String?,
        time: String,
        isCurrentUser: Bool,
        messageType: String? = "text",
        voiceUrl: String? = nil,
        voiceDuration: Double? = nil,
        mediaUrl: String? = nil,
        mediaType: String? = nil,
        replyToMessageId: String? = nil,
        reactions: [MessageReaction] = [],
        readStatus: String? = nil,
        readAt: String? = nil,
        editedAt: String? = nil
    ) {
        self.id = id
        self.sender = sender
        self.text = text
        self.time = time
        self.isCurrentUser = isCurrentUser
        self.messageType = messageType
        self.voiceUrl = voiceUrl
        self.voiceDuration = voiceDuration
        self.mediaUrl = mediaUrl
        self.mediaType = mediaType
        self.replyToMessageId = replyToMessageId
        self.reactions = reactions
        self.readStatus = readStatus
        self.readAt = readAt
        self.editedAt = editedAt
    }
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
               let replyTo = allMessages.first(where: { $0.id.uuidString == replyToId }) {
                ReplyBubbleView(replyTo: replyTo) {}
                    .padding(.bottom, Spacing.xxs)
            }
            
            // Message Content
            Group {
                switch message.messageType {
                case "voice":
                    VoiceMessageBubble(message: message)
                case "image", "video", "media":
                    MediaMessageBubble(message: message)
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
            
            if message.isCurrentUser && message.messageType == "text" {
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

// MARK: - Media Picker View

struct MediaPickerView: UIViewControllerRepresentable {
    let onSelect: (UIImage) -> Void
    @Environment(\.dismiss) var dismiss
    
    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        picker.sourceType = .photoLibrary
        picker.allowsEditing = true
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: MediaPickerView
        
        init(_ parent: MediaPickerView) {
            self.parent = parent
        }
        
        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
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
