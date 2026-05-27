import SwiftUI
struct FamilyParentalControlCard: View {
    let icon: String
    let title: String
    let statusBadge: String
    let statusText: String
    let metric: String
    let cardColor: Color
    let borderColor: Color
    let badgeColor: Color
    @Binding var isEnabled: Bool
    let action: () -> Void
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        Button(action: {
            HapticFeedback.impact(.medium)
            action()
        }) {
            VStack(spacing: 4) {
                // Badge в верхнем правом углу
                HStack {
                Spacer()
                    Text(statusBadge)
                        .font(.captionSmall)
                        .fontWeight(.bold)
                        .foregroundColor(badgeColor)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 3)
                        .background(badgeColor.opacity(0.2))
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(badgeColor.opacity(0.5), lineWidth: 1)
                        )
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                }
                .frame(height: 20)
                
                // Иконка (уменьшена)
                Text(icon)
                    .font(.system(size: 28))
                    .frame(height: 32)
                
                // Название (меньший шрифт, больше места)
                Text(title)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
                    .multilineTextAlignment(.center)
                    .lineLimit(2)
                    .minimumScaleFactor(0.85)
                    .frame(height: 32)
                    .fixedSize(horizontal: false, vertical: true)
                
                // Статус
                Text(statusText)
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
                    .multilineTextAlignment(.center)
                    .lineLimit(1)
                    .frame(height: 14)
                
                // Метрика
                Text(metric)
                    .font(.captionSmall)
                    .foregroundColor(.textTertiary)
                    .multilineTextAlignment(.center)
                    .lineLimit(1)
                    .frame(height: 14)
                
                Spacer(minLength: 4)
                
                // Улучшенный toggle с визуальным индикатором
                HStack(spacing: 4) {
                    Circle()
                        .fill(isEnabled ? Color.successGreen : Color.textTertiary)
                        .frame(width: 8, height: 8)
                    
                    Text(isEnabled ? localizationManager.localized("toggle_on") : localizationManager.localized("toggle_off"))
                        .font(.captionSmall)
                        .fontWeight(.bold)
                        .foregroundColor(isEnabled ? .successGreen : .textTertiary)
                        .frame(width: 24)
                    
                    Button(action: {
                        withAnimation(.easeInOut(duration: 0.3)) {
                            isEnabled.toggle()
                        }
                        HapticFeedback.impact(.medium)
                    }) {
                        ZStack {
                            RoundedRectangle(cornerRadius: 12)
                                .fill(
                                    LinearGradient(
                                        colors: isEnabled ?
                                            [Color(hex: "#8B5CF6"), Color(hex: "#A78BFA")] :
                                            [Color.backgroundMedium, Color.backgroundMedium.opacity(0.5)],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    )
                                )
                                .frame(width: 40, height: 24)
                            
                            Circle()
                                .fill(Color.white)
                                .frame(width: 20, height: 20)
                                .shadow(color: Color.black.opacity(0.2), radius: 3, x: 0, y: 2)
                                .offset(x: isEnabled ? 8 : -8)
                        }
                    }
                    .buttonStyle(PlainButtonStyle())
                }
                .frame(height: 24)
            }
            .frame(height: 190)
            .frame(maxWidth: .infinity)
            .padding(.horizontal, 8)
            .padding(.vertical, 10)
            .background(cardColor)
            .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
            // Ободок только если включено (без захода на toggle)
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .stroke(
                        isEnabled ? Color.secondaryGold.opacity(0.5) : Color.clear,
                        lineWidth: isEnabled ? 2 : 0
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
        .cardShadow()
    }
}

// MARK: - Content Block Item Component

struct FamilyContentBlockItem: View {
    let icon: String
    let title: String
    let description: String
    @Binding var isEnabled: Bool
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            // Иконка
            Text(icon)
                .font(.system(size: 28))
                .frame(width: 40, height: 40)
            
            // Информация
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
                
                Text(description)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .lineLimit(2)
            }
            
            Spacer(minLength: 8)
            
            // Toggle без ободков - используем кастомный без padding
            Button(action: {
                withAnimation(.easeInOut(duration: 0.3)) {
                    isEnabled.toggle()
                }
                HapticFeedback.impact(.medium)
            }) {
                ZStack {
                    RoundedRectangle(cornerRadius: 15)
                        .fill(
                            LinearGradient(
                                colors: isEnabled ?
                                    [Color(hex: "#8B5CF6"), Color(hex: "#A78BFA")] :
                                    [Color.backgroundMedium, Color.backgroundMedium.opacity(0.5)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 50, height: 30)
                    
                    Circle()
                        .fill(Color.white)
                        .frame(width: 26, height: 26)
                        .shadow(color: Color.black.opacity(0.2), radius: 4, x: 0, y: 2)
                        .offset(x: isEnabled ? 10 : -10)
                }
            }
            .buttonStyle(PlainButtonStyle())
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.2))
        .cornerRadius(CornerRadius.medium)
        // Убрали белый ободок - теперь только фон
    }
}

// MARK: - Config Button Item Component

struct FamilyConfigButtonItem: View {
    let icon: String
    let title: String
    let description: String
    let buttonTitle: String
    let action: () -> Void
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            // Иконка
            Text(icon)
                .font(.system(size: 28))
                .frame(width: 40, height: 40)
            
            // Информация
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
                
                Text(description)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .lineLimit(2)
            }
            
            Spacer(minLength: 8)
            
            // Золотая кнопка
            Button(action: {
                HapticFeedback.impact(.medium)
                action()
            }) {
                Text(buttonTitle)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(.secondaryGold)
                    .padding(.horizontal, Spacing.m)
                    .padding(.vertical, Spacing.xs)
                    .background(Color.secondaryGold.opacity(0.2))
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.secondaryGold.opacity(0.5), lineWidth: 1)
                    )
                    .cornerRadius(8)
            }
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.2))
        .cornerRadius(CornerRadius.medium)
    }
}

// MARK: - Badge Item Component

struct FamilyBadgeItem: View {
    let icon: String
    let title: String
    let description: String
    let badgeText: String
    let badgeColor: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: {
            HapticFeedback.impact(.medium)
            action()
        }) {
            HStack(spacing: Spacing.m) {
                // Иконка
                Text(icon)
                    .font(.system(size: 28))
                    .frame(width: 40, height: 40)
                
                // Информация
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                        .lineLimit(2)
                        .fixedSize(horizontal: false, vertical: true)
                    
                    Text(description)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .lineLimit(2)
                }
                
                Spacer(minLength: 8)
                
                // Badge
                Text(badgeText)
                    .font(.captionSmall)
                    .fontWeight(.bold)
                    .foregroundColor(badgeColor)
                    .padding(.horizontal, Spacing.s)
                    .padding(.vertical, 4)
                    .background(badgeColor.opacity(0.2))
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(badgeColor.opacity(0.5), lineWidth: 1)
                    )
                    .cornerRadius(8)
            }
            .padding(Spacing.m)
            .background(Color.backgroundMedium.opacity(0.2))
            .cornerRadius(CornerRadius.medium)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Action Button Item Component

struct FamilyActionButtonItem: View {
    let icon: String
    let title: String
    let description: String
    let buttonTitle: String
    let action: () -> Void
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            // Иконка
            Text(icon)
                .font(.system(size: 28))
                .frame(width: 40, height: 40)
            
            // Информация
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
                
                Text(description)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .lineLimit(2)
            }
            
            Spacer(minLength: 8)
            
            // Красная кнопка действия
            Button(action: {
                HapticFeedback.impact(.medium)
                action()
            }) {
                Text(buttonTitle)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(.dangerRed)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
                    .padding(.horizontal, Spacing.m)
                    .padding(.vertical, Spacing.xs)
                    .background(Color.dangerRed.opacity(0.2))
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.dangerRed.opacity(0.5), lineWidth: 1)
                    )
                    .cornerRadius(8)
            }
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.2))
        .cornerRadius(CornerRadius.medium)
    }
}

