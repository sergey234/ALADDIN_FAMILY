import SwiftUI

/// 🤖 AI Assistant Screen
/// Экран AI помощника - чат с искусственным интеллектом
/// Источник дизайна: /mobile/wireframes/08_ai_assistant.html
struct AIAssistantScreen: View {
    
    // MARK: - State
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @Environment(\.dismiss) private var dismiss
    @State private var messageText: String = ""
    @State private var messages: [ChatMessage] = []
    
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
                .accessibilityLabel("Фон экрана AI помощника")
            
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
                    .accessibilityLabel("Назад")
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text("AI Помощник")
                            .font(.system(size: 24, weight: .bold))
                            .foregroundColor(.white)
                        Text("Чем могу помочь?")
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
                                    title: "Начните общение с AI помощником",
                                    description: "Задайте любой вопрос о безопасности вашей семьи",
                                    actionTitle: nil,
                                    action: nil
                                )
                                
                                // Приветственное сообщение от AI (только для новых пользователей)
                                if !UserDefaults.standard.bool(forKey: hasReceivedWelcomeKey) {
                                    chatBubble(message: ChatMessage(
                                        text: "Здравствуйте! Я AI помощник ALADDIN. Чем могу помочь?",
                                        isUser: false,
                                        time: currentTime()
                                    ))
                                    .onAppear {
                                        // Добавляем приветствие в историю
                                        messages.append(ChatMessage(
                                            text: "Здравствуйте! Я AI помощник ALADDIN. Чем могу помочь?",
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
                        
                        // Spacer для клавиатуры
                        Spacer()
                            .frame(height: 16)
                    }
                    .padding(.top, 12)
                    .padding(.horizontal, 20)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Чат с AI помощником")
                
                // Поле ввода
                messageInputBar
            }
        }
        .onAppear {
            loadMessages()
            // Если сообщений нет и приветствие еще не отправлено - показываем приветствие
            if messages.isEmpty && !UserDefaults.standard.bool(forKey: hasReceivedWelcomeKey) {
                // Приветствие будет показано в ScrollView выше
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
            // Текстовое поле
            TextField("Спросите AI помощника...", text: $messageText)
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
        }
        .padding(12)
        .background(
            Color.black.opacity(0.95)
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
        
        // Сохраняем сообщение
        saveMessages()
        
        // Имитация ответа AI (через 1 секунду)
        // ⚠️ ВРЕМЕННО: Декоративный режим - API будет подключен в Этап 3
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            let aiResponse = ChatMessage(
                text: "🚧 AI Помощник в разработке. Скоро подключусь к реальному API!\n\nПриложение пока работает в демо-режиме с mock-данными.",
                isUser: false,
                time: currentTime()
            )
            messages.append(aiResponse)
            saveMessages() // Сохраняем ответ AI
        }
    }
    
    // MARK: - Data Loading and Saving
    
    private func loadMessages() {
        guard let savedData = UserDefaults.standard.data(forKey: messagesKey),
              let decoded = try? JSONDecoder().decode([ChatMessage].self, from: savedData) else {
            messages = []
            return
        }
        messages = decoded
        print("✅ Загружено сообщений AI помощника: \(messages.count)")
    }
    
    private func saveMessages() {
        guard let encoded = try? JSONEncoder().encode(messages) else {
            print("❌ Ошибка кодирования сообщений")
            return
        }
        UserDefaults.standard.set(encoded, forKey: messagesKey)
        print("✅ Сохранено сообщений AI помощника: \(messages.count)")
        
        // Уведомляем другие экраны об изменении (если нужно синхронизировать)
        NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
    }
    
    private func currentTime() -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        return formatter.string(from: Date())
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




