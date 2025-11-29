import SwiftUI

/// ⚙️ Settings Screen - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
/// Экран настроек - управление приложением и профилем
/// Источник дизайна: /mobile/wireframes/05_settings_screen.html
struct SettingsScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @State private var isVPNEnabled: Bool = true
    @State private var isNotificationsEnabled: Bool = true
    @State private var isBiometricEnabled: Bool = true
    @State private var protectionLevel: Double = 75
    @State private var showProfileEdit: Bool = false
    @State private var showLanguageSettings: Bool = false
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("Фон экрана настроек")
            
            VStack(spacing: 0) {
                // Навигационная панель
                navigationHeader
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Профиль пользователя
                        profileSection
                        
                        // Защита и безопасность
                        securitySection
                        
                        // Уведомления
                        notificationsSection
                        
                        // Приложение
                        appSection
                        
                        // Дополнительно
                        additionalSection
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.xxl)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Список настроек приложения")
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showProfileEdit) {
            ProfileEditView()
        }
        .sheet(isPresented: $showLanguageSettings) {
            LanguageSettingsScreen()
        }
    }
    
    // MARK: - Navigation Header
    
    private var navigationHeader: some View {
        ALADDINNavigationBar(
            title: "НАСТРОЙКИ",
            subtitle: "Управление приложением",
            showBackButton: true,
            onBack: {
                dismiss()
            }
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Навигационная панель настроек")
    }
    
    // MARK: - Profile Section
    
    private var profileSection: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text("ПРОФИЛЬ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            HStack(spacing: Spacing.m) {
                // Аватар
                Circle()
                    .fill(LinearGradient(
                        colors: [.primaryBlue, .secondaryBlue],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    ))
                    .frame(width: 60, height: 60)
                    .overlay(
                        Text("С")
                            .font(.h2)
                            .foregroundColor(.white)
                    )
                    .accessibilityLabel("Аватар пользователя")
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text("Сергей Хлыстов")
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                        .accessibilityLabel("Имя пользователя: Сергей Хлыстов")
                    
                    Text("sergey@aladdin.app")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .accessibilityLabel("Email: sergey@aladdin.app")
                    
                    Text("Premium подписка")
                        .font(.caption)
                        .foregroundColor(.primaryBlue)
                        .padding(.horizontal, Spacing.s)
                        .padding(.vertical, Spacing.xxs)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.small)
                                .fill(Color.primaryBlue.opacity(0.1))
                        )
                        .accessibilityLabel("Статус: Premium подписка")
                }
                
                Spacer()
                
                Button(action: {
                    showProfileEdit = true
                }) {
                    Image(systemName: "pencil")
                        .font(.system(size: 16))
                        .foregroundColor(.primaryBlue)
                        .frame(width: 32, height: 32)
                        .background(
                            Circle()
                                .fill(Color.primaryBlue.opacity(0.1))
                        )
                }
                .accessibilityLabel("Редактировать профиль")
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Security Section
    
    private var securitySection: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text("ЗАЩИТА И БЕЗОПАСНОСТЬ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            VStack(spacing: Spacing.m) {
                // VPN
                settingRow(
                    icon: "shield.fill",
                    title: "VPN защита",
                    subtitle: "Защищённое соединение",
                    isEnabled: $isVPNEnabled
                )
                
                // Биометрическая аутентификация
                settingRow(
                    icon: "faceid",
                    title: "Face ID / Touch ID",
                    subtitle: "Биометрическая аутентификация",
                    isEnabled: $isBiometricEnabled
                )
                
                // Уровень защиты
                VStack(spacing: Spacing.s) {
                    HStack {
                        Image(systemName: "lock.fill")
                            .font(.system(size: 20))
                            .foregroundColor(.primaryBlue)
                        
                        VStack(alignment: .leading, spacing: Spacing.xxs) {
                            Text("Уровень защиты")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            Text("\(Int(protectionLevel))% - \(protectionLevelText)")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        
                        Spacer()
                    }
                    
                    HStack {
                        Text("0%")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        
                        Slider(value: $protectionLevel, in: 0...100, step: 5)
                            .accentColor(.primaryBlue)
                        
                        Text("100%")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                }
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.backgroundMedium.opacity(0.3))
                )
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Уровень защиты: \(Int(protectionLevel))%")
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Notifications Section
    
    private var notificationsSection: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text("УВЕДОМЛЕНИЯ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            VStack(spacing: Spacing.m) {
                settingRow(
                    icon: "bell.fill",
                    title: "Push уведомления",
                    subtitle: "Получать уведомления о угрозах",
                    isEnabled: $isNotificationsEnabled
                )
                
                settingRow(
                    icon: "envelope.fill",
                    title: "Email уведомления",
                    subtitle: "Еженедельные отчёты на email",
                    isEnabled: .constant(true)
                )
                
                settingRow(
                    icon: "speaker.wave.2.fill",
                    title: "Звуковые уведомления",
                    subtitle: "Звук при обнаружении угроз",
                    isEnabled: .constant(false)
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - App Section
    
    private var appSection: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text("ПРИЛОЖЕНИЕ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            VStack(spacing: Spacing.s) {
                settingsButton(
                    icon: "globe",
                    title: "Язык",
                    subtitle: "Русский",
                    action: {
                        showLanguageSettings = true
                    }
                )
                
                settingsButton(
                    icon: "moon.fill",
                    title: "Тёмная тема",
                    subtitle: "Автоматически",
                    action: {
                        // Переключение темы
                    }
                )
                
                settingsButton(
                    icon: "arrow.clockwise",
                    title: "Обновления",
                    subtitle: "Версия 1.0.0",
                    action: {
                        // Проверка обновлений
                    }
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Additional Section
    
    private var additionalSection: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text("ДОПОЛНИТЕЛЬНО")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            VStack(spacing: Spacing.s) {
                settingsButton(
                    icon: "questionmark.circle",
                    title: "Помощь и поддержка",
                    subtitle: "FAQ и контакты",
                    action: {
                        // Открыть поддержку
                    }
                )
                
                settingsButton(
                    icon: "doc.text",
                    title: "Политика конфиденциальности",
                    subtitle: "Как мы защищаем ваши данные",
                    action: {
                        // Открыть политику
                    }
                )
                
                settingsButton(
                    icon: "doc.plaintext",
                    title: "Условия использования",
                    subtitle: "Правила использования сервиса",
                    action: {
                        // Открыть условия
                    }
                )
                
                settingsButton(
                    icon: "square.and.arrow.up",
                    title: "Поделиться приложением",
                    subtitle: "Рассказать друзьям",
                    action: {
                        // Поделиться
                    }
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Helper Views
    
    private func settingRow(icon: String, title: String, subtitle: String, isEnabled: Binding<Bool>) -> some View {
        HStack(spacing: Spacing.m) {
            Image(systemName: icon)
                .font(.system(size: 20))
                .foregroundColor(.primaryBlue)
                .frame(width: 24)
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(title)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                
                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            Spacer()
            
            ALADDINToggle(isOn: isEnabled)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(isEnabled.wrappedValue ? "включено" : "выключено")")
    }
    
    private func settingsButton(icon: String, title: String, subtitle: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack(spacing: Spacing.m) {
                Image(systemName: icon)
                    .font(.system(size: 20))
                    .foregroundColor(.primaryBlue)
                    .frame(width: 24)
                
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(title)
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                    
                    Text(subtitle)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 14))
                    .foregroundColor(.textSecondary)
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(subtitle)")
    }
    
    private var protectionLevelText: String {
        switch protectionLevel {
        case 0...25: return "Низкий"
        case 26...50: return "Средний"
        case 51...75: return "Высокий"
        case 76...100: return "Максимальный"
        default: return "Средний"
        }
    }
    
    private var cardBackground: some View {
        RoundedRectangle(cornerRadius: CornerRadius.large)
            .fill(Color.backgroundMedium.opacity(0.5))
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
    }
}

// MARK: - Preview

struct SettingsScreen_Previews: PreviewProvider {
    static var previews: some View {
        SettingsScreen()
    }
}