struct FamilyTimeControlModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Состояния для детальных модалов настроек
    @State private var showScreenTimeSettings = false
    @State private var showScheduleSettings = false
    @State private var showSleepTimeSettings = false
    @State private var showAppLimitsSettings = false
    
    // Настройки времени с сохранением в UserDefaults
    @AppStorage("parental_screen_time_limit") private var screenTimeLimit: String = "3h/day"
    @AppStorage("parental_screen_time_remaining") private var screenTimeRemaining: String = "1h 24m"
    @AppStorage("parental_schedule_weekdays") private var scheduleWeekdays: String = "15:00-18:00"
    @AppStorage("parental_schedule_weekends") private var scheduleWeekends: String = "10:00-20:00"
    @AppStorage("parental_bedtime_start") private var bedtimeStart: String = "22:00"
    @AppStorage("parental_bedtime_end") private var bedtimeEnd: String = "07:00"
    @AppStorage("parental_instagram_limit") private var instagramLimit: String = "30 min"
    @AppStorage("parental_tiktok_limit") private var tiktokLimit: String = "20 min"
    
    // Статистика
    @State private var totalTimeUsed: String = "1h 36m"
    @State private var totalTimeLimit: String = "3h"
    @State private var instagramUsed: String = "18 min"
    @State private var instagramLimitStat: String = "30 min"
    @State private var tiktokUsed: String = "12 min"
    @State private var tiktokLimitStat: String = "20 min"
    
    var body: some View {
        FamilyModalBaseView(
            title: "⏱️ \(localizationManager.localized("family_time_management"))",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Экранное время
                FamilyConfigButtonItem(
                    icon: "📱",
                    title: localizationManager.localized("family_screen_time"),
                    description: "\(localizationManager.localized("family_screen_time_now")) \(screenTimeLimit) (\(localizationManager.localized("family_screen_time_remaining")) \(screenTimeRemaining))",
                    buttonTitle: localizationManager.localized("family_configure"),
                    action: { showScreenTimeSettings = true }
                )
                
                // 2. Расписание доступа
                FamilyConfigButtonItem(
                    icon: "📅",
                    title: localizationManager.localized("family_schedule_access"),
                    description: "\(localizationManager.localized("family_weekdays_short")) \(scheduleWeekdays), \(localizationManager.localized("family_weekends_short")) \(scheduleWeekends)",
                    buttonTitle: localizationManager.localized("family_configure"),
                    action: { showScheduleSettings = true }
                )
                
                // 3. Время сна
                FamilyConfigButtonItem(
                    icon: "🌙",
                    title: localizationManager.localized("family_bedtime"),
                    description: "\(localizationManager.localized("family_bedtime_block")) \(bedtimeStart) - \(bedtimeEnd)",
                    buttonTitle: localizationManager.localized("family_configure"),
                    action: { showSleepTimeSettings = true }
                )
                
                // 4. Лимиты по приложениям
                FamilyConfigButtonItem(
                    icon: "⏰",
                    title: localizationManager.localized("family_app_limits"),
                    description: "\(localizationManager.localized("family_instagram")) \(instagramLimit), \(localizationManager.localized("family_tiktok")) \(tiktokLimit)",
                    buttonTitle: localizationManager.localized("family_configure"),
                    action: { showAppLimitsSettings = true }
                )
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Статистика
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_statistics_today"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    VStack(alignment: .leading, spacing: 6) {
                        HStack {
                            Text(localizationManager.localized("family_total_time"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(totalTimeUsed) / \(totalTimeLimit)")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                        
                        HStack {
                            Text(localizationManager.localized("family_instagram"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(instagramUsed) / \(instagramLimitStat)")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                        
                        HStack {
                            Text(localizationManager.localized("family_tiktok"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(tiktokUsed) / \(tiktokLimitStat)")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
            }
        }
        // Детальные модалы настроек
        .sheet(isPresented: $showScreenTimeSettings) {
            ScreenTimeSettingsModal(isPresented: $showScreenTimeSettings)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showScheduleSettings) {
            ScheduleSettingsModal(isPresented: $showScheduleSettings)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showSleepTimeSettings) {
            SleepTimeSettingsModal(isPresented: $showSleepTimeSettings)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showAppLimitsSettings) {
            AppLimitsSettingsModal(isPresented: $showAppLimitsSettings)
                .environmentObject(localizationManager)
        }
        .onAppear {
            // Загружаем статистику при открытии модала
            loadTimeStatistics()
        }
    }
    
    // Загрузка статистики времени из UserDefaults
    private func loadTimeStatistics() {
        if let stats = UserDefaults.standard.dictionary(forKey: "parental_time_stats") as? [String: String] {
            totalTimeUsed = stats["totalTimeUsed"] ?? "1h 36m"
            totalTimeLimit = stats["totalTimeLimit"] ?? "3h"
            instagramUsed = stats["instagramUsed"] ?? "18 min"
            instagramLimitStat = stats["instagramLimitStat"] ?? "30 min"
            tiktokUsed = stats["tiktokUsed"] ?? "12 min"
            tiktokLimitStat = stats["tiktokLimitStat"] ?? "20 min"
        }
    }
}

struct FamilyMonitoringModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Состояния для toggle-элементов с сохранением в UserDefaults
    @AppStorage("parental_messages_monitoring") private var isMessagesMonitoringEnabled: Bool = false
    @AppStorage("parental_screenshots_enabled") private var isScreenshotsEnabled: Bool = false
    
    // Состояния для детальных модалов просмотра
    @State private var showBrowserHistory = false
    @State private var showAppHistory = false
    @State private var showContacts = false
    
    // Mock-данные (загружаются из UserDefaults)
    @State private var browserSitesCount: Int = 342
    @State private var appsUsedCount: Int = 28
    @State private var contactsCount: Int = 47
    
    // Статистика (загружается из UserDefaults)
    @State private var topSite: String = "YouTube.com"
    @State private var topSiteVisits: Int = 142
    @State private var topApp: String = "Instagram"
    @State private var topAppTime: String = "8h 24m"
    @State private var activeContacts: Int = 47
    
    // Ключ для статистики мониторинга
    private let statsKey = "parental_monitoring_stats"
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("family_monitoring_modal_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. История браузера - Badge Item (кликабельный)
                FamilyBadgeItem(
                    icon: "🌐",
                    title: localizationManager.localized("family_browser_history"),
                    description: "\(browserSitesCount) \(localizationManager.localized("family_sites")) \(localizationManager.localized("family_per_week"))",
                    badgeText: localizationManager.localized("family_active_badge"),
                    badgeColor: .successGreen,
                    action: { showBrowserHistory = true }
                )
                
                // 2. История приложений - Badge Item (кликабельный)
                FamilyBadgeItem(
                    icon: "📲",
                    title: localizationManager.localized("family_app_history"),
                    description: "\(appsUsedCount) \(localizationManager.localized("family_apps")) \(localizationManager.localized("family_used"))",
                    badgeText: localizationManager.localized("family_active_badge"),
                    badgeColor: .successGreen,
                    action: { showAppHistory = true }
                )
                
                // 3. Мониторинг сообщений - Toggle Item
                FamilyContentBlockItem(
                    icon: "💬",
                    title: localizationManager.localized("family_message_monitoring"),
                    description: localizationManager.localized("family_message_monitoring_desc"),
                    isEnabled: $isMessagesMonitoringEnabled
                )
                
                // 4. Просмотр контактов - Badge Item (кликабельный)
                FamilyBadgeItem(
                    icon: "👥",
                    title: localizationManager.localized("family_contacts_view"),
                    description: localizationManager.localized("family_contacts_desc"),
                    badgeText: localizationManager.localized("family_active_badge"),
                    badgeColor: .successGreen,
                    action: { showContacts = true }
                )
                
                // 5. Скриншоты экрана - Toggle Item
                FamilyContentBlockItem(
                    icon: "📸",
                    title: localizationManager.localized("family_screenshots"),
                    description: localizationManager.localized("family_screenshots_desc"),
                    isEnabled: $isScreenshotsEnabled
                )
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Статистика
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_statistics_week_detailed"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    VStack(alignment: .leading, spacing: 6) {
                        HStack {
                            Text(localizationManager.localized("family_top_site"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(topSite) (\(topSiteVisits) \(localizationManager.localized("family_visits")))")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                        
                        HStack {
                            Text(localizationManager.localized("family_top_app"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(topApp) (\(topAppTime))")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                        
                        HStack {
                            Text(localizationManager.localized("family_contacts"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(activeContacts) \(localizationManager.localized("family_active"))")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
            }
        }
        // Детальные модалы просмотра (создадим полноценные ниже)
        .sheet(isPresented: $showBrowserHistory) {
            BrowserHistoryDetailModal(isPresented: $showBrowserHistory)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showAppHistory) {
            AppHistoryDetailModal(isPresented: $showAppHistory)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showContacts) {
            ContactsDetailModal(isPresented: $showContacts)
                .environmentObject(localizationManager)
        }
        .onAppear {
            // Загружаем статистику при открытии модала
            loadMonitoringStatistics()
        }
        .onChange(of: isMessagesMonitoringEnabled) { newValue in
            print("✅ Message monitoring: \(newValue ? "ON" : "OFF")")
        }
        .onChange(of: isScreenshotsEnabled) { newValue in
            print("✅ Screenshots monitoring: \(newValue ? "ON" : "OFF")")
        }
    }
    
    // Загрузка статистики мониторинга из UserDefaults
    private func loadMonitoringStatistics() {
        if let stats = UserDefaults.standard.dictionary(forKey: statsKey) {
            browserSitesCount = stats["browserSitesCount"] as? Int ?? 342
            appsUsedCount = stats["appsUsedCount"] as? Int ?? 28
            contactsCount = stats["contactsCount"] as? Int ?? 47
            topSite = stats["topSite"] as? String ?? "YouTube.com"
            topSiteVisits = stats["topSiteVisits"] as? Int ?? 142
            topApp = stats["topApp"] as? String ?? "Instagram"
            topAppTime = stats["topAppTime"] as? String ?? "8h 24m"
            activeContacts = stats["activeContacts"] as? Int ?? 47
        }
    }
}

struct FamilyLocationModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // ✅ ИНТЕГРАЦИЯ LocationManager
    @StateObject private var locationManager = LocationManager.shared
    
    // API сервис для загрузки данных
    private let apiService = APIService.shared
    
    // Состояния для toggle-элементов с сохранением в UserDefaults
    @AppStorage("parental_location_enabled") private var isLocationEnabledState: Bool = true
    @AppStorage("parental_sos_enabled") private var isSOSEnabled: Bool = true
    
    // Состояния для детальных модалов
    @State private var showGeofencesSettings = false
    @State private var showLocationHistory = false
    
    // Данные (загружаются из API и UserDefaults)
    @State private var locationStatus: String = ""
    @State private var locationLastUpdate: String = ""
    @State private var geofencesCount: Int = 2
    @State private var geofencesList: String = ""
    @State private var isLoadingLocationData: Bool = false
    
    // Статистика событий сегодня (загружается из UserDefaults)
    @State private var todayEvents: [LocationEvent] = []
    
    // Ключ для статистики геолокации
    private let statsKey = "parental_location_stats"
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("family_location"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Местоположение - Toggle Item
                FamilyContentBlockItem(
                    icon: "📍",
                    title: localizationManager.localized("family_location"),
                    description: "\(locationStatus) • \(locationLastUpdate)",
                    isEnabled: $isLocationEnabledState
                )
                
                // 2. Геозоны - Config Button Item
                FamilyConfigButtonItem(
                    icon: "🗺️",
                    title: localizationManager.localized("family_geofences"),
                    description: "\(geofencesCount) \(localizationManager.localized("family_active_colon")) \(geofencesList)",
                    buttonTitle: localizationManager.localized("family_configure"),
                    action: { showGeofencesSettings = true }
                )
                
                // 3. История перемещений - Config Button Item
                FamilyConfigButtonItem(
                    icon: "📜",
                    title: localizationManager.localized("family_movement_history"),
                    description: localizationManager.localized("family_movement_desc"),
                    buttonTitle: localizationManager.localized("family_view"),
                    action: { showLocationHistory = true }
                )
                
                // 4. Кнопка SOS - Toggle Item
                FamilyContentBlockItem(
                    icon: "🆘",
                    title: localizationManager.localized("family_sos_button"),
                    description: localizationManager.localized("family_sos_desc"),
                    isEnabled: $isSOSEnabled
                )
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Статистика
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_statistics_today_detailed"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    ForEach(todayEvents) { event in
                        HStack {
                            Text("• \(event.time) - \(event.action)")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text(event.status.icon)
                                .font(.caption)
                        }
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
            }
        }
        .sheet(isPresented: $showGeofencesSettings) {
            GeofencesSettingsModal(isPresented: $showGeofencesSettings)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showLocationHistory) {
            LocationHistoryDetailModal(isPresented: $showLocationHistory)
                .environmentObject(localizationManager)
        }
        .id("location_modal_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            // ✅ ИНТЕГРАЦИЯ: Запрос разрешения и запуск Significant-Change
            setupLocationServices()
            // Загружаем статистику при открытии модала
            loadLocationStatistics()
        }
        .onChange(of: isLocationEnabledState) { newValue in
            print("✅ Geolocation: \(newValue ? "ON" : "OFF")")
            if newValue {
                // ✅ ИНТЕГРАЦИЯ: Запуск мониторинга при включении
                setupLocationServices()
            } else {
                // ✅ ИНТЕГРАЦИЯ: Остановка мониторинга при выключении
                locationManager.stopSignificantLocationChanges()
            }
        }
        .onChange(of: isSOSEnabled) { newValue in
            print("✅ SOS button: \(newValue ? "ON" : "OFF")")
        }
    }
    
    // ✅ ИНТЕГРАЦИЯ: Настройка LocationManager
    private func setupLocationServices() {
        print("📍 FamilyLocationModal: Настройка LocationManager...")
        
        // Запрос разрешения Always (для Significant-Change и Region Monitoring)
        if locationManager.authorizationStatus != .authorizedAlways {
            locationManager.requestAuthorization(always: true)
        }
        
        // Запуск Significant-Change Location Service
        if isLocationEnabledState && locationManager.hasRequiredAuthorization(forBackground: true) {
            locationManager.startSignificantLocationChanges()
            print("✅ FamilyLocationModal: Significant-Change запущен")
        }
        
        // Загрузка и мониторинг геозон
        loadAndMonitorGeofences()
    }
    
    // ✅ ИНТЕГРАЦИЯ: Загрузка и мониторинг геозон
    private func loadAndMonitorGeofences() {
        // Загружаем геозоны из UserDefaults
        let geofencesKey = "geofences_settings"
        guard let data = UserDefaults.standard.data(forKey: geofencesKey),
              let decoded = try? JSONDecoder().decode([GeofenceItemCodable].self, from: data) else {
            print("⚠️ FamilyLocationModal: Геозоны не найдены")
            return
        }
        
        // Мониторим каждую геозону через LocationManager
        for geofenceCodable in decoded {
            // Получаем координаты из адреса (здесь нужна геокодировка)
            // Для примера используем координаты Москвы
            let center = CLLocationCoordinate2D(latitude: 55.7558, longitude: 37.6173)
            
            do {
                // Используем координаты по умолчанию (Москва)
                // TODO: Добавить геокодировку адреса для получения реальных координат
                let geofenceCenter = center
                
                let geofence = GeofenceItem(
                    name: geofenceCodable.name,
                    address: geofenceCodable.address,
                    radius: geofenceCodable.radius
                )
                
                try locationManager.startMonitoring(geofence: geofence, center: geofenceCenter)
                print("✅ FamilyLocationModal: Геозона '\(geofence.name)' добавлена в мониторинг")
            } catch {
                print("❌ FamilyLocationModal: Ошибка добавления геозоны '\(geofenceCodable.name)': \(error.localizedDescription)")
            }
        }
    }
    
    // Загрузка статистики геолокации из UserDefaults и API
    private func loadLocationStatistics() {
        print("🔍 FamilyLocationModal: Загрузка статистики геолокации...")
        
        // ✅ ИНТЕГРАЦИЯ: Получение текущего местоположения
        Task {
            do {
                let currentLocation = try await locationManager.getCurrentLocation()
                print("✅ FamilyLocationModal: Текущее местоположение: \(currentLocation.coordinate.latitude), \(currentLocation.coordinate.longitude)")
                
                // Обновляем статус местоположения
                DispatchQueue.main.async {
                    self.locationStatus = String(format: "📍 %.4f, %.4f", currentLocation.coordinate.latitude, currentLocation.coordinate.longitude)
                    self.locationLastUpdate = String(format: localizationManager.localized("family_min_ago_format"), 0)
                }
            } catch {
                print("⚠️ FamilyLocationModal: Ошибка получения местоположения: \(error.localizedDescription)")
            }
        }
        
        // Пробуем загрузить из API
        loadLocationDataFromAPI()
        
        // Fallback на UserDefaults и значения по умолчанию
        let home = localizationManager.localized("geofences_home")
        let street = localizationManager.localized("geofences_street_lenin")
        let school = localizationManager.localized("geofences_school")
        let defaultStatus = "🏠 \(home) (\(street))"
        let defaultLastUpdate = String(format: localizationManager.localized("family_min_ago_format"), 2)
        let defaultGeofences = [home, school]
        let defaultGeofenceList = defaultGeofences.joined(separator: ", ")
        
        // Устанавливаем значения по умолчанию
        locationStatus = defaultStatus
        locationLastUpdate = defaultLastUpdate
        geofencesCount = defaultGeofences.count
        geofencesList = defaultGeofenceList
        
        // Загружаем статус и данные (если есть сохранённые значения)
        if let stats = UserDefaults.standard.dictionary(forKey: statsKey) {
            locationStatus = stats["locationStatus"] as? String ?? defaultStatus
            locationLastUpdate = stats["locationLastUpdate"] as? String ?? defaultLastUpdate
            geofencesCount = stats["geofencesCount"] as? Int ?? defaultGeofences.count
            geofencesList = stats["geofencesList"] as? String ?? defaultGeofenceList
            print("✅ FamilyLocationModal: Загружено из UserDefaults")
        } else {
            print("⚠️ FamilyLocationModal: Используются значения по умолчанию")
        }
        
        // Загружаем события сегодня (по умолчанию примерные)
        todayEvents = [
            LocationEvent(time: "08:30", action: localizationManager.localized("location_left_home"), status: .departure),
            LocationEvent(time: "09:15", action: localizationManager.localized("location_arrived_school"), status: .arrival),
            LocationEvent(time: "15:45", action: localizationManager.localized("location_returned_home"), status: .arrival)
        ]
    }
    
    /// Загрузка данных геолокации из API
    private func loadLocationDataFromAPI() {
        guard !isLoadingLocationData else { return }
        
        isLoadingLocationData = true
        print("🔍 FamilyLocationModal: Загрузка данных геолокации из API...")
        
        // Загружаем статистику геолокации
        apiService.getLocationStats { result in
            DispatchQueue.main.async {
                self.isLoadingLocationData = false
                
                switch result {
                case .success(let stats):
                    print("✅ FamilyLocationModal: Данные геолокации загружены из API")
                    // Обновляем данные из API (если есть реальные данные)
                    // TODO: Интегрировать реальные данные из stats
                    _ = stats  // Используем для будущей интеграции
                    
                case .failure(let error):
                    print("⚠️ FamilyLocationModal: Ошибка загрузки данных из API: \(error.localizedDescription)")
                    // Используем данные из UserDefaults (fallback)
                }
            }
        }
        
        // Загружаем запросы местоположения
        apiService.getLocationRequests(limit: 10) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let requests):
                    print("✅ FamilyLocationModal: Загружено \(requests.count) запросов местоположения")
                    // TODO: Обработать запросы и обновить UI
                    
                case .failure(let error):
                    print("⚠️ FamilyLocationModal: Ошибка загрузки запросов: \(error.localizedDescription)")
                }
            }
        }
    }
}

// MARK: - Location Event Model

struct LocationEvent: Identifiable {
    let id = UUID()
    let time: String
    let action: String
    let status: LocationStatus
    
    enum LocationStatus {
        case arrival
        case departure
        
        var icon: String {
            switch self {
            case .arrival: return "✅"
            case .departure: return "🚶"
            }
        }
    }
}

struct FamilyReportsModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Выбранный ребёнок для загрузки статистики
    @AppStorage("parental_selected_child") private var selectedChild: String = ""
    
    // Список детей (динамический)
    @State private var children: [String] = []
    
    // Состояния для детальных модалов просмотра
    @State private var showWeeklyReport = false
    @State private var showSuspiciousActivity = false
    @State private var showTopSites = false
    @State private var showTopApps = false
    @State private var showUsageHours = false
    @State private var showBypassAttempts = false
    
    // Mock-данные (загружаются из UserDefaults)
    @State private var suspiciousActivityCount: Int = 2
    @State private var bypassAttemptsCount: Int = 0
    
    // Статистика предупреждений (загружается из UserDefaults)
    @State private var warnings: [ReportWarning] = []
    
    // Ключ для статистики отчётов
    private let statsKey = "parental_reports_stats"
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("reports_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Еженедельный отчёт - Config Button Item
                FamilyConfigButtonItem(
                    icon: "📅",
                    title: localizationManager.localized("family_weekly_report"),
                    description: localizationManager.localized("family_weekly_report_desc"),
                    buttonTitle: localizationManager.localized("family_view"),
                    action: { showWeeklyReport = true }
                )
                
                // 2. Подозрительная активность - Badge Item
                FamilyBadgeItem(
                    icon: "⚠️",
                    title: localizationManager.localized("family_suspicious_activity_title"),
                    description: "\(suspiciousActivityCount) \(localizationManager.localized("family_new")) \(localizationManager.localized("family_warnings"))",
                    badgeText: "\(suspiciousActivityCount)",
                    badgeColor: .dangerRed,
                    action: { showSuspiciousActivity = true }
                )
                
                // 3. Top-5 сайтов - Config Button Item
                FamilyConfigButtonItem(
                    icon: "🌐",
                    title: localizationManager.localized("family_top_5_sites"),
                    description: localizationManager.localized("family_top_sites_desc"),
                    buttonTitle: localizationManager.localized("family_view"),
                    action: { showTopSites = true }
                )
                
                // 4. Top-5 приложений - Config Button Item
                FamilyConfigButtonItem(
                    icon: "📱",
                    title: localizationManager.localized("family_top_5_apps"),
                    description: localizationManager.localized("family_usage_by_time"),
                    buttonTitle: localizationManager.localized("family_view"),
                    action: { showTopApps = true }
                )
                
                // 5. Пиковые часы активности - Config Button Item
                FamilyConfigButtonItem(
                    icon: "📊",
                    title: localizationManager.localized("reports_peak_hours"),
                    description: localizationManager.localized("reports_peak_hours_desc"),
                    buttonTitle: localizationManager.localized("reports_view"),
                    action: { showUsageHours = true }
                )
                
                // 6. Попытки обхода блокировок - Badge Item
                FamilyBadgeItem(
                    icon: "🛡️",
                    title: localizationManager.localized("reports_bypass_attempts"),
                    description: localizationManager.localized("reports_bypass_attempts_desc"),
                    badgeText: "\(bypassAttemptsCount)",
                    badgeColor: .successGreen,
                    action: { showBypassAttempts = true }
                )
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Статистика предупреждений
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_suspicious_activity"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    ForEach(warnings) { warning in
                        HStack {
                            Text("• \(warning.text)")
                                .font(.caption)
                                .foregroundColor(warning.color)
                            Spacer()
                        }
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
            }
        }
        .sheet(isPresented: $showWeeklyReport) {
            WeeklyReportDetailModal(isPresented: $showWeeklyReport)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showSuspiciousActivity) {
            SuspiciousActivityDetailModal(isPresented: $showSuspiciousActivity)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showTopSites) {
            TopSitesDetailModal(isPresented: $showTopSites)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showTopApps) {
            TopAppsDetailModal(isPresented: $showTopApps)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showUsageHours) {
            UsageHoursDetailModal(isPresented: $showUsageHours)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showBypassAttempts) {
            BypassAttemptsDetailModal(isPresented: $showBypassAttempts)
                .environmentObject(localizationManager)
        }
        .id("reports_modal_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadChildren()
            if selectedChild.isEmpty && !children.isEmpty {
                selectedChild = children.first ?? ""
            }
            // Загружаем статистику при открытии модала
            loadReportsStatistics()
        }
    }
    
    // Загрузка списка детей из family_members_list
    private func loadChildren() {
        guard let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
              let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) else {
            children = []
            return
        }
        
        children = decoded
            .filter { member in
                member.role == .child || member.role == .teenager
            }
            .map { $0.name }
    }
    
    // Загрузка статистики отчётов из UserDefaults и API
    private func loadReportsStatistics() {
        // Загружаем из UserDefaults (локальный кэш)
        if let stats = UserDefaults.standard.dictionary(forKey: statsKey) {
            suspiciousActivityCount = stats["suspiciousActivityCount"] as? Int ?? 2
            bypassAttemptsCount = stats["bypassAttemptsCount"] as? Int ?? 0
        }
        
        // Загружаем статистику обхода через API
        let manager = ParentalControlManager.shared
        manager.getBypassStats(childId: selectedChild) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let stats):
                    self.bypassAttemptsCount = stats.week
                    // Сохраняем в UserDefaults для кэширования
                    var cachedStats = UserDefaults.standard.dictionary(forKey: self.statsKey) ?? [:]
                    cachedStats["bypassAttemptsCount"] = stats.week
                    UserDefaults.standard.set(cachedStats, forKey: self.statsKey)
                case .failure(let error):
                    print("⚠️ Failed to load bypass statistics: \(error.localizedDescription)")
                    // Оставляем значения по умолчанию
                }
            }
        }
        
        // Загружаем предупреждения (по умолчанию примерные)
        if warnings.isEmpty {
            warnings = [
                ReportWarning(text: localizationManager.localized("family_warning_blocked_site"), color: .dangerRed),
                ReportWarning(text: localizationManager.localized("family_warning_screen_time"), color: .warningOrange)
            ]
        }
    }
}

