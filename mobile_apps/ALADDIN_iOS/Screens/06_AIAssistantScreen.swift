import SwiftUI

/// 🤖 AI Assistant Screen
/// Экран AI помощника - чат с искусственным интеллектом
/// Источник дизайна: /mobile/wireframes/08_ai_assistant.html
struct AIAssistantScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @State private var messageText: String = ""
    @State private var messages: [ChatMessage] = [
        ChatMessage(text: "Здравствуйте! Я AI помощник ALADDIN. Чем могу помочь?", isUser: false, time: "14:30"),
        ChatMessage(text: "Покажи статистику защиты", isUser: true, time: "14:31"),
        ChatMessage(text: "За эту неделю заблокировано 47 угроз:\n• Вредоносные сайты: 23\n• Фишинг: 12\n• Трекеры: 8\n• Вирусы: 4\n\nВаша семья под надёжной защитой! 🛡️", isUser: false, time: "14:31")
    ]
    
    struct ChatMessage: Identifiable {
        let id = UUID()
        let text: String
        let isUser: Bool
        let time: String
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                ALADDINNavigationBar(
                    title: "AI ПОМОЩНИК",
                    subtitle: "Всегда готов помочь",
                    leftButton: .init(icon: "chevron.left") {
                        dismiss()
                    },
                    rightButtons: [
                        .init(icon: "mic.fill") {
                            print("Голосовой ввод")
                        }
                    ]
                )
                
                // Чат
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.m) {
                        ForEach(messages) { message in
                            chatBubble(message: message)
                        }
                        
                        // Spacer для клавиатуры
                        Spacer()
                            .frame(height: Spacing.xl)
                    }
                    .padding(.top, Spacing.m)
                    .padding(.horizontal, Spacing.screenPadding)
                }
                
                // Поле ввода
                messageInputBar
            }
        }
        .navigationBarHidden(true)
    }
    
    // MARK: - Chat Bubble
    
    private func chatBubble(message: ChatMessage) -> some View {
        HStack {
            if message.isUser {
                Spacer()
            }
            
            VStack(alignment: message.isUser ? .trailing : .leading, spacing: Spacing.xs) {
                // Текст сообщения
                Text(message.text)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                    .padding(Spacing.m)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.large)
                            .fill(
                                message.isUser ?
                                LinearGradient(
                                    colors: [Color.primaryBlue, Color.secondaryBlue],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                ) :
                                LinearGradient(
                                    colors: [Color.backgroundMedium, Color.backgroundMedium],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                            )
                    )
                    .cornerRadius(CornerRadius.large)
                
                // Время
                Text(message.time)
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
                    .padding(.horizontal, Spacing.s)
            }
            .frame(maxWidth: 280, alignment: message.isUser ? .trailing : .leading)
            
            if !message.isUser {
                Spacer()
            }
        }
    }
    
    // MARK: - Message Input Bar
    
    private var messageInputBar: some View {
        HStack(spacing: Spacing.s) {
            // Текстовое поле
            TextField("Спросите AI помощника...", text: $messageText)
                .font(.body)
                .foregroundColor(.textPrimary)
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.full)
                        .fill(Color.backgroundMedium.opacity(0.5))
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
                                Color.backgroundMedium :
                                LinearGradient(
                                    colors: [Color.primaryBlue, Color.secondaryBlue],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                            )
                    )
            }
            .disabled(messageText.isEmpty)
        }
        .padding(Spacing.m)
        .background(
            Color.backgroundDark.opacity(0.95)
        )
    }
    
    private func sendMessage() {
        guard !messageText.isEmpty else { return }
        
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
        
        // Добавляем сообщение пользователя
        messages.append(
            ChatMessage(text: messageText, isUser: true, time: currentTime())
        )
        
        messageText = ""
        
        // Имитация ответа AI (через 1 секунду)
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            messages.append(
                ChatMessage(
                    text: "Получил ваш запрос! Обрабатываю... 🤖",
                    isUser: false,
                    time: currentTime()
                )
            )
        }
    }
    
    private func currentTime() -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        return formatter.string(from: Date())
    }
}

// MARK: - Preview

#Preview {
    AIAssistantScreen()
}



