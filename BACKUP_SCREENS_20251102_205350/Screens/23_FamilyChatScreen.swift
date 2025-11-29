import SwiftUI

/**
 * 💬 Family Chat Screen
 * Семейный чат
 * 17_family_chat_screen из HTML
 */

struct FamilyChatScreen: View {
    
    @Environment(\.dismiss) var dismiss
    @State private var messageText: String = ""
    @State private var messages: [FamilyChatMessage] = []
    @State private var isLoading: Bool = false
    @State private var errorMessage: String? = nil
    
    private let apiService = APIService(networkManager: NetworkManager())
    
    var body: some View {
        VStack(spacing: 0) {
            ALADDINNavigationBar(
                title: "СЕМЕЙНЫЙ ЧАТ",
                subtitle: "4 участника онлайн",
                showBackButton: true,
                showProfileButton: false,
                showListButton: false,
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
            loadMessages()
        }
        .overlay {
            if isLoading {
                ProgressView()
                    .scaleEffect(1.5)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .background(Color.black.opacity(0.3))
            }
        }
        .alert("Ошибка", isPresented: .constant(errorMessage != nil)) {
            Button("ОК") {
                errorMessage = nil
            }
        } message: {
            if let error = errorMessage {
                Text(error)
            }
        }
    }
    
    // MARK: - Actions
    
    private func loadMessages() {
        isLoading = true
        errorMessage = nil
        
        apiService.getFamilyChatMessages { result in
            DispatchQueue.main.async {
                isLoading = false
                
                switch result {
                case .success(let responses):
                    messages = responses.map { response in
                        convertToMessage(response)
                    }
                    errorMessage = nil
                    
                case .failure(let error):
                    errorMessage = error.localizedDescription
                    print("❌ Ошибка загрузки сообщений: \(error.localizedDescription)")
                }
            }
        }
    }
    
    private func sendMessage() {
        guard !messageText.isEmpty else { return }
        
        let messageToSend = messageText
        messageText = ""
        
        apiService.sendFamilyChatMessage(message: messageToSend, familyId: nil) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(_):
                    // Перезагружаем сообщения
                    loadMessages()
                    
                case .failure(let error):
                    errorMessage = error.localizedDescription
                    print("❌ Ошибка отправки сообщения: \(error.localizedDescription)")
                }
            }
        }
    }
    
    private func convertToMessage(_ response: FamilyChatMessageResponse) -> FamilyChatMessage {
        // Форматируем время из timestamp
        let timeString = formatTimestamp(response.timestamp)
        
        return FamilyChatMessage(
            id: UUID(uuidString: response.id) ?? UUID(),
            sender: response.sender,
            text: response.text,
            time: timeString,
            isCurrentUser: response.isCurrentUser
        )
    }
    
    private func formatTimestamp(_ timestamp: String) -> String {
        // Форматируем timestamp в HH:mm
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
        
        if let date = formatter.date(from: timestamp) {
            let timeFormatter = DateFormatter()
            timeFormatter.dateFormat = "HH:mm"
            return timeFormatter.string(from: date)
        }
        
        return getCurrentTime()
    }
    
    private func getCurrentTime() -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        return formatter.string(from: Date())
    }
}

// MARK: - Family Chat Message

struct FamilyChatMessage: Identifiable {
    let id: UUID
    let sender: String
    let text: String
    let time: String
    let isCurrentUser: Bool
    
    init(id: UUID = UUID(), sender: String, text: String, time: String, isCurrentUser: Bool) {
        self.id = id
        self.sender = sender
        self.text = text
        self.time = time
        self.isCurrentUser = isCurrentUser
    }
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