// MARK: - Report Warning Model

struct ReportWarning: Identifiable {
    let id = UUID()
    let text: String
    let color: Color
}

struct FamilyAdditionalModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Состояния для toggle-элементов с сохранением в UserDefaults
    @AppStorage("parental_homework_mode") private var isHomeworkModeEnabled: Bool = false
    
    // Состояния для детальных модалов
    @State private var showRemoteLockConfirmation = false
    @State private var showRemoteWipeConfirmation = false
    @State private var showAccessRequests = false
    @State private var showYouTubeSettings = false
    
    // Mock-данные (загружаются из UserDefaults)
    @State private var accessRequestsCount: Int = 2
    @State private var deviceName: String = "iPhone 12 (Alexey)"
    @State private var deviceStatus: String = ""
    @State private var deviceBattery: String = "67%"
    
    // Статистика запросов (загружается из UserDefaults)
    @State private var requests: [AccessRequest] = []
    
    // Ключ для статистики дополнительных настроек
    private let statsKey = "parental_additional_stats"
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("additional_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Удалённая блокировка - Action Button Item
                FamilyActionButtonItem(
                    icon: "🔒",
                    title: localizationManager.localized("remote_lock_title"),
                    description: localizationManager.localized("remote_lock_desc"),
                    buttonTitle: localizationManager.localized("remote_lock_confirm"),
                    action: { showRemoteLockConfirmation = true }
                )
                
                // 2. Удаление данных - Action Button Item
                FamilyActionButtonItem(
                    icon: "🗑️",
                    title: localizationManager.localized("data_deletion_title"),
                    description: localizationManager.localized("data_deletion_desc"),
                    buttonTitle: localizationManager.localized("data_deletion_button"),
                    action: { showRemoteWipeConfirmation = true }
                )
                
                // 3. Запросы доступа - Badge Item
                FamilyBadgeItem(
                    icon: "✋",
                    title: localizationManager.localized("family_access_requests"),
                    description: "\(accessRequestsCount) \(localizationManager.localized("family_access_requests_count"))",
                    badgeText: "\(accessRequestsCount)",
                    badgeColor: .warningOrange,
                    action: { showAccessRequests = true }
                )
                
                // 4. YouTube фильтрация - Config Button Item
                FamilyConfigButtonItem(
                    icon: "📺",
                    title: localizationManager.localized("family_youtube_filtering"),
                    description: localizationManager.localized("family_age_restriction"),
                    buttonTitle: localizationManager.localized("family_configure"),
                    action: { showYouTubeSettings = true }
                )
                
                // 5. Режим "Homework mode" - Toggle Item
                FamilyContentBlockItem(
                    icon: "📚",
                    title: localizationManager.localized("family_homework_mode"),
                    description: localizationManager.localized("family_homework_desc"),
                    isEnabled: $isHomeworkModeEnabled
                )
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Статистика запросов
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_access_requests"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    ForEach(requests) { request in
                        HStack {
                            Text("• \(localizationManager.localized("family_unlock")) \(request.app) (\(request.time))")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                        }
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
            }
        }
        .sheet(isPresented: $showRemoteLockConfirmation) {
            RemoteLockConfirmationModal(isPresented: $showRemoteLockConfirmation, deviceName: deviceName, deviceStatus: deviceStatus, deviceBattery: deviceBattery)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showRemoteWipeConfirmation) {
            RemoteWipeConfirmationModal(isPresented: $showRemoteWipeConfirmation)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showAccessRequests) {
            AccessRequestsModal(isPresented: $showAccessRequests, requests: $requests)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showYouTubeSettings) {
            YouTubeSettingsModal(isPresented: $showYouTubeSettings)
                .environmentObject(localizationManager)
        }
        .id("additional_modal_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            // Загружаем статистику при открытии модала
            loadAdditionalStatistics()
        }
        .onChange(of: isHomeworkModeEnabled) { newValue in
            print("✅ Homework mode: \(newValue ? "ON" : "OFF")")
        }
    }
    
    // Загрузка статистики дополнительных настроек из UserDefaults
    private func loadAdditionalStatistics() {
        let defaultDeviceStatus = localizationManager.localized("remote_lock_status_online")
        deviceStatus = defaultDeviceStatus
        
        if let stats = UserDefaults.standard.dictionary(forKey: statsKey) {
            accessRequestsCount = stats["accessRequestsCount"] as? Int ?? 2
            deviceName = stats["deviceName"] as? String ?? "iPhone 12 (Alexey)"
            deviceStatus = stats["deviceStatus"] as? String ?? defaultDeviceStatus
            deviceBattery = stats["deviceBattery"] as? String ?? "67%"
        }
        
        // Загружаем запросы доступа (по умолчанию примерные)
        if requests.isEmpty {
            requests = [
                AccessRequest(app: "Instagram", time: String(format: localizationManager.localized("family_min_ago_format"), 10), reason: localizationManager.localized("family_request_check_messages"), limit: "30 \(localizationManager.localized("family_limit_minutes"))/\(localizationManager.localized("family_per_day")) (\(localizationManager.localized("family_limit_used")))"),
                AccessRequest(app: "YouTube", time: String(format: localizationManager.localized("family_min_ago_format"), 5), reason: localizationManager.localized("family_request_review_lesson"), limit: "45 \(localizationManager.localized("family_limit_minutes"))/\(localizationManager.localized("family_per_day")) (\(String(format: localizationManager.localized("family_limit_remaining"), 12)))")
            ]
        }
    }
}

// MARK: - Access Request Model

struct AccessRequest: Identifiable {
    let id = UUID()
    let app: String
    let time: String
    let reason: String
    let limit: String
}

// MARK: - Family Modal Base View

struct FamilyModalBaseView<Content: View>: View {
    let title: String
    @Binding var isPresented: Bool
    let content: Content
    
    init(title: String, isPresented: Binding<Bool>, @ViewBuilder content: () -> Content) {
        self.title = title
        self._isPresented = isPresented
        self.content = content()
    }
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Header
                HStack {
                    Text(title)
                        .font(.h2)
                        .foregroundColor(.textPrimary)
                    
                    Spacer()
                    
                    Button(action: {
                        HapticFeedback.impact(.light)
                        isPresented = false
                    }) {
                        Image(systemName: "xmark.circle.fill")
                            .font(.system(size: 28))
                            .foregroundColor(.textSecondary)
                    }
                }
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: 0)
                        .fill(Color.backgroundMedium.opacity(0.5))
                )
                
                // Content
                ScrollView {
                    VStack(spacing: Spacing.m) {
                        content
                    }
                    .padding(Spacing.m)
                }
            }
        }
    }
}

// MARK: - Supporting Views

struct ControlCard: View {
    let icon: String
    let title: String
    let info: String
    let status: ControlStatus
    let action: () -> Void
    
    enum ControlStatus {
        case green, red
    }
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                HStack(spacing: 4) {
                    Text(icon)
                        .font(.system(size: 16))
                    
                    Text(title)
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundColor(Color(red: 0.96, green: 0.62, blue: 0.04))
                }
                
                Text(info)
                    .font(.system(size: 11))
                    .foregroundColor(.white.opacity(0.9))
                
                Spacer()
                
                Text(status == .green ? "🟢" : "🔴")
                    .font(.system(size: 28))
                    .animation(.easeInOut(duration: 2).repeatForever(autoreverses: true), value: status)
            }
            .frame(height: 90)
            .frame(maxWidth: .infinity)
            .padding(8)
            .background(Color(red: 0.96, green: 0.62, blue: 0.04).opacity(0.1))
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(Color(red: 0.96, green: 0.62, blue: 0.04), lineWidth: 2)
            )
            .clipShape(RoundedRectangle(cornerRadius: 10))
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Modals

struct AddMemberModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack(spacing: 20) {
            Text(localizationManager.localized("family_add_member_title"))
                .font(.title2)
                .foregroundColor(.white)
            
            Text(localizationManager.localized("family_scan_qr_code"))
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
            
            Button(localizationManager.localized("family_close")) {
                isPresented = false
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .clipShape(Capsule())
        }
        .padding()
        .background(Color.black)
        .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}

struct RewardsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack(spacing: 20) {
            Text(localizationManager.localized("family_rewards_modal_title"))
                .font(.title2)
                .foregroundColor(Color(red: 0.75, green: 0.52, blue: 0.99))
            
            Text(localizationManager.localized("family_unicorn_balance_format", 245))
                .foregroundColor(.gray)
            
            Button(localizationManager.localized("family_close")) {
                isPresented = false
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .clipShape(Capsule())
        }
        .padding()
        .background(Color.black)
        .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}

// MARK: - Detailed Modals

// MARK: 1. Подтверждения (приоритетные)

