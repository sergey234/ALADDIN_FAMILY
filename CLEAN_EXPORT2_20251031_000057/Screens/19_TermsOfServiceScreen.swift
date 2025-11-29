import SwiftUI
import WebKit

/**
 * 📜 Terms of Service Screen
 * Условия использования
 * ОБЯЗАТЕЛЬНЫ для App Store!
 */

struct TermsOfServiceScreen: View {
    
    @Environment(\.dismiss) var dismiss
    @State private var expandedSection: TermsSectionType? = nil
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
                .accessibilityElement()
                .accessibilityLabel("Фон экрана условий использования")
            
            VStack(spacing: 0) {
                // Navigation Bar
                ALADDINNavigationBar(
                    title: "УСЛОВИЯ ИСПОЛЬЗОВАНИЯ",
                    subtitle: "Правила использования сервиса",
                    showBackButton: true,
                    onBack: { dismiss() }
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
                    Text("УСЛОВИЯ ИСПОЛЬЗОВАНИЯ")
                        .font(.h2)
                        .foregroundColor(.textPrimary)
                    
                    Text("Версия 2.0 | 10 октября 2025")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
            }
            
            Text("Используя приложение ALADDIN, вы соглашаетесь с данными условиями использования и обязуетесь соблюдать правила безопасности.")
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
                        Text(section.title)
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                            .multilineTextAlignment(.leading)
                        
                        Text(section.subtitle)
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
                    
                    ForEach(section.content, id: \.self) { item in
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



