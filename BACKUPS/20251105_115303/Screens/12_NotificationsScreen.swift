import SwiftUI

/// 🔔 Notifications Screen - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
/// Экран уведомлений - список всех уведомлений
/// Источник дизайна: /mobile/wireframes/08_notifications_screen.html
struct NotificationsScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @StateObject private var viewModel = NotificationsViewModel()
    @StateObject private var notificationManager = NotificationManager.shared
    @State private var selectedFilter: NotificationFilter = .all
    @State private var expandedFilter: NotificationFilter? = nil
    
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
        .task {
            // Подключаем callback для push-уведомлений
            notificationManager.onNotificationReceived = { notification in
                Task { @MainActor in
                    await viewModel.addNotificationFromPush(notification)
                }
            }
            
            // Загружаем уведомления при открытии экрана
            await viewModel.loadNotifications()
        }
    }
    
    // MARK: - Navigation Header
    
    private var navigationHeader: some View {
        ALADDINNavigationBar(
            title: "УВЕДОМЛЕНИЯ",
            subtitle: "\(viewModel.unreadCount) непрочитанных",
            showBackButton: true,
            showProfileButton: false,
            showListButton: false,
            rightButtons: [
                .init(icon: "trash", accessibilityLabel: "Очистить все уведомления") {
                    viewModel.clearAll()
                }
            ],
            onBack: {
                // ✅ ГИБРИДНЫЙ ПОДХОД: dismiss() как основной механизм + синхронизация NavigationManager
                // dismiss() - использует встроенный механизм SwiftUI, работает надёжно
                dismiss()
                
                // Дополнительно синхронизируем NavigationManager для корректной работы стека
                DispatchQueue.main.async {
                    if navigationManager.canGoBack {
                        navigationManager.goBack()
                    }
                }
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
                    value: "\(viewModel.notifications.count)",
                    color: .blue
                )
                
                statCard(
                    icon: "bell.badge.fill",
                    title: "Непрочитанных",
                    value: "\(viewModel.unreadCount)",
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
            
            VStack(spacing: 8) {
                ForEach(NotificationFilter.allCases, id: \.self) { filter in
                    notificationFilterCard(filter: filter)
                }
            }
        }
        .padding(16)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Notification Filter Card (Accordion)
    
    private func notificationFilterCard(filter: NotificationFilter) -> some View {
        VStack(spacing: 0) {
            Button(action: {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                    if expandedFilter == filter {
                        expandedFilter = nil
                    } else {
                        expandedFilter = filter
                        selectedFilter = filter
                    }
                }
                HapticFeedback.selection()
            }) {
                HStack(spacing: 12) {
                    Text(filter.emoji)
                        .font(.system(size: 28))
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text(filter.rawValue)
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                            .multilineTextAlignment(.leading)
                        
                        Text(filter.subtitle)
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.leading)
                    }
                    
                    Spacer()
                    
                    // Счетчик
                    Text("\(filterCount(for: filter))")
                        .font(.bodyBold)
                        .foregroundColor(filter.color)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(
                            Capsule()
                                .fill(filter.color.opacity(0.2))
                        )
                    
                    Image(systemName: expandedFilter == filter ? "chevron.up" : "chevron.down")
                        .foregroundColor(.secondaryGold)
                        .font(.headline)
                        .frame(width: 24)
                }
                .padding(Spacing.m)
            }
            
            // Краткий список уведомлений при раскрытии
            if expandedFilter == filter {
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Divider()
                        .background(Color.textTertiary)
                    
                    let previewNotifications = viewModel.getPreviewNotifications(for: filter)
                    
                    if previewNotifications.isEmpty {
                        Text("Нет уведомлений этого типа")
                            .font(.body)
                            .foregroundColor(.textSecondary)
                            .padding(.horizontal, Spacing.m)
                            .padding(.bottom, Spacing.s)
                    } else {
                        ForEach(Array(previewNotifications.prefix(3)), id: \.id) { appNotification in
                            Button(action: {
                                viewModel.markAsRead(appNotification)
                            }) {
                                HStack(spacing: 8) {
                                    Text(appNotification.icon)
                                        .font(.system(size: 20))
                                    
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(appNotification.title)
                                            .font(.body)
                                            .foregroundColor(.textPrimary)
                                        
                                        Text(appNotification.message)
                                            .font(.caption)
                                            .foregroundColor(.textSecondary)
                                            .lineLimit(1)
                                    }
                                    
                                    Spacer()
                                    
                                    Text(appNotification.time)
                                        .font(.caption2)
                                        .foregroundColor(.textTertiary)
                                    
                                    if !appNotification.isRead {
                                        Circle()
                                            .fill(filter.color)
                                            .frame(width: 6, height: 6)
                                    }
                                }
                                .padding(.horizontal, Spacing.m)
                                .padding(.vertical, Spacing.s)
                                .background(
                                    RoundedRectangle(cornerRadius: 8)
                                        .fill(Color.backgroundMedium.opacity(0.3))
                                )
                            }
                            .buttonStyle(PlainButtonStyle())
                        }
                        
                        if filterCount(for: filter) > 3 {
                            Button(action: {
                                // Уже фильтруем - список внизу обновится автоматически
                            }) {
                                HStack {
                                    Text("Показать все (\(filterCount(for: filter)))")
                                        .font(.caption)
                                        .foregroundColor(.secondaryGold)
                                    
                                    Image(systemName: "chevron.right")
                                        .font(.caption)
                                        .foregroundColor(.secondaryGold)
                                }
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, Spacing.s)
                            }
                            .buttonStyle(PlainButtonStyle())
                        }
                    }
                }
                .padding(.horizontal, Spacing.m)
                .padding(.bottom, Spacing.m)
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(expandedFilter == filter ? filter.color.opacity(0.5) : Color.secondaryGold.opacity(0.3), lineWidth: expandedFilter == filter ? 2 : 1)
                )
        )
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
                
                Text("\(viewModel.filteredNotifications(for: selectedFilter).count) из \(viewModel.notifications.count)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            LazyVStack(spacing: 8) {
                ForEach(viewModel.filteredNotifications(for: selectedFilter), id: \.id) { appNotification in
                    NotificationCard(notification: appNotification.toNotification()) {
                        viewModel.markAsRead(appNotification)
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
    
    private var threatCount: Int {
        viewModel.notifications.filter { $0.type == NotificationsViewModel.NotificationType.threat }.count
    }
    
    private func filterCount(for filter: NotificationFilter) -> Int {
        viewModel.filterCount(for: filter)
    }
}

// MARK: - Notification Card

struct NotificationCard: View {
    let notification: NotificationItem
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

// MARK: - Notification Models
// Notification и NotificationType теперь находятся в Core/Models/NotificationModels.swift

// MARK: - Preview

struct NotificationsScreen_Previews: PreviewProvider {
    static var previews: some View {
        NotificationsScreen()
    }
}
