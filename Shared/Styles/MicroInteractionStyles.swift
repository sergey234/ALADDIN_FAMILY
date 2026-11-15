import SwiftUI
import UIKit

/// Лёгкое нажатие: уменьшение scale (Phase 6.2 — микро-анимации), с уважением Reduce Motion.
struct PressScaleButtonStyle: ButtonStyle {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    var pressedScale: CGFloat = 0.96

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect((configuration.isPressed && !reduceMotion) ? pressedScale : 1.0)
            .animation(reduceMotion ? nil : .easeOut(duration: 0.14), value: configuration.isPressed)
    }
}

/// Device QA: haptic + visual press (эталон чипов Единорог/Аладдин/Джин).
/// Используй вместо «голого» `.plain`, когда пользователь должен чувствовать тап.
struct AladdinTapButtonStyle: ButtonStyle {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    var impact: UIImpactFeedbackGenerator.FeedbackStyle = .light
    var pressedScale: CGFloat = 0.96

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect((configuration.isPressed && !reduceMotion) ? pressedScale : 1.0)
            .opacity(configuration.isPressed ? 0.92 : 1.0)
            .animation(reduceMotion ? nil : .easeOut(duration: 0.12), value: configuration.isPressed)
            .onChange(of: configuration.isPressed) { pressed in
                guard pressed else { return }
                HapticFeedback.impact(impact)
            }
    }
}

extension View {
    /// Convenience: press scale + impact haptic on Button.
    func aladdinTapFeedback(
        _ impact: UIImpactFeedbackGenerator.FeedbackStyle = .light
    ) -> some View {
        buttonStyle(AladdinTapButtonStyle(impact: impact))
    }
}