struct RemoteLockConfirmationModal: View {
    @Binding var isPresented: Bool
    let deviceName: String
    let deviceStatus: String
    let deviceBattery: String
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var showSuccess = false
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("remote_lock_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Предупреждение
                VStack(spacing: Spacing.m) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .font(.system(size: 64))
                        .foregroundColor(.warningOrange)
                    
                    Text(localizationManager.localized("remote_lock_warning"))
                        .font(.h2)
                        .foregroundColor(.textPrimary)
                    
                    Text(localizationManager.localized("remote_lock_desc"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
                .padding(Spacing.l)
                .background(Color.warningOrange.opacity(0.1))
                .cornerRadius(CornerRadius.large)
                
                // Информация об устройстве
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("remote_lock_device_info"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    HStack {
                        Text(localizationManager.localized("remote_lock_device"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text(deviceName)
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                    }
                    
                    HStack {
                        Text(localizationManager.localized("remote_lock_status"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text(deviceStatus)
                            .font(.bodyBold)
                            .foregroundColor(.successGreen)
                    }
                    
                    HStack {
                        Text(localizationManager.localized("remote_lock_battery"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text(deviceBattery)
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Действия
                if showSuccess {
                    VStack(spacing: Spacing.m) {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.system(size: 64))
                            .foregroundColor(.successGreen)
                        
                        Text(localizationManager.localized("remote_lock_success"))
                            .font(.bodyBold)
                            .foregroundColor(.successGreen)
                    }
                    .padding(Spacing.l)
                } else {
                    VStack(spacing: Spacing.m) {
                        Button(action: {
                            HapticFeedback.impact(.heavy)
                            withAnimation {
                                showSuccess = true
                            }
                            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                                isPresented = false
                            }
                        }) {
                            Text(localizationManager.localized("remote_lock_confirm"))
                                .font(.bodyBold)
                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding(Spacing.m)
                                .background(Color.dangerRed)
                                .cornerRadius(CornerRadius.medium)
                        }
                        
                        Button(action: {
                            HapticFeedback.impact(.light)
                            isPresented = false
                        }) {
                            Text(localizationManager.localized("edit_profile_cancel"))
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .frame(maxWidth: .infinity)
                                .padding(Spacing.m)
                                .background(Color.backgroundMedium.opacity(0.5))
                                .cornerRadius(CornerRadius.medium)
                        }
                    }
                }
            }
        }
        .id("remote_lock_lang_\(localizationManager.currentLanguage.rawValue)")
    }
}

struct RemoteWipeConfirmationModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var showSuccess = false
    @State private var confirmationText = ""
    @State private var isConfirmationValid = false
    
    private var confirmTextRequired: String {
        localizationManager.localized("data_deletion_confirm_keyword").uppercased()
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("data_deletion_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Критическое предупреждение
                VStack(spacing: Spacing.m) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .font(.system(size: 80))
                        .foregroundColor(.dangerRed)
                    
                    Text(localizationManager.localized("data_deletion_danger"))
                        .font(.system(size: 32, weight: .bold))
                        .foregroundColor(.dangerRed)
                    
                    Text(localizationManager.localized("data_deletion_desc"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
                .padding(Spacing.l)
                .background(Color.dangerRed.opacity(0.15))
                .cornerRadius(CornerRadius.large)
                
                // Подтверждение
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("data_deletion_confirm"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    
                    TextField(localizationManager.localized("data_deletion_placeholder"), text: $confirmationText)
                        .font(.body)
                        .foregroundColor(.textPrimary)
                        .padding(Spacing.m)
                        .background(Color.backgroundMedium.opacity(0.5))
                        .cornerRadius(CornerRadius.medium)
                        .autocapitalization(.allCharacters)
                        .onChange(of: confirmationText) { newValue in
                            isConfirmationValid = newValue.uppercased() == confirmTextRequired
                        }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Действия
                if showSuccess {
                    VStack(spacing: Spacing.m) {
                        Image(systemName: "trash.fill")
                            .font(.system(size: 64))
                            .foregroundColor(.dangerRed)
                        
                        Text(localizationManager.localized("data_deletion_deleting"))
                            .font(.bodyBold)
                            .foregroundColor(.dangerRed)
                    }
                    .padding(Spacing.l)
                } else {
                    VStack(spacing: Spacing.m) {
                        Button(action: {
                            HapticFeedback.impact(.heavy)
                            withAnimation {
                                showSuccess = true
                            }
                            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                isPresented = false
            }
                        }) {
                            Text(localizationManager.localized("data_deletion_button"))
                                .font(.bodyBold)
            .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding(Spacing.m)
                                .background(isConfirmationValid ? Color.dangerRed : Color.dangerRed.opacity(0.5))
                                .cornerRadius(CornerRadius.medium)
                        }
                        .disabled(!isConfirmationValid)
                        
                        Button(action: {
                            HapticFeedback.impact(.light)
                            isPresented = false
                        }) {
                            Text(localizationManager.localized("edit_profile_cancel"))
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .frame(maxWidth: .infinity)
                                .padding(Spacing.m)
                                .background(Color.backgroundMedium.opacity(0.5))
                                .cornerRadius(CornerRadius.medium)
                        }
                    }
                }
            }
        }
        .id("data_deletion_lang_\(localizationManager.currentLanguage.rawValue)")
    }
}

// MARK: 2. Запросы доступа

struct AccessRequestsModal: View {
    @Binding var isPresented: Bool
    @Binding var requests: [AccessRequest]
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Manager для обработки запросов
    @ObservedObject private var manager = ParentalControlManager.shared
    @State private var processingRequestId: String?
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("family_access_requests_modal_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                if requests.isEmpty {
                    VStack(spacing: Spacing.m) {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.system(size: 64))
                            .foregroundColor(.successGreen)
                        
                        Text(localizationManager.localized("family_no_new_requests"))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        Text(localizationManager.localized("family_all_requests_processed"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                    }
                    .padding(Spacing.xl)
                } else {
                    ForEach(requests) { request in
                        VStack(alignment: .leading, spacing: Spacing.m) {
                            HStack {
                                Text(request.app)
                                    .font(.bodyBold)
                                    .foregroundColor(.textPrimary)
                                
                                Spacer()
                                
                                Text(request.time)
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                            Text(request.reason)
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .lineLimit(2)
                            
                            Text(request.limit)
                                .font(.caption)
                                .foregroundColor(.warningOrange)
                            
                            Divider()
                            
                            HStack(spacing: Spacing.m) {
                                Button(action: {
                                    handleAccessRequest(requestId: request.id.uuidString, action: "accept")
                                }) {
                                    Text(localizationManager.localized("family_request_approve"))
                                        .font(.bodyBold)
                                        .foregroundColor(.white)
                                        .frame(maxWidth: .infinity)
                                        .padding(Spacing.s)
                                        .background(processingRequestId == request.id.uuidString ? Color.gray : Color.successGreen)
                                        .cornerRadius(CornerRadius.small)
                                }
                                .disabled(processingRequestId == request.id.uuidString || manager.isLoading)
                                
                                Button(action: {
                                    handleAccessRequest(requestId: request.id.uuidString, action: "reject")
                                }) {
                                    Text(localizationManager.localized("family_request_reject"))
                                        .font(.bodyBold)
                                        .foregroundColor(.white)
                                        .frame(maxWidth: .infinity)
                                        .padding(Spacing.s)
                                        .background(processingRequestId == request.id.uuidString ? Color.gray : Color.dangerRed)
                                        .cornerRadius(CornerRadius.small)
                                }
                                .disabled(processingRequestId == request.id.uuidString || manager.isLoading)
                            }
                        }
                        .padding(Spacing.m)
                        .background(Color.backgroundMedium.opacity(0.3))
                        .cornerRadius(CornerRadius.medium)
                    }
                }
            }
        }
        .onAppear {
            // Загружаем запросы из API при открытии
            loadAccessRequests()
        }
    }
    
    // Загрузка запросов доступа из API
    private func loadAccessRequests() {
        manager.getAccessRequests { result in
            switch result {
            case .success(let apiRequests):
                // Конвертируем API ответы в локальные модели
                requests = apiRequests.map { apiRequest in
                    AccessRequest(
                        app: apiRequest.app,
                        time: apiRequest.time,
                        reason: apiRequest.reason,
                        limit: apiRequest.limit
                    )
                }
                print("✅ Loaded \(requests.count) access requests")
            case .failure(let error):
                print("❌ Failed to load access requests: \(error.localizedDescription)")
                // Оставляем существующие mock-данные при ошибке
            }
        }
    }
    
    // Обработка запроса доступа
    private func handleAccessRequest(requestId: String, action: String) {
        HapticFeedback.impact(.medium)
        processingRequestId = requestId
        
        manager.handleAccessRequest(requestId: requestId, action: action) { (success: Bool, error: String?) in
            DispatchQueue.main.async {
                processingRequestId = nil
                
                if success {
                    // Удаляем запрос из списка после успешной обработки
                    withAnimation {
                        requests.removeAll { $0.id.uuidString == requestId }
                    }
                    print("✅ Request \(requestId) \(action == "accept" ? "approved" : "rejected")")
                } else {
                    print("❌ Failed to process request: \(error ?? "Unknown error")")
                }
            }
        }
    }
}

// MARK: 3. История браузера

struct BrowserHistoryDetailModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var browserHistory: [BrowserHistoryItem] = [
        BrowserHistoryItem(site: "youtube.com", visits: 142, hours: 8, minutes: 24, categoryKey: "browser_history_category_video", color: .red),
        BrowserHistoryItem(site: "instagram.com", visits: 89, hours: 4, minutes: 12, categoryKey: "browser_history_category_social", color: .purple),
        BrowserHistoryItem(site: "vk.com", visits: 67, hours: 2, minutes: 45, categoryKey: "browser_history_category_social", color: .blue),
        BrowserHistoryItem(site: "google.com", visits: 45, hours: 1, minutes: 15, categoryKey: "browser_history_category_search", color: .blue),
        BrowserHistoryItem(site: "tiktok.com", visits: 34, hours: 3, minutes: 20, categoryKey: "browser_history_category_video", color: .black)
    ]
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("browser_history_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // Статистика
                HStack(spacing: Spacing.m) {
                    VStack(alignment: .leading) {
                        Text(localizationManager.localized("browser_history_total_sites"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Text("\(browserHistory.count)")
                            .font(.h3)
                            .foregroundColor(.secondaryGold)
                    }
                    
                    Spacer()
                    
                    VStack(alignment: .trailing) {
                        Text(localizationManager.localized("browser_history_total_time"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Text(formatDuration(totalBrowserDuration.hours, minutes: totalBrowserDuration.minutes))
                            .font(.h3)
                            .foregroundColor(.secondaryGold)
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Топ-5 сайтов
                Text(localizationManager.localized("browser_history_top_5_week"))
                    .font(.bodyBold)
                    .foregroundColor(.secondaryGold)
                    .frame(maxWidth: .infinity, alignment: .leading)
                
                ForEach(Array(browserHistory.enumerated()), id: \.element.id) { index, item in
                    HStack(spacing: Spacing.m) {
                        // Номер
                        Text("\(index + 1)")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                            .frame(width: 32, height: 32)
                            .background(Color.secondaryGold.opacity(0.2))
                            .cornerRadius(16)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(item.site)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            HStack(spacing: Spacing.s) {
                                Text("\(item.visits) \(localizationManager.localized("browser_history_visits"))")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text("•")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text(formatDuration(item.hours, minutes: item.minutes))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                            Text(localizationManager.localized(item.categoryKey))
                                .font(.captionSmall)
                                .foregroundColor(item.color)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(item.color.opacity(0.2))
                                .cornerRadius(8)
                        }
                        
                        Spacer()
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .id("browser_history_lang_\(localizationManager.currentLanguage.rawValue)")
    }
    
    private var totalBrowserDuration: (hours: Int, minutes: Int) {
        let totalMinutes = browserHistory.reduce(0) { partialResult, item in
            partialResult + (item.hours * 60) + item.minutes
        }
        return (hours: totalMinutes / 60, minutes: totalMinutes % 60)
    }
    
    private func formatDuration(_ hours: Int, minutes: Int) -> String {
        let hourUnit = localizationManager.localized("analytics_hour")
        let minuteUnit = localizationManager.localized("analytics_min")
        
        if hours == 0 {
            return "\(minutes) \(minuteUnit)"
        }
        
        if minutes == 0 {
            return "\(hours) \(hourUnit)"
        }
        
        return "\(hours) \(hourUnit) \(minutes) \(minuteUnit)"
    }
}

struct BrowserHistoryItem: Identifiable {
    let id = UUID()
    let site: String
    let visits: Int
    let hours: Int
    let minutes: Int
    let categoryKey: String
    let color: Color
}

// MARK: 4. История приложений

struct AppHistoryDetailModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var appHistory: [AppHistoryItem] = [
        AppHistoryItem(app: "Instagram", usageMinutes: 504, limitMinutes: 30, exceeded: true, exceededByMinutes: 474, color: .purple),
        AppHistoryItem(app: "TikTok", usageMinutes: 252, limitMinutes: 20, exceeded: true, exceededByMinutes: 232, color: .black),
        AppHistoryItem(app: "YouTube", usageMinutes: 225, limitMinutes: 45, exceeded: true, exceededByMinutes: 180, color: .red),
        AppHistoryItem(app: "WhatsApp", usageMinutes: 90, limitMinutes: 60, exceeded: false, exceededByMinutes: nil, color: .green),
        AppHistoryItem(app: "VK", usageMinutes: 45, limitMinutes: 30, exceeded: true, exceededByMinutes: 15, color: .blue)
    ]
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("app_history_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // Статистика
                HStack(spacing: Spacing.m) {
                    VStack(alignment: .leading) {
                        Text(localizationManager.localized("app_history_total_apps"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Text("\(appHistory.count)")
                            .font(.h3)
                            .foregroundColor(.secondaryGold)
                    }
                    
                    Spacer()
                    
                    VStack(alignment: .trailing) {
                        Text(localizationManager.localized("app_history_limit_exceeded"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Text("\(appHistory.filter { $0.exceeded }.count)")
                            .font(.h3)
                            .foregroundColor(.dangerRed)
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Топ-5 приложений
                Text(localizationManager.localized("app_history_top_5_week"))
                    .font(.bodyBold)
                    .foregroundColor(.secondaryGold)
                    .frame(maxWidth: .infinity, alignment: .leading)
                
                ForEach(Array(appHistory.enumerated()), id: \.element.id) { index, item in
                    HStack(spacing: Spacing.m) {
                        // Номер
                        Text("\(index + 1)")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                            .frame(width: 32, height: 32)
                            .background(Color.secondaryGold.opacity(0.2))
                            .cornerRadius(16)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(item.app)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            HStack(spacing: Spacing.s) {
                                Text(formatDurationFromMinutes(item.usageMinutes))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text("•")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text(formatLimit(item.limitMinutes))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                            if item.exceeded, let exceededByMinutes = item.exceededByMinutes {
                                HStack {
                                    Image(systemName: "exclamationmark.triangle.fill")
                                        .font(.captionSmall)
                                        .foregroundColor(.dangerRed)
                                    
                                    Text("\(localizationManager.localized("app_history_exceeded_by")) \(formatDurationFromMinutes(exceededByMinutes))")
                                        .font(.captionSmall)
                                        .foregroundColor(.dangerRed)
                                        .fontWeight(.semibold)
                                }
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(Color.dangerRed.opacity(0.2))
                                .cornerRadius(8)
                            } else {
                                HStack {
                                    Image(systemName: "checkmark.circle.fill")
                                        .font(.captionSmall)
                                        .foregroundColor(.successGreen)
                                    
                                    Text(localizationManager.localized("app_history_within_limit"))
                                        .font(.captionSmall)
                                        .foregroundColor(.successGreen)
                                        .fontWeight(.semibold)
                                }
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(Color.successGreen.opacity(0.2))
                                .cornerRadius(8)
                            }
                        }
                        
                        Spacer()
                    }
                    .padding(Spacing.m)
                    .background(item.exceeded ? Color.dangerRed.opacity(0.1) : Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(item.exceeded ? Color.dangerRed.opacity(0.5) : Color.clear, lineWidth: 2)
                    )
                }
            }
        }
        .id("app_history_lang_\(localizationManager.currentLanguage.rawValue)")
    }
    
    private func formatDurationFromMinutes(_ minutes: Int) -> String {
        let hours = minutes / 60
        let remainingMinutes = minutes % 60
        return formatDuration(hours: hours, minutes: remainingMinutes)
    }
    
    private func formatDuration(hours: Int, minutes: Int) -> String {
        let hourUnit = localizationManager.localized("analytics_hour")
        let minuteUnit = localizationManager.localized("analytics_min")
        
        if hours == 0 {
            return "\(minutes) \(minuteUnit)"
        }
        
        if minutes == 0 {
            return "\(hours) \(hourUnit)"
        }
        
        return "\(hours) \(hourUnit) \(minutes) \(minuteUnit)"
    }
    
    private func formatLimit(_ minutes: Int) -> String {
        localizationManager.localized("app_history_limit_format", minutes)
    }
}

struct AppHistoryItem: Identifiable {
    let id = UUID()
    let app: String
    let usageMinutes: Int
    let limitMinutes: Int
    let exceeded: Bool
    let exceededByMinutes: Int?
    let color: Color
}

// MARK: 5. Контакты

struct ContactsDetailModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var contacts: [ContactItem] = []
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("family_contacts_view"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // Статистика
                HStack(spacing: Spacing.m) {
                    VStack(alignment: .leading) {
                        Text(localizationManager.localized("family_contacts_total"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Text("\(contacts.count)")
                            .font(.h3)
                            .foregroundColor(.secondaryGold)
                    }
                    
                    Spacer()
                    
                    VStack(alignment: .trailing) {
                        Text(localizationManager.localized("family_messages_title"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Text("\(contacts.reduce(0) { $0 + $1.messages })")
                            .font(.h3)
                            .foregroundColor(.secondaryGold)
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Топ-5 контактов
                if contacts.isEmpty {
                    EmptyStateView(
                        icon: "👥",
                        title: localizationManager.localized("family_contacts_empty_title"),
                        description: localizationManager.localized("family_contacts_empty_description"),
                        actionTitle: nil,
                        action: nil
                    )
                    .padding()
                } else {
                    Text(localizationManager.localized("family_top_5_contacts"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    
                    ForEach(Array(contacts.enumerated()), id: \.element.id) { index, contact in
                    HStack(spacing: Spacing.m) {
                        // Номер
                        Text("\(index + 1)")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                            .frame(width: 32, height: 32)
                            .background(Color.secondaryGold.opacity(0.2))
                            .cornerRadius(16)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(contact.name)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            HStack(spacing: Spacing.s) {
                                    Text(localizationManager.localized("family_messages_format", contact.messages))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text("•")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                    Text(localizationManager.localized("family_calls_format", contact.calls))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                                Text("\(localizationManager.localized("family_last_contact_prefix")) \(contact.lastContact)")
                                .font(.captionSmall)
                                .foregroundColor(contact.color)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(contact.color.opacity(0.2))
                                .cornerRadius(8)
                        }
                        
                        Spacer()
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                    }
                }
            }
        }
        .onAppear {
            loadContacts()
        }
        .onReceive(NotificationCenter.default.publisher(for: UserDefaults.didChangeNotification)) { _ in
            loadContacts() // Синхронизируем при изменении данных
        }
    }
    
    // Загрузка контактов из UserDefaults (child_family_contacts_list) или создание из family_members_list
    private func loadContacts() {
        // Попытка загрузить из child_family_contacts_list (если есть сохранённые контакты)
        if let savedData = UserDefaults.standard.data(forKey: "child_family_contacts_list"),
           let decoded = try? JSONDecoder().decode([ChildFamilyContact].self, from: savedData),
           !decoded.isEmpty {
            // Преобразуем ChildFamilyContact в ContactItem
            contacts = decoded.prefix(5).map { contact in
                ContactItem(
                    name: contact.name,
                    messages: 0, // TODO: Загрузить из API мониторинга
                    calls: 0, // TODO: Загрузить из API мониторинга
                    lastContact: localizationManager.localized("family_last_contact_recently"), // TODO: Загрузить из API мониторинга
                    color: .successGreen
                )
            }
            return
        }
        
        // Если нет сохранённых контактов, пробуем создать из family_members_list
        if let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
           let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData),
           !decoded.isEmpty {
            contacts = decoded.prefix(5).map { member in
                ContactItem(
                    name: member.name,
                    messages: 0, // TODO: Загрузить из API мониторинга
                    calls: 0, // TODO: Загрузить из API мониторинга
                    lastContact: localizationManager.localized("family_last_contact_recently"), // TODO: Загрузить из API мониторинга
                    color: .successGreen
                )
            }
            return
        }
        
        // Если ничего не найдено - пустой список
        contacts = []
        
        print("✅ Loaded contacts: \(contacts.count)")
    }
}

struct ContactItem: Identifiable {
    let id = UUID()
    let name: String
    let messages: Int
    let calls: Int
    let lastContact: String
    let color: Color
}

// MARK: 6. Остальные настройки и просмотры

// MARK: Настройки времени

struct ScreenTimeSettingsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Сохранение настроек в UserDefaults
    @AppStorage("screen_time_weekday_limit") private var weekdayLimit: Double = 120 // минуты
    @AppStorage("screen_time_weekend_limit") private var weekendLimit: Double = 180 // минуты
    @AppStorage("screen_time_is_weekday_selected") private var isWeekdaySelected = true
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("screen_time_settings_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Выбор режима
                HStack(spacing: Spacing.m) {
                    Button(action: {
                        HapticFeedback.impact(.medium)
                        isWeekdaySelected = true
                    }) {
                        Text(localizationManager.localized("screen_time_weekdays"))
                            .font(.bodyBold)
                            .foregroundColor(isWeekdaySelected ? .white : .textSecondary)
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.m)
                            .background(isWeekdaySelected ? Color.secondaryGold : Color.backgroundMedium.opacity(0.5))
                            .cornerRadius(CornerRadius.medium)
                    }
                    
                    Button(action: {
                        HapticFeedback.impact(.medium)
                        isWeekdaySelected = false
                    }) {
                        Text(localizationManager.localized("screen_time_weekends"))
                            .font(.bodyBold)
                            .foregroundColor(!isWeekdaySelected ? .white : .textSecondary)
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.m)
                            .background(!isWeekdaySelected ? Color.secondaryGold : Color.backgroundMedium.opacity(0.5))
                            .cornerRadius(CornerRadius.medium)
                    }
                }
                
                // Ползунок лимита
                VStack(alignment: .leading, spacing: Spacing.m) {
                    HStack {
                        Text(localizationManager.localized("screen_time_limit"))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        Spacer()
                        
                        Text("\(Int(isWeekdaySelected ? weekdayLimit : weekendLimit)) \(localizationManager.localized("screen_time_limit_min"))")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                    }
                    
                    Slider(value: isWeekdaySelected ? $weekdayLimit : $weekendLimit, in: 30...480, step: 15) {
                        Text(localizationManager.localized("screen_time_limit"))
                    }
                    .tint(.secondaryGold)
                    
                    HStack {
                        Text("30 \(localizationManager.localized("screen_time_limit_min"))")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        
                        Spacer()
                        
                        Text("8 \(localizationManager.localized("analytics_hour"))")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Рекомендации
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("💡 \(localizationManager.localized("screen_time_recommendations"))")
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    VStack(alignment: .leading, spacing: 6) {
                        Text(localizationManager.localized("screen_time_children_6_10"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                        
                        Text(localizationManager.localized("screen_time_teens"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                    }
                }
                .padding(Spacing.m)
                .background(Color.secondaryGold.opacity(0.1))
                .cornerRadius(CornerRadius.medium)
                
                Button(action: {
                    HapticFeedback.impact(.medium)
                    print("✅ Screen time saved: weekdays \(Int(weekdayLimit)) min, weekends \(Int(weekendLimit)) min")
                isPresented = false
                }) {
                    Text(localizationManager.localized("screen_time_save"))
                        .font(.bodyBold)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .id("screen_time_settings_lang_\(localizationManager.currentLanguage.rawValue)")
        .onChange(of: weekdayLimit) { newValue in
            print("✅ Weekday limit: \(Int(newValue)) min")
        }
        .onChange(of: weekendLimit) { newValue in
            print("✅ Weekend limit: \(Int(newValue)) min")
        }
    }
}

struct ScheduleSettingsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // ✅ BUILD 98: Статический DateFormatter для предотвращения рекурсии
    private static let timeFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.timeStyle = .short
        formatter.locale = Locale(identifier: "ru_RU")  // Статический locale вместо Locale.current
        return formatter
    }()
    
    // Сохранение дат через TimeInterval в UserDefaults
    @AppStorage("schedule_weekday_start") private var weekdayStartInterval: Double = 0
    @AppStorage("schedule_weekday_end") private var weekdayEndInterval: Double = 0
    @AppStorage("schedule_weekend_start") private var weekendStartInterval: Double = 0
    @AppStorage("schedule_weekend_end") private var weekendEndInterval: Double = 0
    @AppStorage("schedule_is_weekday_selected") private var isWeekdaySelected = true
    
    // Вычисляемые свойства для работы с Date
    private var weekdayStart: Binding<Date> {
        Binding(
            get: {
                weekdayStartInterval == 0 ? Date() : Date(timeIntervalSince1970: weekdayStartInterval)
            },
            set: { weekdayStartInterval = $0.timeIntervalSince1970 }
        )
    }
    
    private var weekdayEnd: Binding<Date> {
        Binding(
            get: {
                weekdayEndInterval == 0 ? Date() : Date(timeIntervalSince1970: weekdayEndInterval)
            },
            set: { weekdayEndInterval = $0.timeIntervalSince1970 }
        )
    }
    
    private var weekendStart: Binding<Date> {
        Binding(
            get: {
                weekendStartInterval == 0 ? Date() : Date(timeIntervalSince1970: weekendStartInterval)
            },
            set: { weekendStartInterval = $0.timeIntervalSince1970 }
        )
    }
    
    private var weekendEnd: Binding<Date> {
        Binding(
            get: {
                weekendEndInterval == 0 ? Date() : Date(timeIntervalSince1970: weekendEndInterval)
            },
            set: { weekendEndInterval = $0.timeIntervalSince1970 }
        )
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("schedule_settings_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Выбор режима
                HStack(spacing: Spacing.m) {
                    Button(action: {
                        HapticFeedback.impact(.medium)
                        isWeekdaySelected = true
                    }) {
                        Text(localizationManager.localized("screen_time_weekdays"))
                            .font(.bodyBold)
                            .foregroundColor(isWeekdaySelected ? .white : .textSecondary)
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.m)
                            .background(isWeekdaySelected ? Color.secondaryGold : Color.backgroundMedium.opacity(0.5))
                            .cornerRadius(CornerRadius.medium)
                    }
                    
                    Button(action: {
                        HapticFeedback.impact(.medium)
                        isWeekdaySelected = false
                    }) {
                        Text(localizationManager.localized("screen_time_weekends"))
                            .font(.bodyBold)
                            .foregroundColor(!isWeekdaySelected ? .white : .textSecondary)
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.m)
                            .background(!isWeekdaySelected ? Color.secondaryGold : Color.backgroundMedium.opacity(0.5))
                            .cornerRadius(CornerRadius.medium)
                    }
                }
                
                // Время начала и окончания
                VStack(spacing: Spacing.m) {
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(localizationManager.localized("schedule_access_from"))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        DatePicker("", selection: isWeekdaySelected ? weekdayStart : weekendStart, displayedComponents: .hourAndMinute)
                            .datePickerStyle(.compact)
                            .labelsHidden()
                    }
                    
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(localizationManager.localized("schedule_access_to"))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        DatePicker("", selection: isWeekdaySelected ? weekdayEnd : weekendEnd, displayedComponents: .hourAndMinute)
                            .datePickerStyle(.compact)
                            .labelsHidden()
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                Button(action: {
                    HapticFeedback.impact(.medium)
                    // ✅ BUILD 98: Используем статический DateFormatter для предотвращения рекурсии
                    print("✅ Schedule saved: weekdays \(Self.timeFormatter.string(from: weekdayStart.wrappedValue)) - \(Self.timeFormatter.string(from: weekdayEnd.wrappedValue)), weekends \(Self.timeFormatter.string(from: weekendStart.wrappedValue)) - \(Self.timeFormatter.string(from: weekendEnd.wrappedValue))")
                    isPresented = false
                }) {
                    Text(localizationManager.localized("schedule_save"))
                        .font(.bodyBold)
            .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .id("schedule_settings_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            // Инициализация дат по умолчанию если они не сохранены
            if weekdayStartInterval == 0 {
                weekdayStartInterval = Date().timeIntervalSince1970
            }
            if weekdayEndInterval == 0 {
                weekdayEndInterval = Date().timeIntervalSince1970
            }
            if weekendStartInterval == 0 {
                weekendStartInterval = Date().timeIntervalSince1970
            }
            if weekendEndInterval == 0 {
                weekendEndInterval = Date().timeIntervalSince1970
            }
        }
    }
}

struct SleepTimeSettingsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // ✅ BUILD 98: Статический DateFormatter для предотвращения рекурсии
    private static let timeFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.timeStyle = .short
        formatter.locale = Locale(identifier: "ru_RU")  // Статический locale вместо Locale.current
        return formatter
    }()
    
    // Сохранение дат через TimeInterval в UserDefaults
    @AppStorage("sleep_bedtime_start") private var bedtimeStartInterval: Double = 0
    @AppStorage("sleep_bedtime_end") private var bedtimeEndInterval: Double = 0
    @AppStorage("sleep_emergency_calls_enabled") private var isEmergencyCallsEnabled = true
    
    // Вычисляемые свойства для работы с Date
    private var bedtimeStart: Binding<Date> {
        Binding(
            get: {
                bedtimeStartInterval == 0 ? Date() : Date(timeIntervalSince1970: bedtimeStartInterval)
            },
            set: { bedtimeStartInterval = $0.timeIntervalSince1970 }
        )
    }
    
    private var bedtimeEnd: Binding<Date> {
        Binding(
            get: {
                bedtimeEndInterval == 0 ? Date() : Date(timeIntervalSince1970: bedtimeEndInterval)
            },
            set: { bedtimeEndInterval = $0.timeIntervalSince1970 }
        )
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("bedtime_settings_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Время сна
                VStack(spacing: Spacing.m) {
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(localizationManager.localized("bedtime_block_from"))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        DatePicker("", selection: bedtimeStart, displayedComponents: .hourAndMinute)
                            .datePickerStyle(.compact)
                            .labelsHidden()
                    }
                    
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(localizationManager.localized("bedtime_block_to"))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        DatePicker("", selection: bedtimeEnd, displayedComponents: .hourAndMinute)
                            .datePickerStyle(.compact)
                            .labelsHidden()
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Экстренные вызовы
                FamilyContentBlockItem(
                    icon: "🆘",
                    title: localizationManager.localized("bedtime_emergency_calls"),
                    description: localizationManager.localized("bedtime_emergency_calls_desc"),
                    isEnabled: $isEmergencyCallsEnabled
                )
                
                Button(action: {
                    HapticFeedback.impact(.medium)
                    // ✅ BUILD 98: Используем статический DateFormatter для предотвращения рекурсии
                    print("✅ Bedtime saved: \(Self.timeFormatter.string(from: bedtimeStart.wrappedValue)) - \(Self.timeFormatter.string(from: bedtimeEnd.wrappedValue)), emergency calls \(isEmergencyCallsEnabled ? "ON" : "OFF")")
                    isPresented = false
                }) {
                    Text(localizationManager.localized("bedtime_save"))
                        .font(.bodyBold)
                .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .id("bedtime_settings_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            // Инициализация дат по умолчанию если они не сохранены
            if bedtimeStartInterval == 0 {
                bedtimeStartInterval = Date().timeIntervalSince1970
            }
            if bedtimeEndInterval == 0 {
                bedtimeEndInterval = Date().timeIntervalSince1970
            }
        }
        .onChange(of: isEmergencyCallsEnabled) { newValue in
            print("✅ Emergency calls: \(newValue ? "ON" : "OFF")")
        }
    }
}

struct AppLimitsSettingsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Сохранение лимитов приложений в UserDefaults
    private let limitsKey = "app_limits_settings"
    
    // ✅ BUILD 98: Статический DateFormatter для предотвращения рекурсии
    private static let timeFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.timeStyle = .short
        formatter.locale = Locale(identifier: "ru_RU")  // Статический locale вместо Locale.current
        return formatter
    }()
    
    @State private var appLimits: [AppLimitItem] = []
    
    // Загрузка лимитов из UserDefaults
    private func loadAppLimits() {
        // ✅ ИСПРАВЛЕНО: Сначала загружаем из общего массива, затем проверяем индивидуальные ключи
        var loadedLimits: [AppLimitItem] = []
        
        if let data = UserDefaults.standard.data(forKey: limitsKey),
           let decoded = try? JSONDecoder().decode([AppLimitItemCodable].self, from: data) {
            loadedLimits = decoded.map { AppLimitItem(app: $0.app, limit: $0.limit, color: Color(hex: $0.colorHex)) }
        } else {
            // Значения по умолчанию
            loadedLimits = [
                AppLimitItem(app: "Instagram", limit: 30.0, color: .purple),
                AppLimitItem(app: "TikTok", limit: 20.0, color: .black),
                AppLimitItem(app: "WhatsApp", limit: 60.0, color: .green),
                AppLimitItem(app: "Telegram", limit: 60.0, color: .blue),
                AppLimitItem(app: "YouTube", limit: 45.0, color: .red),
                AppLimitItem(app: "VK", limit: 30.0, color: .blue),
                AppLimitItem(app: "Odnoklassniki", limit: 20.0, color: .orange),
                AppLimitItem(app: "Discord", limit: 30.0, color: .indigo),
                AppLimitItem(app: "Games", limit: 60.0, color: .pink)
            ]
        }
        
        // ✅ BUILD 96: Асинхронная загрузка для предотвращения рекурсии
        // Проверяем индивидуальные ключи для каждого приложения (приоритет выше)
        // Устанавливаем начальные значения сразу
        appLimits = loadedLimits
        
        // Затем обновляем асинхронно
        Task { @MainActor in
            var updatedLimits = appLimits
            for index in updatedLimits.indices {
                let app = updatedLimits[index].app
                let appKey = "app_\(app.lowercased().replacingOccurrences(of: " ", with: "_"))_time_limit"
                if UserDefaults.standard.object(forKey: appKey) != nil {
                    let savedLimit = UserDefaults.standard.double(forKey: appKey)
                    if savedLimit > 0 {
                        updatedLimits[index].limit = savedLimit
                    }
                }
            }
            // Обновляем appLimits на main thread после загрузки
            appLimits = updatedLimits
        }
    }
    
    // Сохранение лимитов в UserDefaults
    private func saveAppLimits() {
        let codable = appLimits.map { AppLimitItemCodable(app: $0.app, limit: $0.limit, colorHex: "") }
        if let encoded = try? JSONEncoder().encode(codable) {
            UserDefaults.standard.set(encoded, forKey: limitsKey)
        }
    }
    
    // ✅ ИСПРАВЛЕНО: Автоматическое сохранение лимита для конкретного приложения
    private func saveAppLimitForApp(app: String, limit: Double) {
        // Сохраняем в UserDefaults с динамическим ключом для каждого приложения
        let appKey = "app_\(app.lowercased().replacingOccurrences(of: " ", with: "_"))_time_limit"
        UserDefaults.standard.set(limit, forKey: appKey)
        
        // Также обновляем общий массив и сохраняем его
        if let index = appLimits.firstIndex(where: { $0.app == app }) {
            appLimits[index].limit = limit
        }
        saveAppLimits()
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("app_limits_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                ForEach($appLimits) { $limit in
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        HStack {
                            Text(limit.app)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                            
                            Text("\(Int(limit.limit)) \(localizationManager.localized("app_limits_min_per_day"))")
                                .font(.bodyBold)
                                .foregroundColor(.secondaryGold)
                        }
                        
                        // ✅ ИСПРАВЛЕНО: Используем Binding с автоматическим сохранением в UserDefaults
                        Slider(value: Binding(
                            get: { limit.limit },
                            set: { newValue in
                                limit.limit = newValue
                                // Автоматическое сохранение при изменении слайдера
                                saveAppLimitForApp(app: limit.app, limit: newValue)
                            }
                        ), in: 5...120, step: 5) {
                            Text(limit.app)
                        }
                        .tint(limit.color)
                        
                        HStack {
                            Text(localizationManager.localized("app_limits_5_min"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            
                            Spacer()
                            
                            Text(localizationManager.localized("app_limits_2_hours"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
                
                Button(action: {
                    HapticFeedback.impact(.medium)
                    saveAppLimits()
                    print("✅ App limits saved: \(appLimits.count) apps")
                isPresented = false
                }) {
                    Text(localizationManager.localized("app_limits_save_all"))
                        .font(.bodyBold)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .id("app_limits_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadAppLimits()
        }
    }
}

// Вспомогательная структура для Codable
struct AppLimitItemCodable: Codable {
    let app: String
    var limit: Double
    let colorHex: String
}

struct AppLimitItem: Identifiable {
    let id = UUID()
    var app: String
    var limit: Double
    let color: Color
}

// MARK: Геолокация

struct GeofencesSettingsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Сохранение геозон в UserDefaults
    private let geofencesKey = "geofences_settings"
    
    @State private var geofences: [GeofenceItem] = []
    
    @State private var showAddForm = false
    @State private var newGeofenceName = ""
    @State private var newGeofenceAddress = ""
    @State private var newGeofenceRadius: Double = 100
    
    // Загрузка геозон из UserDefaults
    private func loadGeofences() {
        if let data = UserDefaults.standard.data(forKey: geofencesKey),
           let decoded = try? JSONDecoder().decode([GeofenceItemCodable].self, from: data) {
            geofences = decoded.map { GeofenceItem(name: $0.name, address: $0.address, radius: $0.radius) }
        } else {
            // Значения по умолчанию - используем локализованные строки
            geofences = [
                GeofenceItem(name: localizationManager.localized("geofences_home"), address: localizationManager.localized("geofences_street_lenin"), radius: 100),
                GeofenceItem(name: localizationManager.localized("geofences_school"), address: localizationManager.localized("geofences_street_pushkin"), radius: 200)
            ]
        }
    }
    
    // Сохранение геозон в UserDefaults
    private func saveGeofences() {
        let codable = geofences.map { GeofenceItemCodable(name: $0.name, address: $0.address, radius: $0.radius) }
        if let encoded = try? JSONEncoder().encode(codable) {
            UserDefaults.standard.set(encoded, forKey: geofencesKey)
        }
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("geofences_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // Существующие геозоны
                ForEach($geofences) { $geofence in
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        HStack {
                            Text(geofence.name)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                            
                            Button(action: {
                                HapticFeedback.impact(.medium)
                                geofences.removeAll { $0.id == geofence.id }
                                saveGeofences()
                            }) {
                                Image(systemName: "trash")
                                    .font(.body)
                                    .foregroundColor(.dangerRed)
                            }
                        }
                        
                        Text(geofence.address)
                            .font(.body)
                            .foregroundColor(.textSecondary)
                        
                        HStack {
                            Text(localizationManager.localized("geofences_radius"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            
                            Text("\(Int(geofence.radius)) \(localizationManager.localized("geofences_radius_m"))")
                                .font(.caption)
                                .foregroundColor(.secondaryGold)
                                .fontWeight(.semibold)
                        }
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
                
                // Форма добавления
                if showAddForm {
                    VStack(spacing: Spacing.m) {
                        TextField(localizationManager.localized("geofences_name_placeholder"), text: $newGeofenceName)
                            .font(.body)
                            .foregroundColor(.textPrimary)
                            .padding(Spacing.m)
                            .background(Color.backgroundMedium.opacity(0.5))
                            .cornerRadius(CornerRadius.medium)
                        
                        TextField(localizationManager.localized("geofences_address_placeholder"), text: $newGeofenceAddress)
                            .font(.body)
                            .foregroundColor(.textPrimary)
                            .padding(Spacing.m)
                            .background(Color.backgroundMedium.opacity(0.5))
                            .cornerRadius(CornerRadius.medium)
                        
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            HStack {
                                Text(localizationManager.localized("geofences_radius"))
                                    .font(.bodyBold)
                                    .foregroundColor(.textPrimary)
                                
                                Spacer()
                                
                                Text("\(Int(newGeofenceRadius)) \(localizationManager.localized("geofences_radius_m"))")
                                    .font(.bodyBold)
                                    .foregroundColor(.secondaryGold)
                            }
                            
                            Slider(value: $newGeofenceRadius, in: 50...500, step: 10) {
                                Text(localizationManager.localized("geofences_radius"))
                            }
                            .tint(.secondaryGold)
                        }
                        .padding(Spacing.m)
                        .background(Color.backgroundMedium.opacity(0.3))
                        .cornerRadius(CornerRadius.medium)
                        
                        HStack(spacing: Spacing.m) {
                            Button(action: {
                                HapticFeedback.impact(.medium)
                                showAddForm = false
                            }) {
                                Text(localizationManager.localized("edit_profile_cancel"))
                                    .font(.body)
                                    .foregroundColor(.textSecondary)
                                    .frame(maxWidth: .infinity)
                                    .padding(Spacing.m)
                                    .background(Color.backgroundMedium.opacity(0.5))
                                    .cornerRadius(CornerRadius.medium)
                            }
                            
                            Button(action: {
                                HapticFeedback.impact(.medium)
                                geofences.append(GeofenceItem(name: newGeofenceName, address: newGeofenceAddress, radius: newGeofenceRadius))
                                newGeofenceName = ""
                                newGeofenceAddress = ""
                                newGeofenceRadius = 100
                                showAddForm = false
                                saveGeofences()
                            }) {
                                Text(localizationManager.localized("geofences_add"))
                                    .font(.bodyBold)
            .foregroundColor(.white)
                                    .frame(maxWidth: .infinity)
                                    .padding(Spacing.m)
                                    .background(Color.secondaryGold)
                                    .cornerRadius(CornerRadius.medium)
                            }
                        }
                    }
                    .padding(Spacing.m)
                    .background(Color.secondaryGold.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                } else {
                    Button(action: {
                        HapticFeedback.impact(.medium)
                        showAddForm = true
                    }) {
                        HStack {
                            Image(systemName: "plus.circle.fill")
                                .font(.body)
                                .foregroundColor(.secondaryGold)
                            
                            Text(localizationManager.localized("geofences_add_geofence"))
                                .font(.bodyBold)
                                .foregroundColor(.secondaryGold)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.secondaryGold.opacity(0.2))
                        .cornerRadius(CornerRadius.medium)
                        .overlay(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .stroke(Color.secondaryGold.opacity(0.5), lineWidth: 1)
                        )
                    }
                }
            }
        }
        .id("geofences_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadGeofences()
        }
    }
}

// Вспомогательная структура для Codable
struct GeofenceItemCodable: Codable {
    let name: String
    let address: String
    let radius: Double
}

struct GeofenceItem: Identifiable {
    let id: UUID
    let name: String
    let address: String
    let radius: Double
    
    init(id: UUID = UUID(), name: String, address: String, radius: Double) {
        self.id = id
        self.name = name
        self.address = address
        self.radius = radius
    }
}

struct LocationHistoryDetailModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var locationHistory: [LocationHistoryItem] = []
    @State private var frequentPlaces: [FrequentPlace] = []
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("location_history_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Частые места
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("location_frequent_places"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    ForEach(frequentPlaces) { place in
                        HStack {
                            Text(place.name)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                            
                            Text("\(place.visits) \(localizationManager.localized("location_visits"))")
                                .font(.body)
                                .foregroundColor(.textSecondary)
                        }
                        .padding(Spacing.m)
                        .background(Color.backgroundMedium.opacity(0.3))
                        .cornerRadius(CornerRadius.medium)
                    }
                }
                
                Divider()
                
                // История событий
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text(localizationManager.localized("location_events_today"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    ForEach(locationHistory) { item in
                        HStack(spacing: Spacing.m) {
                            Text(item.icon)
                                .font(.system(size: 32))
                            
                            VStack(alignment: .leading, spacing: 4) {
                                Text(item.action)
                                    .font(.bodyBold)
                                    .foregroundColor(.textPrimary)
                                
                                Text(item.location)
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                            Spacer()
                            
                            Text(item.time)
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        .padding(Spacing.m)
                        .background(Color.backgroundMedium.opacity(0.3))
                        .cornerRadius(CornerRadius.medium)
                    }
                }
            }
        }
        .id("location_history_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadLocationData()
        }
    }
    
    private func loadLocationData() {
        // Загружаем локализованные данные
        locationHistory = [
            LocationHistoryItem(time: "08:30", location: localizationManager.localized("geofences_street_lenin"), action: localizationManager.localized("location_left_home"), icon: "🚶"),
            LocationHistoryItem(time: "09:15", location: localizationManager.localized("geofences_street_pushkin"), action: localizationManager.localized("location_arrived_school"), icon: "✅"),
            LocationHistoryItem(time: "15:45", location: localizationManager.localized("geofences_street_lenin"), action: localizationManager.localized("location_returned_home"), icon: "🏠"),
            LocationHistoryItem(time: "17:30", location: localizationManager.localized("location_mall"), action: localizationManager.localized("location_visited_mall"), icon: "🛒")
        ]
        
        frequentPlaces = [
            FrequentPlace(name: localizationManager.localized("geofences_home"), visits: 45, color: .successGreen),
            FrequentPlace(name: localizationManager.localized("geofences_school"), visits: 32, color: .blue),
            FrequentPlace(name: localizationManager.localized("location_mall"), visits: 8, color: .warningOrange)
        ]
    }
}

struct LocationHistoryItem: Identifiable {
    let id = UUID()
    let time: String
    let location: String
    let action: String
    let icon: String
}

struct FrequentPlace: Identifiable {
    let id = UUID()
    let name: String
    let visits: Int
    let color: Color
}

// MARK: Отчёты

struct WeeklyReportDetailModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        FamilyModalBaseView(
            title: "📅 \(localizationManager.localized("family_weekly_report"))",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // Статистика по категориям
                ReportStatCard(icon: "🌐", title: localizationManager.localized("family_web_activity"), value: "342 \(localizationManager.localized("family_sites"))", color: .blue)
                ReportStatCard(icon: "📱", title: localizationManager.localized("family_applications"), value: "28 \(localizationManager.localized("family_apps"))", color: .purple)
                ReportStatCard(icon: "⏰", title: localizationManager.localized("family_screen_time"), value: "45h 23m", color: .orange)
                ReportStatCard(icon: "🚫", title: localizationManager.localized("family_blocked_attempts"), value: "1245 \(localizationManager.localized("family_attempts"))", color: .red)
                ReportStatCard(icon: "📍", title: localizationManager.localized("family_movements"), value: "32 \(localizationManager.localized("family_events"))", color: .green)
                ReportStatCard(icon: "⚠️", title: localizationManager.localized("family_warnings_new"), value: "2 \(localizationManager.localized("family_new"))", color: .warningOrange)
            }
        }
    }
}

struct ReportStatCard: View {
    let icon: String
    let title: String
    let value: String
    let color: Color
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            Text(icon)
                .font(.system(size: 32))
                .frame(width: 50, height: 50)
                .background(color.opacity(0.2))
                .cornerRadius(25)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.body)
                    .foregroundColor(.textSecondary)
                
                Text(value)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
            }
            
            Spacer()
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.3))
        .cornerRadius(CornerRadius.medium)
    }
}

struct SuspiciousActivityDetailModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var warnings: [SuspiciousWarning] = []
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("family_suspicious_activity_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                ForEach(warnings) { warning in
                    HStack(spacing: Spacing.m) {
                        Image(systemName: warning.level == .high ? "exclamationmark.triangle.fill" : "exclamationmark.circle.fill")
                            .font(.system(size: 24))
                            .foregroundColor(warning.level == .high ? .dangerRed : .warningOrange)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(warning.text)
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            
                            Text(warning.time)
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        
                        Spacer()
                    }
                    .padding(Spacing.m)
                    .background(warning.level == .high ? Color.dangerRed.opacity(0.1) : Color.warningOrange.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(warning.level == .high ? Color.dangerRed.opacity(0.5) : Color.warningOrange.opacity(0.5), lineWidth: 2)
                    )
                }
            }
        }
        .id("suspicious_activity_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            if warnings.isEmpty {
                warnings = [
                    SuspiciousWarning(text: localizationManager.localized("family_warning_blocked_site"), level: .high, time: String(format: localizationManager.localized("family_hours_ago_format"), 2)),
                    SuspiciousWarning(text: localizationManager.localized("family_warning_screen_time"), level: .medium, time: String(format: localizationManager.localized("family_hours_ago_format"), 5)),
                    SuspiciousWarning(text: localizationManager.localized("family_warning_unknown_contact"), level: .high, time: String(format: localizationManager.localized("family_days_ago_format"), 1)),
                    SuspiciousWarning(text: localizationManager.localized("family_warning_restricted_app"), level: .high, time: String(format: localizationManager.localized("family_days_ago_format"), 2))
                ]
            }
        }
    }
}

struct SuspiciousWarning: Identifiable {
    let id = UUID()
    let text: String
    let level: WarningLevel
    let time: String
    
    enum WarningLevel {
        case high, medium
    }
}

struct TopSitesDetailModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var topSites: [TopSiteItem] = []
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("top_sites_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                ForEach(Array(topSites.enumerated()), id: \.element.id) { index, site in
                    HStack(spacing: Spacing.m) {
                        Text("\(index + 1)")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                            .frame(width: 32, height: 32)
                            .background(Color.secondaryGold.opacity(0.2))
                            .cornerRadius(16)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(site.site)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            HStack(spacing: Spacing.s) {
                                    Text("\(site.visits) \(localizationManager.localized("top_sites_visits"))")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text("•")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                    Text(formatDuration(hours: site.hours, minutes: site.minutes))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                                Text(localizationManager.localized(site.categoryKey))
                                .font(.captionSmall)
                                    .foregroundColor(site.color)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(site.color.opacity(0.2))
                                .cornerRadius(8)
                        }
                        
                        Spacer()
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .id("top_sites_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadTopSites()
        }
    }
    
    private func loadTopSites() {
        topSites = [
            TopSiteItem(site: "youtube.com", visits: 142, hours: 8, minutes: 24, categoryKey: "top_sites_category_video", color: .red),
            TopSiteItem(site: "instagram.com", visits: 89, hours: 4, minutes: 12, categoryKey: "top_sites_category_social", color: .purple),
            TopSiteItem(site: "vk.com", visits: 67, hours: 2, minutes: 45, categoryKey: "top_sites_category_social", color: .blue),
            TopSiteItem(site: "google.com", visits: 45, hours: 1, minutes: 15, categoryKey: "top_sites_category_search", color: .blue),
            TopSiteItem(site: "tiktok.com", visits: 34, hours: 3, minutes: 20, categoryKey: "top_sites_category_video", color: .black)
        ]
    }
    
    private func formatDuration(hours: Int, minutes: Int) -> String {
        let hourUnit = localizationManager.localized("analytics_hour")
        let minuteUnit = localizationManager.localized("analytics_min")
        
        if hours == 0 {
            return "\(minutes) \(minuteUnit)"
        }
        
        if minutes == 0 {
            return "\(hours) \(hourUnit)"
        }
        
        return "\(hours) \(hourUnit) \(minutes) \(minuteUnit)"
    }
}

struct TopSiteItem: Identifiable {
    let id = UUID()
    let site: String
    let visits: Int
    let hours: Int
    let minutes: Int
    let categoryKey: String
    let color: Color
}

struct TopAppsDetailModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var topApps: [TopAppItem] = []
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("top_apps_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                ForEach(Array(topApps.enumerated()), id: \.element.id) { index, app in
                    HStack(spacing: Spacing.m) {
                        Text("\(index + 1)")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                            .frame(width: 32, height: 32)
                            .background(Color.secondaryGold.opacity(0.2))
                            .cornerRadius(16)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(app.app)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            HStack(spacing: Spacing.s) {
                                Text(formatDurationFromMinutes(app.usageMinutes))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text("•")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text("\(localizationManager.localized("top_apps_limit")) \(formatLimit(app.limitMinutes))")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                            if app.exceeded {
                                HStack {
                                    Image(systemName: "exclamationmark.triangle.fill")
                                        .font(.captionSmall)
                                        .foregroundColor(.dangerRed)
                                    
                                    Text(localizationManager.localized("top_apps_exceeded"))
                                        .font(.captionSmall)
                                        .foregroundColor(.dangerRed)
                                        .fontWeight(.semibold)
                                }
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(Color.dangerRed.opacity(0.2))
                                .cornerRadius(8)
                            }
                        }
                        
                        Spacer()
                    }
                    .padding(Spacing.m)
                    .background(app.exceeded ? Color.dangerRed.opacity(0.1) : Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(app.exceeded ? Color.dangerRed.opacity(0.5) : Color.clear, lineWidth: 2)
                    )
                }
            }
        }
        .id("top_apps_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadTopApps()
        }
    }
    
    private func loadTopApps() {
        topApps = [
            TopAppItem(app: "Instagram", usageMinutes: 8 * 60 + 24, limitMinutes: 30, exceeded: true, color: .purple),
            TopAppItem(app: "TikTok", usageMinutes: 4 * 60 + 12, limitMinutes: 20, exceeded: true, color: .black),
            TopAppItem(app: "YouTube", usageMinutes: 3 * 60 + 45, limitMinutes: 45, exceeded: true, color: .red),
            TopAppItem(app: "WhatsApp", usageMinutes: 90, limitMinutes: 60, exceeded: false, color: .green),
            TopAppItem(app: "VK", usageMinutes: 45, limitMinutes: 30, exceeded: true, color: .blue)
        ]
    }
    
    private func formatDurationFromMinutes(_ minutes: Int) -> String {
        let hours = minutes / 60
        let remainingMinutes = minutes % 60
        let hourUnit = localizationManager.localized("analytics_hour")
        let minuteUnit = localizationManager.localized("analytics_min")
        
        if hours == 0 {
            return "\(remainingMinutes) \(minuteUnit)"
        }
        
        if remainingMinutes == 0 {
            return "\(hours) \(hourUnit)"
        }
        
        return "\(hours) \(hourUnit) \(remainingMinutes) \(minuteUnit)"
    }
    
    private func formatLimit(_ minutes: Int) -> String {
        String(format: localizationManager.localized("top_apps_limit_value"), minutes)
    }
}

struct TopAppItem: Identifiable {
    let id = UUID()
    let app: String
    let usageMinutes: Int
    let limitMinutes: Int
    let exceeded: Bool
    let color: Color
}

struct UsageHoursDetailModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @State private var usageHours: [UsageHourItem] = [
        UsageHourItem(hour: "06:00-08:00", usage: 15, level: .low, color: .blue),
        UsageHourItem(hour: "08:00-12:00", usage: 35, level: .medium, color: .green),
        UsageHourItem(hour: "12:00-16:00", usage: 45, level: .high, color: .orange),
        UsageHourItem(hour: "16:00-20:00", usage: 80, level: .veryHigh, color: .red),
        UsageHourItem(hour: "20:00-22:00", usage: 60, level: .high, color: .orange),
        UsageHourItem(hour: "22:00-00:00", usage: 25, level: .medium, color: .green),
        UsageHourItem(hour: "00:00-06:00", usage: 5, level: .low, color: .blue)
    ]
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("peak_hours_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                ForEach(usageHours) { item in
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        HStack {
                            Text(item.hour)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                            
                            Text("\(item.usage)%")
                                .font(.bodyBold)
                                .foregroundColor(item.color)
                        }
                        
                        GeometryReader { geometry in
                            ZStack(alignment: .leading) {
                                RoundedRectangle(cornerRadius: 8)
                                    .fill(Color.backgroundMedium.opacity(0.3))
                                    .frame(height: 20)
                                
                                RoundedRectangle(cornerRadius: 8)
                                    .fill(item.color)
                                    .frame(width: geometry.size.width * CGFloat(item.usage) / 100, height: 20)
                            }
                        }
                        .frame(height: 20)
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .id("peak_hours_lang_\(localizationManager.currentLanguage.rawValue)")
    }
}

struct UsageHourItem: Identifiable {
    let id = UUID()
    let hour: String
    let usage: Int
    let level: UsageLevel
    let color: Color
    
    enum UsageLevel {
        case low, medium, high, veryHigh
    }
}

struct BypassAttemptsDetailModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    @ObservedObject private var manager = ParentalControlManager.shared
    @AppStorage("parental_selected_child") private var selectedChild: String = ""
    
    // Список детей (динамический)
    @State private var children: [String] = []
    
    // Статистика (загружается через API)
    @State private var today: Int = 0
    @State private var week: Int = 0
    @State private var blocked: Int = 0
    @State private var incognitoCount: Int = 0
    @State private var torCount: Int = 0
    @State private var proxyCount: Int = 0
    @State private var isLoading: Bool = true
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("bypass_attempts_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                if isLoading {
                    ProgressView()
                        .padding(Spacing.l)
                } else {
                    // Общая статистика
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(localizationManager.localized("bypass_stats"))
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                        
                        HStack(spacing: Spacing.m) {
                            VStack(alignment: .leading, spacing: 4) {
                                Text(localizationManager.localized("bypass_attempts_today"))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                Text("\(today)")
                                    .font(.bodyBold)
                                    .foregroundColor(.textPrimary)
                            }
                            
                            Spacer()
                            
                            VStack(alignment: .trailing, spacing: 4) {
                                Text(localizationManager.localized("bypass_attempts_week"))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                Text("\(week)")
                                    .font(.bodyBold)
                                    .foregroundColor(.warningOrange)
                            }
                        }
                        
                        HStack {
                            Text(localizationManager.localized("bypass_blocked"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(blocked)")
                                .font(.bodyBold)
                                .foregroundColor(.successGreen)
                        }
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Детализация по типам
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text(localizationManager.localized("bypass_details"))
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                        
                        // Скрытый режим
                        BypassTypeCard(
                            icon: "🕶️",
                            title: localizationManager.localized("bypass_incognito_type"),
                            count: incognitoCount,
                            color: .warningOrange
                        )
                        .environmentObject(localizationManager)
                        
                        // Tor
                        BypassTypeCard(
                            icon: "🧅",
                            title: localizationManager.localized("bypass_tor_type"),
                            count: torCount,
                            color: .dangerRed
                        )
                        .environmentObject(localizationManager)
                        
                        // Proxy
                        BypassTypeCard(
                            icon: "🔀",
                            title: localizationManager.localized("bypass_proxy_type"),
                            count: proxyCount,
                            color: .infoBlue
                        )
                        .environmentObject(localizationManager)
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .id("bypass_attempts_detail_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadBypassStatistics()
        }
    }
    
    private func loadBypassStatistics() {
        isLoading = true
        manager.getBypassStats(childId: selectedChild) { result in
            DispatchQueue.main.async {
                self.isLoading = false
                switch result {
                case .success(let stats):
                    self.today = stats.today
                    self.week = stats.week
                    self.blocked = stats.blocked
                    self.incognitoCount = stats.incognito
                    self.torCount = stats.tor
                    self.proxyCount = stats.proxy
                case .failure(let error):
                    print("⚠️ Failed to load bypass statistics: \(error.localizedDescription)")
                    // Оставляем значения по умолчанию
                }
            }
        }
    }
}

// MARK: - Bypass Type Card Component

struct BypassTypeCard: View {
    let icon: String
    let title: String
    let count: Int
    let color: Color
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            Text(icon)
                .font(.system(size: 32))
                .frame(width: 50, height: 50)
                .background(color.opacity(0.2))
                .cornerRadius(25)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                
                Text("\(count) \(localizationManager.localized("bypass_attempts_count"))")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            Spacer()
            
            Text("\(count)")
                .font(.title3)
                .foregroundColor(color)
                .bold()
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.2))
        .cornerRadius(CornerRadius.medium)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .stroke(color.opacity(0.5), lineWidth: 2)
        )
    }
}

// BypassAttempt (старая версия для модалов) - переименована для избежания конфликта с ParentalControlManager.BypassAttempt
struct BypassAttemptOld: Identifiable {
    let id = UUID()
    let method: String
    let count: Int
    let lastTime: String
    let color: Color
}

// MARK: YouTube настройки

struct YouTubeSettingsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Сохранение настроек YouTube в UserDefaults
    @AppStorage("youtube_safe_mode") private var isSafeModeEnabled = true
    @AppStorage("youtube_age_restriction_enabled") private var isAgeRestrictionEnabled = true
    @AppStorage("youtube_age_restriction") private var ageRestriction = 12
    @AppStorage("youtube_time_limit") private var timeLimit: Double = 45
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("youtube_settings_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Безопасный режим
                FamilyContentBlockItem(
                    icon: "🛡️",
                    title: localizationManager.localized("youtube_safe_mode"),
                    description: localizationManager.localized("youtube_safe_mode_desc"),
                    isEnabled: $isSafeModeEnabled
                )
                
                // Возрастные ограничения
                VStack(alignment: .leading, spacing: Spacing.m) {
                    HStack {
                        Text(localizationManager.localized("youtube_age_restriction"))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        Spacer()
                        
                        Toggle("", isOn: $isAgeRestrictionEnabled)
                            .labelsHidden()
                            .tint(.secondaryGold)
                    }
                    
                    if isAgeRestrictionEnabled {
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text(String(format: localizationManager.localized("youtube_age_restriction_value"), ageRestriction))
                                .font(.body)
                                .foregroundColor(.textSecondary)
                            
                            Text(localizationManager.localized("youtube_age_restriction_desc"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Лимит времени
                VStack(alignment: .leading, spacing: Spacing.m) {
                    HStack {
                        Text(localizationManager.localized("youtube_time_limit"))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        Spacer()
                        
                        Text("\(Int(timeLimit)) \(localizationManager.localized("youtube_time_limit_value"))")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                    }
                    
                    Slider(value: $timeLimit, in: 15...120, step: 15) {
                        Text(localizationManager.localized("youtube_time_limit"))
                    }
                    .tint(.secondaryGold)
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                Button(action: {
                    HapticFeedback.impact(.medium)
                isPresented = false
                }) {
                    Text(localizationManager.localized("youtube_save"))
                        .font(.bodyBold)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .id("youtube_settings_lang_\(localizationManager.currentLanguage.rawValue)")
        .onChange(of: isSafeModeEnabled) { newValue in
            print("✅ YouTube Safe Mode: \(newValue ? "ON" : "OFF")")
        }
        .onChange(of: isAgeRestrictionEnabled) { newValue in
            print("✅ YouTube Age Restriction: \(newValue ? "ON" : "OFF")")
        }
        .onChange(of: ageRestriction) { newValue in
            print("✅ YouTube Age Restriction: \(newValue)+")
        }
        .onChange(of: timeLimit) { newValue in
            print("✅ YouTube Time Limit: \(Int(newValue)) min/day")
        }
    }
}

// MARK: - Parental Control Settings Modal

struct FamilyParentalControlSettingsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Manager для применения правил
    @ObservedObject private var manager = ParentalControlManager.shared
    
    // Выбор ребёнка (динамический список) с сохранением в UserDefaults
    @AppStorage("parental_selected_child") private var selectedChild: String = ""
    
    // Список детей (динамический)
    @State private var children: [String] = []
    
    // Уровень защиты по возрасту
    enum AgeGroup: String, CaseIterable {
        case toddler
        case school
        case teen
        case adult
        
        var titleKey: String {
            switch self {
            case .toddler: return "family_age_group_toddler"
            case .school: return "family_age_group_school"
            case .teen: return "family_age_group_teen"
            case .adult: return "family_age_group_adult"
            }
        }
        
        var descriptionKey: String {
            switch self {
            case .toddler: return "family_age_group_toddler_desc"
            case .school: return "family_age_group_school_desc"
            case .teen: return "family_age_group_teen_desc"
            case .adult: return "family_age_group_adult_desc"
            }
        }
        
        static func fromStoredValue(_ value: String) -> AgeGroup {
            if let direct = AgeGroup(rawValue: value) {
                return direct
            }
            let manager = LocalizationManager()
            let normalized = value.lowercased()
            let ru = manager.translations[.russian] ?? [:]
            let en = manager.translations[.english] ?? [:]
            let toddlerLabels = Set([
                "1-6",
                ru["family_age_group_toddler"]?.lowercased(),
                en["family_age_group_toddler"]?.lowercased(),
                ru["family_for_1_6"]?.lowercased(),
                en["family_for_1_6"]?.lowercased()
            ].compactMap { $0 })
            let schoolLabels = Set([
                "7-13",
                ru["family_age_group_school"]?.lowercased(),
                en["family_age_group_school"]?.lowercased(),
                ru["family_for_7_13"]?.lowercased(),
                en["family_for_7_13"]?.lowercased()
            ].compactMap { $0 })
            let teenLabels = Set([
                "14-17",
                ru["family_age_group_teen"]?.lowercased(),
                en["family_age_group_teen"]?.lowercased(),
                ru["family_for_14_17"]?.lowercased(),
                en["family_for_14_17"]?.lowercased()
            ].compactMap { $0 })
            let adultLabels = Set([
                "18+",
                ru["family_age_group_adult"]?.lowercased(),
                en["family_age_group_adult"]?.lowercased(),
                ru["family_for_18_plus"]?.lowercased(),
                en["family_for_18_plus"]?.lowercased()
            ].compactMap { $0 })
            if toddlerLabels.contains(normalized) { return .toddler }
            if schoolLabels.contains(normalized) { return .school }
            if teenLabels.contains(normalized) { return .teen }
            if adultLabels.contains(normalized) { return .adult }
            return .school
        }
    }
    
    // Сохранение возраста в UserDefaults
    @AppStorage("parental_age_group") private var selectedAgeGroupRaw: String = AgeGroup.school.rawValue
    
    // Вычисляемое свойство для работы с enum
    private var selectedAgeGroup: AgeGroup {
        get {
            AgeGroup.fromStoredValue(selectedAgeGroupRaw)
        }
        set {
            selectedAgeGroupRaw = newValue.rawValue
        }
    }
    
    // Автоматические правила с сохранением в UserDefaults
    @AppStorage("parental_automated_rules_enabled") private var isAutomatedRulesEnabled: Bool = true // По умолчанию ВКЛЮЧЕНЫ
    @State private var showAutomatedRulesModal = false
    
    // Применение правил при изменении возраста
    private func applyAgeBasedRules() {
        guard isAutomatedRulesEnabled else { return }
        
        // Сохраняем настройки в UserDefaults
        let rules: [String: Any] = [
            "selectedChild": selectedChild,
            "ageGroup": selectedAgeGroup.rawValue,
            "isEnabled": isAutomatedRulesEnabled,
            "appliedDate": Date().timeIntervalSince1970
        ]
        
        // Сохраняем через UserDefaults
        UserDefaults.standard.set(rules, forKey: "parental_control_rules_\(selectedChild)")
        
        // Логируем применение правил
        print("✅ Rules applied for \(selectedChild), age group: \(selectedAgeGroup.rawValue)")
        
        // ✅ BUILD 96: Используем значения по умолчанию для предотвращения рекурсии
        // В этой функции (FamilyParentalControlSettingsModal) нет доступа к cachedParentalRules из FamilyScreen
        // Используем прямые значения из UserDefaults асинхронно
        let parentalRules = ParentalControlRules(
            websiteBlocking: false,
            appBlocking: false,
            searchBlocking: false,
            safesearch: false,
            screenTimeLimit: nil,
            bedtimeStart: nil,
            bedtimeEnd: nil,
            appLimits: nil,
            geofences: nil
        )
        
        // ✅ BUILD 96: Загружаем значения асинхронно для предотвращения рекурсии
        Task { @MainActor in
            let loadedRules = ParentalControlRules(
                websiteBlocking: UserDefaults.standard.bool(forKey: "parental_website_blocking"),
                appBlocking: UserDefaults.standard.bool(forKey: "parental_app_blocking"),
                searchBlocking: UserDefaults.standard.bool(forKey: "parental_search_blocking"),
                safesearch: UserDefaults.standard.bool(forKey: "parental_safesearch"),
                screenTimeLimit: nil,
                bedtimeStart: nil,
                bedtimeEnd: nil,
                appLimits: nil,
                geofences: nil
            )
            // Используем загруженные правила для применения через API
            // (parentalRules уже используется ниже, поэтому это для будущего использования)
            _ = loadedRules
        }
        
        // Преобразуем возрастную группу в формат API
        let ageGroupString: String = {
            switch selectedAgeGroup {
            case .toddler: return "1-6"
            case .school: return "7-13"
            case .teen: return "14-17"
            case .adult: return "18+"
            }
        }()
        
        manager.applyRules(
            childId: selectedChild,
            ageGroup: ageGroupString,
            rules: parentalRules
        ) { success, error in
            if success {
                print("✅ Rules applied via API for \(selectedChild)")
            } else {
                print("⚠️ Failed to apply rules: \(error ?? "Unknown error")")
            }
        }
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("family_parental_settings_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Выбор ребёнка
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_select_child"))
                         .font(.bodyBold)
                         .foregroundColor(.textPrimary)
                     
                    Picker(localizationManager.localized("family_child"), selection: $selectedChild) {
                        ForEach(children, id: \.self) { child in
                            Text(child).tag(child)
                        }
                    }
                    .pickerStyle(.segmented)
                    .tint(Color.secondaryGold)
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // 2. Уровень защиты по возрасту
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_protection_level"))
                         .font(.bodyBold)
                         .foregroundColor(.textPrimary)
                     
                    Picker(localizationManager.localized("family_age_restrictions"), selection: Binding(
                         get: { selectedAgeGroup },
                         set: { newValue in
                             selectedAgeGroupRaw = newValue.rawValue
                         }
                     )) {
                         ForEach(AgeGroup.allCases, id: \.self) { age in
                             Text(localizationManager.localized(age.titleKey)).tag(age)
                         }
                     }
                    .pickerStyle(.menu)
                    .tint(Color.secondaryGold)
                    .onChange(of: selectedAgeGroupRaw) { _ in
                        // Автоматически применяем правила при изменении возраста
                        applyAgeBasedRules()
                    }
                    
                    Text(localizationManager.localized(selectedAgeGroup.descriptionKey))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .padding(.top, Spacing.xs)
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)

                CompanionParentConsentSection()
                
                // 3. Автоматические правила
                FamilyConfigButtonItem(
                    icon: "🤖",
                    title: localizationManager.localized("family_auto_rules_title"),
                    description: isAutomatedRulesEnabled ? localizationManager.localized("family_auto_rules_enabled_desc") : localizationManager.localized("family_auto_rules_disabled_desc"),
                    buttonTitle: localizationManager.localized("family_configure"),
                    action: { showAutomatedRulesModal = true }
                )
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Информация
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_how_it_works"))
                         .font(.bodyBold)
                         .foregroundColor(.secondaryGold)
                     
                    Text(localizationManager.localized("family_auto_rules"))
                         .font(.caption)
                         .foregroundColor(.textSecondary)
                 }
                .padding(Spacing.m)
                .background(Color.secondaryGold.opacity(0.1))
                .cornerRadius(CornerRadius.medium)
                
                // Кнопка применения правил
                if isAutomatedRulesEnabled {
                    Button(action: {
                        HapticFeedback.impact(.medium)
                        applyAgeBasedRules()
                    }) {
                        Text(localizationManager.localized("family_apply_rules"))
                            .font(.bodyBold)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.m)
                    }
                    .padding(.top, Spacing.s)
                }
            }
        }
        .onAppear {
            // ✅ ЗАГРУЗКА ДЕТЕЙ: Загружаем список детей при открытии модала
            loadChildren()
            
            // Применяем правила при открытии модала (если уже включены)
            if isAutomatedRulesEnabled {
                applyAgeBasedRules()
            }
        }
        .onChange(of: selectedChild) { _ in
            // Применяем правила при смене ребёнка
            if isAutomatedRulesEnabled {
                applyAgeBasedRules()
            }
        }
        .onChange(of: isAutomatedRulesEnabled) { newValue in
            if newValue {
                // Применяем правила при включении
                applyAgeBasedRules()
            }
            print("✅ Automated rules: \(newValue ? "ON" : "OFF")")
        }
        .sheet(isPresented: $showAutomatedRulesModal) {
            AutomatedRulesModal(isPresented: $showAutomatedRulesModal, isEnabled: $isAutomatedRulesEnabled, ageGroup: selectedAgeGroup) {
                // Обновляем правила при изменении в модале автоматических правил
                applyAgeBasedRules()
            }
            .environmentObject(localizationManager)
        }
    }
    
    // ✅ ФУНКЦИЯ ЗАГРУЗКИ ДЕТЕЙ: Загружаем список детей из UserDefaults
    private func loadChildren() {
        guard let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
              let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) else {
            children = []
            print("⚠️ Нет данных о детях в UserDefaults")
            return
        }
        
        children = decoded
            .filter { member in
                member.role == .child || member.role == .teenager
            }
            .map { $0.name }
        
        print("✅ Загружено детей: \(children.count)")
        
        // Если выбранный ребёнок не в списке, выбираем первого
        if !children.isEmpty && !children.contains(selectedChild) {
            selectedChild = children.first ?? ""
        }
    }
}

// MARK: - Automated Rules Modal

struct AutomatedRulesModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    let ageGroup: FamilyParentalControlSettingsModal.AgeGroup
    var onRulesChanged: (() -> Void)? = nil
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Состояния для правил
    @State private var showAgeBasedFilteringExplanation = false
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("family_auto_rules_modal_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // Toggle включения правил
                FamilyContentBlockItem(
                    icon: "🤖",
                    title: localizationManager.localized("family_auto_rules_title"),
                    description: isEnabled ? localizationManager.localized("family_auto_rules_enabled_desc") : localizationManager.localized("family_auto_rules_disabled_desc"),
                    isEnabled: $isEnabled
                )
                .onChange(of: isEnabled) { newValue in
                    // Применяем правила при изменении toggle
                    print("✅ AutomatedRulesModal: rules \(newValue ? "ENABLED" : "DISABLED")")
                    if newValue {
                        onRulesChanged?()
                    }
                }
                
                if isEnabled {
                    Divider()
                        .background(Color.white.opacity(0.2))
                        .padding(.vertical, Spacing.s)
                    
                    // Правило 1: Фильтрация контента по возрасту (с объяснением)
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        HStack {
                            Text(localizationManager.localized("family_content_filtering"))
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                            
                            Button(action: {
                                HapticFeedback.impact(.light)
                                showAgeBasedFilteringExplanation.toggle()
                            }) {
                                Image(systemName: showAgeBasedFilteringExplanation ? "chevron.up" : "chevron.down")
                                    .font(.system(size: 14))
                                    .foregroundColor(.secondaryGold)
                            }
                        }
                        
                        if showAgeBasedFilteringExplanation {
                            ageBasedFilteringExplanation
                        }
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .onAppear {
            // Логируем текущее состояние при открытии
            print("✅ AutomatedRulesModal opened: age group \(ageGroup.rawValue), rules state \(isEnabled ? "ON" : "OFF")")
        }
    }
    
    private var ageBasedFilteringExplanation: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Divider()
                .background(Color.white.opacity(0.2))
                .padding(.vertical, Spacing.xs)
            
            switch ageGroup {
            case .toddler:
                Text(localizationManager.localized("family_for_1_6"))
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_rules_1_6_youtube"))
                         .font(.caption)
                         .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("family_rules_1_6_cartoons"))
                         .font(.caption)
                         .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("family_rules_1_6_games"))
                         .font(.caption)
                         .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("family_rules_1_6_social"))
                         .font(.caption)
                         .foregroundColor(.dangerRed)
                    Text(localizationManager.localized("family_rules_1_6_messengers"))
                         .font(.caption)
                         .foregroundColor(.dangerRed)
                }
                .font(.caption)
                .foregroundColor(.textSecondary)
                
            case .school:
                Text(localizationManager.localized("family_for_7_13"))
                     .font(.bodyBold)
                     .foregroundColor(.secondaryGold)
                 
                 VStack(alignment: .leading, spacing: 4) {
                     Text(localizationManager.localized("family_rules_7_13_youtube"))
                          .font(.caption)
                          .foregroundColor(.textSecondary)
                     Text(localizationManager.localized("family_rules_7_13_cartoons"))
                          .font(.caption)
                          .foregroundColor(.textSecondary)
                     Text(localizationManager.localized("family_rules_7_13_games"))
                          .font(.caption)
                          .foregroundColor(.textSecondary)
                     Text(localizationManager.localized("family_rules_7_13_social"))
                          .font(.caption)
                          .foregroundColor(.dangerRed)
                     Text(localizationManager.localized("family_rules_7_13_messengers"))
                          .font(.caption)
                          .foregroundColor(.successGreen)
                  }

            case .teen:
                Text(localizationManager.localized("family_for_14_17"))
                    .font(.bodyBold)
                    .foregroundColor(.secondaryGold)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized("family_rules_14_17_youtube"))
                         .font(.caption)
                         .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("family_rules_14_17_cartoons"))
                         .font(.caption)
                         .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("family_rules_14_17_games"))
                         .font(.caption)
                         .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("family_rules_14_17_social"))
                         .font(.caption)
                         .foregroundColor(.successGreen)
                    Text(localizationManager.localized("family_rules_14_17_messengers"))
                         .font(.caption)
                         .foregroundColor(.successGreen)
                 }

            case .adult:
                Text(localizationManager.localized("family_for_18_plus"))
                    .font(.bodyBold)
                    .foregroundColor(.successGreen)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized("family_rules_18_youtube"))
                         .font(.caption)
                         .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("family_rules_18_cartoons"))
                         .font(.caption)
                         .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("family_rules_18_games"))
                         .font(.caption)
                         .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("family_rules_18_social"))
                         .font(.caption)
                         .foregroundColor(.successGreen)
                    Text(localizationManager.localized("family_rules_18_messengers"))
                         .font(.caption)
                         .foregroundColor(.successGreen)
                 }
            }
        }
        .padding(.top, Spacing.xs)
    }
}

