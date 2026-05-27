import XCTest
@testable import ALADDIN

/// HERO-3-26 — debounce ≥400 ms на stream emotion.
@MainActor
final class CompanionStreamEmotionDebouncerTests: XCTestCase {

    func testSubmitAppliesAfterDebounceInterval() async {
        let debouncer = CompanionStreamEmotionDebouncer(intervalNs: 50_000_000)
        var applied: CompanionHeroEmotion?
        debouncer.submit(.playful) { applied = $0 }
        XCTAssertNil(applied)
        try? await Task.sleep(nanoseconds: 80_000_000)
        XCTAssertEqual(applied, .playful)
    }

    func testSubmitReplacesPendingBeforeFire() async {
        let debouncer = CompanionStreamEmotionDebouncer(intervalNs: 50_000_000)
        var applied: CompanionHeroEmotion?
        debouncer.submit(.playful) { applied = $0 }
        debouncer.submit(.sad) { applied = $0 }
        try? await Task.sleep(nanoseconds: 80_000_000)
        XCTAssertEqual(applied, .sad)
    }

    func testCancelPreventsApply() async {
        let debouncer = CompanionStreamEmotionDebouncer(intervalNs: 50_000_000)
        var applied: CompanionHeroEmotion?
        debouncer.submit(.happy) { applied = $0 }
        debouncer.cancel()
        try? await Task.sleep(nanoseconds: 80_000_000)
        XCTAssertNil(applied)
    }

    func testFlushAppliesImmediately() {
        let debouncer = CompanionStreamEmotionDebouncer(intervalNs: 400_000_000)
        var applied: CompanionHeroEmotion?
        debouncer.submit(.comfort) { applied = $0 }
        debouncer.flush { applied = $0 }
        XCTAssertEqual(applied, .comfort)
    }

    func testDialoguePhaseVsContentEmotion() {
        XCTAssertTrue(CompanionHeroEmotion.thinking.isDialoguePhase)
        XCTAssertFalse(CompanionHeroEmotion.thinking.isStreamContentEmotion)
        XCTAssertTrue(CompanionHeroEmotion.sad.isStreamContentEmotion)
        XCTAssertTrue(CompanionHeroEmotion.sad.suppressesPlayfulVisuals)
        XCTAssertFalse(CompanionHeroEmotion.playful.suppressesPlayfulVisuals)
    }
}
