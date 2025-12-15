import SwiftUI

/// 🌍 Language Settings Screen - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
/// Экран настроек языка приложения
struct LanguageSettingsScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // ✅ Используем единый ключ через AppStorage
    @AppStorage(AppConfig.UserDefaultsKeys.appLanguage) private var selectedLanguageRaw: String = "ru"
    
    var selectedLanguage: Language {
        get {
            if let managerLang = Language(rawValue: localizationManager.currentLanguage.rawValue) {
                return managerLang
            }
            return Language(rawValue: selectedLanguageRaw) ?? .russian
        }
        nonmutating set {
            applyLanguage(newValue)
        }
    }
    
    @State private var isSystemLanguage: Bool = false
    
    // Сохраняем размер шрифта
    @AppStorage("selected_font_size") private var fontSizeRaw: String = "medium"
    var fontSize: FontSize {
        get {
            FontSize(rawValue: fontSizeRaw) ?? .medium
        }
        nonmutating set {
            fontSizeRaw = newValue.rawValue
        }
    }
    @State private var textDirection: TextDirection = .leftToRight
    @State private var dateFormat: DateFormat = .ddMMyyyy
    @State private var showFontSizePicker: Bool = false
    @State private var showTextDirectionPicker: Bool = false
    @State private var showDateFormatPicker: Bool = false
    
    enum Language: String, CaseIterable {
        case russian = "ru"
        case english = "en"
        
        var displayName: String {
            switch self {
            case .russian: return "Русский"
            case .english: return "English"
            }
        }
        
        var flag: String {
            switch self {
            case .russian: return "🇷🇺"
            case .english: return "🇺🇸"
            }
        }
    }
    
    enum FontSize: String, CaseIterable {
        case small = "small"
        case medium = "medium"
        case large = "large"
        case extraLarge = "extraLarge"
        
        var displayName: String {
            switch self {
            case .small: return "Мелкий"
            case .medium: return "Средний"
            case .large: return "Крупный"
            case .extraLarge: return "Очень крупный"
            }
        }
        
        func localizedDisplayName(_ localizationManager: LocalizationManager) -> String {
            switch self {
            case .small: return localizationManager.localized("language_settings_font_size_small")
            case .medium: return localizationManager.localized("language_settings_font_size_medium")
            case .large: return localizationManager.localized("language_settings_font_size_large")
            case .extraLarge: return localizationManager.localized("language_settings_font_size_extra_large")
            }
        }
        
        var systemFont: Font {
            switch self {
            case .small: return .caption
            case .medium: return .body
            case .large: return .title3
            case .extraLarge: return .title2
            }
        }
    }
    
    enum TextDirection: String, CaseIterable {
        case leftToRight = "ltr"
        case rightToLeft = "rtl"
        
        var displayName: String {
            switch self {
            case .leftToRight: return "Слева направо"
            case .rightToLeft: return "Справа налево"
            }
        }
        
        func localizedDisplayName(_ localizationManager: LocalizationManager) -> String {
            switch self {
            case .leftToRight: return localizationManager.localized("language_settings_text_direction_ltr")
            case .rightToLeft: return localizationManager.localized("language_settings_text_direction_rtl")
            }
        }
    }
    
    enum DateFormat: String, CaseIterable {
        case ddMMyyyy = "dd.MM.yyyy"
        case mmDDyyyy = "MM/dd/yyyy"
        case yyyyMMdd = "yyyy-MM-dd"
        
        var displayName: String {
            switch self {
            case .ddMMyyyy: return "ДД.ММ.ГГГГ"
            case .mmDDyyyy: return "ММ/ДД/ГГГГ"
            case .yyyyMMdd: return "ГГГГ-ММ-ДД"
            }
        }
        
        func localizedDisplayName(_ localizationManager: LocalizationManager) -> String {
            switch self {
            case .ddMMyyyy: return localizationManager.localized("language_settings_date_format_dd_mm_yyyy")
            case .mmDDyyyy: return localizationManager.localized("language_settings_date_format_mm_dd_yyyy")
            case .yyyyMMdd: return localizationManager.localized("language_settings_date_format_yyyy_mm_dd")
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
        // ✅ Отслеживаем изменения языка в LocalizationManager
        .onChange(of: localizationManager.currentLanguage) { newLanguage in
            print("🌍 Language changed in LanguageSettingsScreen: \(newLanguage.displayName)")
            if let lang = Language(rawValue: newLanguage.rawValue) {
                selectedLanguageRaw = lang.rawValue
            }
        }
        .confirmationDialog(localizationManager.localized("language_settings_font_size"), isPresented: $showFontSizePicker) {
            ForEach(FontSize.allCases, id: \.self) { size in
                Button(size.localizedDisplayName(localizationManager)) {
                    fontSize = size
                }
            }
            Button(localizationManager.localized("language_settings_cancel"), role: .cancel) { }
        }
        .confirmationDialog(localizationManager.localized("language_settings_text_direction"), isPresented: $showTextDirectionPicker) {
            ForEach(TextDirection.allCases, id: \.self) { direction in
                Button(direction.localizedDisplayName(localizationManager)) {
                    textDirection = direction
                }
            }
            Button(localizationManager.localized("language_settings_cancel"), role: .cancel) { }
        }
        .confirmationDialog(localizationManager.localized("language_settings_date_format"), isPresented: $showDateFormatPicker) {
            ForEach(DateFormat.allCases, id: \.self) { format in
                Button(format.localizedDisplayName(localizationManager)) {
                    dateFormat = format
                }
            }
            Button(localizationManager.localized("language_settings_cancel"), role: .cancel) { }
        }
        .id("language_settings_lang_\(localizationManager.currentLanguage.rawValue)")
    }
    
    // MARK: - Navigation Header
    
    private var navigationHeader: some View {
        ALADDINNavigationBar(
            title: localizationManager.localized("language_settings_title"),
            subtitle: localizationManager.localized("language_settings_subtitle"),
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
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Навигационная панель настроек языка")
    }
    
    // MARK: - Auto Language Section
    
    private var autoLanguageSection: some View {
        VStack(spacing: Spacing.m) {
            Text(localizationManager.localized("language_settings_auto_selection"))
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
                    Text(localizationManager.localized("language_settings_follow_system"))
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                    
                    Text(localizationManager.localized("language_settings_follow_system_desc"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                // ✅ УНИФИЦИРОВАНО: Используем ALADDINToggle с размером 40 для соответствия дизайну карточек родительского контроля
                ALADDINToggle(isOn: Binding(
                    get: { isSystemLanguage },
                    set: { newValue in
                        isSystemLanguage = newValue
                        if newValue {
                            let systemLangCode = Locale.current.languageCode?.lowercased() ?? ""
                            let resolvedLanguage = Language(rawValue: systemLangCode) ?? .english
                            applyLanguage(resolvedLanguage)
                        }
                    }
                ), size: 40)
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
            .accessibilityElement(children: .combine)
            .accessibilityLabel("\(localizationManager.localized("language_settings_follow_system")): \(isSystemLanguage ? localizationManager.localized("settings_enabled") : localizationManager.localized("settings_disabled"))")
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Languages List
    
    private var languagesList: some View {
        VStack(spacing: Spacing.m) {
            Text(localizationManager.localized("language_settings_available_languages"))
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
            Text(localizationManager.localized("language_settings_additional"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: Spacing.s) {
                settingsButton(
                    icon: "textformat.size",
                    title: localizationManager.localized("language_settings_font_size"),
                    subtitle: fontSize.localizedDisplayName(localizationManager),
                    action: {
                        showFontSizePicker = true
                    }
                )
                
                settingsButton(
                    icon: "text.alignleft",
                    title: localizationManager.localized("language_settings_text_direction"),
                    subtitle: textDirection.localizedDisplayName(localizationManager),
                    action: {
                        showTextDirectionPicker = true
                    }
                )
                
                settingsButton(
                    icon: "calendar",
                    title: localizationManager.localized("language_settings_date_format"),
                    subtitle: dateFormat.localizedDisplayName(localizationManager),
                    action: {
                        showDateFormatPicker = true
                    }
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Helper Views
    
    private func applyLanguage(_ language: Language) {
        selectedLanguageRaw = language.rawValue
        
        guard let managerLanguage = LocalizationManager.Language(rawValue: language.rawValue) else {
            return
        }
        
        localizationManager.changeLanguage(to: managerLanguage)
        DispatchQueue.main.async {
            localizationManager.objectWillChange.send()
            HapticFeedback.impact(.light)
        }
    }
    
    private func languageRow(language: Language) -> some View {
        Button(action: {
            applyLanguage(language)
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
                
                // ✅ Показываем галочку для выбранного языка
                if selectedLanguage == language && !isSystemLanguage {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 20))
                        .foregroundColor(.primaryBlue)
                        .transition(.scale.combined(with: .opacity))
                } else if localizationManager.currentLanguage.rawValue.replacingOccurrences(of: "-Hans", with: "") == language.rawValue && !isSystemLanguage {
                    // ✅ Дополнительная проверка через LocalizationManager
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 20))
                        .foregroundColor(.primaryBlue)
                        .transition(.scale.combined(with: .opacity))
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