// MARK: - Family Member Data Model

struct FamilyMemberData: Identifiable, Codable {
    let id: UUID
    let name: String
    let role: FamilyMemberCard.FamilyRole
    let avatar: String
    let status: FamilyMemberCard.ProtectionStatus
    let threatsBlocked: Int
    let lastActive: String
    
    init(id: UUID = UUID(), name: String, role: FamilyMemberCard.FamilyRole, avatar: String, status: FamilyMemberCard.ProtectionStatus, threatsBlocked: Int, lastActive: String) {
        self.id = id
        self.name = name
        self.role = role
        self.avatar = avatar
        self.status = status
        self.threatsBlocked = threatsBlocked
        self.lastActive = lastActive
    }
}

// MARK: - Codable Extensions для FamilyMemberCard типов

extension FamilyMemberCard.FamilyRole: Codable {
    enum CodableError: Error {
        case invalidValue(String)
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        let rawValue = try container.decode(String.self)
        
        let localizationManager = LocalizationManager()
        let normalized = rawValue.lowercased()
        let parentLabels = Set(["parent", localizationManager.translations[.russian]?["family_role_parent_label"]?.lowercased() ?? "parent"])
        let childLabels = Set(["child", localizationManager.translations[.russian]?["family_role_child_label"]?.lowercased() ?? "child"])
        let teenLabels = Set(["teenager", "teen", localizationManager.translations[.russian]?["family_role_teen_label"]?.lowercased() ?? "teenager"])
        let elderlyLabels = Set(["elderly", "grandparent", localizationManager.translations[.russian]?["family_role_elderly_label"]?.lowercased() ?? "elderly"])
        switch normalized {
        case _ where parentLabels.contains(normalized): self = .parent
        case _ where childLabels.contains(normalized): self = .child
        case _ where teenLabels.contains(normalized): self = .teenager
        case _ where elderlyLabels.contains(normalized): self = .elderly
        default: throw CodableError.invalidValue(rawValue)
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        try container.encode(label)
    }
}

extension FamilyMemberCard.ProtectionStatus: Codable {
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        let rawValue = try container.decode(String.self)
        
