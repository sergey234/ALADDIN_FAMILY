import SwiftUI
import WebKit

/**
 * 📋 Privacy Policy Screen
 * Политика конфиденциальности
 * ОБЯЗАТЕЛЬНА для App Store!
 */

struct PrivacyPolicyScreen: View {
    
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var expandedSection: PrivacySectionType? = nil
    @State private var selectedTab: PrivacyTab = .main
    
    var body: some View {
        ZStack {
            StormMeshBackground(variant: .legal)
                .accessibilityElement()
                .accessibilityLabel(localizationManager.localized("privacy_policy_background"))
            
            VStack(spacing: 0) {
                // Navigation Bar
                ALADDINNavigationBar(
                    title: localizationManager.localized("privacy_policy_title"),
                    subtitle: localizationManager.localized("privacy_policy_subtitle"),
                    showBackButton: true,
                    showProfileButton: false,
                    showListButton: false,
                    onBack: {
                        // ✅ ИСПРАВЛЕНО: Правильная навигация назад для sheet
                        // dismiss() закрывает sheet и возвращает на предыдущий экран
                        dismiss()
                    }
                )
                
                // Main Content
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Header Card
                        headerCard
                        
                        // Tabs
                        tabsView
                        
                        // Content based on selected tab
                        if selectedTab == .main {
                            mainSectionsContent
                        } else {
                            networkProtectionSectionsContent
                        }
                        
                        // Spacer
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
        .id("privacy_policy_lang_\(localizationManager.currentLanguage.rawValue)")
        .task {
            print("🚨 PrivacyPolicyScreen загружен!")
        }
    }
    
    // MARK: - Header Card
    
    private var headerCard: some View {
        VStack(spacing: Spacing.s) {
            HStack {
                Text("🛡️")
                    .font(.system(size: 40))
                
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(localizationManager.localized("privacy_policy_header_title"))
                        .font(.h2)
                        .foregroundColor(.textPrimary)
                    
                    Text(localizationManager.localized("privacy_policy_version"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
            }
            
            Text(localizationManager.localized("privacy_policy_intro"))
                .font(.body)
                .foregroundColor(.textPrimary)
                .multilineTextAlignment(.leading)
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .stroke(Color.primaryBlue.opacity(0.3), lineWidth: 1)
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Tabs View
    
    private var tabsView: some View {
        HStack(spacing: 0) {
            tabButton(title: PrivacyTab.main.localizedTitle(localizationManager), tab: .main)
            tabButton(title: PrivacyTab.networkProtection.localizedTitle(localizationManager), tab: .networkProtection)
        }
        .stormGlassCard(cornerRadius: CornerRadius.medium)
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func tabButton(title: String, tab: PrivacyTab) -> some View {
        Button(action: {
            withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                selectedTab = tab
            }
            HapticFeedback.selection()
        }) {
            Text(title)
                .font(.body)
                .foregroundColor(selectedTab == tab ? .textPrimary : .textSecondary)
                .frame(maxWidth: .infinity)
                .padding(.vertical, Spacing.s)
                .background(
                    Group {
                        if selectedTab == tab {
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(Color.secondaryGold.opacity(0.3))
                        }
                    }
                )
        }
    }
    
    // MARK: - Main Sections Content
    
    private var mainSectionsContent: some View {
        VStack(spacing: Spacing.m) {
            ForEach(PrivacyMainSection.allCases, id: \.self) { section in
                privacySectionCard(section: section)
            }
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Network Protection Sections Content
    
    private var networkProtectionSectionsContent: some View {
        VStack(spacing: Spacing.m) {
            ForEach(NetworkProtectionSection.allCases, id: \.self) { section in
                networkProtectionSectionCard(section: section)
            }
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Privacy Section Card
    
    private func privacySectionCard(section: PrivacyMainSection) -> some View {
        VStack(spacing: 0) {
            Button(action: {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                    if expandedSection == .main(section) {
                        expandedSection = nil
                    } else {
                        expandedSection = .main(section)
                    }
                }
                HapticFeedback.selection()
            }) {
                HStack(spacing: Spacing.m) {
                    Text(section.emoji)
                        .font(.system(size: 28))
                    
                    VStack(alignment: .leading, spacing: Spacing.xxs) {
                        Text(section.localizedTitle(localizationManager))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                            .multilineTextAlignment(.leading)
                        
                        Text(section.localizedSubtitle(localizationManager))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.leading)
                    }
                    
                    Spacer()
                    
                    Image(systemName: expandedSection == .main(section) ? "chevron.up" : "chevron.down")
                        .foregroundColor(.secondaryGold)
                        .font(.headline)
                        .frame(width: 24)
                }
                .padding(Spacing.m)
            }
            
            if expandedSection == .main(section) {
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Divider()
                        .background(Color.textTertiary)
                    
                    ForEach(section.localizedContent(localizationManager), id: \.self) { item in
                        HStack(alignment: .top, spacing: Spacing.xs) {
                            Circle()
                                .fill(Color.secondaryGold.opacity(0.5))
                                .frame(width: 6, height: 6)
                                .padding(.top, 6)
                            
                            Text(item)
                                .font(.body)
                                .foregroundColor(.textPrimary)
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                    }
                }
                .padding(.horizontal, Spacing.m)
                .padding(.bottom, Spacing.m)
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .stormGlassCard(cornerRadius: CornerRadius.large)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .stroke(Color.secondaryGold.opacity(0.3), lineWidth: 1)
        )
    }
    
    // MARK: - Network Protection Section Card
    
    private func networkProtectionSectionCard(section: NetworkProtectionSection) -> some View {
        VStack(spacing: 0) {
            Button(action: {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                    if expandedSection == .networkProtection(section) {
                        expandedSection = nil
                    } else {
                        expandedSection = .networkProtection(section)
                    }
                }
                HapticFeedback.selection()
            }) {
                HStack(spacing: Spacing.m) {
                    Text(section.emoji)
                        .font(.system(size: 28))
                    
                    VStack(alignment: .leading, spacing: Spacing.xxs) {
                        Text(section.localizedTitle(localizationManager))
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                            .multilineTextAlignment(.leading)
                        
                        Text(section.localizedSubtitle(localizationManager))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.leading)
                    }
                    
                    Spacer()
                    
                    Image(systemName: expandedSection == .networkProtection(section) ? "chevron.up" : "chevron.down")
                        .foregroundColor(.primaryBlue)
                        .font(.headline)
                        .frame(width: 24)
                }
                .padding(Spacing.m)
            }
            
            if expandedSection == .networkProtection(section) {
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Divider()
                        .background(Color.textTertiary)
                    
                    ForEach(section.localizedContent(localizationManager), id: \.self) { item in
                        HStack(alignment: .top, spacing: Spacing.xs) {
                            Circle()
                                .fill(Color.primaryBlue.opacity(0.5))
                                .frame(width: 6, height: 6)
                                .padding(.top, 6)
                            
                            Text(item)
                                .font(.body)
                                .foregroundColor(.textPrimary)
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                    }
                }
                .padding(.horizontal, Spacing.m)
                .padding(.bottom, Spacing.m)
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .stormGlassCard(cornerRadius: CornerRadius.large)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .stroke(Color.primaryBlue.opacity(0.3), lineWidth: 1)
        )
    }
    
    // MARK: - Fallback Content
    
    private var fallbackPrivacyContent: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("privacy_policy_header_title"))
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Text(localizationManager.localized("privacy_policy_last_update"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    privacySection(
                        title: localizationManager.localized("privacy_policy_section_1"),
                        content: localizationManager.localized("privacy_policy_section_1_content")
                    )
                    
                    privacySection(
                        title: localizationManager.localized("privacy_policy_section_2"),
                        content: localizationManager.localized("privacy_policy_section_2_content")
                    )
                    
                    privacySection(
                        title: localizationManager.localized("privacy_policy_section_3"),
                        content: localizationManager.localized("privacy_policy_section_3_content")
                    )
                    
                    privacySection(
                        title: localizationManager.localized("privacy_policy_section_4"),
                        content: localizationManager.localized("privacy_policy_section_4_content")
                    )
                    
                    privacySection(
                        title: localizationManager.localized("privacy_policy_section_5"),
                        content: localizationManager.localized("privacy_policy_section_5_content")
                    )
                }
            }
            .padding(Spacing.m)
        }
        .stormGlassCard(cornerRadius: 12)
    }
    
    private func privacySection(title: String, content: String) -> some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            Text(title)
                .font(.bodyBold)
                .foregroundColor(.primaryBlue)
            
            Text(content)
                .font(.body)
                .foregroundColor(.textPrimary)
                .lineSpacing(4)
        }
        .padding(Spacing.s)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
    }
}

/**
 * 🌐 Web View Wrapper
 * UIKit WebView обёрнутый в SwiftUI
 */

struct WebView: UIViewRepresentable {
    
    let url: URL
    
    func makeUIView(context: Context) -> WKWebView {
        let webView = WKWebView()
        webView.backgroundColor = .clear
        webView.isOpaque = false
        // Note: LocalizationManager недоступен в UIViewRepresentable, используем дефолтные значения
        // В будущем можно передать через параметр, но для accessibility это не критично
        webView.accessibilityLabel = "Веб-страница политики конфиденциальности"
        webView.accessibilityHint = "Прокрутите для просмотра содержимого политики конфиденциальности"
        webView.load(URLRequest(url: url))
        return webView
    }
    
    func updateUIView(_ uiView: WKWebView, context: Context) {
        // No updates needed
    }
}

// MARK: - Preview

struct PrivacyPolicyScreen_Previews: PreviewProvider {
    static var previews: some View {
        PrivacyPolicyScreen()
    }
}

// MARK: - Enums & Models

enum PrivacyTab: String, CaseIterable {
    case main = "Основное"
    case networkProtection = "Защита сети"
    
    func localizedTitle(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .main: return localizationManager.localized("privacy_policy_tab_main")
        case .networkProtection: return localizationManager.localized("privacy_policy_tab_network_protection")
        }
    }
}

enum PrivacySectionType: Equatable {
    case main(PrivacyMainSection)
    case networkProtection(NetworkProtectionSection)
}

enum PrivacyMainSection: String, CaseIterable {
    case general = "Общие положения"
    case principles = "Принципы работы"
    case auth = "Регистрация и аутентификация"
    case crashDiagnostics = "Диагностика сбоев и поддержка в Telegram"
    case notCollected = "Данные, НЕ собираемые"
    case collected = "Данные, собираемые (обезличенные)"
    case purposes = "Цели обработки"
    case protection = "Меры защиты"
    case rights = "Права пользователей"
    case storage = "Сроки хранения"
    case transfer = "Трансграничная передача"
    case responsibility = "Ответственность"
    case contacts = "Контакты"
    case wellness = "Эмоциональная поддержка (Wellness)"
    case final = "Заключительные положения"
    
    var emoji: String {
        switch self {
        case .general: return "📋"
        case .principles: return "⭐"
        case .auth: return "🔐"
        case .crashDiagnostics: return "💬"
        case .notCollected: return "❌"
        case .collected: return "✅"
        case .purposes: return "🎯"
        case .protection: return "🛡️"
        case .rights: return "⚖️"
        case .storage: return "⏰"
        case .transfer: return "🌐"
        case .responsibility: return "🤝"
        case .contacts: return "📞"
        case .wellness: return "💜"
        case .final: return "📜"
        }
    }
    
    func localizedTitle(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .general: return localizationManager.localized("privacy_policy_section_general")
        case .principles: return localizationManager.localized("privacy_policy_section_principles")
        case .auth: return localizationManager.localized("privacy_policy_section_auth")
        case .crashDiagnostics: return localizationManager.localized("privacy_policy_section_crash_diagnostics")
        case .notCollected: return localizationManager.localized("privacy_policy_section_not_collected")
        case .collected: return localizationManager.localized("privacy_policy_section_collected")
        case .purposes: return localizationManager.localized("privacy_policy_section_purposes")
        case .protection: return localizationManager.localized("privacy_policy_section_protection")
        case .rights: return localizationManager.localized("privacy_policy_section_rights")
        case .storage: return localizationManager.localized("privacy_policy_section_storage")
        case .transfer: return localizationManager.localized("privacy_policy_section_transfer")
        case .responsibility: return localizationManager.localized("privacy_policy_section_responsibility")
        case .contacts: return localizationManager.localized("privacy_policy_section_contacts")
        case .wellness: return localizationManager.localized("privacy_policy_section_wellness")
        case .final: return localizationManager.localized("privacy_policy_section_final")
        }
    }
    
    func localizedSubtitle(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .general: return localizationManager.localized("privacy_policy_section_general_subtitle")
        case .principles: return localizationManager.localized("privacy_policy_section_principles_subtitle")
        case .auth: return localizationManager.localized("privacy_policy_section_auth_subtitle")
        case .crashDiagnostics: return localizationManager.localized("privacy_policy_section_crash_diagnostics_subtitle")
        case .notCollected: return localizationManager.localized("privacy_policy_section_not_collected_subtitle")
        case .collected: return localizationManager.localized("privacy_policy_section_collected_subtitle")
        case .purposes: return localizationManager.localized("privacy_policy_section_purposes_subtitle")
        case .protection: return localizationManager.localized("privacy_policy_section_protection_subtitle")
        case .rights: return localizationManager.localized("privacy_policy_section_rights_subtitle")
        case .storage: return localizationManager.localized("privacy_policy_section_storage_subtitle")
        case .transfer: return localizationManager.localized("privacy_policy_section_transfer_subtitle")
        case .responsibility: return localizationManager.localized("privacy_policy_section_responsibility_subtitle")
        case .contacts: return localizationManager.localized("privacy_policy_section_contacts_subtitle")
        case .wellness: return localizationManager.localized("privacy_policy_section_wellness_subtitle")
        case .final: return localizationManager.localized("privacy_policy_section_final_subtitle")
        }
    }
    
