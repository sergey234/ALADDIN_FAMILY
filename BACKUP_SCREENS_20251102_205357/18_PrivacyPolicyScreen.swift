import SwiftUI
import WebKit

/**
 * 📋 Privacy Policy Screen
 * Политика конфиденциальности
 * ОБЯЗАТЕЛЬНА для App Store!
 */

struct PrivacyPolicyScreen: View {
    
    @Environment(\.dismiss) var dismiss
    @State private var expandedSection: PrivacySectionType? = nil
    @State private var selectedTab: PrivacyTab = .main
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
                .accessibilityElement()
                .accessibilityLabel("Фон экрана политики конфиденциальности")
            
            VStack(spacing: 0) {
                // Navigation Bar
                ALADDINNavigationBar(
                    title: "ПОЛИТИКА КОНФИДЕНЦИАЛЬНОСТИ",
                    subtitle: "Как мы защищаем ваши данные",
                    showBackButton: true,
                    showProfileButton: false,
                    showListButton: false,
                    onBack: { dismiss() }
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
                            vpnSectionsContent
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
                    Text("ПОЛИТИКА КОНФИДЕНЦИАЛЬНОСТИ")
                        .font(.h2)
                        .foregroundColor(.textPrimary)
                    
                    Text("Версия 2.0 | 10 октября 2025")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
            }
            
            Text("Система ALADDIN спроектирована для работы БЕЗ сбора персональных данных, обеспечивая полную функциональность системы безопасности.")
                .font(.body)
                .foregroundColor(.textPrimary)
                .multilineTextAlignment(.leading)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.primaryBlue.opacity(0.1))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.primaryBlue.opacity(0.3), lineWidth: 1)
                )
        )
        .cardShadow()
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Tabs View
    
    private var tabsView: some View {
        HStack(spacing: 0) {
            tabButton(title: "Основное", tab: .main)
            tabButton(title: "VPN", tab: .vpn)
        }
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
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
    
    // MARK: - VPN Sections Content
    
    private var vpnSectionsContent: some View {
        VStack(spacing: Spacing.m) {
            ForEach(VPNSection.allCases, id: \.self) { section in
                vpnSectionCard(section: section)
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
    
    // MARK: - VPN Section Card
    
    private func vpnSectionCard(section: VPNSection) -> some View {
        VStack(spacing: 0) {
            Button(action: {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                    if expandedSection == .vpn(section) {
                        expandedSection = nil
                    } else {
                        expandedSection = .vpn(section)
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
                    
                    Image(systemName: expandedSection == .vpn(section) ? "chevron.up" : "chevron.down")
                        .foregroundColor(.primaryBlue)
                        .font(.headline)
                        .frame(width: 24)
                }
                .padding(Spacing.m)
            }
            
            if expandedSection == .vpn(section) {
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Divider()
                        .background(Color.textTertiary)
                    
                    ForEach(section.content, id: \.self) { item in
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
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.primaryBlue.opacity(0.3), lineWidth: 1)
                )
        )
        .cardShadow()
    }
    
    // MARK: - Fallback Content
    
    private var fallbackPrivacyContent: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text("ПОЛИТИКА КОНФИДЕНЦИАЛЬНОСТИ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Text("Последнее обновление: 29 октября 2025")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                
                VStack(alignment: .leading, spacing: Spacing.s) {
                    privacySection(
                        title: "1. Сбор данных",
                        content: "ALADDIN не собирает личные данные. Регистрация осуществляется через QR-коды без использования email, телефона или иных персональных данных."
                    )
                    
                    privacySection(
                        title: "2. Использование данных",
                        content: "Все данные хранятся локально на устройстве пользователя. Мы не передаем данные третьим лицам."
                    )
                    
                    privacySection(
                        title: "3. Защита данных",
                        content: "Мы используем современные методы шифрования для защиты данных на устройстве пользователя."
                    )
                    
                    privacySection(
                        title: "4. Права пользователя",
                        content: "Вы имеете право на доступ, изменение и удаление своих данных в любое время."
                    )
                    
                    privacySection(
                        title: "5. Изменения политики",
                        content: "Мы уведомим вас об изменениях в политике конфиденциальности. Датой вступления в силу считается дата обновления."
                    )
                }
            }
            .padding(Spacing.m)
        }
        .background(Color.white)
        .cornerRadius(12)
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
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
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
    case vpn = "VPN"
}

enum PrivacySectionType: Equatable {
    case main(PrivacyMainSection)
    case vpn(VPNSection)
}

enum PrivacyMainSection: String, CaseIterable {
    case general = "Общие положения"
    case principles = "Принципы работы"
    case auth = "Регистрация и аутентификация"
    case notCollected = "Данные, НЕ собираемые"
    case collected = "Данные, собираемые (обезличенные)"
    case purposes = "Цели обработки"
    case protection = "Меры защиты"
    case rights = "Права пользователей"
    case storage = "Сроки хранения"
    case transfer = "Трансграничная передача"
    case responsibility = "Ответственность"
    case contacts = "Контакты"
    case final = "Заключительные положения"
    
    var emoji: String {
        switch self {
        case .general: return "📋"
        case .principles: return "⭐"
        case .auth: return "🔐"
        case .notCollected: return "❌"
        case .collected: return "✅"
        case .purposes: return "🎯"
        case .protection: return "🛡️"
        case .rights: return "⚖️"
        case .storage: return "⏰"
        case .transfer: return "🌐"
        case .responsibility: return "🤝"
        case .contacts: return "📞"
        case .final: return "📜"
        }
    }
    
    var title: String {
        return rawValue
    }
    
    var subtitle: String {
        switch self {
        case .general: return "Правовая основа и применение"
        case .principles: return "4 основных принципа ALADDIN"
        case .auth: return "Анонимная регистрация через QR"
        case .notCollected: return "Список данных, которые мы НЕ собираем"
        case .collected: return "Обезличенные данные для безопасности"
        case .purposes: return "Для чего используются данные"
        case .protection: return "Технические и организационные меры"
        case .rights: return "Ваши права на данные"
        case .storage: return "Сколько времени хранятся данные"
        case .transfer: return "Передача данных за границу"
        case .responsibility: return "Гарантии Оператора"
        case .contacts: return "Техподдержка и вопросы"
        case .final: return "Вступление в силу"
        }
    }
    
    var content: [String] {
        switch self {
        case .general:
            return [
                "Правовая основа: ФЗ-152 «О персональных данных»",
                "ALADDIN спроектирована БЕЗ сбора персональных данных",
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
                "Семейные группы: через QR-код без имён"
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
                "Полная анонимность пользователей",
                "Соответствие требованиям 152-ФЗ",
                "Регулярный аудит системы"
            ]
        case .contacts:
            return [
                "Email: sergey21-02-84@list.ru",
                "Телефон: +7 (927) 005-15-77",
                "Адрес: Россия, г. Самара",
                "Чат в приложении ALADDIN"
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

enum VPNSection: String, CaseIterable {
    case noLogs = "NO-LOGS POLICY"
    case encryption = "Технологии шифрования"
    case servers = "Серверы"
    case features = "Дополнительные функции"
    case energy = "Энергосбережение"
    
    var emoji: String {
        switch self {
        case .noLogs: return "🔒"
        case .encryption: return "🔐"
        case .servers: return "🌐"
        case .features: return "🛡️"
        case .energy: return "⚡"
        }
    }
    
    var title: String {
        return rawValue
    }
    
    var subtitle: String {
        switch self {
        case .noLogs: return "Что мы НЕ собираем"
        case .encryption: return "3 вида военного шифрования"
        case .servers: return "50+ серверов по всему миру"
        case .features: return "Дополнительная защита"
        case .energy: return "Экономия батареи"
        }
    }
    
    var content: [String] {
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
                "Все 3 вида: НЕВОЗМОЖНО взломать"
            ]
        case .servers:
            return [
                "🇷🇺 Россия: 15 серверов",
                "🇪🇺 Европа: 20 серверов",
                "🇺🇸 США: 10 серверов",
                "🇦🇪 Азия: 5 серверов",
                "Быстрое подключение и низкая задержка"
            ]
        case .features:
            return [
                "Kill Switch: защита от утечек",
                "DNS Protection: защита DNS",
                "IPv6 Protection: защита IPv6",
                "WebRTC Protection: защита WebRTC",
                "Split Tunneling: гибкая маршрутизация"
            ]
        case .energy:
            return [
                "5 режимов работы VPN",
                "Экономия 30-40% батареи",
                "Умное управление подключением",
                "Автоматическая адаптация",
                "Энергосберегающий режим"
            ]
        }
    }
}



