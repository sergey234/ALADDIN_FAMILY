import SwiftUI

/// ⚙️ Member Settings Modal
/// Настройки участника семьи
struct MemberSettingsModalView: View {
    
    let memberName: String
    let memberRole: String
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    
    // MARK: - State для переключателей
    
    // Администратор
    @State private var criticalThreatsEnabled: Bool = true
    @State private var childrenActionsEnabled: Bool = true
    @State private var familyAlertsEnabled: Bool = true
    @State private var twoFactorEnabled: Bool = true
    @State private var showTwoFactorSettings: Bool = false
    @State private var showPasswordChange: Bool = false
    @State private var showLoginHistory: Bool = false
    
    // Родитель
    @State private var contentBlockingEnabled: Bool = true
    @State private var timeExceededEnabled: Bool = true
    @State private var accessRequestsEnabled: Bool = true
    @State private var securityThreatsEnabled: Bool = true
    @State private var protectionUpdatesEnabled: Bool = true
    
    // Подросток
    @State private var dangerousSitesEnabled: Bool = true
    @State private var timeLimitEnabled: Bool = true
    @State private var newFeaturesEnabled: Bool = false
    
    // Ребёнок
    @State private var soundsEnabled: Bool = true
    
    // Люди 60+
    @State private var largeFontEnabled: Bool = true
    @State private var brightButtonsEnabled: Bool = true
    @State private var autoPlayEnabled: Bool = true
    @State private var simpleAuthEnabled: Bool = true
    @State private var autoProtectionEnabled: Bool = true
    @State private var criticalOnlyEnabled: Bool = true
    @State private var largeTextEnabled: Bool = true
    @State private var soundAlertsEnabled: Bool = true
    
