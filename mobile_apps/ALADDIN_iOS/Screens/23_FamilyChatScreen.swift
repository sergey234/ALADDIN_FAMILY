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
            
            // Messages List
            ScrollView {
                VStack(spacing: Spacing.m) {
                    ForEach(messages) { message in
                        ChatBubbleView(message: message)
                    }
                }
                .padding(Spacing.screenPadding)
            }
            
            // Input Field
            HStack(spacing: Spacing.s) {
                ALADDINTextField(
                    placeholder: "Ваше сообщение...",
                    text: $messageText,
                    icon: "💬"
                )
                
                Button(action: {
                    sendMessage()
                    HapticFeedback.lightImpact()
                }) {
                    Image(systemName: "paperplane.fill")
                        .font(.body)
                        .foregroundColor(.backgroundDark)
                        .frame(width: Size.navButtonSize, height: Size.navButtonSize)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
                
                Button(action: {
                    // Voice message
                    HapticFeedback.lightImpact()
                }) {
                    Image(systemName: "mic.fill")
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
        .navigationBarHidden(true)
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
            
            if !message.isCurrentUser {
                Spacer()
            }
        }
    }
}

// MARK: - Preview

struct FamilyChatScreen_Previews: PreviewProvider {
    static var previews: some View {
        FamilyChatScreen()
    }
}




