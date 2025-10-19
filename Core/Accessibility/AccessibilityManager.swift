import SwiftUI
import Combine

/**
 * 🦯 Accessibility Manager
 * Управление доступностью для людей с ограниченными возможностями
 * VoiceOver, Dynamic Type, Color Blind Mode, Reduce Motion
 */

class AccessibilityManager: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var isVoiceOverEnabled: Bool = false
    @Published var isReduceMotionEnabled: Bool = false
    @Published var contentSizeCategory: UIContentSizeCategory = .large
    @Published var colorBlindMode: ColorBlindMode = .none
    
    // MARK: - Color Blind Mode
    
    enum ColorBlindMode: String, CaseIterable {
        case none = "Обычный"
        case protanopia = "Протанопия (красный-зелёный)"
        case deuteranopia = "Дейтеранопия (красный-зелёный)"
        case tritanopia = "Тританопия (сине-жёлтый)"
        case monochromacy = "Монохромазия (ч/б)"
        
        var icon: String {
            switch self {
            case .none: return "👁️"
            case .protanopia: return "🔴"
            case .deuteranopia: return "🟢"
            case .tritanopia: return "🔵"
            case .monochromacy: return "⚫"
            }
        }
    }
    
    // MARK: - Init
    
    init() {
        // Проверить VoiceOver
        isVoiceOverEnabled = UIAccessibility.isVoiceOverRunning
        
        // Проверить Reduce Motion
        isReduceMotionEnabled = UIAccessibility.isReduceMotionEnabled
        
        // Проверить Content Size Category
        contentSizeCategory = UIApplication.shared.preferredContentSizeCategory
        
        // Подписаться на изменения
        setupObservers()
    }
    
    // MARK: - Setup Observers
    
    private func setupObservers() {
        // VoiceOver изменился
        NotificationCenter.default.addObserver(
            forName: UIAccessibility.voiceOverStatusDidChangeNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.isVoiceOverEnabled = UIAccessibility.isVoiceOverRunning
            print("🦯 VoiceOver: \(UIAccessibility.isVoiceOverRunning ? "ON" : "OFF")")
        }
        
        // Reduce Motion изменился
        NotificationCenter.default.addObserver(
            forName: UIAccessibility.reduceMotionStatusDidChangeNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.isReduceMotionEnabled = UIAccessibility.isReduceMotionEnabled
            print("🎬 Reduce Motion: \(UIAccessibility.isReduceMotionEnabled ? "ON" : "OFF")")
        }
        
        // Content Size изменился
        NotificationCenter.default.addObserver(
            forName: UIContentSizeCategory.didChangeNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.contentSizeCategory = UIApplication.shared.preferredContentSizeCategory
            print("📏 Text Size Changed: \(UIApplication.shared.preferredContentSizeCategory.rawValue)")
        }
    }
    
    // MARK: - Animation with Accessibility
    
    /**
     * Анимация с учётом Reduce Motion
     */
    func animation<V: Equatable>(_ animation: Animation?, value: V, completion: @escaping () -> Void = {}) -> Animation? {
        if isReduceMotionEnabled {
            return nil // Без анимации
        } else {
            return animation
        }
    }
    
    /**
     * Transition с учётом Reduce Motion
     */
    func transition(_ transition: AnyTransition) -> AnyTransition {
        if isReduceMotionEnabled {
            return .identity // Без transition
        } else {
            return transition
        }
    }
    
    // MARK: - Color Adjustment
    
    /**
     * Получить цвет с учётом Color Blind Mode
     */
    func adjustColor(_ color: Color) -> Color {
        switch colorBlindMode {
        case .none:
            return color
        case .protanopia:
            return adjustForProtanopia(color)
        case .deuteranopia:
            return adjustForDeuteranopia(color)
        case .tritanopia:
            return adjustForTritanopia(color)
        case .monochromacy:
            return adjustForMonochromacy(color)
        }
    }
    
    // MARK: - Color Blind Adjustments
    
    private func adjustForProtanopia(_ color: Color) -> Color {
        // Упрощённая коррекция для протанопии (красный → синий)
        if color == .red {
            return Color.blue
        } else if color == .green {
            return Color.cyan
        }
        return color
    }
    
    private func adjustForDeuteranopia(_ color: Color) -> Color {
        // Коррекция для дейтеранопии
        if color == .green {
            return Color.blue
        } else if color == .red {
            return Color.orange
        }
        return color
    }
    
    private func adjustForTritanopia(_ color: Color) -> Color {
        // Коррекция для тританопии (синий → красный)
        if color == .blue {
            return Color.red
        }
        return color
    }
    
    private func adjustForMonochromacy(_ color: Color) -> Color {
        // Чёрно-белый режим
        return Color.gray
    }
    
    // MARK: - Haptic Feedback with Accessibility
    
    /**
     * Haptic feedback с учётом доступности
     */
    func hapticFeedback(style: UIImpactFeedbackGenerator.FeedbackStyle) {
        // VoiceOver пользователи полагаются на haptic
        let generator = UIImpactFeedbackGenerator(style: style)
        generator.impactOccurred()
    }
}

// MARK: - View Extensions

extension View {
    
    /**
     * Добавить VoiceOver label
     */
    func voiceOverLabel(_ label: String) -> some View {
        self.accessibilityLabel(label)
    }
    
    /**
     * Добавить VoiceOver hint
     */
    func voiceOverHint(_ hint: String) -> some View {
        self.accessibilityHint(hint)
    }
    
    /**
     * Добавить VoiceOver value
     */
    func voiceOverValue(_ value: String) -> some View {
        self.accessibilityValue(value)
    }
    
    /**
     * Сделать элемент accessibility элементом
     */
    func accessibilityElement(label: String, hint: String? = nil, value: String? = nil) -> some View {
        self
            .accessibilityLabel(label)
            .accessibilityHint(hint ?? "")
            .accessibilityValue(value ?? "")
    }
}