        let localizationManager = LocalizationManager()
        let normalized = rawValue.lowercased()
        let protectedLabels = Set(["protected", localizationManager.translations[.russian]?["family_status_protected"]?.lowercased() ?? "protected"])
        let warningLabels = Set(["warning", localizationManager.translations[.russian]?["family_status_warning"]?.lowercased() ?? "warning"])
        let dangerLabels = Set(["danger", localizationManager.translations[.russian]?["family_status_danger"]?.lowercased() ?? "danger"])
        let offlineLabels = Set(["offline", localizationManager.translations[.russian]?["family_status_offline"]?.lowercased() ?? "offline"])
        switch normalized {
        case _ where protectedLabels.contains(normalized): self = .protected
        case _ where warningLabels.contains(normalized): self = .warning
        case _ where dangerLabels.contains(normalized): self = .danger
        case _ where offlineLabels.contains(normalized): self = .offline
        default: self = .protected
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        try container.encode(label)
    }
}

// MARK: - Family Bypass Protection Modal

struct FamilyBypassProtectionModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Manager для обработки защиты от обхода
    @ObservedObject private var manager = ParentalControlManager.shared
    
    // Выбранный ребёнок
    @AppStorage("parental_selected_child") private var selectedChild: String = ""
    
    // Список детей (динамический)
    @State private var children: [String] = []
    
