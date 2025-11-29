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
            // ✅ Сначала проверяем LocalizationManager
            let managerLang = localizationManager.currentLanguage.rawValue
            // ✅ Конвертируем zh-Hans в zh для совместимости
            let normalizedLang = managerLang.replacingOccurrences(of: "-Hans", with: "")
            if let lang = Language(rawValue: normalizedLang) {
                return lang
            }
            // ✅ Fallback на сохранённое значение
            return Language(rawValue: selectedLanguageRaw) ?? .russian
        }
        nonmutating set {
            selectedLanguageRaw = newValue.rawValue
            // ✅ Обновляем LocalizationManager (конвертируем обратно)
            let managerLangValue = newValue.rawValue == "zh" ? "zh-Hans" : newValue.rawValue
            if let lang = LocalizationManager.Language(rawValue: managerLangValue) {
                localizationManager.changeLanguage(to: lang)
            }
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
        case chinese = "zh"  // ✅ Используем "zh", конвертируем в "zh-Hans" для LocalizationManager
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
            // Обновляем локальное состояние при изменении языка извне
            let normalizedLang = newLanguage.rawValue.replacingOccurrences(of: "-Hans", with: "")
            if let lang = Language(rawValue: normalizedLang) {
                selectedLanguageRaw = lang.rawValue
            }
        }
        .confirmationDialog("Размер шрифта", isPresented: $showFontSizePicker) {
            ForEach(FontSize.allCases, id: \.self) { size in
                Button(size.displayName) {
                    fontSize = size
                }
            }
            Button("Отмена", role: .cancel) { }
        }
        .confirmationDialog("Направление текста", isPresented: $showTextDirectionPicker) {
            ForEach(TextDirection.allCases, id: \.self) { direction in
                Button(direction.displayName) {
                    textDirection = direction
                }
            }
            Button("Отмена", role: .cancel) { }
        }
        .confirmationDialog("Формат даты", isPresented: $showDateFormatPicker) {
            ForEach(DateFormat.allCases, id: \.self) { format in
                Button(format.displayName) {
                    dateFormat = format
                }
            }
            Button("Отмена", role: .cancel) { }
        }
    }
    
    // MARK: - Navigation Header
    
    private var navigationHeader: some View {
        ALADDINNavigationBar(
            title: "ЯЗЫК ПРИЛОЖЕНИЯ",
            subtitle: "Выберите язык интерфейса",
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
                
                // ✅ УНИФИЦИРОВАНО: Используем ALADDINToggle с размером 40 для соответствия дизайну карточек родительского контроля
                ALADDINToggle(isOn: Binding(
                    get: { isSystemLanguage },
                    set: { newValue in
                        isSystemLanguage = newValue
                        if newValue {
                            // ✅ Используем системный язык
                            if let systemLang = Locale.current.languageCode {
                                // ✅ Конвертируем системный язык (zh -> zh-Hans если нужно)
                                let managerLangValue = systemLang == "zh" ? "zh-Hans" : systemLang
                                if let lang = LocalizationManager.Language(rawValue: managerLangValue) {
                                    localizationManager.changeLanguage(to: lang)
                                }
                            }
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
                    subtitle: fontSize.displayName,
                    action: {
                        showFontSizePicker = true
                    }
                )
                
                settingsButton(
                    icon: "text.alignleft",
                    title: "Направление текста",
                    subtitle: textDirection.displayName,
                    action: {
                        showTextDirectionPicker = true
                    }
                )
                
                settingsButton(
                    icon: "calendar",
                    title: "Формат даты",
                    subtitle: dateFormat.displayName,
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
    
    private func languageRow(language: Language) -> some View {
        Button(action: {
            // ✅ Сначала обновляем локальное состояние
            selectedLanguageRaw = language.rawValue
            isSystemLanguage = false
            
            // ✅ Затем обновляем LocalizationManager (конвертируем zh -> zh-Hans)
            let managerLangValue = language.rawValue == "zh" ? "zh-Hans" : language.rawValue
            if let lang = LocalizationManager.Language(rawValue: managerLangValue) {
                // ✅ Принудительно обновляем язык в LocalizationManager
                localizationManager.changeLanguage(to: lang)
                
                // ✅ Дополнительно обновляем через DispatchQueue для гарантии
                DispatchQueue.main.async {
                    // Принудительно обновляем UI
                    localizationManager.objectWillChange.send()
                    
                    // ✅ Дополнительная синхронизация через хaptic feedback
                    HapticFeedback.impact(.light)
                }
            }
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
