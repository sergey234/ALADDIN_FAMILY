import SwiftUI
import Combine

// Master Logger for AI assistant logging
private let logger = MasterLogger.shared

/// 🤖 AI Assistant View Model
/// Логика для AI чата
@MainActor
class AIAssistantViewModel: ObservableObject {
    
    @Published var messages: [ChatMessage] = []
    @Published var currentMessage: String = ""
    @Published var isAITyping: Bool = false
    @Published var isStreaming: Bool = false
    @Published var isResumingStream: Bool = false     // Индикатор восстановления после reconnect
    
    private let apiService: APIService
    private let streamingService = AIStreamingService.shared
    
    struct ChatMessage: Identifiable {
        let id = UUID()
        var text: String
        let isUser: Bool
        let timestamp: Date
        
        var timeString: String {
            let formatter = DateFormatter()
            formatter.dateFormat = "HH:mm"
            formatter.locale = LocalizationManager.shared.locale
            return formatter.string(from: timestamp)
        }
    }
    
    init(apiService: APIService? = nil) {
        self.apiService = apiService ?? APIService.shared
        logger.business("Initializing AI Assistant ViewModel")
        loadInitialMessages()
    }
    
    func loadInitialMessages() {
        let loc = LocalizationManager.shared
        messages = [
            ChatMessage(text: loc.localized("ai_chat_seed_greeting"), isUser: false, timestamp: Date().addingTimeInterval(-3600)),
            ChatMessage(text: loc.localized("ai_chat_seed_user"), isUser: true, timestamp: Date().addingTimeInterval(-3540)),
            ChatMessage(text: loc.localized("ai_chat_seed_assistant"), isUser: false, timestamp: Date().addingTimeInterval(-3530))
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
            let errorMessage = ChatMessage(
                text: LocalizationManager.shared.localized("ai_assistant_error_sanitization", error.localizedDescription),
                isUser: false,
                timestamp: Date()
            )
            messages.append(errorMessage)

            #if DEBUG
            print("❌ AIAssistantViewModel: Ошибка санитизации: \(error.localizedDescription)")
            #endif

        } catch {
            let errorMessage = ChatMessage(
                text: LocalizationManager.shared.localized("ai_assistant_error_unknown_processing"),
                isUser: false,
                timestamp: Date()
            )
            messages.append(errorMessage)
        }
    }

    // ✅ ЗАДАЧА 67: Приватный метод для отправки санитизированного сообщения
    private func sendSanitizedMessage(_ sanitizedMessage: String) {
        // ✅ НОВАЯ РЕАЛИЗАЦИЯ: Используем токен-стриминг (Phase 2026)
        isAITyping = true
        isStreaming = true

        logger.business("🤖 AIAssistantViewModel: Starting AI token streaming for message: \(sanitizedMessage.prefix(50))...")

        // Добавляем временное сообщение AI, которое будет обновляться в реальном времени
        let streamingMessage = ChatMessage(
            text: "",
            isUser: false,
            timestamp: Date()
        )
        messages.append(streamingMessage)
        let messageIndex = messages.count - 1

        Task {
            await streamingService.streamMessage(
                message: sanitizedMessage,
                context: "general"
            ) { token in
                // Каждое новое слово/токен
                Task { @MainActor in
                    if messageIndex < self.messages.count {
                        var updatedMessage = self.messages[messageIndex]
                        updatedMessage.text += token
                        self.messages[messageIndex] = updatedMessage
                    }
                }
            } onComplete: { fullResponse in
                Task { @MainActor in
                    self.isAITyping = false
                    self.isStreaming = false
                    logger.business("✅ AI streaming completed. Full response length: \(fullResponse.count)")
                }
            } onError: { error in
                Task { @MainActor in
                    self.isAITyping = false
                    self.isStreaming = false
                    
                    let errorMessage = ChatMessage(
                        text: LocalizationManager.shared.localized("ai_assistant_error_stream", error.localizedDescription),
                        isUser: false,
                        timestamp: Date()
                    )
                    if messageIndex < self.messages.count {
                        self.messages[messageIndex] = errorMessage
                    } else {
                        self.messages.append(errorMessage)
                    }
                    logger.error("❌ AI streaming error: \(error.localizedDescription)")
                }
            }
        }
    }
}



