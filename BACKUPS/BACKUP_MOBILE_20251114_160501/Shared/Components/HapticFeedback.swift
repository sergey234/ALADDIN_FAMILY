import UIKit

/// 📳 Haptic Feedback Helper
/// Управление тактильной обратной связью
struct HapticFeedback {
    
    /// Легкая вибрация для выбора
    static func selection() {
        let generator = UISelectionFeedbackGenerator()
        generator.selectionChanged()
    }
    
    /// Средняя вибрация для уведомлений
    static func notification(_ type: UINotificationFeedbackGenerator.FeedbackType) {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(type)
    }
    
    /// Сильная вибрация для воздействия
    static func impact(_ style: UIImpactFeedbackGenerator.FeedbackStyle) {
        let generator = UIImpactFeedbackGenerator(style: style)
        generator.impactOccurred()
    }
}
