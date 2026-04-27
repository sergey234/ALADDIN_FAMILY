import UIKit

/// 📳 Haptic Feedback Helper
/// Управление тактильной обратной связью
struct HapticFeedback {
    private static let lock = NSLock()
    private static var lastSelection: TimeInterval = 0
    private static var lastNotification: TimeInterval = 0
    private static var lastImpact: TimeInterval = 0

    /// Легкая вибрация для выбора
    static func selection() {
        let now = ProcessInfo.processInfo.systemUptime
        lock.lock()
        if now - lastSelection < PerformanceBudget.hapticMinIntervalSelection {
            lock.unlock()
            return
        }
        lastSelection = now
        lock.unlock()
        let generator = UISelectionFeedbackGenerator()
        generator.selectionChanged()
    }

    /// Средняя вибрация для уведомлений
    static func notification(_ type: UINotificationFeedbackGenerator.FeedbackType) {
        let now = ProcessInfo.processInfo.systemUptime
        lock.lock()
        if now - lastNotification < PerformanceBudget.hapticMinIntervalNotification {
            lock.unlock()
            return
        }
        lastNotification = now
        lock.unlock()
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(type)
    }

    /// Сильная вибрация для воздействия
    static func impact(_ style: UIImpactFeedbackGenerator.FeedbackStyle) {
        let now = ProcessInfo.processInfo.systemUptime
        lock.lock()
        if now - lastImpact < PerformanceBudget.hapticMinIntervalImpact {
            lock.unlock()
            return
        }
        lastImpact = now
        lock.unlock()
        let generator = UIImpactFeedbackGenerator(style: style)
        generator.impactOccurred()
    }
}