    var title: String {
        return rawValue
    }
    
    var subtitle: String {
        // Deprecated: используйте localizedSubtitle вместо этого
        switch self {
        case .general: return "Правовая основа и применение"
        case .principles: return "4 основных принципа ALADDIN AI"
        case .auth: return "Анонимная регистрация через QR"
        case .crashDiagnostics: return "Бот @AladdinchatAI_bot, только по вашей команде"
        case .notCollected: return "Список данных, которые мы НЕ собираем"
        case .collected: return "Обезличенные данные для безопасности"
        case .purposes: return "Для чего используются данные"
        case .protection: return "Технические и организационные меры"
        case .rights: return "Ваши права на данные"
        case .storage: return "Сколько времени хранятся данные"
        case .transfer: return "Передача данных за границу"
        case .responsibility: return "Гарантии Оператора"
        case .contacts: return "Техподдержка и вопросы"
        case .wellness: return "Самопомощь и цифровой друг (ИИ)"
        case .final: return "Вступление в силу"
        }
    }
    
    func localizedContent(_ localizationManager: LocalizationManager) -> [String] {
        switch self {
        case .general:
            return [
                localizationManager.localized("privacy_policy_section_general_content_1"),
                localizationManager.localized("privacy_policy_section_general_content_2"),
                localizationManager.localized("privacy_policy_section_general_content_3")
            ]
        case .principles:
            return [
                localizationManager.localized("privacy_policy_section_principles_content_1"),
                localizationManager.localized("privacy_policy_section_principles_content_2"),
                localizationManager.localized("privacy_policy_section_principles_content_3"),
                localizationManager.localized("privacy_policy_section_principles_content_4")
            ]
        case .auth:
            return [
                localizationManager.localized("privacy_policy_section_auth_content_1"),
                localizationManager.localized("privacy_policy_section_auth_content_2"),
                localizationManager.localized("privacy_policy_section_auth_content_3"),
                localizationManager.localized("privacy_policy_section_auth_content_4"),
                localizationManager.localized("privacy_policy_section_auth_content_5"),
                localizationManager.localized("privacy_policy_section_auth_content_6")
            ]
        case .crashDiagnostics:
            return [
                localizationManager.localized("privacy_policy_section_crash_diagnostics_content_1"),
                localizationManager.localized("privacy_policy_section_crash_diagnostics_content_2"),
                localizationManager.localized("privacy_policy_section_crash_diagnostics_content_3"),
                localizationManager.localized("privacy_policy_section_crash_diagnostics_content_4"),
                localizationManager.localized("privacy_policy_section_crash_diagnostics_content_5"),
                localizationManager.localized("privacy_policy_section_crash_diagnostics_content_6")
            ]
        case .notCollected:
            return [
                localizationManager.localized("privacy_policy_section_not_collected_content_1"),
                localizationManager.localized("privacy_policy_section_not_collected_content_2"),
                localizationManager.localized("privacy_policy_section_not_collected_content_3"),
                localizationManager.localized("privacy_policy_section_not_collected_content_4"),
                localizationManager.localized("privacy_policy_section_not_collected_content_5")
            ]
        case .collected:
            return [
                localizationManager.localized("privacy_policy_section_collected_content_1"),
                localizationManager.localized("privacy_policy_section_collected_content_2"),
                localizationManager.localized("privacy_policy_section_collected_content_3"),
                localizationManager.localized("privacy_policy_section_collected_content_4"),
                localizationManager.localized("privacy_policy_section_collected_content_5")
            ]
        case .purposes:
            return [
                localizationManager.localized("privacy_policy_section_purposes_content_1"),
                localizationManager.localized("privacy_policy_section_purposes_content_2"),
                localizationManager.localized("privacy_policy_section_purposes_content_3"),
                localizationManager.localized("privacy_policy_section_purposes_content_4"),
                localizationManager.localized("privacy_policy_section_purposes_content_5")
            ]
        case .protection:
            return [
                localizationManager.localized("privacy_policy_section_protection_content_1"),
                localizationManager.localized("privacy_policy_section_protection_content_2"),
                localizationManager.localized("privacy_policy_section_protection_content_3"),
                localizationManager.localized("privacy_policy_section_protection_content_4"),
                localizationManager.localized("privacy_policy_section_protection_content_5"),
                localizationManager.localized("privacy_policy_section_protection_content_6"),
                localizationManager.localized("privacy_policy_section_protection_content_7"),
                localizationManager.localized("privacy_policy_section_protection_content_8")
            ]
        case .rights:
            return [
                localizationManager.localized("privacy_policy_section_rights_content_1"),
                localizationManager.localized("privacy_policy_section_rights_content_2"),
                localizationManager.localized("privacy_policy_section_rights_content_3"),
                localizationManager.localized("privacy_policy_section_rights_content_4")
            ]
        case .storage:
            return [
                localizationManager.localized("privacy_policy_section_storage_content_1"),
                localizationManager.localized("privacy_policy_section_storage_content_2"),
                localizationManager.localized("privacy_policy_section_storage_content_3"),
                localizationManager.localized("privacy_policy_section_storage_content_4")
            ]
        case .transfer:
            return [
                localizationManager.localized("privacy_policy_section_transfer_content_1"),
                localizationManager.localized("privacy_policy_section_transfer_content_2"),
                localizationManager.localized("privacy_policy_section_transfer_content_3")
            ]
        case .responsibility:
            return [
                localizationManager.localized("privacy_policy_section_responsibility_content_1"),
                localizationManager.localized("privacy_policy_section_responsibility_content_2"),
                localizationManager.localized("privacy_policy_section_responsibility_content_3"),
                localizationManager.localized("privacy_policy_section_responsibility_content_4")
            ]
        case .contacts:
            return [
                localizationManager.localized("privacy_policy_section_contacts_content_1"),
                localizationManager.localized("privacy_policy_section_contacts_content_2"),
                localizationManager.localized("privacy_policy_section_contacts_content_4")
            ]
        case .wellness:
            return [
                localizationManager.localized("privacy_policy_section_wellness_content_1"),
                localizationManager.localized("privacy_policy_section_wellness_content_2"),
                localizationManager.localized("privacy_policy_section_wellness_content_3"),
                localizationManager.localized("privacy_policy_section_wellness_content_4"),
                localizationManager.localized("privacy_policy_section_wellness_content_5"),
                localizationManager.localized("privacy_policy_section_wellness_content_6"),
                localizationManager.localized("privacy_policy_section_wellness_content_7")
            ]
        case .final:
            return [
                localizationManager.localized("privacy_policy_section_final_content_1"),
                localizationManager.localized("privacy_policy_section_final_content_2"),
                localizationManager.localized("privacy_policy_section_final_content_3"),
                localizationManager.localized("privacy_policy_section_final_content_4")
            ]
        }
    }
    