    var body: some View {
        NavigationView {
            ZStack {
                // Фон
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.m) {
                        // Заголовок
                        VStack(spacing: Spacing.xs) {
                            Text("⚙️")
                                .font(.system(size: 64))
                            
                            Text("Настройки")
                                .font(.h1)
                                .foregroundColor(.textPrimary)
                            
                            Text(memberName)
                                .font(.h3)
                                .foregroundColor(.primaryBlue)
                            
                            Text(memberRole)
                                .font(.body)
                                .foregroundColor(.textSecondary)
                        }
                        .padding(.top, Spacing.xxl)
                        
                        // Настройки в зависимости от роли
                        if memberRole == "Администратор" || memberRole == "Папа" {
                            administratorSettings
                        } else if memberRole == "Родитель" {
                            parentSettings
                        } else if memberRole == "Подросток" {
                            teenagerSettings
                        } else if memberRole == "Ребёнок" {
                            childSettings
                        } else if memberRole == "Люди 60+" || memberRole == "Дедушка" {
                            elderlySettings
                        }
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                }
            }
            .navigationTitle("Настройки")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        dismiss()
                    }
                }
            }
            .sheet(isPresented: $showTwoFactorSettings) {
                TwoFactorSettingsView(enabled: $twoFactorEnabled)
            }
            .sheet(isPresented: $showLoginHistory) {
                LoginHistoryView()
            }
            .alert("Смена пароля", isPresented: $showPasswordChange) {
                TextField("Новый пароль", text: .constant(""))
                TextField("Подтверждение", text: .constant(""))
                Button("Отмена", role: .cancel) {}
                Button("Изменить") {
                    // TODO: Реализовать смену пароля
                }
            } message: {
                Text("Введите новый пароль")
            }
        }
        .environmentObject(navigationManager)
    }
    
    // MARK: - Administrator Settings
    
    private var administratorSettings: some View {
        VStack(spacing: Spacing.m) {
            SettingsSection(title: "Роль и права") {
                SettingsRow(icon: "👑", title: "Администратор семьи", value: nil)
                Button(action: {
                    dismiss()
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                        navigationManager.navigateTo(.family)
                    }
                }) {
                    SettingsRow(icon: "👥", title: "Управление участниками", value: nil)
                }
                .buttonStyle(PlainButtonStyle())
                Button(action: {
                    dismiss()
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                        navigationManager.navigateTo(.settings)
                    }
                }) {
                    SettingsRow(icon: "🛡️", title: "Настройки защиты", value: nil)
                }
                .buttonStyle(PlainButtonStyle())
            }
            
            SettingsSection(title: "Уведомления") {
                ToggleRow(icon: "🔴", title: "Критические угрозы", isOn: $criticalThreatsEnabled)
                ToggleRow(icon: "👨‍👩‍👧‍👦", title: "Действия детей", isOn: $childrenActionsEnabled)
                ToggleRow(icon: "🔔", title: "Оповещения семьи", isOn: $familyAlertsEnabled)
            }
            
            SettingsSection(title: "Безопасность") {
                Button(action: {
                    showTwoFactorSettings = true
                }) {
                    SettingsRow(
                        icon: "🔐",
                        title: "Двухфакторная аутентификация",
                        value: twoFactorEnabled ? "Включена" : "Выключена"
                    )
                }
                .buttonStyle(PlainButtonStyle())
                Button(action: {
                    showPasswordChange = true
                }) {
                    SettingsRow(icon: "🔑", title: "Пароль учётной записи", value: "Изменить")
                }
                .buttonStyle(PlainButtonStyle())
                Button(action: {
                    showLoginHistory = true
                }) {
                    SettingsRow(icon: "📊", title: "История входов", value: nil)
                }
                .buttonStyle(PlainButtonStyle())
            }
        }
    }
    
    // MARK: - Parent Settings
    
    private var parentSettings: some View {
        VStack(spacing: Spacing.m) {
            SettingsSection(title: "Родительский контроль") {
                Button(action: {
                    dismiss()
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                        navigationManager.navigateTo(.family)
                    }
                }) {
                    SettingsRow(icon: "👨‍👩‍👧‍👦", title: "Управление детьми", value: nil)
                }
                .buttonStyle(PlainButtonStyle())
                SettingsRow(icon: "📱", title: "Разрешения для приложений", value: nil)
                SettingsRow(icon: "⏰", title: "Время экрана", value: nil)
            }
            
            SettingsSection(title: "Уведомления о детях") {
                ToggleRow(icon: "🚫", title: "Блокировки контента", isOn: $contentBlockingEnabled)
                ToggleRow(icon: "⏱️", title: "Превышение времени", isOn: $timeExceededEnabled)
                ToggleRow(icon: "✋", title: "Запросы доступа", isOn: $accessRequestsEnabled)
            }
            
            SettingsSection(title: "Уведомления") {
                ToggleRow(icon: "⚠️", title: "Угрозы безопасности", isOn: $securityThreatsEnabled)
                ToggleRow(icon: "🔄", title: "Обновления защиты", isOn: $protectionUpdatesEnabled)
            }
        }
    }
    
    // MARK: - Teenager Settings
    
    private var teenagerSettings: some View {
        VStack(spacing: Spacing.m) {
            SettingsSection(title: "Приватность") {
                SettingsRow(icon: "👁️", title: "Что могут видеть родители", value: nil)
                SettingsRow(icon: "📜", title: "История просмотров", value: nil)
                SettingsRow(icon: "📊", title: "Данные для аналитики", value: nil)
            }
            
            SettingsSection(title: "Уведомления") {
                ToggleRow(icon: "🚨", title: "Опасные сайты", isOn: $dangerousSitesEnabled)
                ToggleRow(icon: "⏰", title: "Превышение времени", isOn: $timeLimitEnabled)
                ToggleRow(icon: "🆕", title: "Новые функции защиты", isOn: $newFeaturesEnabled)
            }
        }
    }
    
    // MARK: - Child Settings
    
    private var childSettings: some View {
        VStack(spacing: Spacing.m) {
            SettingsSection(title: "Внешний вид") {
                SettingsRow(icon: "🎨", title: "Цвет темы", value: "Синий")
                SettingsRow(icon: "😊", title: "Иконка аватара", value: "👧")
                ToggleRow(icon: "🔔", title: "Звуки уведомлений", isOn: $soundsEnabled)
            }
            
            SettingsSection(title: "Игровые настройки") {
                SettingsRow(icon: "🦄", title: "Выбор единорога", value: nil)
                SettingsRow(icon: "⭐", title: "Уровень в игре", value: "5")
                SettingsRow(icon: "🏆", title: "Достижения", value: nil)
            }
        }
    }
    
    // MARK: - Elderly Settings
    
    private var elderlySettings: some View {
        VStack(spacing: Spacing.m) {
            SettingsSection(title: "Интерфейс") {
                ToggleRow(icon: "🔤", title: "Крупный шрифт", isOn: $largeFontEnabled)
                ToggleRow(icon: "🔘", title: "Яркие кнопки", isOn: $brightButtonsEnabled)
                ToggleRow(icon: "🔊", title: "Автовоспроизведение уведомлений", isOn: $autoPlayEnabled)
            }
            
            SettingsSection(title: "Безопасность") {
                ToggleRow(icon: "🔐", title: "Простая авторизация", isOn: $simpleAuthEnabled)
                ToggleRow(icon: "🤖", title: "Автоматическая защита", isOn: $autoProtectionEnabled)
                SettingsRow(icon: "🆘", title: "SOS-кнопка", value: "Настроить")
            }
            
            SettingsSection(title: "Уведомления") {
                ToggleRow(icon: "🚨", title: "Только критичные угрозы", isOn: $criticalOnlyEnabled)
                ToggleRow(icon: "🔤", title: "Крупный текст", isOn: $largeTextEnabled)
                ToggleRow(icon: "🔊", title: "Звуковые оповещения", isOn: $soundAlertsEnabled)
            }
        }
    }
}

