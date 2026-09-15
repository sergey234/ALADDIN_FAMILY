import SwiftUI

/// ⚙️ Member Settings Modal
/// Настройки участника семьи
struct MemberSettingsModalView: View {
    
    let memberName: String
    let memberRole: String
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // MARK: - State для переключателей (сохранение через @AppStorage)
    
    // Администратор
    @AppStorage("member_critical_threats_enabled") private var criticalThreatsEnabled: Bool = true
    @AppStorage("member_children_actions_enabled") private var childrenActionsEnabled: Bool = true
    @AppStorage("member_family_alerts_enabled") private var familyAlertsEnabled: Bool = true
    @AppStorage("member_two_factor_enabled") private var twoFactorEnabled: Bool = true
    @State private var showTwoFactorSettings: Bool = false
    @State private var showPasswordChange: Bool = false
    @State private var showLoginHistory: Bool = false
    
    // Родитель
    @AppStorage("member_content_blocking_enabled") private var contentBlockingEnabled: Bool = true
    @AppStorage("member_time_exceeded_enabled") private var timeExceededEnabled: Bool = true
    @AppStorage("member_access_requests_enabled") private var accessRequestsEnabled: Bool = true
    @AppStorage("member_security_threats_enabled") private var securityThreatsEnabled: Bool = true
    @AppStorage("member_protection_updates_enabled") private var protectionUpdatesEnabled: Bool = true
    
    // Подросток
    @AppStorage("member_dangerous_sites_enabled") private var dangerousSitesEnabled: Bool = true
    @AppStorage("member_time_limit_enabled") private var timeLimitEnabled: Bool = true
    @AppStorage("member_new_features_enabled") private var newFeaturesEnabled: Bool = false
    
    // Ребёнок
    @AppStorage("member_sounds_enabled") private var soundsEnabled: Bool = true
    
    // Люди 60+
    @AppStorage("member_large_font_enabled") private var largeFontEnabled: Bool = true
    @AppStorage("member_bright_buttons_enabled") private var brightButtonsEnabled: Bool = true
    @AppStorage("member_auto_play_enabled") private var autoPlayEnabled: Bool = true
    @AppStorage("member_simple_auth_enabled") private var simpleAuthEnabled: Bool = true
    @AppStorage("member_auto_protection_enabled") private var autoProtectionEnabled: Bool = true
    @AppStorage("member_critical_only_enabled") private var criticalOnlyEnabled: Bool = true
    @AppStorage("member_large_text_enabled") private var largeTextEnabled: Bool = true
    @AppStorage("member_sound_alerts_enabled") private var soundAlertsEnabled: Bool = true
    
