import SwiftUI

/// Central place to pick transitions and motion-friendly defaults.
enum AppScreenTransition: String, CaseIterable, Identifiable {
    case fade
    case slideLeading
    case slideTrailing
    case scale

    var id: String { rawValue }

    var insertion: AnyTransition {
        switch self {
        case .fade:
            return .opacity
        case .slideLeading:
            return .move(edge: .leading).combined(with: .opacity)
        case .slideTrailing:
            return .move(edge: .trailing).combined(with: .opacity)
        case .scale:
            return .scale(scale: 0.96).combined(with: .opacity)
        }
    }

    var removal: AnyTransition {
        switch self {
        case .fade:
            return .opacity
        case .slideLeading:
            return .move(edge: .trailing).combined(with: .opacity)
        case .slideTrailing:
            return .move(edge: .leading).combined(with: .opacity)
        case .scale:
            return .scale(scale: 1.02).combined(with: .opacity)
        }
    }
}

enum TransitionManager {
    static func animation(for transition: AppScreenTransition, reduceMotion: Bool) -> Animation? {
        if reduceMotion { return nil }
        switch transition {
        case .fade:
            return .easeInOut(duration: 0.22)
        case .slideLeading, .slideTrailing:
            return .spring(response: 0.32, dampingFraction: 0.86, blendDuration: 0.12)
        case .scale:
            return .spring(response: 0.30, dampingFraction: 0.82, blendDuration: 0.12)
        }
    }

    static func asymmetric(_ style: AppScreenTransition, reduceMotion: Bool) -> AnyTransition {
        if reduceMotion { return .identity }
        return .asymmetric(insertion: style.insertion, removal: style.removal)
    }
}

extension View {
    func appContentTransition<V: Equatable>(_ style: AppScreenTransition, value: V) -> some View {
        modifier(AppContentTransitionModifier(style: style, value: value))
    }
}

private struct AppContentTransitionModifier<Value: Equatable>: ViewModifier {
    let style: AppScreenTransition
    let value: Value

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    func body(content: Content) -> some View {
        let anim = TransitionManager.animation(for: style, reduceMotion: reduceMotion)
        content
            .transition(TransitionManager.asymmetric(style, reduceMotion: reduceMotion))
            .animation(anim, value: value)
    }
}