// MARK: - Two Factor Settings View

struct TwoFactorSettingsView: View {
    @Binding var enabled: Bool
    @Environment(\.dismiss) private var dismiss
    @State private var code: String = ""
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                VStack(spacing: Spacing.l) {
                    Text("🔐")
                        .font(.system(size: 64))
                    
                    Text("Двухфакторная аутентификация")
                        .font(.h2)
                        .foregroundColor(.textPrimary)
                        .multilineTextAlignment(.center)
                    
                    Text(enabled ? "Уже включена" : "Сейчас выключена")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    
                    Toggle("Включить 2FA", isOn: $enabled)
                        .toggleStyle(SwitchToggleStyle(tint: .primaryBlue))
                    
                    if enabled {
                        VStack(spacing: Spacing.m) {
                            TextField("Код подтверждения", text: $code)
                                .textFieldStyle(RoundedBorderTextFieldStyle())
                            
                            Button("Сохранить") {
                                dismiss()
                            }
                            .buttonStyle(.borderedProminent)
                        }
                        .padding()
                    }
                    
                    Spacer()
                }
                .padding()
            }
            .navigationTitle("2FA")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        dismiss()
                    }
                }
            }
        }
    }
}

// MARK: - Login History View

struct LoginHistoryView: View {
    @Environment(\.dismiss) private var dismiss
    
    let history = [
        ("26.01.2025 14:30", "iPhone 13", "Успешный вход"),
        ("26.01.2025 10:15", "iPhone 13", "Успешный вход"),
        ("25.01.2025 18:45", "iPad Air", "Успешный вход"),
        ("25.01.2025 09:00", "iPhone 13", "Успешный вход"),
        ("24.01.2025 16:20", "iPhone 13", "Успешный вход")
    ]
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.m) {
                        ForEach(history, id: \.0) { date, device, status in
                            HStack {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(date)
                                        .font(.body)
                                        .foregroundColor(.textPrimary)
                                    
                                    Text(device)
                                        .font(.caption)
                                        .foregroundColor(.textSecondary)
                                }
                                
                                Spacer()
                                
                                Text(status)
                                    .font(.caption)
                                    .foregroundColor(.green)
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 6)
                                    .background(Color.green.opacity(0.2))
                                    .cornerRadius(12)
                            }
                            .padding()
                            .background(Color.white.opacity(0.05))
                            .cornerRadius(12)
                        }
                    }
                    .padding()
                }
            }
            .navigationTitle("История входов")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        dismiss()
                    }
                }
            }
        }
    }
}

// MARK: - Helper Views

struct SettingsSection<Content: View>: View {
    let title: String
    let content: Content
    
    init(title: String, @ViewBuilder content: () -> Content) {
        self.title = title
        self.content = content()
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(title)
                .font(.h3)
                .foregroundColor(.primaryBlue)
                .padding(.horizontal, Spacing.s)
            
            VStack(spacing: Spacing.xxs) {
                content
            }
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.5))
            )
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
        }
    }
}

struct SettingsRow: View {
    let icon: String
    let title: String
    let value: String?
    
    var body: some View {
        HStack {
            Text(icon)
                .font(.system(size: 24))
            
            Text(title)
                .font(.body)
                .foregroundColor(.textPrimary)
            
            Spacer()
            
            if let value = value {
                Text(value)
                    .font(.body)
                    .foregroundColor(.textSecondary)
            }
            
            Image(systemName: "chevron.right")
                .font(.system(size: 12))
                .foregroundColor(.textSecondary)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.small)
                .fill(Color.white.opacity(0.05))
        )
    }
}

struct ToggleRow: View {
    let icon: String?
    let title: String
    @Binding var isOn: Bool
    
    init(title: String, isOn: Binding<Bool>) {
        self.icon = nil
        self.title = title
        self._isOn = isOn
    }
    
    init(icon: String, title: String, isOn: Binding<Bool>) {
        self.icon = icon
        self.title = title
        self._isOn = isOn
    }
    
    var body: some View {
        HStack {
            if let icon = icon {
                Text(icon)
                    .font(.system(size: 24))
            }
            
            Text(title)
                .font(.body)
                .foregroundColor(.textPrimary)
            
            Spacer()
            
            Toggle("", isOn: $isOn)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.small)
                .fill(Color.white.opacity(0.05))
        )
    }
}

// MARK: - Preview

#if DEBUG
struct MemberSettingsModalView_Previews: PreviewProvider {
    static var previews: some View {
        MemberSettingsModalView(memberName: "Сергей", memberRole: "Администратор")
    }
}
#endif