    var content: [String] {
        // Deprecated: используйте localizedContent вместо этого
        switch self {
        case .general:
            return [
                "Правовая основа: ФЗ-152 «О персональных данных»",
                "ALADDIN AI спроектирована БЕЗ сбора персональных данных",
                "Применение: мобильное приложение и веб-интерфейс"
            ]
        case .principles:
            return [
                "Принцип анонимности: НЕ собираем, НЕ обрабатываем, НЕ храним ПД",
                "Принцип локальной обработки: всё на вашем устройстве",
                "Принцип обезличивания: автоматическое удаление привязки",
                "Принцип минимальной необходимости: только для безопасности"
            ]
        case .auth:
            return [
                "Анонимная регистрация: роль + возрастная группа",
                "Локальная аутентификация: PIN, Face ID (на устройстве)",
                "Семейные группы: через QR-код без имён",
                "Face ID: Данные лица НЕ собираются — приложение использует только встроенную функцию iOS для локальной аутентификации",
                "Face ID: Данные лица НЕ передаются третьим лицам — вся обработка происходит локально на устройстве в Secure Enclave",
                "Face ID: Данные лица НЕ хранятся на наших серверах — они остаются только на устройстве пользователя и удаляются при удалении приложения"
            ]
        case .crashDiagnostics:
            return [
                "Бот @AladdinchatAI_bot (отображаемое имя может быть «AladdinAi_bot»).",
                "Отправка логов только по вашей инициативе.",
                "Пароли, карты, SMS, контакты, медиа через этот экран не собираем.",
                "В отчёте — технические данные, уже записанные на устройстве; лишнее можно стереть вручную.",
                "После отправки в Telegram действуют правила Telegram.",
                "Цель — исправление сбоев; не для рекламы и не продаём."
            ]
        case .notCollected:
            return [
                "Имена, фамилии, даты рождения",
                "Адреса, телефоны, email",
                "Паспортные данные, СНИЛС, ИНН",
                "Финансовые и медицинские данные",
                "Политические и религиозные взгляды"
            ]
        case .collected:
            return [
                "Анонимные ID сессий (хеши)",
                "ID устройств (без привязки к владельцу)",
                "Тип устройства и ОС",
                "Статистика угроз (обезличенная)",
                "Агрегированная аналитика"
            ]
        case .purposes:
            return [
                "Обеспечение безопасности пользователей",
                "Обнаружение и блокировка угроз",
                "Предоставление образовательного контента",
                "Мониторинг семейной безопасности",
                "Анализ эффективности защиты"
            ]
        case .protection:
            return [
                "Шифрование всех данных",
                "Анонимизация на этапе сбора",
                "Локальное хранение",
                "Регулярные обновления безопасности",
                "Обучение персонала принципам анонимности",
                "Регулярный аудит системы"
            ]
        case .rights:
            return [
                "Получать информацию о данных",
                "Требовать удаления всех данных",
                "Отозвать согласие на обработку",
                "Получать отчёты в анонимном виде"
            ]
        case .storage:
            return [
                "Анонимные сессии: 24 часа",
                "Статистика угроз: 30 дней (обезличенная)",
                "Агрегированная аналитика: 1 год",
                "Локальные данные: до удаления приложения"
            ]
        case .transfer:
            return [
                "НЕ осуществляем трансграничную передачу ПД",
                "Не собираем персональные данные",
                "Обезличенные данные для обновлений"
            ]
        case .responsibility:
            return [
                "Отсутствие сбора персональных данных",
                "Анонимная модель аккаунта (роль и возрастная группа)",
                "Соответствие требованиям 152-ФЗ",
                "Регулярный аудит системы"
            ]
        case .contacts:
            return [
                "Telegram: @AladdinchatAI_bot",
                "Телефон: +7 (927) 005-15-77",
                "Чат в приложении ALADDIN"
            ]
        case .wellness:
            return [
                "Раздел «Настроение и поддержка» — инструменты самопомощи, не медицинская услуга",
                "Данные wellness (настроение, ответы упражнений) хранятся в привязке к анонимному аккаунту",
                "Родитель не видит дословный текст подростка в companion/wellness",
                "При признаках кризиса — подсказки обратиться к взрослому или на линию помощи",
                "Можно отозвать согласие и удалить данные в настройках раздела",
                "Не заменяет психотерапию, психиатрию и экстренную помощь"
            ]
        case .final:
            return [
                "Действует бессрочно до замены",
                "Актуальная версия в приложении",
                "Изменения через уведомления",
                "Продолжение использования = согласие"
            ]
        }
    }
}

