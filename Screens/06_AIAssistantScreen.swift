import SwiftUI
import Speech
import AVFoundation

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
    @State private var isRecording = false
    @State private var showVoicePermissionAlert = false
    @State private var showFeedbackSheet = false

    // Сервисы
    @StateObject private var apiService = APIService.shared
    @StateObject private var speechManager = SpeechManager()

    // Ключ для сохранения истории сообщений
    private let messagesKey = "ai_assistant_messages_list"
    private let hasReceivedWelcomeKey = "ai_assistant_welcome_sent"
    
    struct ChatMessage: Identifiable, Codable {
        let id: UUID
        let text: String
        let isUser: Bool
        let time: String
        
        init(id: UUID = UUID(), text: String, isUser: Bool, time: String) {
            self.id = id
            self.text = text
            self.isUser = isUser
            self.time = time
        }
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient(
                colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
                .ignoresSafeArea()
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
                    }
                    
                    Spacer()
                }
                .padding(.horizontal, 20)
                .padding(.top, 16)
                .padding(.bottom, 12)
                
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
                                
                                // Приветственное сообщение от AI (только для новых пользователей)
                                if !UserDefaults.standard.bool(forKey: hasReceivedWelcomeKey) {
                                    chatBubble(message: ChatMessage(
                                        text: localizationManager.localized("ai_assistant_welcome"),
                                        isUser: false,
                                        time: currentTime()
                                    ))
                                    .onAppear {
                                        // Добавляем приветствие в историю
                                        messages.append(ChatMessage(
                                            text: localizationManager.localized("ai_assistant_welcome"),
                                            isUser: false,
                                            time: currentTime()
                                        ))
                                        UserDefaults.standard.set(true, forKey: hasReceivedWelcomeKey)
                                        saveMessages()
                                    }
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
                            TypingIndicatorView(typingUsers: ["AI Assistant"])
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
        .onAppear {
            logger.business("🤖 AI Assistant: Screen appeared, loading messages")
            loadMessages()
            setupNotifications()
            // Если сообщений нет и приветствие еще не отправлено - показываем приветствие
            if messages.isEmpty && !UserDefaults.standard.bool(forKey: hasReceivedWelcomeKey) {
                logger.business("🤖 AI Assistant: Showing welcome message for new user")
            }
        }
        .onDisappear {
            removeNotifications()
        }
        .navigationBarHidden(true)
        .id("ai_assistant_lang_\(localizationManager.currentLanguage.rawValue)")
        .sheet(isPresented: $showFeedbackSheet) {
            AIFeedbackSheet(isPresented: $showFeedbackSheet, apiService: apiService)
        }
    }
    
    // MARK: - Chat Bubble
    
    private func chatBubble(message: ChatMessage) -> some View {
        HStack {
            if message.isUser {
                Spacer()
            }
            
            VStack(alignment: message.isUser ? .trailing : .leading, spacing: 4) {
                // Текст сообщения
                Text(message.text)
                    .font(.body)
                    .foregroundColor(.primary)
                    .padding(12)
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(
                                message.isUser ?
                                LinearGradient(
                                    colors: [Color.blue, Color.blue.opacity(0.8)],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                ) :
                                LinearGradient(
                                    colors: [Color.gray, Color.gray],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                            )
                    )
                    .cornerRadius(12)
                
                // Время
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
    
    // MARK: - Message Input Bar
    
    private var messageInputBar: some View {
        HStack(spacing: 8) {
            // Кнопка голосового ввода
            Button(action: toggleVoiceRecording) {
                Image(systemName: isRecording ? "mic.fill" : "mic")
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundColor(isRecording ? .red : .blue)
                    .frame(width: 44, height: 44)
                    .background(
                        Circle()
                            .fill(isRecording ? Color.red.opacity(0.2) : Color.blue.opacity(0.2))
                    )
            }

            // Текстовое поле
            TextField(localizationManager.localized("ai_assistant_placeholder"), text: $messageText)
                .font(.body)
                .foregroundColor(.primary)
                .padding(12)
                .background(
                    RoundedRectangle(cornerRadius: 16)
                        .fill(Color.gray.opacity(0.3))
                )

            // Кнопка отправки
            Button(action: sendMessage) {
                Image(systemName: messageText.isEmpty ? "paperplane" : "paperplane.fill")
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(width: 48, height: 48)
                    .background(
                        Circle()
                            .fill(
                                messageText.isEmpty ?
                                LinearGradient(colors: [Color.gray, Color.gray], startPoint: .top, endPoint: .bottom) :
                                LinearGradient(
                                    colors: [Color.blue, Color.blue.opacity(0.8)],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                            )
                    )
            }
            .disabled(messageText.isEmpty)

            // Кнопка обратной связи
            Button(action: { showFeedbackSheet = true }) {
                Image(systemName: "star")
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundColor(.orange)
                    .frame(width: 44, height: 44)
                    .background(
                        Circle()
                            .fill(Color.orange.opacity(0.2))
                    )
            }
        }
        .padding(12)
        .background(
            Color.black.opacity(0.95)
        )
    }
    
    private func sendMessage() {
        guard !messageText.isEmpty else {
            logger.warn("AI Assistant: Attempted to send empty message")
            return
        }

        logger.business("🤖 AI Assistant: Sending message (length: \(messageText.count) chars)")

        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()

        // Добавляем сообщение пользователя
        messages.append(
            ChatMessage(text: messageText, isUser: true, time: currentTime())
        )

        let userMessage = messageText
        let context = determineMessageContext(userMessage)

        logger.business("🤖 AI Assistant: Message context determined: \(context)")

        messageText = ""

        // Сохраняем сообщение
        saveMessages()

        // Показываем индикатор загрузки
        isLoading = true

        // Если это feedback сообщение - отправляем как обратную связь
        if context == "feedback" {
            logger.business("🤖 AI Assistant: Detected feedback message, sending to feedback system")
            sendFeedbackMessage(userMessage)
        } else {
            // Обычное сообщение AI
            logger.business("🤖 AI Assistant: Sending regular message to AI service")
            sendRegularMessage(userMessage, context: context)
        }
    }

    private func sendFeedbackMessage(_ message: String) {
        logger.business("🤖 AI Assistant: Processing feedback message")

        // Определяем тип feedback для персонализированного ответа
        let feedbackType = determineFeedbackType(message)
        logger.business("🤖 AI Assistant: Feedback type determined: \(feedbackType)")

        // Отправляем как обратную связь
        logger.network("🤖 AI Assistant: Sending feedback to server")
        apiService.sendAIFeedback(
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
                    errorMessage = "Не удалось отправить отзыв: \(error.localizedDescription)"

                    let errorResponse = ChatMessage(
                        text: "Извините, не удалось отправить ваш отзыв. Попробуйте позже через раздел обратной связи.",
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

    private func sendRegularMessage(_ message: String, context: String) {
        logger.business("🤖 AI Assistant: Sending message to AI service (context: \(context))")

        // Hybrid FAQ+AI: сначала пытаемся закрыть вопрос готовым FAQ-ответом.
        if let faqMatch = UnifiedFAQCatalog.bestMatch(for: message, localize: localizationManager.localized) {
            logger.business("📚 AI Assistant: FAQ match found id=\(faqMatch.id)")
            isLoading = false
            let faqResponse = ChatMessage(
                text: "\(faqMatch.answer)\n\n📚 Источник: FAQ (\(faqMatch.id))",
                isUser: false,
                time: currentTime()
            )
            messages.append(faqResponse)
            saveMessages()
            return
        }

        // Отправляем обычное сообщение AI
        logger.network("🤖 AI Assistant: Making API call to AI service")
        apiService.sendMessageToAI(message: message, context: context) { [self] result in
            DispatchQueue.main.async {
                isLoading = false

                switch result {
                case .success(let response):
                    logger.business("✅ AI Assistant: Received AI response (length: \(response.response.count) chars)")

                    // Проверяем, является ли ответ стандартным mock ответом сервера
                    let finalResponse = response.response

                    // ✅ ПРОДАКШН: Всегда используем серверный AI, без fallback на локальный
                    logger.business("🤖 AI Assistant: Using real server AI response")

                    let aiResponse = ChatMessage(
                        text: finalResponse,
                        isUser: false,
                        time: currentTime()
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
                    errorMessage = "Не удалось получить ответ от AI: \(error.localizedDescription)"

                    let errorResponse = ChatMessage(
                        text: "Извините, произошла ошибка. Попробуйте позже.",
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

    private func loadMessages() {
        guard let savedData = UserDefaults.standard.data(forKey: messagesKey),
              let decoded = try? JSONDecoder().decode([ChatMessage].self, from: savedData) else {
            logger.business("🤖 AI Assistant: No saved messages found, starting fresh")
            messages = []
            return
        }
        messages = decoded
        logger.business("✅ AI Assistant: Loaded \(messages.count) messages from storage")
    }
    
    private func saveMessages() {
        guard let encoded = try? JSONEncoder().encode(messages) else {
            logger.error("❌ AI Assistant: Failed to encode messages")
            return
        }
        UserDefaults.standard.set(encoded, forKey: messagesKey)
        logger.business("✅ AI Assistant: Saved \(messages.count) messages to storage")

        // Уведомляем другие экраны об изменении (если нужно синхронизировать)
        NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
    }
    
    // ✅ ИСПРАВЛЕНИЕ BUILD 90: Статический форматтер для предотвращения рекурсии
    private static let timeFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        formatter.locale = Locale(identifier: "ru_RU") // Статический locale
        return formatter
    }()
    
    private func currentTime() -> String {
        // ✅ Используем статический formatter вместо создания нового каждый раз
        return Self.timeFormatter.string(from: Date())
    }

    private func handleQuickAction(_ action: QuickActionType) {
        logger.business("🤖 AI Assistant: Quick action selected: \(action)")

        let message: String
        switch action {
        case .protectionStatus:
            message = "Какой статус моей защиты ALADDIN?"
        case .analyzeThreats:
            message = "Проанализируй возможные угрозы для моей семьи"
        case .securityTips:
            message = "Дай советы по улучшению безопасности"
        case .help:
            message = "Помоги настроить приложение"
        case .familySetup:
            message = "Как настроить семейную защиту?"
        case .reportIncident:
            message = "Я заметил подозрительную активность"
        }

        messageText = message
        logger.business("🤖 AI Assistant: Quick action message set: '\(message)'")
        sendMessage()
    }

    private func setupNotifications() {
        NotificationCenter.default.addObserver(forName: NSNotification.Name("SpeechPermissionDenied"), object: nil, queue: .main) { _ in
            showVoicePermissionAlert = true
        }
    }

    private func removeNotifications() {
        NotificationCenter.default.removeObserver(self, name: NSNotification.Name("SpeechPermissionDenied"), object: nil)
    }

    private func toggleVoiceRecording() {
        if speechManager.isRecording {
            logger.business("🎤 AI Assistant: Stopping voice recording")
            speechManager.stopRecording()
        } else {
            logger.business("🎤 AI Assistant: Starting voice recording")
            speechManager.startRecording { recognizedText in
                if let text = recognizedText, !text.isEmpty {
                    logger.business("🎤 AI Assistant: Voice recognized: '\(text.prefix(50))...' (length: \(text.count))")
                    messageText = text
                    // Автоматически отправляем сообщение
                    sendMessage()
                } else {
                    logger.warn("🎤 AI Assistant: Voice recognition returned empty text")
                }
            }
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
    let onActionSelected: (QuickActionType) -> Void

    private let actions = [
        QuickAction(type: .protectionStatus, icon: "🛡️", title: "Статус защиты"),
        QuickAction(type: .analyzeThreats, icon: "🔍", title: "Анализ угроз"),
        QuickAction(type: .securityTips, icon: "💡", title: "Советы"),
        QuickAction(type: .help, icon: "❓", title: "Помощь"),
        QuickAction(type: .familySetup, icon: "👨‍👩‍👧‍👦", title: "Семья"),
        QuickAction(type: .reportIncident, icon: "🚨", title: "Инцидент")
    ]

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

    private func openSettings() {
        if let url = URL(string: UIApplication.openSettingsURLString) {
            UIApplication.shared.open(url)
        }
    }
}

// MARK: - Speech Manager

class SpeechManager: ObservableObject {
    @Published var isRecording = false
    @Published var recognizedText: String?

    private let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "ru-RU"))
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    private let audioEngine = AVAudioEngine()

    // Master Logger for speech recognition logging
    private let logger = MasterLogger.shared

    func startRecording(completion: @escaping (String?) -> Void) {
        logger.business("🎤 SpeechManager: Starting speech recognition process")

        // Проверяем разрешение
        SFSpeechRecognizer.requestAuthorization { status in
            DispatchQueue.main.async {
                switch status {
                case .authorized:
                    self.startRecordingInternal(completion: completion)
                case .denied, .restricted:
                    self.showPermissionAlert()
                case .notDetermined:
                    // Разрешение еще не запрошено
                    break
                @unknown default:
                    break
                }
            }
        }

        // Запрашиваем разрешение на микрофон
        AVAudioSession.sharedInstance().requestRecordPermission { granted in
            if !granted {
                DispatchQueue.main.async {
                    self.showPermissionAlert()
                }
            }
        }
    }

    private func startRecordingInternal(completion: @escaping (String?) -> Void) {
        do {
            // ✅ ИСПРАВЛЕНИЕ: Меняем режим с .measurement на .default для совместимости
            let audioSession = AVAudioSession.sharedInstance()
            try audioSession.setCategory(.record, mode: .default, options: [])
            try audioSession.setActive(true, options: .notifyOthersOnDeactivation)

            logger.business("🎤 SpeechManager: Audio session configured successfully")

            // Создаем запрос распознавания
            recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
            guard let recognitionRequest = recognitionRequest else { return }

            recognitionRequest.shouldReportPartialResults = true

            // Создаем задачу распознавания
            recognitionTask = speechRecognizer?.recognitionTask(with: recognitionRequest) { result, error in
                if let result = result {
                    let text = result.bestTranscription.formattedString
                    DispatchQueue.main.async {
                        self.recognizedText = text
                    }
                }

                if error != nil || result?.isFinal == true {
                    self.stopRecording()
                    DispatchQueue.main.async {
                        completion(result?.bestTranscription.formattedString)
                    }
                }
            }

            // Настраиваем входной узел
            let inputNode = audioEngine.inputNode
            let recordingFormat = inputNode.outputFormat(forBus: 0)

            logger.business("🎤 SpeechManager: Installing audio tap")

            // ✅ Устанавливаем audio tap
            inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
                self.recognitionRequest?.append(buffer)
            }
            logger.business("🎤 SpeechManager: Audio tap installed successfully")

            logger.business("🎤 SpeechManager: Starting audio engine")

            // Запускаем запись
            audioEngine.prepare()
            try audioEngine.start()

            isRecording = true
            print("🎤 SpeechManager: Запись запущена успешно")

        } catch {
            print("🚨 SpeechManager: КРИТИЧЕСКАЯ ОШИБКА запуска записи: \(error.localizedDescription)")
            print("🚨 SpeechManager: Детали ошибки: \(error)")
            completion(nil)
        }
    }

    func stopRecording() {
        logger.business("🎤 SpeechManager: Stopping recording")

        audioEngine.stop()
        recognitionRequest?.endAudio()
        recognitionTask?.cancel()
        recognitionTask = nil
        recognitionRequest = nil
        isRecording = false

        logger.business("🎤 SpeechManager: Recording stopped")

        // Восстанавливаем аудио сессию
        do {
            try AVAudioSession.sharedInstance().setActive(false)
        } catch {
            logger.error("🎤 SpeechManager: Failed to stop audio session", error: error)
        }
    }

    private func showPermissionAlert() {
        // Показываем алерт через NotificationCenter
        NotificationCenter.default.post(name: NSNotification.Name("SpeechPermissionDenied"), object: nil)
    }
}

// MARK: - AI Feedback Sheet

struct AIFeedbackSheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var isPresented: Bool
    @State private var rating: Int = 5
    @State private var comment: String = ""
    @State private var isSubmitting = false
    @State private var showSuccess = false

    let apiService: APIService

    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text(localizationManager.localized("ai_assistant_feedback_title"))
                    .font(.title2)
                    .fontWeight(.bold)
                    .multilineTextAlignment(.center)

                Text(localizationManager.localized("ai_assistant_feedback_description"))
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)

                // Рейтинг
                VStack(spacing: 12) {
                    Text(localizationManager.localized("ai_assistant_feedback_rating"))
                        .font(.headline)

                    HStack(spacing: 8) {
                        ForEach(1...5, id: \.self) { star in
                            Image(systemName: star <= rating ? "star.fill" : "star")
                                .font(.system(size: 30))
                                .foregroundColor(star <= rating ? .yellow : .gray)
                                .onTapGesture {
                                    rating = star
                                }
                        }
                    }
                }

                // Комментарий
                VStack(alignment: .leading, spacing: 8) {
                    Text(localizationManager.localized("ai_assistant_feedback_comment"))
                        .font(.headline)

                    TextEditor(text: $comment)
                        .frame(height: 100)
                        .padding(8)
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(8)
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                        )
                }

                Spacer()

                // Кнопки
                HStack(spacing: 12) {
                    Button("Отмена") {
                        isPresented = false
                    }
                    .buttonStyle(.bordered)
                    .tint(.gray)

                    Button(action: submitFeedback) {
                        if isSubmitting {
                            ProgressView()
                                .tint(.white)
                        } else {
                            Text(localizationManager.localized("ai_assistant_feedback_submit"))
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(isSubmitting)
                }
            }
            .padding()
            .navigationBarHidden(true)
            .alert(localizationManager.localized("ai_assistant_feedback_thanks_title"), isPresented: $showSuccess) {
                Button(localizationManager.localized("common_ok")) {
                    isPresented = false
                }
            } message: {
                Text(localizationManager.localized("ai_assistant_feedback_success"))
            }
        }
    }

    private func submitFeedback() {
        isSubmitting = true
        let queryText = comment.isEmpty ? nil : comment

        apiService.sendAIFeedback(
            rating: rating,
            comment: comment.isEmpty ? nil : comment,
            messageId: nil,
            queryText: queryText,
            resolvedBy: "feedback_sheet",
            faqId: nil,
            confidence: nil,
            sessionId: currentFeedbackSessionId()
        ) { result in
            DispatchQueue.main.async {
                isSubmitting = false

                switch result {
                case .success:
                    showSuccess = true
                case .failure(let error):
                    print("Ошибка отправки обратной связи: \(error)")
                    // Показываем ошибку пользователю
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
}

// MARK: - Preview

#if DEBUG
struct AIAssistantScreen_Previews: PreviewProvider {
    static var previews: some View {
        AIAssistantScreen()
    }
}
#endif




