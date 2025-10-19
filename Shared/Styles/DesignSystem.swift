import SwiftUI

// MARK: - Design System
struct DesignSystem {
    
    // MARK: - Spacing
    struct Spacing {
        static let xxs: CGFloat = 2
        static let xs: CGFloat = 4
        static let s: CGFloat = 8
        static let sm: CGFloat = 8
        static let m: CGFloat = 16
        static let md: CGFloat = 16
        static let l: CGFloat = 24
        static let lg: CGFloat = 24
        static let xl: CGFloat = 32
        static let xxl: CGFloat = 48
        static let screenPadding: CGFloat = 20
        static let cardPadding: CGFloat = 16
    }
    
    // MARK: - Corner Radius
    struct CornerRadius {
        static let small: CGFloat = 4
        static let sm: CGFloat = 4
        static let medium: CGFloat = 8
        static let md: CGFloat = 8
        static let lg: CGFloat = 12
        static let large: CGFloat = 12
        static let xl: CGFloat = 16
        static let xxl: CGFloat = 24
    }
    
    // MARK: - Colors
    struct Colors {
        static let primaryBlue = Color(red: 0.18, green: 0.36, blue: 1.0)
        static let secondaryBlue = Color(red: 0.0, green: 0.5, blue: 1.0)
        static let textPrimary = Color.white
        static let textSecondary = Color(red: 0.6, green: 0.6, blue: 0.6)
        static let background = Color(red: 0.05, green: 0.05, blue: 0.05)
        static let backgroundMedium = Color(red: 0.1, green: 0.1, blue: 0.1)
        static let cardBackground = Color(red: 0.1, green: 0.1, blue: 0.1)
        static let successGreen = Color.green
        static let warningOrange = Color.orange
        static let dangerRed = Color.red
        static let secondaryGold = Color.yellow
    }
    
    // MARK: - Gradients
    struct Gradients {
        static let backgroundGradient = LinearGradient(
            colors: [Colors.background, Colors.cardBackground],
            startPoint: .top,
            endPoint: .bottom
        )
    }
}

// MARK: - Extensions
extension Color {
    static let primaryBlue = DesignSystem.Colors.primaryBlue
    static let secondaryBlue = DesignSystem.Colors.secondaryBlue
    static let textPrimary = DesignSystem.Colors.textPrimary
    static let textSecondary = DesignSystem.Colors.textSecondary
    static let backgroundMedium = DesignSystem.Colors.backgroundMedium
    static let successGreen = DesignSystem.Colors.successGreen
    static let warningOrange = DesignSystem.Colors.warningOrange
    static let dangerRed = DesignSystem.Colors.dangerRed
    static let secondaryGold = DesignSystem.Colors.secondaryGold
}

extension Font {
    static let h2 = Font.title2
    static let h3 = Font.title2
    static let bodyBold = Font.body.bold()
    static let captionSmall = Font.caption
    static let buttonText = Font.headline
}

extension LinearGradient {
    static let backgroundGradient = DesignSystem.Gradients.backgroundGradient
}

// MARK: - Sizes
struct Size {
    static let buttonHeight: CGFloat = 50
    static let cardHeight: CGFloat = 120
}

// MARK: - Type Aliases
typealias Spacing = DesignSystem.Spacing
typealias CornerRadius = DesignSystem.CornerRadius
