import SwiftUI

/// 🔔 Notifications Screen - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
/// Экран уведомлений - список всех уведомлений
/// Источник дизайна: /mobile/wireframes/08_notifications_screen.html
struct NotificationsScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @State private var selectedFilter: NotificationFilter = .all
    @State private var notifications: [Notification] = [
        Notification(icon: "🛡️", title: "Угроза заблокирована", message: "Заблокирован вредоносный сайт", time: "5 мин назад", isRead: false, type: .threat),
        Notification(icon: "✅", title: "VPN подключён", message: "Ваше соединение защищено", time: "1 час назад", isRead: true, type: .success),
        Notification(icon: "⚠️", title: "Подозрительная активность", message: "Обнаружена попытка доступа", time: "2 часа назад", isRead: true, type: .warning),
        Notification(icon: "ℹ️", title: "Обновление доступно", message: "Доступна новая версия ALADDIN", time: "Вчера", isRead: true, type: .info),
        Notification(icon: "🔒", title: "Устройство заблокировано", message: "iPhone 12 заблокирован родителем", time: "2 дня назад", isRead: true, type: .info),
        Notification(icon: "🎉", title: "Достижение получено", message: "Вы получили награду за безопасность", time: "3 дня назад", isRead: true, type: .success),
        Notification(icon: "📱", title: "Новое устройство", message: "MacBook Pro добавлен в семью", time: "1 неделя назад", isRead: true, type: .info)
    ]
    
    enum NotificationFilter: String, CaseIterable {
        case all = "Все"
        case unread = "Непрочитанные"
        case threats = "Угрозы"
        case success = "Успех"
        case info = "Информация"
        case warning = "Предупреждения"
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient(colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)], startPoint: .topLeading, endPoint: .bottomTrailing)
                .ignoresSafeArea()
                .accessibilityElement()
                .accessibilityLabel("Фон экрана уведомлений")
            
            VStack(spacing: 0) {
                // Навигационная панель
                navigationHeader
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: 16) {
                        // Статистика уведомлений
                        notificationStats
                        
                        // Фильтры
                        notificationFilters
                        
                        // Список уведомлений
                        notificationList
                    }
                    .padding(.horizontal, 20)
                    .padding(.bottom, 32)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Список уведомлений")
            }
        }
        .navigationBarHidden(true)
    }
    
    // MARK: - Navigation Header
    
    private var navigationHeader: some View {
        ALADDINNavigationBar(
            title: "УВЕДОМЛЕНИЯ",
            subtitle: "\(unreadCount) непрочитанных",
            showBackButton: true,
            rightButtons: [
                .init(icon: "trash", accessibilityLabel: "Очистить все уведомления") {
                    clearAllNotifications()
                }
            ],
            onBack: {
                dismiss()
            }
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Навигационная панель уведомлений")
    }
    
    // MARK: - Notification Stats
    
    private var notificationStats: some View {
        VStack(spacing: 12) {
            Text("📊 СТАТИСТИКА")
                .font(.title2)
                .foregroundColor(.primary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            HStack(spacing: 12) {
                statCard(
                    icon: "bell.fill",
                    title: "Всего",
                    value: "\(notifications.count)",
                    color: .blue
                )
                
                statCard(
                    icon: "bell.badge.fill",
                    title: "Непрочитанных",
                    value: "\(unreadCount)",
                    color: .orange
                )
                
                statCard(
                    icon: "shield.fill",
                    title: "Угроз",
                    value: "\(threatCount)",
                    color: .red
                )
            }
        }
        .padding(16)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Notification Filters
    
    private var notificationFilters: some View {
        VStack(spacing: 12) {
            Text("ФИЛЬТРЫ")
                .font(.title2)
                .foregroundColor(.primary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(NotificationFilter.allCases, id: \.self) { filter in
                        Button(action: {
                            selectedFilter = filter
                        }) {
                            Text(filter.rawValue)
                                .font(.body)
                                .foregroundColor(selectedFilter == filter ? .white : .primary)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 8)
                                .background(
                                    RoundedRectangle(cornerRadius: 8)
                                        .fill(selectedFilter == filter ? Color.blue : Color.gray.opacity(0.3))
                                )
                        }
                        .accessibilityLabel("Фильтр: \(filter.rawValue)")
                        .accessibilityAddTraits(selectedFilter == filter ? .isSelected : [])
                    }
                }
                .padding(.horizontal, 20)
            }
            .padding(.horizontal, -20)
        }
        .padding(16)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Notification List
    
    private var notificationList: some View {
        VStack(spacing: 12) {
            HStack {
                Text("УВЕДОМЛЕНИЯ")
                    .font(.title2)
                    .foregroundColor(.primary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
                
                Text("\(filteredNotifications.count) из \(notifications.count)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            LazyVStack(spacing: 8) {
                ForEach(filteredNotifications) { notification in
                    NotificationCard(notification: notification) {
                        markAsRead(notification)
                    }
                }
            }
        }
        .padding(16)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Helper Views
    
    private func statCard(icon: String, title: String, value: String, color: Color) -> some View {
        VStack(spacing: 4) {
            Image(systemName: icon)
                .font(.system(size: 24))
                .foregroundColor(color)
            
            Text(value)
                .font(.title)
                .foregroundColor(.primary)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(color.opacity(0.1))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(value)")
    }
    
    private var cardBackground: some View {
        RoundedRectangle(cornerRadius: 12)
            .fill(Color.gray.opacity(0.3).opacity(0.5))
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
    }
    
    // MARK: - Computed Properties
    
    private var unreadCount: Int {
        notifications.filter { !$0.isRead }.count
    }
    
    private var threatCount: Int {
        notifications.filter { $0.type == .threat }.count
    }
    
    private var filteredNotifications: [Notification] {
        switch selectedFilter {
        case .all:
            return notifications
        case .unread:
            return notifications.filter { !$0.isRead }
        case .threats:
            return notifications.filter { $0.type == .threat }
        case .success:
            return notifications.filter { $0.type == .success }
        case .info:
            return notifications.filter { $0.type == .info }
        case .warning:
            return notifications.filter { $0.type == .warning }
        }
    }
    
    // MARK: - Actions
    
    private func markAsRead(_ notification: Notification) {
        if let index = notifications.firstIndex(where: { $0.id == notification.id }) {
            notifications[index].isRead = true
        }
    }
    
    private func clearAllNotifications() {
        notifications.removeAll()
    }
}

// MARK: - Notification Card

struct NotificationCard: View {
    let notification: Notification
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 12) {
                // Иконка уведомления
                Text(notification.icon)
                    .font(.system(size: 24))
                    .frame(width: 40, height: 40)
                    .background(
                        Circle()
                            .fill(notification.type.color.opacity(0.1))
                    )
                    .accessibilityLabel("Тип уведомления: \(notification.type.rawValue)")
                
                // Содержимое уведомления
                VStack(alignment: .leading, spacing: 4) {
                    HStack {
                        Text(notification.title)
                            .font(.body.weight(.bold))
                            .foregroundColor(.primary)
                            .multilineTextAlignment(.leading)
                        
                        if !notification.isRead {
                            Circle()
                                .fill(Color.blue)
                                .frame(width: 8, height: 8)
                                .accessibilityLabel("Непрочитанное уведомление")
                        }
                        
                        Spacer()
                    }
                    
                    Text(notification.message)
                        .font(.body)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.leading)
                        .lineLimit(2)
                    
                    Text(notification.time)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                // Стрелка
                Image(systemName: "chevron.right")
                    .font(.system(size: 14))
                    .foregroundColor(.secondary)
            }
            .padding(12)
            .background(
                RoundedRectangle(cornerRadius: 8)
                    .fill(notification.isRead ? Color.gray.opacity(0.3).opacity(0.3) : Color.blue.opacity(0.05))
            )
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(notification.title): \(notification.message), время: \(notification.time)")
        .accessibilityAddTraits(notification.isRead ? [] : .isSelected)
    }
}

// MARK: - Notification Model

struct Notification: Identifiable {
    let id = UUID()
    let icon: String
    let title: String
    let message: String
    let time: String
    var isRead: Bool
    let type: NotificationType
}

enum NotificationType: String, CaseIterable {
    case threat = "Угроза"
    case success = "Успех"
    case info = "Информация"
    case warning = "Предупреждение"
    
    var color: Color {
        switch self {
        case .threat: return .red
        case .success: return .green
        case .info: return .blue
        case .warning: return .orange
        }
    }
}

// MARK: - Preview

struct NotificationsScreen_Previews: PreviewProvider {
    static var previews: some View {
        NotificationsScreen()
    }
}
