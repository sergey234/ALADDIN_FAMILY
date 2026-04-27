import Foundation

/// W4-2: Central caps for celebration particles, haptic/sound throttling, and cheap animation constants.
/// Values are conservative for battery/thermal; tune with profiling on real devices.
enum PerformanceBudget {
    /// Hard cap on particles per single burst (kind-specific base counts are clamped to this).
    static let celebrationParticlesGlobalMax = 48

    static func celebrationParticleCount(for kind: CelebrationBurstKind) -> Int {
        let base: Int
        switch kind {
        case .confetti: base = 44
        case .correctAnswerStars: base = 18
        case .achievementMagic: base = 36
        case .rewardPurchase: base = 22
        }
        return min(base, celebrationParticlesGlobalMax)
    }

    /// Canvas refresh for `CelebrationParticleBurstView` (Hz).
    static let celebrationParticleCanvasFPS: Double = 30

    // MARK: - Haptics (min interval between similar events, seconds)

    static let hapticMinIntervalSelection: TimeInterval = 0.05
    static let hapticMinIntervalImpact: TimeInterval = 0.07
    static let hapticMinIntervalNotification: TimeInterval = 0.12

    // MARK: - Sound (SoundEffectPlayer)

    static func soundMinInterval(priority: SoundPriority) -> TimeInterval {
        switch priority {
        case .critical: return 0
        case .high: return 0.04
        case .medium: return 0.09
        case .low: return 0.16
        }
    }

    /// Extra spacing when the same `AppSoundEffect` is triggered repeatedly.
    static let soundSameEffectMinInterval: TimeInterval = 0.2
}
