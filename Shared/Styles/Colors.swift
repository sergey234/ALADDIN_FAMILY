import SwiftUI

/// 🎨 ALADDIN Color Palette
/// Все цвета взяты из HTML wireframes (CSS)
extension Color {
    
    // MARK: - Primary Colors
    
    /// Основной синий цвет (кнопки, акценты)
    /// Источник: HTML CSS --primary-blue
    static let primaryBlue = Color(hex: "#2E5BFF")
    
    /// Вторичный синий (для градиентов)
    /// Источник: HTML CSS градиенты
    static let secondaryBlue = Color(hex: "#60A5FA")
    
    /// Вторичный золотой цвет (акценты, иконки)
    /// Источник: HTML CSS --secondary-gold
    static let secondaryGold = Color(hex: "#F59E0B")
    
    // MARK: - Semantic Colors
    
    /// Успех, OK статус 🟢
    /// Источник: HTML CSS --success-color
    static let successGreen = Color(hex: "#10B981")
    
    /// Опасность, ошибка, угроза 🔴
    /// Источник: HTML CSS --danger-color
    static let dangerRed = Color(hex: "#EF4444")
    
    /// Предупреждение ⚠️
    /// Источник: HTML CSS --warning-color
    static let warningOrange = Color(hex: "#F59E0B")
    
    /// Информация ℹ️
    /// Источник: HTML CSS --info-color
    static let infoBlue = Color(hex: "#3B82F6")
    
    // MARK: - Background Colors
    
    /// Основной фон приложения (тёмный)
    /// Источник: HTML body background
    static let backgroundDark = Color(hex: "#0F172A")

    /// Основной фон (алиас для backgroundDark)
    static let backgroundPrimary = Color(hex: "#0F172A")

    /// Средний фон (для inputs, toggles)
    /// Источник: HTML .input background
    static let backgroundMedium = Color(hex: "#1E293B")

    /// Фон карточек и модальных окон
    /// Источник: HTML .card background
    static let surfaceDark = Color(hex: "#1E293B")

    /// Фон карточек (алиас для surfaceDark)
    static let cardBackground = Color(hex: "#1E293B")
    
    /// Градиент фона (используется для больших экранов)
    static let gradientStart = Color(hex: "#0a1128")
    static let gradientMiddle = Color(hex: "#1e3a5f")
    static let gradientEnd = Color(hex: "#2e5090")

    // MARK: - Storm Mesh (грозовое небо + золото)

    /// Ночное небо — база всех mesh-фонов
    static let stormBase = Color(hex: "#070B14")

    /// = backgroundDark
    static let stormDeep = Color(hex: "#0F172A")

    /// Blob «облако»
    static let stormCloud = Color(hex: "#1E293B")

    /// Грозовой indigo
    static let stormIndigo = Color(hex: "#312E81")

    /// Семья / воспитание
    static let stormViolet = Color(hex: "#4C1D95")

    /// Обучение детей (Grow)
    static let stormTeal = Color(hex: "#0D9488")

    /// AI, analytics
    static let stormLightning = Color(hex: "#6366F1")

    /// = secondaryGold
    static let goldPrimary = Color(hex: "#F59E0B")

    /// Blob под header (~18% в mesh)
    static let goldSoft = Color(hex: "#F59E0B").opacity(0.18)

    /// Elderly 60+, warm companion
    static let goldWarm = Color(hex: "#D97706")

    /// Child growWarm base (~8% светлее stormBase)
    static let stormGrowWarmBase = Color(hex: "#0C1220")
    
    // MARK: - Text Colors
    
    /// Основной текст (белый)
    static let textPrimary = Color.white
    
    /// Вторичный текст (серый)
    static let textSecondary = Color(hex: "#94A3B8")
    
    /// Третичный текст (более серый)
    static let textTertiary = Color(hex: "#64748B")
    
    // MARK: - Status Indicator Colors
    
    /// Защищено, онлайн
    static let statusProtected = Color(hex: "#10B981")
    
    /// Угроза, офлайн
    static let statusThreat = Color(hex: "#EF4444")
    
    /// Предупреждение
    static let statusWarning = Color(hex: "#F59E0B")
    
    // MARK: - Helper
    
    /// Инициализация цвета из HEX строки
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (1, 1, 1, 0)
        }
        
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue:  Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

// MARK: - Gradient Helpers

extension LinearGradient {
    
    /// Основной градиент фона (как в HTML)
    static let backgroundGradient = LinearGradient(
        colors: [
            Color.gradientStart,
            Color.gradientMiddle,
            Color.gradientEnd
        ],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
    
    /// Градиент для карточек
    static let cardGradient = LinearGradient(
        colors: [
            Color(hex: "#1e3a5f"),
            Color(hex: "#2e5090")
        ],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
    
    /// Фирменный золотой градиент как у логотипа Aladdin
    static let aladdinGold = LinearGradient(
        colors: [
            Color(red: 1.0, green: 0.84, blue: 0.0),
            Color(red: 0.96, green: 0.77, blue: 0.19),
            Color(red: 0.85, green: 0.65, blue: 0.13)
        ],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
    
    static let appGlassmorphism = LinearGradient(
        colors: [
            Color.white.opacity(0.1),
            Color.white.opacity(0.05)
        ],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
}

