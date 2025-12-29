import SwiftUI
import WebKit

/**
 * 📜 Terms of Service Screen
 * Условия использования
 * ОБЯЗАТЕЛЬНЫ для App Store!
 */

struct TermsOfServiceScreen: View {
    
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var expandedSection: TermsSectionType? = nil
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
                .accessibilityElement()
                .accessibilityLabel(localizationManager.localized("terms_of_service_background"))
            
            VStack(spacing: 0) {
                // Navigation Bar
                ALADDINNavigationBar(
                    title: localizationManager.localized("terms_of_service_title"),
                    subtitle: localizationManager.localized("terms_of_service_subtitle"),
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
                
                // Main Content
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Header Card
                        headerCard
                        
                        // Sections
                        sectionsContent
                        
                        // Spacer
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
        .id("terms_of_service_lang_\(localizationManager.currentLanguage.rawValue)")
        .task {
            print("🚨 TermsOfServiceScreen загружен!")
        }
    }
    
    // MARK: - Header Card
    
    private var headerCard: some View {
        VStack(spacing: Spacing.s) {
            HStack {
                Text("📜")
                    .font(.system(size: 40))
                
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(localizationManager.localized("terms_of_service_header_title"))
                        .font(.h2)
                        .foregroundColor(.textPrimary)
                    
                    Text(localizationManager.localized("terms_of_service_version"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
            }
            
            Text(localizationManager.localized("terms_of_service_intro"))
                .font(.body)
                .foregroundColor(.textPrimary)
                .multilineTextAlignment(.leading)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.secondaryGold.opacity(0.1))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.secondaryGold.opacity(0.3), lineWidth: 1)
                )
        )
        .cardShadow()
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Sections Content
    
    private var sectionsContent: some View {
        VStack(spacing: Spacing.m) {
            ForEach(TermsSection.allCases, id: \.self) { section in
                termsSectionCard(section: section)
            }
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Terms Section Card
    
    private func termsSectionCard(section: TermsSection) -> some View {
        VStack(spacing: 0) {
            Button(action: {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                    if expandedSection == .general(section) {
                        expandedSection = nil
                    } else {
                        expandedSection = .general(section)
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
                    
                    Image(systemName: expandedSection == .general(section) ? "chevron.up" : "chevron.down")
                        .foregroundColor(.secondaryGold)
                        .font(.headline)
                        .frame(width: 24)
                }
                .padding(Spacing.m)
            }
            
            if expandedSection == .general(section) {
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
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.secondaryGold.opacity(0.3), lineWidth: 1)
                )
        )
        .cardShadow()
    }
}

// MARK: - Preview

struct TermsOfServiceScreen_Previews: PreviewProvider {
    static var previews: some View {
        TermsOfServiceScreen()
    }
}

// MARK: - Enums & Models

enum TermsSectionType: Equatable {
    case general(TermsSection)
}

enum TermsSection: String, CaseIterable {
    case acceptance = "Принятие условий"
    case description = "Описание сервиса"
    case registration = "Регистрация и учетные записи"
    case responsibilities = "Обязанности пользователя"
    case parental = "Родительский контроль"
    case vpn = "VPN и безопасность"
    case restrictions = "Ограничения"
    case payments = "Платежи и подписки"
    case intellectual = "Интеллектуальная собственность"
    case liability = "Ответственность"
    case termination = "Прекращение использования"
    case changes = "Изменения условий"
    
    var emoji: String {
        switch self {
        case .acceptance: return "✅"
        case .description: return "📱"
        case .registration: return "🔐"
        case .responsibilities: return "🤝"
        case .parental: return "👨‍👩‍👧‍👦"
        case .vpn: return "🔒"
        case .restrictions: return "🚫"
        case .payments: return "💳"
        case .intellectual: return "📜"
        case .liability: return "⚖️"
        case .termination: return "🔚"
        case .changes: return "📝"
        }
    }
    
    var title: String {
        return rawValue
    }
    
    var subtitle: String {
        switch self {
        case .acceptance: return "Ваше согласие с условиями"
        case .description: return "Что такое ALADDIN"
        case .registration: return "Создание аккаунта"
        case .responsibilities: return "Что нужно делать"
        case .parental: return "Ответственность родителей"
        case .vpn: return "Использование VPN"
        case .restrictions: return "Что запрещено"
        case .payments: return "Оплата подписки"
        case .intellectual: return "Права на контент"
        case .liability: return "Наша ответственность"
        case .termination: return "Завершение доступа"
        case .changes: return "Обновление условий"
        }
    }
    
    var content: [String] {
        switch self {
        case .acceptance:
            return [
                "Используя приложение ALADDIN, вы соглашаетесь с данными условиями",
                "Вы обязуетесь соблюдать все правила использования",
                "До начала использования ознакомьтесь со всеми разделами",
                "При несогласии с условиями - прекратите использование"
            ]
        case .description:
            return [
                "ALADDIN - система семейной безопасности от киберугроз",
                "Включает: VPN, антивирус, родительский контроль, мониторинг",
                "Защита для всей семьи: детей, подростков, пожилых",
                "Образовательный контент и игры по безопасности"
            ]
        case .registration:
            return [
                "Регистрация через QR-код (анонимная)",
                "Вы несете ответственность за сохранение данных доступа",
                "Рекомендуется использовать биометрическую защиту",
                "При утере доступа обращайтесь в поддержку"
            ]
        case .responsibilities:
            return [
                "Использовать приложение только в законных целях",
                "Не нарушать права других пользователей",
                "Не использовать приложение для незаконной деятельности",
                "Соблюдать все нормы безопасности и конфиденциальности",
                "Регулярно обновлять приложение до последней версии"
            ]
        case .parental:
            return [
                "Родители несут полную ответственность за детей",
                "Необходимо настроить родительский контроль",
                "Регулярно проверяйте настройки безопасности",
                "Обучайте детей правилам безопасности в сети",
                "Мониторьте активность детей в приложении"
            ]
        case .vpn:
            return [
                "VPN предоставляется для защиты соединения",
                "Вы несете ответственность за соблюдение законов",
                "Запрещена незаконная деятельность через VPN",
                "Мы не храним историю ваших посещений (NO-LOGS)",
                "Используется военное шифрование"
            ]
        case .restrictions:
            return [
                "Запрещена незаконная деятельность",
                "Взлом и нарушение работы сервиса",
                "Нарушение интеллектуальной собственности",
                "Создание вредоносного контента",
                "Любые действия, нарушающие законодательство РФ"
            ]
        case .payments:
            return [
                "Платежи через App Store или платежные системы",
                "Отмена подписки через настройки Apple ID",
                "Возврат средств по правилам App Store",
                "Подписка продлевается автоматически",
                "Уведомление за 24 часа до списания"
            ]
        case .intellectual:
            return [
                "Все материалы - собственность ALADDIN",
                "Дизайн, код, функциональность защищены",
                "Запрещено копирование и распространение",
                "Торговая марка ALADDIN защищена",
                "Все права принадлежат правообладателю"
            ]
        case .liability:
            return [
                "Не несем ответственности за неправильное использование",
                "Не гарантируем 100% защиту от всех угроз",
                "Не несем ущерб от действий третьих лиц",
                "Вы несете ответственность за свои действия",
                "Используйте приложение на свой риск"
            ]
        case .termination:
            return [
                "Мы можем прекратить доступ при нарушении",
                "Без возмещения ущерба при нарушении",
                "Вы можете удалить аккаунт в любой момент",
                "Данные будут удалены по запросу",
                "Уведомление за 7 дней до прекращения"
            ]
        case .changes:
            return [
                "Оставляем право изменять условия",
                "Уведомление через приложение",
                "Дальнейшее использование = согласие",
                "Изменения вступают в силу немедленно",
                "Актуальная версия всегда в приложении"
            ]
        }
    }
}

// MARK: - TermsSection Localization Extension

extension TermsSection {
    func localizedTitle(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .acceptance: return localizationManager.localized("terms_section_acceptance_title")
        case .description: return localizationManager.localized("terms_section_description_title")
        case .registration: return localizationManager.localized("terms_section_registration_title")
        case .responsibilities: return localizationManager.localized("terms_section_responsibilities_title")
        case .parental: return localizationManager.localized("terms_section_parental_title")
        case .vpn: return localizationManager.localized("terms_section_vpn_title")
        case .restrictions: return localizationManager.localized("terms_section_restrictions_title")
        case .payments: return localizationManager.localized("terms_section_payments_title")
        case .intellectual: return localizationManager.localized("terms_section_intellectual_title")
        case .liability: return localizationManager.localized("terms_section_liability_title")
        case .termination: return localizationManager.localized("terms_section_termination_title")
        case .changes: return localizationManager.localized("terms_section_changes_title")
        }
    }
    
    func localizedSubtitle(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .acceptance: return localizationManager.localized("terms_section_acceptance_subtitle")
        case .description: return localizationManager.localized("terms_section_description_subtitle")
        case .registration: return localizationManager.localized("terms_section_registration_subtitle")
        case .responsibilities: return localizationManager.localized("terms_section_responsibilities_subtitle")
        case .parental: return localizationManager.localized("terms_section_parental_subtitle")
        case .vpn: return localizationManager.localized("terms_section_vpn_subtitle")
        case .restrictions: return localizationManager.localized("terms_section_restrictions_subtitle")
        case .payments: return localizationManager.localized("terms_section_payments_subtitle")
        case .intellectual: return localizationManager.localized("terms_section_intellectual_subtitle")
        case .liability: return localizationManager.localized("terms_section_liability_subtitle")
        case .termination: return localizationManager.localized("terms_section_termination_subtitle")
        case .changes: return localizationManager.localized("terms_section_changes_subtitle")
        }
    }
    
    func localizedContent(_ localizationManager: LocalizationManager) -> [String] {
        switch self {
        case .acceptance:
            return [
                localizationManager.localized("terms_section_acceptance_content_1"),
                localizationManager.localized("terms_section_acceptance_content_2"),
                localizationManager.localized("terms_section_acceptance_content_3"),
                localizationManager.localized("terms_section_acceptance_content_4")
            ]
        case .description:
            return [
                localizationManager.localized("terms_section_description_content_1"),
                localizationManager.localized("terms_section_description_content_2"),
                localizationManager.localized("terms_section_description_content_3"),
                localizationManager.localized("terms_section_description_content_4")
            ]
        case .registration:
            return [
                localizationManager.localized("terms_section_registration_content_1"),
                localizationManager.localized("terms_section_registration_content_2"),
                localizationManager.localized("terms_section_registration_content_3"),
                localizationManager.localized("terms_section_registration_content_4")
            ]
        case .responsibilities:
            return [
                localizationManager.localized("terms_section_responsibilities_content_1"),
                localizationManager.localized("terms_section_responsibilities_content_2"),
                localizationManager.localized("terms_section_responsibilities_content_3"),
                localizationManager.localized("terms_section_responsibilities_content_4"),
                localizationManager.localized("terms_section_responsibilities_content_5")
            ]
        case .parental:
            return [
                localizationManager.localized("terms_section_parental_content_1"),
                localizationManager.localized("terms_section_parental_content_2"),
                localizationManager.localized("terms_section_parental_content_3"),
                localizationManager.localized("terms_section_parental_content_4"),
                localizationManager.localized("terms_section_parental_content_5")
            ]
        case .vpn:
            return [
                localizationManager.localized("terms_section_vpn_content_1"),
                localizationManager.localized("terms_section_vpn_content_2"),
                localizationManager.localized("terms_section_vpn_content_3"),
                localizationManager.localized("terms_section_vpn_content_4"),
                localizationManager.localized("terms_section_vpn_content_5")
            ]
        case .restrictions:
            return [
                localizationManager.localized("terms_section_restrictions_content_1"),
                localizationManager.localized("terms_section_restrictions_content_2"),
                localizationManager.localized("terms_section_restrictions_content_3"),
                localizationManager.localized("terms_section_restrictions_content_4"),
                localizationManager.localized("terms_section_restrictions_content_5")
            ]
        case .payments:
            return [
                localizationManager.localized("terms_section_payments_content_1"),
                localizationManager.localized("terms_section_payments_content_2"),
                localizationManager.localized("terms_section_payments_content_3"),
                localizationManager.localized("terms_section_payments_content_4"),
                localizationManager.localized("terms_section_payments_content_5")
            ]
        case .intellectual:
            return [
                localizationManager.localized("terms_section_intellectual_content_1"),
                localizationManager.localized("terms_section_intellectual_content_2"),
                localizationManager.localized("terms_section_intellectual_content_3"),
                localizationManager.localized("terms_section_intellectual_content_4"),
                localizationManager.localized("terms_section_intellectual_content_5")
            ]
        case .liability:
            return [
                localizationManager.localized("terms_section_liability_content_1"),
                localizationManager.localized("terms_section_liability_content_2"),
                localizationManager.localized("terms_section_liability_content_3"),
                localizationManager.localized("terms_section_liability_content_4"),
                localizationManager.localized("terms_section_liability_content_5")
            ]
        case .termination:
            return [
                localizationManager.localized("terms_section_termination_content_1"),
                localizationManager.localized("terms_section_termination_content_2"),
                localizationManager.localized("terms_section_termination_content_3"),
                localizationManager.localized("terms_section_termination_content_4"),
                localizationManager.localized("terms_section_termination_content_5")
            ]
        case .changes:
            return [
                localizationManager.localized("terms_section_changes_content_1"),
                localizationManager.localized("terms_section_changes_content_2"),
                localizationManager.localized("terms_section_changes_content_3"),
                localizationManager.localized("terms_section_changes_content_4"),
                localizationManager.localized("terms_section_changes_content_5")
            ]
        }
    }
}



