import SwiftUI

/// 🔲 ALADDIN Corner Radius System
/// Все радиусы скругления взяты из HTML wireframes (CSS border-radius)
enum CornerRadius {
    
    // MARK: - Standard Corner Radius
    
    /// Small: 8pt
    static let small: CGFloat = 8
    
    /// Medium: 12pt  
    static let medium: CGFloat = 12
    
    /// Large: 16pt
    static let large: CGFloat = 16
    
    /// Extra Large: 20pt
    static let xl: CGFloat = 20
    
    /// Medium: 14pt (для уведомлений)
    static let md: CGFloat = 14
    
    // MARK: - Special Corner Radius
    
    /// Card: 16pt (для карточек)
    static let card: CGFloat = 16
    
    /// Button: 12pt (для кнопок)
    static let button: CGFloat = 12
    
    /// Modal: 20pt (для модальных окон)
    static let modal: CGFloat = 20
}
