import SwiftUI

/// S18/S09/S43/S51 Snowball B — owner color lock 2026-11-09.
/// SSOT: `docs/competitors/SNOWBALL_S18_COLOR_CANON_FOR_ML_2026-11-09.md`
/// Эталон: `docs/competitors/snowball_s18_ref/OWNER_SNOWBALL_COLOR_REF_2026-11-09.jpg`
/// Vertical purple → magenta glow (NOT navy). Icon from ref is NOT pasted onto screens.
enum AladdinSnowballPalette {
    // MARK: Canvas stops (sampled from owner jpg, mid-frame avoiding icon)
    static let canvasTop = Color(red: 0.067, green: 0.043, blue: 0.075)       // #110B13
    static let canvasDeep = Color(red: 0.137, green: 0.090, blue: 0.153)      // #231727
    static let canvasMid = Color(red: 0.494, green: 0.329, blue: 0.514)       // #7E5483
    static let canvasGlow = Color(red: 0.816, green: 0.612, blue: 0.788)      // #D09CC9
    static let canvasBottom = Color(red: 0.690, green: 0.569, blue: 0.722)    // #B091B8

    static let glass = Color.white.opacity(0.12)
    static let glassStroke = Color.white.opacity(0.18)
    static let gold = Color.secondaryGold
    static let goldSoft = Color.secondaryGold.opacity(0.35)
    static let ink = Color.white
    static let inkMuted = Color.white.opacity(0.78)

    /// Vertical multi-stop gradient — top → bottom (owner canon).
    static var canvasGradient: LinearGradient {
        LinearGradient(
            stops: [
                .init(color: canvasTop, location: 0.00),
                .init(color: canvasDeep, location: 0.12),
                .init(color: canvasMid, location: 0.36),
                .init(color: canvasGlow, location: 0.62),
                .init(color: canvasBottom, location: 1.00)
            ],
            startPoint: .top,
            endPoint: .bottom
        )
    }

    static func glassCard(cornerRadius: CGFloat = CornerRadius.medium) -> some View {
        RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
            .fill(glass)
            .overlay(
                RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                    .stroke(glassStroke, lineWidth: 1)
            )
    }
}