enum NetworkProtectionSection: String, CaseIterable {
    case noLogs = "NO-LOGS POLICY"
    case encryption = "Технологии шифрования"
    
    var emoji: String {
        switch self {
        case .noLogs: return "🔒"
        case .encryption: return "🔐"
        }
    }
    
    func localizedTitle(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .noLogs: return localizationManager.localized("privacy_policy_network_protection_no_logs")
        case .encryption: return localizationManager.localized("privacy_policy_network_protection_encryption")
        }
    }
    
    func localizedSubtitle(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .noLogs: return localizationManager.localized("privacy_policy_network_protection_no_logs_subtitle")
        case .encryption: return localizationManager.localized("privacy_policy_network_protection_encryption_subtitle")
        }
    }
    
    var title: String {
        return rawValue
    }
    
    var subtitle: String {
        // Deprecated: используйте localizedSubtitle вместо этого
        switch self {
        case .noLogs: return "Что мы НЕ собираем"
        case .encryption: return "3 вида военного шифрования"
        }
    }
    
    func localizedContent(_ localizationManager: LocalizationManager) -> [String] {
        switch self {
        case .noLogs:
            return [
                localizationManager.localized("privacy_policy_network_protection_no_logs_content_1"),
                localizationManager.localized("privacy_policy_network_protection_no_logs_content_2"),
                localizationManager.localized("privacy_policy_network_protection_no_logs_content_3"),
                localizationManager.localized("privacy_policy_network_protection_no_logs_content_4"),
                localizationManager.localized("privacy_policy_network_protection_no_logs_content_5"),
                localizationManager.localized("privacy_policy_network_protection_no_logs_content_6")
            ]
        case .encryption:
            return [
                localizationManager.localized("privacy_policy_network_protection_encryption_content_1"),
                localizationManager.localized("privacy_policy_network_protection_encryption_content_2"),
                localizationManager.localized("privacy_policy_network_protection_encryption_content_3"),
                localizationManager.localized("privacy_policy_network_protection_encryption_content_4")
            ]
        }
    }
    
    var content: [String] {
        // Deprecated: используйте localizedContent вместо этого
        switch self {
        case .noLogs:
            return [
                "История посещений",
                "История подключений",
                "Интернет-активность",
                "IP-адреса",
                "DNS-запросы",
                "Личная информация"
            ]
        case .encryption:
            return [
                "AES-256-GCM: банковский сейф, военный уровень ⭐⭐⭐⭐⭐",
                "ChaCha20-Poly1305: быстрое и надёжное ⚡⭐⭐⭐⭐⭐",
                "XChaCha20-Poly1305: квантовая защита будущего ⭐⭐⭐⭐⭐+",
                "Все 3 вида: стойкость военного уровня"
            ]
        }
    }
}