    var body: some View {
        NavigationView {
            ZStack {
                // Фон
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView(.vertical, showsIndicators: true) {
                    VStack(spacing: Spacing.m) {
                        // Заголовок
                        VStack(spacing: Spacing.xs) {
                            Text("⚙️")
                                .font(.system(size: 64))
                            
                            Text(localizationManager.localized("member_settings_title"))
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
            .navigationTitle(localizationManager.localized("member_settings_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("companion_conversation_done")) {
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
            .alert(localizationManager.localized("member_settings_change_password_title"), isPresented: $showPasswordChange) {
                TextField("Новый пароль", text: .constant(""))
                TextField("Подтверждение", text: .constant(""))
                Button(localizationManager.localized("language_settings_cancel"), role: .cancel) {}
                Button(localizationManager.localized("rewards_modal_edit")) {
                    // TODO: Реализовать смену пароля
                }
            } message: {
                Text(localizationManager.localized("member_settings_enter_new_password"))
            }
        }
        .environmentObject(navigationManager)
    }
    
    // MARK: - Administrator Settings
    
    private var administratorSettings: some View {
        VStack(spacing: Spacing.m) {
            SettingsSection(title: localizationManager.localized("member_settings_role_and_rights")) {
                SettingsRow(icon: "👑", title: localizationManager.localized("member_settings_family_admin"), value: nil)
                Button(action: {
                    dismiss()
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                        navigationManager.navigateTo(.family)
                    }
                }) {
                    SettingsRow(icon: "👥", title: localizationManager.localized("member_settings_manage_members"), value: nil)
                }
                .buttonStyle(PlainButtonStyle())
                Button(action: {
                    dismiss()
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                        navigationManager.navigateTo(.settings)
                    }
                }) {
                    SettingsRow(icon: "🛡️", title: localizationManager.localized("nav_screen_threat_settings"), value: nil)
                }
                .buttonStyle(PlainButtonStyle())
            }
            
            SettingsSection(title: localizationManager.localized("nav_screen_notifications")) {
                ToggleRow(icon: "🔴", title: localizationManager.localized("member_settings_critical_threats"), isOn: $criticalThreatsEnabled)
                ToggleRow(icon: "👨‍👩‍👧‍👦", title: localizationManager.localized("member_settings_children_actions"), isOn: $childrenActionsEnabled)
                ToggleRow(icon: "🔔", title: localizationManager.localized("member_settings_family_alerts"), isOn: $familyAlertsEnabled)
            }
            
            SettingsSection(title: localizationManager.localized("profile_security_title")) {
                Button(action: {
                    showTwoFactorSettings = true
                }) {
                    SettingsRow(
                        icon: "🔐",
                        title: localizationManager.localized("member_settings_two_factor_auth"),
                        value: twoFactorEnabled ? "Включена" : "Выключена"
                    )
                }
                .buttonStyle(PlainButtonStyle())
                Button(action: {
                    showPasswordChange = true
                }) {
                    SettingsRow(icon: "🔑", title: localizationManager.localized("member_settings_account_password"), value: localizationManager.localized("rewards_modal_edit"))
                }
                .buttonStyle(PlainButtonStyle())
                Button(action: {
                    showLoginHistory = true
                }) {
                    SettingsRow(icon: "📊", title: localizationManager.localized("member_settings_login_history"), value: nil)
                }
                .buttonStyle(PlainButtonStyle())
            }
        }
    }
    
    // MARK: - Parent Settings
    
    private var parentSettings: some View {
        VStack(spacing: Spacing.m) {
            SettingsSection(title: localizationManager.localized("nav_screen_parental_control")) {
                Button(action: {
                    dismiss()
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                        navigationManager.navigateTo(.family)
                    }
                }) {
                    SettingsRow(icon: "👨‍👩‍👧‍👦", title: localizationManager.localized("member_settings_manage_children"), value: nil)
                }
                .buttonStyle(PlainButtonStyle())
                SettingsRow(icon: "📱", title: localizationManager.localized("member_settings_app_permissions"), value: nil)
                SettingsRow(icon: "⏰", title: localizationManager.localized("family_screen_time"), value: nil)
            }
            
            SettingsSection(title: localizationManager.localized("member_settings_children_notifications")) {
                ToggleRow(icon: "🚫", title: localizationManager.localized("member_settings_content_blocking"), isOn: $contentBlockingEnabled)
                ToggleRow(icon: "⏱️", title: localizationManager.localized("member_settings_time_exceeded"), isOn: $timeExceededEnabled)
                ToggleRow(icon: "✋", title: localizationManager.localized("member_settings_access_requests"), isOn: $accessRequestsEnabled)
            }
            
            SettingsSection(title: localizationManager.localized("nav_screen_notifications")) {
                ToggleRow(icon: "⚠️", title: localizationManager.localized("member_settings_security_threats"), isOn: $securityThreatsEnabled)
                ToggleRow(icon: "🔄", title: localizationManager.localized("member_settings_protection_updates"), isOn: $protectionUpdatesEnabled)
            }
        }
    }
    
    // MARK: - Teenager Settings
    
    private var teenagerSettings: some View {
        VStack(spacing: Spacing.m) {
            SettingsSection(title: localizationManager.localized("member_settings_privacy")) {
                SettingsRow(icon: "👁️", title: localizationManager.localized("member_settings_what_parents_see"), value: nil)
                SettingsRow(icon: "📜", title: localizationManager.localized("member_settings_browsing_history"), value: nil)
                SettingsRow(icon: "📊", title: localizationManager.localized("member_settings_analytics_data"), value: nil)
            }
            
            SettingsSection(title: localizationManager.localized("nav_screen_notifications")) {
                ToggleRow(icon: "🚨", title: localizationManager.localized("tariffs_threat_internet_1"), isOn: $dangerousSitesEnabled)
                ToggleRow(icon: "⏰", title: localizationManager.localized("member_settings_time_exceeded"), isOn: $timeLimitEnabled)
                ToggleRow(icon: "🆕", title: localizationManager.localized("member_settings_new_protection_features"), isOn: $newFeaturesEnabled)
            }
        }
    }
    
    // MARK: - Child Settings
    
    private var childSettings: some View {
        VStack(spacing: Spacing.m) {
            SettingsSection(title: localizationManager.localized("member_settings_appearance")) {
                SettingsRow(
                    icon: "🎨",
                    title: localizationManager.localized("member_settings_theme_color"),
                    value: localizationManager.localized("member_settings_color_blue")
                )
                SettingsRow(icon: "😊", title: localizationManager.localized("member_settings_avatar_icon"), value: "👧")
                ToggleRow(icon: "🔔", title: localizationManager.localized("member_settings_notification_sounds"), isOn: $soundsEnabled)
            }
            
            SettingsSection(title: localizationManager.localized("member_settings_game_settings")) {
                SettingsRow(icon: "🦄", title: localizationManager.localized("member_settings_unicorn_choice"), value: nil)
                SettingsRow(icon: "⭐", title: localizationManager.localized("member_settings_game_level"), value: "5")
                SettingsRow(icon: "🏆", title: localizationManager.localized("child_rewards_tab_achievements"), value: nil)
            }
        }
    }
    
    // MARK: - Elderly Settings
    
    private var elderlySettings: some View {
        VStack(spacing: Spacing.m) {
            SettingsSection(title: localizationManager.localized("member_settings_interface")) {
                ToggleRow(icon: "🔤", title: localizationManager.localized("member_settings_large_font"), isOn: $largeFontEnabled)
                ToggleRow(icon: "🔘", title: localizationManager.localized("member_settings_bright_buttons"), isOn: $brightButtonsEnabled)
                ToggleRow(icon: "🔊", title: localizationManager.localized("member_settings_autoplay_notifications"), isOn: $autoPlayEnabled)
            }
            
            SettingsSection(title: localizationManager.localized("profile_security_title")) {
                ToggleRow(icon: "🔐", title: localizationManager.localized("member_settings_simple_auth"), isOn: $simpleAuthEnabled)
                ToggleRow(icon: "🤖", title: localizationManager.localized("member_settings_auto_protection"), isOn: $autoProtectionEnabled)
                SettingsRow(
                    icon: "🆘",
                    title: localizationManager.localized("tariff_parental_location_sos_family"),
                    value: localizationManager.localized("family_configure")
                )
            }
            
            SettingsSection(title: localizationManager.localized("nav_screen_notifications")) {
                ToggleRow(icon: "🚨", title: localizationManager.localized("member_settings_critical_only"), isOn: $criticalOnlyEnabled)
                ToggleRow(icon: "🔤", title: localizationManager.localized("member_settings_large_text"), isOn: $largeTextEnabled)
                ToggleRow(icon: "🔊", title: localizationManager.localized("member_settings_sound_alerts"), isOn: $soundAlertsEnabled)
            }
        }
    }
}

// MARK: - Two Factor Settings View

struct TwoFactorSettingsView: View {
    @Binding var enabled: Bool
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var code: String = ""
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                VStack(spacing: Spacing.l) {
                    Text("🔐")
                        .font(.system(size: 64))
                    
                    Text(localizationManager.localized("member_settings_two_factor_auth"))
                        .font(.h2)
                        .foregroundColor(.textPrimary)
                        .multilineTextAlignment(.center)
                    
                    Text(enabled
                         ? localizationManager.localized("member_settings_2fa_already_on")
                         : localizationManager.localized("member_settings_2fa_currently_off"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    
                    Toggle("Включить 2FA", isOn: $enabled)
                        .toggleStyle(SwitchToggleStyle(tint: .primaryBlue))
                    
                    if enabled {
                        VStack(spacing: Spacing.m) {
                            TextField("Код подтверждения", text: $code)
                                .textFieldStyle(RoundedBorderTextFieldStyle())
                            
                            Button(localizationManager.localized("profile_edit_save")) {
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
            .navigationTitle(localizationManager.localized("member_settings_2fa_short"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("companion_conversation_done")) {
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
    @EnvironmentObject private var localizationManager: LocalizationManager
    
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
                
                ScrollView(.vertical, showsIndicators: true) {
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
            .navigationTitle(localizationManager.localized("member_settings_login_history"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("companion_conversation_done")) {
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
