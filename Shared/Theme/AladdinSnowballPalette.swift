import SwiftUI

/// Family Hub canvas — Hub Calm Navy (Device QA 2026-11-10).
/// Supersedes lilac/magenta mid·glow for contrast; keeps `canvasTop` + gold accents.
/// Prior lock: `docs/competitors/SNOWBALL_S18_COLOR_CANON_FOR_ML_2026-11-09.md` (historical).
/// Vertical: near-black → deep indigo → soft navy + light gold veil. No pink/lilac.
enum AladdinSnowballPalette {
    // MARK: Canvas stops — Hub Calm Navy
    static let canvasTop = Color(red: 0.067, green: 0.043, blue: 0.075)       // #110B13
    static let canvasDeep = Color(red: 0.078, green: 0.094, blue: 0.165)      // #14182A
    static let canvasMid = Color(red: 0.110, green: 0.141, blue: 0.220)       // #1C2438
    static let canvasGlow = Color(red: 0.145, green: 0.165, blue: 0.255)      // #252A41 soft indigo
    static let canvasBottom = Color(red: 0.090, green: 0.100, blue: 0.145)    // #171A25

    static let glass = Color.white.opacity(0.12)
    static let glassStroke = Color.white.opacity(0.18)
    static let gold = Color.secondaryGold
    static let goldSoft = Color.secondaryGold.opacity(0.35)
    static let ink = Color.white
    static let inkMuted = Color.white.opacity(0.92)

    /// Vertical Calm Navy — readable body text on glass cards.
    static var canvasGradient: LinearGradient {
        LinearGradient(
            stops: [
                .init(color: canvasTop, location: 0.00),
                .init(color: canvasDeep, location: 0.28),
                .init(color: canvasMid, location: 0.55),
                .init(color: canvasGlow.opacity(0.85), location: 0.78),
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
