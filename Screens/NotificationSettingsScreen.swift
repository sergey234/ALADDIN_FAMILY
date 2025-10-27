import SwiftUI

/**
 * 🔔 Notification Settings Screen
 * Экран настроек уведомлений
 * Управление типами и настройками уведомлений
 */

struct NotificationSettingsScreen: View {
    
    // MARK: - Properties
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var notificationManager: NotificationManager
    @State private var settings: NotificationSettings
    
    // MARK: - Init
    
    init() {
        _settings = State(initialValue: NotificationManager.shared.notificationSettings)
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Background
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Navigation Bar
                ALADDINNavigationBar()
                
                // Settings List
                ScrollView {
                    VStack(spacing: 20) {
                        // Notification Types
                        notificationTypesSection
                        
                        // Sound & Badge
                        soundAndBadgeSection
                        
                        // Quiet Hours
                        quietHoursSection
                        
                        // Test Notifications
                        testNotificationsSection
                    }
                    .padding(.horizontal, 20)
                    .padding(.top, 20)
                }
                
                Spacer()
            }
        }
        .onDisappear {
            // Сохранить настройки при закрытии
            notificationManager.updateNotificationSettings(settings)
        }
    }
    
    // MARK: - Notification Types Section
    
    private var notificationTypesSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("notification.types".localized)
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                NotificationToggle(
                    title: "notification.security".localized,
                    subtitle: "notification.security.subtitle".localized,
                    icon: "🛡️",
                    isOn: $settings.securityEnabled
                )
                
                NotificationToggle(
                    title: "notification.family".localized,
                    subtitle: "notification.family.subtitle".localized,
                    icon: "👨‍👩‍👧‍👦",
                    isOn: $settings.familyEnabled
                )
                
                NotificationToggle(
                    title: "notification.vpn".localized,
                    subtitle: "notification.vpn.subtitle".localized,
                    icon: "🔒",
                    isOn: $settings.vpnEnabled
                )
                
                NotificationToggle(
                    title: "notification.ai".localized,
                    subtitle: "notification.ai.subtitle".localized,
                    icon: "🤖",
                    isOn: $settings.aiEnabled
                )
            }
        }
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.white.opacity(0.1))
        )
    }
    
    // MARK: - Sound & Badge Section
    
    private var soundAndBadgeSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("notification.sound.badge".localized)
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                NotificationToggle(
                    title: "notification.sound".localized,
                    subtitle: "notification.sound.subtitle".localized,
                    icon: "🔊",
                    isOn: $settings.soundEnabled
                )
                
                NotificationToggle(
                    title: "notification.badge".localized,
                    subtitle: "notification.badge.subtitle".localized,
                    icon: "🔴",
                    isOn: $settings.badgeEnabled
                )
            }
        }
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.white.opacity(0.1))
        )
    }
    
    // MARK: - Quiet Hours Section
    
    private var quietHoursSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("notification.quiet.hours".localized)
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                NotificationToggle(
                    title: "notification.quiet.enabled".localized,
                    subtitle: "notification.quiet.subtitle".localized,
                    icon: "🌙",
                    isOn: $settings.quietHoursEnabled
                )
                
                if settings.quietHoursEnabled {
                    VStack(spacing: 8) {
                        HStack {
                            Text("notification.quiet.start".localized)
                                .foregroundColor(.white.opacity(0.8))
                            Spacer()
                            Text(settings.quietHoursStart)
                                .foregroundColor(.white)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 6)
                                .background(
                                    RoundedRectangle(cornerRadius: 8)
                                        .fill(Color.white.opacity(0.2))
                                )
                        }
                        
                        HStack {
                            Text("notification.quiet.end".localized)
                                .foregroundColor(.white.opacity(0.8))
                            Spacer()
                            Text(settings.quietHoursEnd)
                                .foregroundColor(.white)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 6)
                                .background(
                                    RoundedRectangle(cornerRadius: 8)
                                        .fill(Color.white.opacity(0.2))
                                )
                        }
                    }
                    .padding(.top, 8)
                }
            }
        }
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.white.opacity(0.1))
        )
    }
    
    // MARK: - Test Notifications Section
    
    private var testNotificationsSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("notification.test".localized)
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
            
            VStack(spacing: 12) {
                Button(action: {
                    notificationManager.sendThreatBlockedNotification(
                        threatType: "Вредоносный сайт",
                        url: "example.com"
                    )
                }) {
                    HStack {
                        Text("🛡️")
                        Text("notification.test.security".localized)
                        Spacer()
                        Image(systemName: "chevron.right")
                    }
                    .foregroundColor(.white)
                    .padding(.vertical, 12)
                }
                
                Button(action: {
                    notificationManager.sendFamilyMemberAddedNotification(
                        memberName: "Тестовый пользователь"
                    )
                }) {
                    HStack {
                        Text("👨‍👩‍👧‍👦")
                        Text("notification.test.family".localized)
                        Spacer()
                        Image(systemName: "chevron.right")
                    }
                    .foregroundColor(.white)
                    .padding(.vertical, 12)
                }
                
                Button(action: {
                    notificationManager.sendVPNConnectedNotification(
                        server: "Германия"
                    )
                }) {
                    HStack {
                        Text("🔒")
                        Text("notification.test.vpn".localized)
                        Spacer()
                        Image(systemName: "chevron.right")
                    }
                    .foregroundColor(.white)
                    .padding(.vertical, 12)
                }
            }
        }
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.white.opacity(0.1))
        )
    }
}

// MARK: - Notification Toggle

struct NotificationToggle: View {
    let title: String
    let subtitle: String
    let icon: String
    @Binding var isOn: Bool
    
    var body: some View {
        HStack(spacing: 12) {
            Text(icon)
                .font(.system(size: 20))
            
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                
                Text(subtitle)
                    .font(.system(size: 12))
                    .foregroundColor(.white.opacity(0.7))
            }
            
            Spacer()
            
            Toggle("", isOn: $isOn)
                .toggleStyle(SwitchToggleStyle(tint: .green))
        }
    }
}

// MARK: - Preview

#if DEBUG
struct NotificationSettingsScreen_Previews: PreviewProvider {
    static var previews: some View {
        NotificationSettingsScreen()
            .environmentObject(NotificationManager.shared)
    }
}
#endif
