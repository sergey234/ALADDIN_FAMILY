import SwiftUI

/// 🔔 Notifications Screen
/// Экран уведомлений - список всех уведомлений
/// Источник дизайна: /mobile/wireframes/08_notifications_screen.html
struct NotificationsScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    
    struct Notification: Identifiable {
        let id = UUID()
        let icon: String
        let title: String
        let message: String
        let time: String
        let isRead: Bool
        let type: NotificationType
    }
    
    enum NotificationType {
        case threat, success, info, warning
        
        var color: Color {
            switch self {
            case .threat: return .red
            case .success: return .green
            case .info: return .primaryBlue
            case .warning: return .orange
            }
        }
    }
    
    @State private var notifications: [Notification] = [
        Notification(icon: "🛡️", title: "Угроза заблокирована", message: "Заблокирован вредоносный сайт", time: "5 мин назад", isRead: false, type: .threat),
        Notification(icon: "✅", title: "VPN подключён", message: "Ваше соединение защищено", time: "1 час назад", isRead: true, type: .success),
        Notification(icon: "⚠️", title: "Подозрительная активность", message: "Обнаружена попытка доступа", time: "2 часа назад", isRead: true, type: .warning),
        Notification(icon: "ℹ️", title: "Обновление доступно", message: "Доступна новая версия ALADDIN", time: "Вчера", isRead: true, type: .info)
    ]
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("Фон экрана уведомлений")
            
            VStack(spacing: 0) {
                // Навигационная панель
                HStack {
                    Button(action: { dismiss() }) {
                        Image(systemName: "chevron.left")
                            .foregroundColor(.white)
                    }
                    .accessibilityLabel("Назад")
                    .accessibilityHint("Нажмите для возврата к предыдущему экрану")
                    
                    Spacer()
                    
                    VStack {
                        Text("УВЕДОМЛЕНИЯ")
                            .font(.headline)
                            .foregroundColor(.white)
                            .accessibilityLabel("УВЕДОМЛЕНИЯ")
                            .accessibilityAddTraits(.isHeader)
                        
                        Text("\(notifications.filter { !$0.isRead }.count) непрочитанных")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                            .accessibilityLabel("\(notifications.filter { !$0.isRead }.count) непрочитанных уведомлений")
                    }
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel("Заголовок уведомлений")
                    
                    Spacer()
                    
                    Button(action: { print("Отметить всё прочитанным") }) {
                        Image(systemName: "checkmark.circle")
                            .foregroundColor(.white)
                    }
                    .accessibilityLabel("Отметить всё прочитанным")
                    .accessibilityHint("Нажмите для отметки всех уведомлений как прочитанных")
                }
                .padding()
                .background(Color.black.opacity(0.5))
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Навигационная панель уведомлений")
                
                // Список уведомлений
                if notifications.isEmpty {
                    emptyState
                } else {
                    ScrollView(.vertical, showsIndicators: false) {
                        VStack(spacing: Spacing.m) {
                            ForEach(notifications) { notification in
                                notificationCard(notification)
                            }
                            
                            Spacer()
                                .frame(height: Spacing.xxl)
                        }
                        .padding(.top, Spacing.m)
                    }
                    .accessibilityElement(children: .contain)
                    .accessibilityLabel("Список уведомлений")
                }
            }
        }
        .navigationBarHidden(true)
        .safeAreaInset(edge: .top) {
            Color.clear.frame(height: Spacing.m)
        }
        .task {
            print("🚨 NotificationsScreen загружен!")
        }
    }
    
    // MARK: - Notification Card
    
    private func notificationCard(_ notification: Notification) -> some View {
        Button(action: {
            print("Открыть уведомление")
        }) {
            HStack(spacing: Spacing.m) {
                // Иконка типа
                Text(notification.icon)
                    .font(.system(size: 32))
                    .frame(width: 50, height: 50)
                    .background(
                        Circle()
                            .fill(notification.type.color.opacity(0.2))
                    )
                    .accessibilityLabel("Иконка типа уведомления: \(notification.type == .threat ? "угроза" : notification.type == .success ? "успех" : notification.type == .warning ? "предупреждение" : "информация")")
                
                // Текст
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(notification.title)
                        .font(notification.isRead ? .body : .body.bold())
                        .foregroundColor(.textPrimary)
                        .accessibilityLabel("Заголовок: \(notification.title)")
                    
                    Text(notification.message)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .lineLimit(2)
                        .accessibilityLabel("Сообщение: \(notification.message)")
                    
                    Text(notification.time)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .accessibilityLabel("Время: \(notification.time)")
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("\(notification.title). \(notification.message). \(notification.time)")
                
                Spacer()
                
                // Индикатор непрочитанного
                if !notification.isRead {
                    Circle()
                        .fill(notification.type.color)
                        .frame(width: 10, height: 10)
                        .accessibilityLabel("Непрочитанное уведомление")
                }
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.md)
                    .fill(
                        notification.isRead ?
                        Color.backgroundMedium.opacity(0.3) :
                        Color.backgroundMedium.opacity(0.5)
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.md)
                            .stroke(
                                notification.isRead ?
                                Color.clear :
                                notification.type.color.opacity(0.3),
                                lineWidth: 1
                            )
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, Spacing.screenPadding)
        .cardShadow()
        .appGlassmorphism()
        .accessibilityLabel(
            label: notification.isRead ? "\(notification.title)" : "Новое уведомление: \(notification.title)",
            hint: "Нажмите для открытия уведомления"
        )
    }
    
    // MARK: - Empty State
    
    private var emptyState: some View {
        VStack(spacing: Spacing.l) {
            Spacer()
            
            Text("🔔")
                .font(.system(size: 80))
                .accessibilityLabel("Иконка уведомлений")
            
            Text("Нет уведомлений")
                .font(.title2)
                .foregroundColor(.textPrimary)
                .accessibilityLabel("Нет уведомлений")
                .accessibilityAddTraits(.isHeader)
            
            Text("Все уведомления появятся здесь")
                .font(.body)
                .foregroundColor(.textSecondary)
                .accessibilityLabel("Все уведомления появятся здесь")
            
            Spacer()
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Пустое состояние: нет уведомлений")
    }
}

// MARK: - Preview

struct NotificationsScreen_Previews: PreviewProvider {
    static var previews: some View {
        NotificationsScreen()
    }
}



