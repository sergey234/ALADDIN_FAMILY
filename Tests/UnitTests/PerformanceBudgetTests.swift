import XCTest
@testable import ALADDIN

@MainActor
final class PerformanceBudgetTests: XCTestCase {

    func testCelebrationParticleCountNeverExceedsGlobalMax() {
        for kind in [
            CelebrationBurstKind.confetti,
            .correctAnswerStars,
            .achievementMagic,
            .rewardPurchase
        ] {
            let n = PerformanceBudget.celebrationParticleCount(for: kind)
            XCTAssertLessThanOrEqual(n, PerformanceBudget.celebrationParticlesGlobalMax, "\(kind)")
            XCTAssertGreaterThan(n, 0, "\(kind)")
        }
    }

    func testSoundPriorityIntervalsAreOrdered() {
        let c = PerformanceBudget.soundMinInterval(priority: .critical)
        let h = PerformanceBudget.soundMinInterval(priority: .high)
        let m = PerformanceBudget.soundMinInterval(priority: .medium)
        let l = PerformanceBudget.soundMinInterval(priority: .low)
        XCTAssertEqual(c, 0, accuracy: 0.0001)
        XCTAssertLessThanOrEqual(h, m)
        XCTAssertLessThanOrEqual(m, l)
    }
}
