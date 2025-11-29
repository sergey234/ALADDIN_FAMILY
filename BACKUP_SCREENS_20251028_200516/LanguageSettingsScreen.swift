import SwiftUI

/// 🌍 Language Settings Screen - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
/// Экран настроек языка приложения
struct LanguageSettingsScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @State private var selectedLanguage: Language = .russian
    @State private var isSystemLanguage: Bool = true
    
    enum Language: String, CaseIterable {
        case russian = "ru"
        case english = "en"
        case chinese = "zh"
        case spanish = "es"
        case french = "fr"
        case german = "de"
        
        var displayName: String {
            switch self {
            case .russian: return "Русский"
            case .english: return "English"
            case .chinese: return "中文"
            case .spanish: return "Español"
            case .french: return "Français"
            case .german: return "Deutsch"
            }
        }
        
        var flag: String {
            switch self {
            case .russian: return "🇷🇺"
            case .english: return "🇺🇸"
            case .chinese: return "🇨🇳"
            case .spanish: return "🇪🇸"
            case .french: return "🇫🇷"
            case .german: return "🇩🇪"
            }
        }
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("Фон настроек языка")
            
            VStack(spacing: 0) {
                // Навигационная панель
                navigationHeader
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Автоматический выбор языка
                        autoLanguageSection
                        
                        // Список языков
                        languagesList
                        
                        // Дополнительные настройки
                        additionalSettings
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.xxl)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Настройки языка приложения")
            }
        }
        .navigationBarHidden(true)
    }
    
    // MARK: - Navigation Header
    
    private var navigationHeader: some View {
        ALADDINNavigationBar(
            title: "ЯЗЫК ПРИЛОЖЕНИЯ",
            subtitle: "Выберите язык интерфейса",
            showBackButton: true,
            onBack: {
                dismiss()
            }
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Навигационная панель настроек языка")
    }
    
    // MARK: - Auto Language Section
    
    private var autoLanguageSection: some View {
        VStack(spacing: Spacing.m) {
            Text("АВТОМАТИЧЕСКИЙ ВЫБОР")
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            HStack(spacing: Spacing.m) {
                Image(systemName: "globe")
                    .font(.system(size: 20))
                    .foregroundColor(.primaryBlue)
                    .frame(width: 24)
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text("Следовать системному языку")
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                    
                    Text("Автоматически использовать язык системы")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                ALADDINToggle(isOn: $isSystemLanguage)
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
            .accessibilityElement(children: .combine)
            .accessibilityLabel("Следовать системному языку: \(isSystemLanguage ? "включено" : "выключено")")
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Languages List
    
    private var languagesList: some View {
        VStack(spacing: Spacing.m) {
            Text("ДОСТУПНЫЕ ЯЗЫКИ")
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: Spacing.s) {
                ForEach(Language.allCases, id: \.self) { language in
                    languageRow(language: language)
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Additional Settings
    
    private var additionalSettings: some View {
        VStack(spacing: Spacing.m) {
            Text("ДОПОЛНИТЕЛЬНО")
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: Spacing.s) {
                settingsButton(
                    icon: "textformat.size",
                    title: "Размер шрифта",
                    subtitle: "Средний",
                    action: {
                        // Настройки шрифта
                    }
                )
                
                settingsButton(
                    icon: "text.alignleft",
                    title: "Направление текста",
                    subtitle: "Слева направо",
                    action: {
                        // Настройки направления текста
                    }
                )
                
                settingsButton(
                    icon: "calendar",
                    title: "Формат даты",
                    subtitle: "ДД.ММ.ГГГГ",
                    action: {
                        // Настройки формата даты
                    }
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Helper Views
    
    private func languageRow(language: Language) -> some View {
        Button(action: {
            selectedLanguage = language
            isSystemLanguage = false
        }) {
            HStack(spacing: Spacing.m) {
                Text(language.flag)
                    .font(.system(size: 24))
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(language.displayName)
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                    
                    Text(language.rawValue.uppercased())
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                if selectedLanguage == language && !isSystemLanguage {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 20))
                        .foregroundColor(.primaryBlue)
                }
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(selectedLanguage == language && !isSystemLanguage ? 
                          Color.primaryBlue.opacity(0.1) : 
                          Color.backgroundMedium.opacity(0.3))
            )
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(language.displayName), \(language.rawValue.uppercased())")
        .accessibilityAddTraits(selectedLanguage == language && !isSystemLanguage ? .isSelected : [])
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

struct LanguageSettingsScreen_Previews: PreviewProvider {
    static var previews: some View {
        LanguageSettingsScreen()
    }
}
