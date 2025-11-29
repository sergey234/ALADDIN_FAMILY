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
                ALADDINNavigationBar(
                    title: "НАСТРОЙКИ УВЕДОМЛЕНИЙ",
                    subtitle: "Управление режимами и приоритетами",
                    showBackButton: true,
                    showProfileButton: false,
                    showListButton: false,
                    onBack: {
                        dismiss()
                    }
                )
                
                // Settings List
                ScrollView {
                    VStack(spacing: 20) {
                        // Notification Types
                        notificationTypesSection
                        
                        // Sound & Badge
                        soundAndBadgeSection
                        
                        // Новые режимы
                        advancedModesSection
                        
                        // Quiet Hours
                        quietHoursSection
                    }
                    .padding(.horizontal, 20)
                    .padding(.top, 20)
                }
                
                Spacer()
            }
        }
        .onAppear {
            // Синхронизируем с актуальными настройками при открытии
            settings = notificationManager.notificationSettings
        }
        .onChange(of: settings) { newSettings in
            // Сохраняем настройки в реальном времени при изменении
            notificationManager.updateNotificationSettings(newSettings)
        }
        .onDisappear {
            // Финальное сохранение при закрытии
            notificationManager.updateNotificationSettings(settings)
        }
    }
    
    // MARK: - Notification Types Section
    
    private var notificationTypesSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("ТИПЫ УВЕДОМЛЕНИЙ")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
                .lineLimit(1)
            
            VStack(spacing: 12) {
                NotificationToggle(
                    title: "Безопасность",
                    subtitle: "Уведомления об угрозах и блокировках",
                    icon: "🛡️",
                    isOn: $settings.securityEnabled
                )
                
                NotificationToggle(
                    title: "Семья",
                    subtitle: "Уведомления о действиях членов семьи",
                    icon: "👨‍👩‍👧‍👦",
                    isOn: $settings.familyEnabled
                )
                
                NotificationToggle(
                    title: "VPN",
                    subtitle: "Уведомления о подключении VPN",
                    icon: "🔒",
                    isOn: $settings.vpnEnabled
                )
                
                NotificationToggle(
                    title: "AI Помощник",
                    subtitle: "Уведомления от AI помощника",
                    icon: "🤖",
                    isOn: $settings.aiEnabled
                )
                
                NotificationToggle(
                    title: "Попытки обхода",
                    subtitle: "Уведомления о заблокированных попытках обхода",
                    icon: "🚨",
                    isOn: $settings.bypassEnabled
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
            Text("ЗВУК И BADGE")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
                .lineLimit(1)
            
            VStack(spacing: 12) {
                NotificationToggle(
                    title: "Звук",
                    subtitle: "Звуковые уведомления",
                    icon: "🔊",
                    isOn: $settings.soundEnabled
                )
                
                NotificationToggle(
                    title: "Badge",
                    subtitle: "Счетчик непрочитанных на иконке",
                    icon: "🔴",
                    isOn: $settings.badgeEnabled
                )
                
                // Тихий режим
                NotificationToggle(
                    title: "Тихий режим",
                    subtitle: "Уведомления без звука и баннера, только badge",
                    icon: "🔇",
                    isOn: $settings.quietModeEnabled
                )
            }
        }
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color.white.opacity(0.1))
        )
    }
    
    // MARK: - Advanced Modes Section
    
    private var advancedModesSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("ДОПОЛНИТЕЛЬНЫЕ РЕЖИМЫ")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
                .lineLimit(1)
            
            VStack(spacing: 12) {
                // Режим "Только важные"
                NotificationToggle(
                    title: "Только важные",
                    subtitle: "Только угрозы безопасности, остальные в тихий режим",
                    icon: "🎯",
                    isOn: $settings.importantOnlyMode
                )
                
                // Режим "Не беспокоить"
                VStack(alignment: .leading, spacing: 8) {
                    NotificationToggle(
                        title: "Не беспокоить",
                        subtitle: "Полностью отключает уведомления на время",
                        icon: "🔕",
                        isOn: $settings.doNotDisturbMode
                    )
                    
                    if settings.doNotDisturbMode {
                        DatePicker(
                            "Отключить до",
                            selection: Binding(
                                get: { settings.doNotDisturbUntil ?? Date().addingTimeInterval(3600) },
                                set: { settings.doNotDisturbUntil = $0 }
                            ),
                            displayedComponents: [.date, .hourAndMinute]
                        )
                        .datePickerStyle(.compact)
                        .foregroundColor(.white)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .fill(Color.white.opacity(0.2))
                        )
                    }
                }
                
                // Только высокий приоритет
                NotificationToggle(
                    title: "Только высокий приоритет",
                    subtitle: "Показывать только уведомления высокого приоритета",
                    icon: "⭐",
                    isOn: $settings.highPriorityOnly
                )
                
                // Ограничение частоты
                VStack(alignment: .leading, spacing: 8) {
                    HStack(alignment: .center, spacing: 12) {
                        Text("Ограничение частоты")
                            .font(.system(size: 16, weight: .medium))
                            .foregroundColor(.white)
                            .lineLimit(2)
                            .fixedSize(horizontal: false, vertical: true)
                            .multilineTextAlignment(.leading)
                        
                        Spacer()
                        
                        // ✅ УНИФИЦИРОВАНО: Используем ALADDINToggle с размером 40 для соответствия дизайну карточек родительского контроля
                        ALADDINToggle(isOn: Binding(
                            get: { settings.maxNotificationsPerHour != nil },
                            set: { enabled in
                                if enabled {
                                    settings.maxNotificationsPerHour = settings.maxNotificationsPerHour ?? 10
                                } else {
                                    settings.maxNotificationsPerHour = nil
                                }
                            }
                        ), size: 40)
                    }
                    
                    if let maxPerHour = settings.maxNotificationsPerHour {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Максимум уведомлений в час: \(maxPerHour)")
                                .font(.system(size: 12))
                                .foregroundColor(.white.opacity(0.8))
                                .lineLimit(2)
                                .fixedSize(horizontal: false, vertical: true)
                                .multilineTextAlignment(.leading)
                            
                            Stepper(
                                "",
                                value: Binding(
                                    get: { maxPerHour },
                                    set: { settings.maxNotificationsPerHour = $0 }
                                ),
                                in: 1...60,
                                step: 1
                            )
                            .labelsHidden()
                        }
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .fill(Color.white.opacity(0.1))
                        )
                    }
                }
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
            Text("ТИХИЕ ЧАСЫ")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
                .lineLimit(1)
            
            VStack(spacing: 12) {
                NotificationToggle(
                    title: "Включить тихие часы",
                    subtitle: "Отключить звук и баннер в указанное время",
                    icon: "🌙",
                    isOn: $settings.quietHoursEnabled
                )
                
                if settings.quietHoursEnabled {
                    VStack(spacing: 8) {
                        HStack(alignment: .center) {
                            Text("Начало")
                                .font(.system(size: 14))
                                .foregroundColor(.white.opacity(0.8))
                                .lineLimit(1)
                            Spacer()
                            Text(settings.quietHoursStart)
                                .font(.system(size: 14, design: .monospaced))
                                .foregroundColor(.white)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 6)
                                .background(
                                    RoundedRectangle(cornerRadius: 8)
                                        .fill(Color.white.opacity(0.2))
                                )
                        }
                        
                        HStack(alignment: .center) {
                            Text("Конец")
                                .font(.system(size: 14))
                                .foregroundColor(.white.opacity(0.8))
                                .lineLimit(1)
                            Spacer()
                            Text(settings.quietHoursEnd)
                                .font(.system(size: 14, design: .monospaced))
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
    
}

// MARK: - Notification Toggle

struct NotificationToggle: View {
    let title: String
    let subtitle: String
    let icon: String
    @Binding var isOn: Bool
    
    var body: some View {
        HStack(alignment: .center, spacing: 12) {
            Text(icon)
                .font(.system(size: 20))
                .frame(width: 28, alignment: .leading)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(.white)
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
                    .multilineTextAlignment(.leading)
                    .allowsTightening(false)
                
                Text(subtitle)
                    .font(.system(size: 12))
                    .foregroundColor(.white.opacity(0.7))
                    .lineLimit(3)
                    .fixedSize(horizontal: false, vertical: true)
                    .multilineTextAlignment(.leading)
                    .allowsTightening(false)
            }
            
            Spacer(minLength: 8)
            
            // ✅ УНИФИЦИРОВАНО: Используем ALADDINToggle с размером 40 для соответствия дизайну карточек родительского контроля
            ALADDINToggle(isOn: $isOn, size: 40)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
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