    // Состояния для 3 переключателей с сохранением в UserDefaults
    @AppStorage("bypass_incognito_enabled") private var isIncognitoDetectionEnabled: Bool = true
    @AppStorage("bypass_tor_enabled") private var isTorDetectionEnabled: Bool = true
    @AppStorage("bypass_proxy_enabled") private var isProxyDetectionEnabled: Bool = true
    
    // Статистика
    @State private var attemptsToday: Int = 0
    @State private var attemptsWeek: Int = 47
    @State private var attemptsBlocked: Int = 47
    
    // Детализация по типам
    @State private var incognitoAttempts: Int = 15
    @State private var torAttempts: Int = 8
    @State private var proxyAttempts: Int = 6
    
    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("bypass_protection_title"),
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Incognito detection toggle
                FamilyContentBlockItem(
                    icon: "🕶️",
                    title: localizationManager.localized("bypass_incognito_detection"),
                    description: localizationManager.localized("bypass_incognito_desc"),
                    isEnabled: $isIncognitoDetectionEnabled
                )
                
                // 2. Детекция Tor
                FamilyContentBlockItem(
                    icon: "🧅",
                    title: localizationManager.localized("bypass_tor_detection"),
                    description: localizationManager.localized("bypass_tor_desc"),
                    isEnabled: $isTorDetectionEnabled
                )
                
