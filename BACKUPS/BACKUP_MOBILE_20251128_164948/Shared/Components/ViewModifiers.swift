import SwiftUI

// MARK: - Glassmorphism Effect
struct GlassmorphismModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .background(.ultraThinMaterial)
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(Color.white.opacity(0.2), lineWidth: 1)
            )
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
    
    func cardShadow() -> some View {
        modifier(CardShadowModifier())
    }
}




