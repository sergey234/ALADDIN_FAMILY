import SwiftUI
import Combine

// Master Logger for AI assistant logging
private let logger = MasterLogger.shared

/// 🤖 AI Assistant View Model
/// Логика для AI чата
class AIAssistantViewModel: ObservableObject {
    
    @Published var messages: [ChatMessage] = []
    @Published var currentMessage: String = ""
    @Published var isAITyping: Bool = false
    
    private let apiService = APIService.shared
    
    struct ChatMessage: Identifiable {
        let id = UUID()
        let text: String
        let isUser: Bool
        let timestamp: Date
        
        var timeString: String {
            let formatter = DateFormatter()
            formatter.dateFormat = "HH:mm"
            return formatter.string(from: timestamp)
        }
    }
    
    init() {
        logger.business("Initializing AI Assistant ViewModel")
        loadInitialMessages()
    }
    
    func loadInitialMessages() {
        messages = [
            ChatMessage(text: "Здравствуйте! Я AI помощник ALADDIN. Чем могу помочь?", isUser: false, timestamp: Date().addingTimeInterval(-3600)),
            ChatMessage(text: "Покажи статистику защиты", isUser: true, timestamp: Date().addingTimeInterval(-3540)),
            ChatMessage(text: "За эту неделю заблокировано 47 угроз:\n• Вредоносные сайты: 23\n• Фишинг: 12\n• Трекеры: 8\n• Вирусы: 4\n\nВаша семья под надёжной защитой! 🛡️", isUser: false, timestamp: Date().addingTimeInterval(-3530))
        ]
    }
    
    func sendMessage() {
        logger.business("User sent message to AI assistant: \(currentMessage.count) characters")
        guard !currentMessage.isEmpty else { return }

        // ✅ ЗАДАЧА 67: Санитизация пользовательского ввода перед отправкой
        do {
            let sanitizedMessage = try InputSanitizer.shared.sanitizeMessage(currentMessage)

            let userMessage = ChatMessage(text: sanitizedMessage, isUser: true, timestamp: Date())
            messages.append(userMessage)
            currentMessage = ""

            // ✅ ЗАДАЧА 67: Используем санитизированное сообщение для отправки
            sendSanitizedMessage(sanitizedMessage)

        } catch let error as InputSanitizer.SanitizationError {
            // Показываем ошибку валидации пользователю
            let errorMessage = ChatMessage(
                text: "Ошибка: \(error.localizedDescription)",
                isUser: false,
                timestamp: Date()
            )
            messages.append(errorMessage)

            #if DEBUG
            print("❌ AIAssistantViewModel: Ошибка санитизации: \(error.localizedDescription)")
            #endif

        } catch {
            let errorMessage = ChatMessage(
                text: "Произошла неизвестная ошибка при обработке сообщения.",
                isUser: false,
                timestamp: Date()
            )
            messages.append(errorMessage)
        }
    }

    // ✅ ЗАДАЧА 67: Приватный метод для отправки санитизированного сообщения
    private func sendSanitizedMessage(_ sanitizedMessage: String) {

        // ✅ ИСПРАВЛЕНО: Используем реальный API вместо симуляции
        isAITyping = true

        // 🔍 ЛОГИРОВАНИЕ: Проверяем состояние токена перед отправкой
        print("🤖 AIAssistantViewModel: About to call sendMessageToAI")
        print("🤖 AIAssistantViewModel: AppConfig.authToken is nil = \(AppConfig.authToken == nil)")
        if let token = AppConfig.authToken {
            print("🤖 AIAssistantViewModel: Token exists, length = \(token.count)")
        } else {
            print("🤖 AIAssistantViewModel: No token available - this will cause 401 error")
        }

        apiService.sendMessageToAI(message: sanitizedMessage, context: "general") { [weak self] result in
            DispatchQueue.main.async {
                self?.isAITyping = false
                
                switch result {
                case .success(let response):
                    // ChatMessageResponse содержит поле "response" с текстом ответа AI
                    let aiMessage = ChatMessage(
                        text: response.response,
                        isUser: false,
                        timestamp: response.timestampDate ?? Date()  // ✅ ИСПРАВЛЕНО: Используем timestampDate вместо timestamp
                    )
                    self?.messages.append(aiMessage)
                case .failure(let error):
                    // При ошибке показываем сообщение об ошибке
                    let errorMessage = ChatMessage(
                        text: "Извините, произошла ошибка. Попробуйте позже.",
                        isUser: false,
                        timestamp: Date()
                    )
                    self?.messages.append(errorMessage)
                }
            }
        }
    }
}



