import SwiftUI
import Combine

/// 🤖 AI Assistant View Model
/// Логика для AI чата
class AIAssistantViewModel: ObservableObject {
    
    @Published var messages: [ChatMessage] = []
    @Published var currentMessage: String = ""
    @Published var isAITyping: Bool = false
    
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
        guard !currentMessage.isEmpty else { return }
        
        let userMessage = ChatMessage(text: currentMessage, isUser: true, timestamp: Date())
        messages.append(userMessage)
        currentMessage = ""
        
        // Имитация ответа AI
        isAITyping = true
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { [weak self] in
            let aiResponse = ChatMessage(text: "Понял ваш запрос! Обрабатываю... 🤖", isUser: false, timestamp: Date())
            self?.messages.append(aiResponse)
            self?.isAITyping = false
        }
    }
}



