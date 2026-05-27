import CoreGraphics
import Foundation

/// HERO-3-19 — lip-sync MVP: `mouth_open` 0…1 (§2.2 плана героев).
enum CompanionHeroLipSync {
    static let minOpen: CGFloat = 0.35
    static let amplitude: CGFloat = 0.25
    static let angularSpeed: Double = 12

    static func proceduralMouthOpen(isActive: Bool, time: TimeInterval) -> CGFloat {
        guard isActive else { return 0 }
        let wave = sin(time * angularSpeed) * Double(amplitude)
        return CGFloat(min(1, max(0, Double(minOpen) + wave)))
    }
}
