import SwiftUI

/**
 * 🔔 Notification Settings Screen
 * Экран настроек уведомлений
 * Управление типами и настройками уведомлений
 */

struct NotificationSettingsScreen: View {
    
    // MARK: - Properties
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var notificationManager: NotificationManager
    
    // ✅ ИСПРАВЛЕНО: Заменено @State на @AppStorage для всех 12 тумблеров
    @AppStorage("notification_security_enabled") private var securityEnabled: Bool = true
    @AppStorage("notification_family_enabled") private var familyEnabled: Bool = true
    @AppStorage("notification_network_protection_enabled") private var networkProtectionEnabled: Bool = true
    @AppStorage("notification_ai_enabled") private var aiEnabled: Bool = true
    @AppStorage("notification_bypass_enabled") private var bypassEnabled: Bool = true
    @AppStorage("notification_sound_enabled") private var soundEnabled: Bool = true
    @AppStorage("notification_badge_enabled") private var badgeEnabled: Bool = true
    @AppStorage("notification_quiet_mode_enabled") private var quietModeEnabled: Bool = false
    @AppStorage("notification_important_only_mode") private var importantOnlyMode: Bool = false
    @AppStorage("notification_do_not_disturb_mode") private var doNotDisturbMode: Bool = false
    @AppStorage("notification_high_priority_only") private var highPriorityOnly: Bool = false
    @AppStorage("notification_quiet_hours_enabled") private var quietHoursEnabled: Bool = false
    
    // Дополнительные настройки (не тумблеры, но нужны для сохранения)
    @AppStorage("notification_quiet_hours_start") private var quietHoursStart: String = "22:00"
    @AppStorage("notification_quiet_hours_end") private var quietHoursEnd: String = "08:00"
    @AppStorage("notification_max_per_hour") private var maxNotificationsPerHour: Int = 10
    @AppStorage("notification_max_per_hour_enabled") private var maxNotificationsPerHourEnabled: Bool = false
    
    // doNotDisturbUntil сохраняется через UserDefaults как timestamp
    @State private var doNotDisturbUntil: Date? = nil
    
    private func setDoNotDisturbUntil(_ date: Date?) {
        doNotDisturbUntil = date
        if let date = date {
            UserDefaults.standard.set(date.timeIntervalSince1970, forKey: "notification_do_not_disturb_until")
        } else {
            UserDefaults.standard.removeObject(forKey: "notification_do_not_disturb_until")
        }
    }
    
    private func loadDoNotDisturbUntil() {
        let timestamp = UserDefaults.standard.double(forKey: "notification_do_not_disturb_until")
        if timestamp > 0 {
            doNotDisturbUntil = Date(timeIntervalSince1970: timestamp)
        } else {
            doNotDisturbUntil = nil
        }
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
            // ✅ ИСПРАВЛЕНО: Загружаем настройки из NotificationManager и синхронизируем с @AppStorage
            let loadedSettings = notificationManager.notificationSettings
            
            // Загружаем doNotDisturbUntil из UserDefaults
            loadDoNotDisturbUntil()
            
            // Синхронизируем только если значения в UserDefaults пустые (первый запуск)
            if UserDefaults.standard.object(forKey: "notification_security_enabled") == nil {
                securityEnabled = loadedSettings.securityEnabled
                familyEnabled = loadedSettings.familyEnabled
                networkProtectionEnabled = loadedSettings.networkProtectionEnabled
                aiEnabled = loadedSettings.aiEnabled
                bypassEnabled = loadedSettings.bypassEnabled
                soundEnabled = loadedSettings.soundEnabled
                badgeEnabled = loadedSettings.badgeEnabled
                quietModeEnabled = loadedSettings.quietModeEnabled
                importantOnlyMode = loadedSettings.importantOnlyMode
                doNotDisturbMode = loadedSettings.doNotDisturbMode
                doNotDisturbUntil = loadedSettings.doNotDisturbUntil
                highPriorityOnly = loadedSettings.highPriorityOnly
                quietHoursEnabled = loadedSettings.quietHoursEnabled
                quietHoursStart = loadedSettings.quietHoursStart
                quietHoursEnd = loadedSettings.quietHoursEnd
                maxNotificationsPerHour = loadedSettings.maxNotificationsPerHour ?? 10
                maxNotificationsPerHourEnabled = loadedSettings.maxNotificationsPerHour != nil
            }
            
            // Синхронизируем обратно в NotificationManager
            syncToNotificationManager()
        }
        .onChange(of: securityEnabled) { _ in syncToNotificationManager() }
        .onChange(of: familyEnabled) { _ in syncToNotificationManager() }
        .onChange(of: networkProtectionEnabled) { _ in syncToNotificationManager() }
        .onChange(of: aiEnabled) { _ in syncToNotificationManager() }
        .onChange(of: bypassEnabled) { _ in syncToNotificationManager() }
        .onChange(of: soundEnabled) { _ in syncToNotificationManager() }
        .onChange(of: badgeEnabled) { _ in syncToNotificationManager() }
        .onChange(of: quietModeEnabled) { _ in syncToNotificationManager() }
        .onChange(of: importantOnlyMode) { _ in syncToNotificationManager() }
        .onChange(of: doNotDisturbMode) { _ in syncToNotificationManager() }
        .onChange(of: highPriorityOnly) { _ in syncToNotificationManager() }
        .onChange(of: quietHoursEnabled) { _ in syncToNotificationManager() }
        .onChange(of: quietHoursStart) { _ in syncToNotificationManager() }
        .onChange(of: quietHoursEnd) { _ in syncToNotificationManager() }
        .onChange(of: maxNotificationsPerHour) { _ in syncToNotificationManager() }
        .onChange(of: maxNotificationsPerHourEnabled) { _ in syncToNotificationManager() }
        .onDisappear {
            // Финальное сохранение при закрытии
            syncToNotificationManager()
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
                    isOn: $securityEnabled
                )
                
