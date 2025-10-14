import SwiftUI

/// ⚙️ Settings Screen
/// Экран настроек - управление приложением и профилем
/// Источник дизайна: /mobile/wireframes/05_settings_screen.html
struct SettingsScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @State private var isVPNEnabled: Bool = true
    @State private var isNotificationsEnabled: Bool = true
    @State private var isBiometricEnabled: Bool = true
    @State private var protectionLevel: Double = 75
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                ALADDINNavigationBar(
                    title: "НАСТРОЙКИ",
                    subtitle: "Управление приложением",
                    leftButton: .init(icon: "chevron.left") {
                        dismiss()
                    }
                )
                
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
                        
                        // Аккаунт
                        accountSection
                        
                        // Spacer
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
    }
    
    // MARK: - Profile Section
    
    private var profileSection: some View {
        VStack(spacing: Spacing.m) {
            // Аватар и имя
            HStack(spacing: Spacing.m) {
                // Аватар
                ZStack {
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [Color.primaryBlue, Color.secondaryBlue],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 70, height: 70)
                    
                    Text("👨")
                        .font(.system(size: 40))
                }
                
                // Информация
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text("Сергей Хлыстов")
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                    
                    Text("sergey@aladdin.family")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    
                    // Статус подписки
                    HStack(spacing: Spacing.xs) {
                        Text("⭐")
                            .font(.caption)
                        
                        Text("Premium до 31.12.2025")
                            .font(.caption)
                            .foregroundColor(.secondaryGold)
                    }
                }
                
                Spacer()
                
                // Кнопка редактирования
                Button(action: {
                    print("Редактировать профиль")
                }) {
                    Image(systemName: "pencil")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.primaryBlue)
                }
            }
            .padding(Spacing.cardPadding)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(Color.backgroundMedium.opacity(0.5))
            )
            .cardShadow()
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Security Section
    
    private var securitySection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            // Заголовок
            sectionHeader(title: "ЗАЩИТА И БЕЗОПАСНОСТЬ", icon: "🛡️")
            
            // Настройки
            VStack(spacing: Spacing.s) {
                // VPN
                ALADDINToggle(
                    "VPN Защита",
                    subtitle: "Шифрование всего трафика",
                    icon: "🌐",
                    isOn: $isVPNEnabled
                )
                
                // Биометрия
                ALADDINToggle(
                    "Face ID / Touch ID",
                    subtitle: "Вход по биометрии",
                    icon: "🔐",
                    isOn: $isBiometricEnabled
                )
                
                // Уровень защиты
                ALADDINSlider(
                    "Уровень защиты",
                    subtitle: "От базового до максимального",
                    icon: "🛡️",
                    value: $protectionLevel,
                    range: 0...100,
                    unit: "%"
                )
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    // MARK: - Notifications Section
    
    private var notificationsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            // Заголовок
            sectionHeader(title: "УВЕДОМЛЕНИЯ", icon: "🔔")
            
            // Настройки
            VStack(spacing: Spacing.s) {
                ALADDINToggle(
                    "Уведомления об угрозах",
                    subtitle: "Сообщения о заблокированных угрозах",
                    icon: "⚠️",
                    isOn: $isNotificationsEnabled
                )
                
                settingsItem(
                    icon: "📱",
                    title: "Push уведомления",
                    value: "Включены"
                )
                
                settingsItem(
                    icon: "📧",
                    title: "Email отчёты",
                    value: "Еженедельно"
                )
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    // MARK: - App Section
    
    private var appSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            // Заголовок
            sectionHeader(title: "ПРИЛОЖЕНИЕ", icon: "📱")
            
            // Настройки
            VStack(spacing: Spacing.s) {
                settingsItem(
                    icon: "🌍",
                    title: "Язык",
                    value: "Русский"
                )
                
                settingsItem(
                    icon: "🎨",
                    title: "Тема оформления",
                    value: "Тёмная"
                )
                
                settingsItem(
                    icon: "💾",
                    title: "Кэш и данные",
                    value: "47 MB"
                )
                
                settingsItem(
                    icon: "ℹ️",
                    title: "О приложении",
                    value: "v1.0.0"
                )
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    // MARK: - Account Section
    
    private var accountSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            // Заголовок
            sectionHeader(title: "АККАУНТ", icon: "👤")
            
            // Опции
            VStack(spacing: Spacing.s) {
                settingsButton(
                    icon: "⭐",
                    title: "Управление подпиской",
                    color: .secondaryGold
                ) {
                    print("Подписка")
                }
                
                settingsButton(
                    icon: "📄",
                    title: "Условия использования",
                    color: .primaryBlue
                ) {
                    print("Terms")
                }
                
                settingsButton(
                    icon: "🔒",
                    title: "Политика конфиденциальности",
                    color: .primaryBlue
                ) {
                    print("Privacy")
                }
                
                settingsButton(
                    icon: "🚪",
                    title: "Выйти из аккаунта",
                    color: .dangerRed
                ) {
                    print("Logout")
                }
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    // MARK: - Helper Views
    
    private func sectionHeader(title: String, icon: String) -> some View {
        HStack(spacing: Spacing.s) {
            Text(icon)
                .font(.system(size: 20))
            
            Text(title)
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            Spacer()
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func settingsItem(icon: String, title: String, value: String) -> some View {
        Button(action: {
            print("Открыть \(title)")
        }) {
            HStack(spacing: Spacing.m) {
                Text(icon)
                    .font(.system(size: 24))
                
                Text(title)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                
                Spacer()
                
                Text(value)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.textSecondary)
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private func settingsButton(
        icon: String,
        title: String,
        color: Color,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .light)
            generator.impactOccurred()
            action()
        }) {
            HStack(spacing: Spacing.m) {
                Text(icon)
                    .font(.system(size: 24))
                
                Text(title)
                    .font(.body)
                    .foregroundColor(color)
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(color)
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(color.opacity(0.3), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Preview

#Preview {
    SettingsScreen()
}




