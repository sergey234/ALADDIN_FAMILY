import SwiftUI
import UIKit

// MARK: - Glassmorphism Effect
struct GlassmorphismModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .background(glassBackground)
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(Color.white.opacity(0.2), lineWidth: 1)
            )
    }

    /// iOS 26 sheet + `.ultraThinMaterial` в layout даёт ResetGlassEnvironmentModifier / malloc corruption — светлый opaque fill.
    @ViewBuilder
    private var glassBackground: some View {
        if #available(iOS 26.0, *) {
            RoundedRectangle(cornerRadius: 12)
                .fill(Color(UIColor.systemBackground).opacity(0.94))
        } else {
            RoundedRectangle(cornerRadius: 12)
                .fill(.ultraThinMaterial)
        }
    }
}

// MARK: - Sheet presentation (iOS 26 Liquid Glass)
/// Явный непрозрачный фон sheet — обход краша `CoreSheetPresentationModifier` / `ResetGlassEnvironmentModifier`.
struct AladdinSheetPresentationModifier: ViewModifier {
    func body(content: Content) -> some View {
        if #available(iOS 16.4, *) {
            content
                .presentationBackground(Color(UIColor.systemBackground))
                .presentationDragIndicator(.visible)
        } else {
            content
        }
    }
}

// MARK: - Card Shadow
struct CardShadowModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .shadow(color: Color.black.opacity(0.1), radius: 8, x: 0, y: 4)
    }
}

// MARK: - Extensions
extension View {
    func appGlassmorphism() -> some View {
        modifier(GlassmorphismModifier())
    }

    func aladdinSheetPresentation() -> some View {
        modifier(AladdinSheetPresentationModifier())
    }
    
    func cardShadow() -> some View {
        modifier(CardShadowModifier())
    }
}