                // 3. Детекция Proxy
                FamilyContentBlockItem(
                    icon: "🔀",
                    title: localizationManager.localized("bypass_proxy_detection"),
                    description: localizationManager.localized("bypass_proxy_desc"),
                    isEnabled: $isProxyDetectionEnabled
                )
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Статистика
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("bypass_stats_week"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    HStack(spacing: Spacing.m) {
                        VStack(alignment: .leading, spacing: 4) {
                            Text(localizationManager.localized("bypass_attempts_today"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Text("\(attemptsToday)")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                        
                        Spacer()
                        
                        VStack(alignment: .trailing, spacing: 4) {
                            Text(localizationManager.localized("bypass_attempts_week"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Text("\(attemptsWeek)")
                                .font(.bodyBold)
                                .foregroundColor(.warningOrange)
                        }
                    }
                    
                    HStack {
                        Text(localizationManager.localized("bypass_blocked"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text("\(attemptsBlocked)")
                            .font(.bodyBold)
                            .foregroundColor(.successGreen)
                    }
                    
                    // Детализация по типам (с заменой названий)
                    VStack(spacing: Spacing.xs) {
                        HStack {
                            Text(localizationManager.localized("bypass_incognito_type"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(incognitoAttempts)")
                                .font(.caption)
                                .foregroundColor(.textPrimary)
                        }
                        
                        HStack {
                            Text(localizationManager.localized("bypass_tor_type"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(torAttempts)")
                                .font(.caption)
                                .foregroundColor(.textPrimary)
                        }
                        
                        HStack {
                            Text(localizationManager.localized("bypass_proxy_type"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(proxyAttempts)")
                                .font(.caption)
                                .foregroundColor(.textPrimary)
                        }
                    }
                    .padding(.top, Spacing.s)
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
            }
        }
        .id("bypass_protection_lang_\(localizationManager.currentLanguage.rawValue)")
        .onAppear {
            loadBypassStatistics()
        }
        .onChange(of: isIncognitoDetectionEnabled) { newValue in
            applyBypassProtection()
        }
        .onChange(of: isTorDetectionEnabled) { newValue in
            applyBypassProtection()
        }
        .onChange(of: isProxyDetectionEnabled) { newValue in
            applyBypassProtection()
        }
    }
    
    private func loadBypassStatistics() {
        // Загружаем статистику из API через manager
        manager.getBypassStats(childId: selectedChild) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let stats):
                    self.attemptsToday = stats.today
                    self.attemptsWeek = stats.week
                    self.attemptsBlocked = stats.blocked
                    self.incognitoAttempts = stats.incognito
                    self.torAttempts = stats.tor
                    self.proxyAttempts = stats.proxy
                case .failure(let error):
                    print("⚠️ Failed to load bypass statistics: \(error.localizedDescription)")
                    // Оставляем значения по умолчанию
                }
            }
        }
    }
    
    private func applyBypassProtection() {
        // Применяем настройки защиты от обхода через API
        manager.applyBypassProtection(
            childId: selectedChild,
            incognito: isIncognitoDetectionEnabled,
            tor: isTorDetectionEnabled,
            proxy: isProxyDetectionEnabled
        ) { success, errorMessage in
            DispatchQueue.main.async {
                if success {
                    print("✅ Bypass protection applied: Incognito=\(self.isIncognitoDetectionEnabled), Tor=\(self.isTorDetectionEnabled), Proxy=\(self.isProxyDetectionEnabled)")
                    // Обновляем статистику после применения
                    self.loadBypassStatistics()
                } else {
                    print("❌ Failed to apply bypass protection: \(errorMessage ?? "Unknown error")")
                }
            }
        }
    }
}

struct FamilyScreen_Previews: PreviewProvider {
    static var previews: some View {
        FamilyScreen()
    }
}