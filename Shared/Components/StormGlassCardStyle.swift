import SwiftUI
import UIKit

// MARK: - Storm glass card chrome

/// Матовое стекло + золотая обводка + тень. Только визуал — контент не меняет.
struct StormGlassCardStyle: ViewModifier {
    var cornerRadius: CGFloat = 10
    var accentStripColor: Color? = nil
    var accentStripWidth: CGFloat = 3

    func body(content: Content) -> some View {
        content
            .background(glassBackground)
            .overlay { frostRimHighlight }
            .overlay {
                RoundedRectangle(cornerRadius: cornerRadius)
                    .stroke(Color.secondaryGold.opacity(0.38), lineWidth: 1)
            }
            .overlay(alignment: .leading) {
                if let accentStripColor {
                    RoundedRectangle(cornerRadius: accentStripWidth / 2)
                        .fill(accentStripColor)
                        .frame(width: accentStripWidth)
                        .padding(.vertical, 6)
                        .padding(.leading, 2)
                }
            }
            .shadow(color: Color.stormIndigo.opacity(0.35), radius: 12, x: 0, y: 6)
            .shadow(color: .black.opacity(0.2), radius: 4, x: 0, y: 2)
    }

    /// Матовое стекло на тёмном storm-фоне: frost + indigo tint (не серая плита).
    @ViewBuilder
    private var glassBackground: some View {
        ZStack {
            if #available(iOS 26.0, *) {
                RoundedRectangle(cornerRadius: cornerRadius)
                    .fill(Color.stormIndigo.opacity(0.14))
                RoundedRectangle(cornerRadius: cornerRadius)
                    .fill(Color.white.opacity(0.10))
            } else {
                RoundedRectangle(cornerRadius: cornerRadius)
                    .fill(.ultraThinMaterial)
                RoundedRectangle(cornerRadius: cornerRadius)
                    .fill(Color.white.opacity(0.06))
            }
        }
    }

    /// Верхний блик — матовое стекло читается на грозовом mesh.
    private var frostRimHighlight: some View {
        RoundedRectangle(cornerRadius: cornerRadius)
            .strokeBorder(
                LinearGradient(
                    colors: [
                        Color.white.opacity(0.22),
                        Color.white.opacity(0.04),
                        Color.clear
                    ],
                    startPoint: .top,
                    endPoint: .bottom
                ),
                lineWidth: 1
            )
    }
}

extension View {
    /// Storm premium glass surface для карточек (Batch 6+).
    func stormGlassCard(
        cornerRadius: CGFloat = 10,
        accentStripColor: Color? = nil
    ) -> some View {
        modifier(
            StormGlassCardStyle(
                cornerRadius: cornerRadius,
                accentStripColor: accentStripColor
            )
        )
    }
}

#if DEBUG
struct StormGlassCardStyle_Previews: PreviewProvider {
    static var previews: some View {
        ZStack {
            StormMeshBackground(variant: .hub)
            VStack(spacing: 16) {
                Text("Антивирус")
                    .font(.caption.bold())
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 24)
                    .stormGlassCard()

                Text("VPN активен")
                    .font(.caption.bold())
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 24)
                    .stormGlassCard(accentStripColor: .statusProtected)
            }
            .padding()
        }
        .previewDisplayName("Storm Glass on Hub")
    }
}
#endif
