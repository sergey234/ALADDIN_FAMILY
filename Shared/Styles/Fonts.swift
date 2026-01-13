import SwiftUI

/// 📝 ALADDIN Typography System
/// Все размеры взяты из HTML wireframes (CSS font-size)
extension Font {
    
    // MARK: - Headings
    
    /// H1: Заголовки экранов
    /// Источник: HTML h1 { font-size: 32px; font-weight: 900; }
    static let h1 = Font.system(size: 32, weight: .bold, design: .default)
    
    /// H2: Подзаголовки
    /// Источник: HTML h2 { font-size: 24px; font-weight: 700; }
    static let h2 = Font.system(size: 24, weight: .bold, design: .default)
    
    /// H3: Секции
    /// Источник: HTML h3 { font-size: 20px; font-weight: 600; }
    static let h3 = Font.system(size: 20, weight: .semibold, design: .default)
    
    /// H4: Мелкие заголовки
    /// Источник: HTML h4 { font-size: 18px; font-weight: 600; }
    static let h4 = Font.system(size: 18, weight: .semibold, design: .default)
    
    // MARK: - Body Text
    
    /// Body: Основной текст
    /// Источник: HTML body { font-size: 16px; }
    static let body = Font.system(size: 16, weight: .regular, design: .default)
    
    /// Body Medium: Средний текст
    static let bodyMedium = Font.system(size: 16, weight: .medium, design: .default)
    
    /// Body Bold: Жирный текст
    static let bodyBold = Font.system(size: 16, weight: .bold, design: .default)
    
    // MARK: - Small Text
    
    /// Caption: Подписи
    /// Источник: HTML .caption { font-size: 14px; }
    static let caption = Font.system(size: 14, weight: .regular, design: .default)
    
    /// Caption Bold: Жирные подписи
    static let captionBold = Font.system(size: 14, weight: .bold, design: .default)
    
    /// Caption Small: Мелкие подписи
    /// Источник: HTML .caption-small { font-size: 12px; }
    static let captionSmall = Font.system(size: 12, weight: .regular, design: .default)
    
    /// Small: Мелкий текст
    /// Источник: HTML .small { font-size: 12px; }
    static let small = Font.system(size: 12, weight: .regular, design: .default)
    
    // MARK: - Special
    
    /// Large Title: Очень большие заголовки (для детского/пожилого интерфейса)
    /// Поддержка Dynamic Type согласно Apple HIG
    static let largeTitle = Font.system(size: 40, weight: .heavy, design: .default)
    
    /// Button: Текст на кнопках
    /// Источник: HTML .button { font-size: 16px; font-weight: 600; }
    /// Поддержка Dynamic Type согласно Apple HIG
    static let button = Font.system(size: 16, weight: .semibold, design: .default)
    
    /// Button Text: Alias для button (совместимость)
    static let buttonText = Font.system(size: 16, weight: .semibold, design: .default)
    
    /// Button Large: Большие кнопки (для пожилых)
    /// Поддержка Dynamic Type согласно Apple HIG
    static let buttonLarge = Font.system(size: 20, weight: .bold, design: .default)
}

// MARK: - Typography для Dynamic Type (Accessibility)

/// Адаптивная типография с поддержкой Dynamic Type
extension Font {
    
    /// Заголовок с Dynamic Type
    static let adaptiveH1 = Font.custom("System", size: 32, relativeTo: .title)
    
    /// Подзаголовок с Dynamic Type
    static let adaptiveH2 = Font.custom("System", size: 24, relativeTo: .title2)
    
    /// Основной текст с Dynamic Type
    static let adaptiveBody = Font.custom("System", size: 16, relativeTo: .body)
    
    /// Подпись с Dynamic Type
    static let adaptiveCaption = Font.custom("System", size: 14, relativeTo: .caption)
}

// MARK: - Line Height

/// Межстрочный интервал
enum LineHeight {
    /// Плотный (для заголовков)
    static let tight: CGFloat = 1.2
    
    /// Нормальный (для body)
    static let normal: CGFloat = 1.5
    
    /// Свободный (для читаемости)
    static let loose: CGFloat = 1.8
}

// MARK: - Letter Spacing

/// Межбуквенное расстояние
enum LetterSpacing {
    /// Для заголовков ALADDIN
    /// Источник: HTML letter-spacing: 6px
    static let title: CGFloat = 6
    
    /// Для подзаголовков
    /// Источник: HTML letter-spacing: 3px
    static let subtitle: CGFloat = 3
    
    /// Для обычного текста
    static let normal: CGFloat = 0
    
    /// Для плотного текста
    static let tight: CGFloat = -0.5
}