                NotificationToggle(
                    title: "Семья",
                    subtitle: "Уведомления о действиях членов семьи",
                    icon: "👨‍👩‍👧‍👦",
                    isOn: $familyEnabled
                )
                
                NotificationToggle(
                    title: "Защита сети",
                    subtitle: "Уведомления о подключении защиты сети",
                    icon: "🔒",
                    isOn: $networkProtectionEnabled
                )
                
                NotificationToggle(
                    title: "AI Помощник",
                    subtitle: "Уведомления от AI помощника",
                    icon: "🤖",
                    isOn: $aiEnabled
                )
                
                NotificationToggle(
                    title: "Попытки обхода",
                    subtitle: "Уведомления о заблокированных попытках обхода",
                    icon: "🚨",
                    isOn: $bypassEnabled
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
                    isOn: $soundEnabled
                )
                
                NotificationToggle(
                    title: "Badge",
                    subtitle: "Счетчик непрочитанных на иконке",
                    icon: "🔴",
                    isOn: $badgeEnabled
                )
                
                // Тихий режим
                NotificationToggle(
                    title: "Тихий режим",
                    subtitle: "Уведомления без звука и баннера, только badge",
                    icon: "🔇",
                    isOn: $quietModeEnabled
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
                    isOn: $importantOnlyMode
                )
                
                // Режим "Не беспокоить"
                VStack(alignment: .leading, spacing: 8) {
                    NotificationToggle(
                        title: "Не беспокоить",
                        subtitle: "Полностью отключает уведомления на время",
                        icon: "🔕",
                        isOn: $doNotDisturbMode
                    )
                    
                    if doNotDisturbMode {
                        DatePicker(
                            "Отключить до",
                            selection: Binding(
                                get: { doNotDisturbUntil ?? Date().addingTimeInterval(3600) },
                                set: { setDoNotDisturbUntil($0) }
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
                    isOn: $highPriorityOnly
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
                            get: { maxNotificationsPerHourEnabled },
                            set: { enabled in
                                maxNotificationsPerHourEnabled = enabled
                                if !enabled {
                                    maxNotificationsPerHour = 0
                                } else if maxNotificationsPerHour == 0 {
                                    maxNotificationsPerHour = 10
                                }
                            }
                        ), size: 40)
                    }
                    
                    if maxNotificationsPerHourEnabled && maxNotificationsPerHour > 0 {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Максимум уведомлений в час: \(maxNotificationsPerHour)")
                                .font(.system(size: 12))
                                .foregroundColor(.white.opacity(0.8))
                                .lineLimit(2)
                                .fixedSize(horizontal: false, vertical: true)
                                .multilineTextAlignment(.leading)
                            
                            Stepper(
                                "",
                                value: $maxNotificationsPerHour,
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
                    isOn: $quietHoursEnabled
                )
                
                if quietHoursEnabled {
                    VStack(spacing: 8) {
                        HStack(alignment: .center) {
                            Text("Начало")
                                .font(.system(size: 14))
                                .foregroundColor(.white.opacity(0.8))
                                .lineLimit(1)
                            Spacer()
                            Text(quietHoursStart)
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
                            Text(quietHoursEnd)
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
    
    // MARK: - Helper Methods
    
    /// Синхронизирует @AppStorage значения с NotificationManager
    private func syncToNotificationManager() {
        var updatedSettings = NotificationSettings()
        updatedSettings.securityEnabled = securityEnabled
        updatedSettings.familyEnabled = familyEnabled
        updatedSettings.networkProtectionEnabled = networkProtectionEnabled
        updatedSettings.aiEnabled = aiEnabled
        updatedSettings.bypassEnabled = bypassEnabled
        updatedSettings.soundEnabled = soundEnabled
        updatedSettings.badgeEnabled = badgeEnabled
        updatedSettings.quietModeEnabled = quietModeEnabled
        updatedSettings.importantOnlyMode = importantOnlyMode
        updatedSettings.doNotDisturbMode = doNotDisturbMode
        updatedSettings.doNotDisturbUntil = doNotDisturbUntil
        updatedSettings.highPriorityOnly = highPriorityOnly
        updatedSettings.quietHoursEnabled = quietHoursEnabled
        updatedSettings.quietHoursStart = quietHoursStart
        updatedSettings.quietHoursEnd = quietHoursEnd
        updatedSettings.maxNotificationsPerHour = maxNotificationsPerHourEnabled ? maxNotificationsPerHour : nil
        
        notificationManager.updateNotificationSettings(updatedSettings)
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
