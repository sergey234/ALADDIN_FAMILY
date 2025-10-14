import SwiftUI

/// 📐 ALADDIN Spacing System
/// Все отступы взяты из HTML wireframes (CSS margin, padding)
enum Spacing {
    
    // MARK: - Standard Spacing
    
    /// Extra Extra Small: 4pt
    /// Источник: HTML CSS - минимальные отступы
    static let xxs: CGFloat = 4
    
    /// Extra Small: 8pt
    /// Источник: HTML .gap-xs, padding-xs
    static let xs: CGFloat = 8
    
    /// Small: 12pt
    /// Источник: HTML .gap-sm, padding-sm
    static let s: CGFloat = 12
    
    /// Medium: 16pt (базовый отступ)
    /// Источник: HTML .gap-md, padding-md
    static let m: CGFloat = 16
    
    /// Large: 24pt
    /// Источник: HTML .gap-lg, padding-lg
    static let l: CGFloat = 24
    
    /// Extra Large: 32pt
    /// Источник: HTML .gap-xl, padding-xl
    static let xl: CGFloat = 32
    
    /// Extra Extra Large: 48pt
    /// Источник: HTML .gap-xxl, padding-xxl
    static let xxl: CGFloat = 48
    
    // MARK: - Specific Use Cases
    
    /// Отступ между карточками
    static let cardSpacing: CGFloat = 16
    
    /// Padding внутри карточек
    /// Источник: HTML .card { padding: 20px }
    static let cardPadding: CGFloat = 20
    
    /// Отступ по краям экрана
    /// Источник: HTML .screen { padding: 20px }
    static let screenPadding: CGFloat = 20
    
    /// Отступ между секциями
    static let sectionSpacing: CGFloat = 32
}

/// 🔲 ALADDIN Corner Radius System
/// Все скругления взяты из HTML wireframes (CSS border-radius)
enum CornerRadius {
    
    /// Маленькое скругление: 8pt
    /// Источник: HTML .rounded-sm { border-radius: 8px }
    static let small: CGFloat = 8
    
    /// Среднее скругление: 12pt
    /// Источник: HTML .rounded-md { border-radius: 12px }
    static let medium: CGFloat = 12
    
    /// Большое скругление: 16pt
    /// Источник: HTML .card { border-radius: 16px }
    static let large: CGFloat = 16
    
    /// Очень большое: 24pt
    /// Источник: HTML .rounded-xl { border-radius: 24px }
    static let xlarge: CGFloat = 24
    
    /// Полное скругление (для ползунков)
    static let full: CGFloat = 999
    
    /// Круг: 50%
    static let circle: CGFloat = 999
}

/// ☁️ ALADDIN Shadow System
/// Все тени взяты из HTML wireframes (CSS box-shadow)
extension View {
    
    /// Маленькая тень
    /// Источник: HTML box-shadow: 0 2px 4px rgba(0,0,0,0.1)
    func shadowSmall() -> some View {
        self.shadow(color: Color.black.opacity(0.1), radius: 2, x: 0, y: 2)
    }
    
    /// Средняя тень
    /// Источник: HTML box-shadow: 0 4px 12px rgba(0,0,0,0.2)
    func shadowMedium() -> some View {
        self.shadow(color: Color.black.opacity(0.2), radius: 6, x: 0, y: 4)
    }
    
    /// Большая тень
    /// Источник: HTML box-shadow: 0 8px 24px rgba(0,0,0,0.3)
    func shadowLarge() -> some View {
        self.shadow(color: Color.black.opacity(0.3), radius: 12, x: 0, y: 8)
    }
    
    /// Тень для карточек (стандартная)
    /// Источник: HTML .card { box-shadow: 0 4px 12px rgba(0,0,0,0.2) }
    func cardShadow() -> some View {
        self.shadowMedium()
    }
}

/// 📏 ALADDIN Size System
/// Стандартные размеры элементов
enum Size {
    
    // MARK: - Icons
    
    /// Маленькая иконка
    static let iconSmall: CGFloat = 16
    
    /// Средняя иконка
    static let iconMedium: CGFloat = 24
    
    /// Большая иконка (в карточках)
    static let iconLarge: CGFloat = 48
    
    /// Огромная иконка (в детском/пожилом интерфейсе)
    static let iconXLarge: CGFloat = 64
    
    // MARK: - Buttons
    
    /// Минимальная высота кнопки (Apple HIG)
    static let buttonMinHeight: CGFloat = 44
    
    /// Стандартная высота кнопки
    /// Источник: HTML .button { height: 48px }
    static let buttonHeight: CGFloat = 48
    
    /// Большая кнопка (для пожилых)
    static let buttonLargeHeight: CGFloat = 60
    
    /// SOS кнопка (огромная)
    static let sosButtonSize: CGFloat = 120
    
    // MARK: - Cards
    
    /// Минимальная высота карточки
    static let cardMinHeight: CGFloat = 100
    
    /// Стандартная высота карточки функции
    /// Источник: HTML .function-card { height: 140px }
    static let functionCardHeight: CGFloat = 140
    
    // MARK: - Avatar
    
    /// Маленький аватар
    static let avatarSmall: CGFloat = 32
    
    /// Средний аватар (стандартный)
    static let avatarMedium: CGFloat = 48
    
    /// Alias для avatarMedium (используется в FamilyMemberCard)
    static let avatarSize: CGFloat = 48
    
    /// Большой аватар
    static let avatarLarge: CGFloat = 80
    
    // MARK: - Status Indicator
    
    /// Индикатор статуса 🟢🔴
    static let statusIndicator: CGFloat = 12
    
    /// Индикатор в карточке члена семьи
    static let statusIndicatorLarge: CGFloat = 16
    
    // MARK: - Toggle Switch
    
    /// Ширина переключателя
    static let toggleWidth: CGFloat = 51
    
    /// Высота переключателя
    static let toggleHeight: CGFloat = 31
    
    /// Размер ползунка переключателя
    static let toggleKnob: CGFloat = 27
    
    // MARK: - Slider
    
    /// Высота трека ползунка
    static let sliderTrackHeight: CGFloat = 4
    
    /// Размер ползунка
    static let sliderKnob: CGFloat = 28
    
    // MARK: - Navigation
    
    /// Размер кнопки навигации
    static let navButtonSize: CGFloat = 40
}

