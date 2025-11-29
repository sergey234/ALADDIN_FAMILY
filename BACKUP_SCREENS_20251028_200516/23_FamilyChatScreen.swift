import SwiftUI

/**
 * 💬 Family Chat Screen
 * Семейный чат
 * 17_family_chat_screen из HTML
 */

struct FamilyChatScreen: View {
    
    @Environment(\.dismiss) var dismiss
    @State private var messageText: String = ""
    @State private var messages: [FamilyChatMessage] = [
        FamilyChatMessage(sender: "Сергей", text: "Всем привет! Как дела?", time: "10:30", isCurrentUser: true),
        FamilyChatMessage(sender: "Мария", text: "Привет! У нас всё хорошо 😊", time: "10:32", isCurrentUser: false),
        FamilyChatMessage(sender: "Маша", text: "Папа, можно мне ещё 30 минут?", time: "10:35", isCurrentUser: false),
        FamilyChatMessage(sender: "Сергей", text: "Конечно, дочка!", time: "10:36", isCurrentUser: true),
        FamilyChatMessage(sender: "Бабушка", text: "Как мне настроить VPN?", time: "11:15", isCurrentUser: false),
        FamilyChatMessage(sender: "Сергей", text: "Сейчас помогу! Открой настройки...", time: "11:16", isCurrentUser: true)
    ]
    
    var body: some View {
        VStack(spacing: 0) {
            ALADDINNavigationBar(
                title: "СЕМЕЙНЫЙ ЧАТ",
                subtitle: "4 участника онлайн",
                showBackButton: true,
                onBack: { dismiss() }
            )
            .accessibilityElement(children: .combine)
            .accessibilityLabel("Навигационная панель семейного чата")
            
            // Messages List
            ScrollView {
                VStack(spacing: Spacing.m) {
                    ForEach(messages) { message in
                        ChatBubbleView(message: message)
                    }
                }
                .padding(Spacing.screenPadding)
            }
            .accessibilityElement(children: .contain)
            .accessibilityLabel("Список сообщений семейного чата")
            
            // Input Field
            HStack(spacing: Spacing.s) {
                TextField("Ваше сообщение...", text: $messageText)
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium)
                    .cornerRadius(CornerRadius.md)
                    .foregroundColor(.textPrimary)
                    .font(.body)
                .accessibilityLabel("Поле ввода сообщения")
                .accessibilityHint("Введите текст сообщения для отправки в семейный чат")
                
                Button(action: {
                    sendMessage()
                    // HapticFeedback.lightImpact()
                }) {
                    Image(systemName: "paperplane.fill")
                        .font(.body)
                        .foregroundColor(.backgroundDark)
                        .frame(width: Size.navButtonSize, height: Size.navButtonSize)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
                .accessibilityLabel("Отправить сообщение")
                .accessibilityHint("Нажмите для отправки сообщения в чат")
                
                Button(action: {
                    // Voice message
                    // HapticFeedback.lightImpact()
                }) {
                    Image(systemName: "mic.fill")
                        .font(.body)
                        .foregroundColor(.textPrimary)
                        .frame(width: Size.navButtonSize, height: Size.navButtonSize)
                        .background(Color.surfaceDark.opacity(0.6))
                        .cornerRadius(CornerRadius.medium)
                }
                .accessibilityLabel("Голосовое сообщение")
                .accessibilityHint("Нажмите для записи голосового сообщения")
            }
            .padding(Spacing.screenPadding)
            .background(
                LinearGradient.cardGradient
                    .appGlassmorphism()
            )
        }
        .background(LinearGradient.backgroundGradient.ignoresSafeArea())
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Семейный чат")
        .navigationBarHidden(true)
        .safeAreaInset(edge: .top) {
            Color.clear.frame(height: Spacing.m)
        }
        .task {
            print("🚨 FamilyChatScreen загружен!")
        }
    }
    
    // MARK: - Actions
    
    private func sendMessage() {
        guard !messageText.isEmpty else { return }
        
        let newMessage = FamilyChatMessage(
            sender: "Сергей",
            text: messageText,
            time: getCurrentTime(),
            isCurrentUser: true
        )
        messages.append(newMessage)
        messageText = ""
        
        // TODO: Send to backend via WebSocket
    }
    
    private func getCurrentTime() -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        return formatter.string(from: Date())
    }
}

// MARK: - Family Chat Message

struct FamilyChatMessage: Identifiable {
    let id = UUID()
    let sender: String
    let text: String
    let time: String
    let isCurrentUser: Bool
}

// MARK: - Chat Bubble View

struct ChatBubbleView: View {
    let message: FamilyChatMessage
    
    var body: some View {
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
                
                Text(message.text)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                    .padding(Spacing.m)
                    .background(
                        message.isCurrentUser
                            ? Color.primaryBlue
                            : Color.surfaceDark
                    )
                    .cornerRadius(CornerRadius.medium)
                
                Text(message.time)
                    .font(.captionSmall)
                    .foregroundColor(.textTertiary)
            }
            .frame(maxWidth: UIScreen.main.bounds.width * 0.7, alignment: message.isCurrentUser ? .trailing : .leading)
            .accessibilityElement(children: .combine)
            .accessibilityLabel("\(message.isCurrentUser ? "Вы" : message.sender): \(message.text), время \(message.time)")
            
            if !message.isCurrentUser {
                Spacer()
            }
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Сообщение от \(message.isCurrentUser ? "вас" : message.sender)")
    }
}

// MARK: - Preview

struct FamilyChatScreen_Previews: PreviewProvider {
    static var previews: some View {
        FamilyChatScreen()
    }
}



