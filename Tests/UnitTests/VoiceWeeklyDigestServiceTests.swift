import XCTest
@testable import ALADDIN

final class VoiceWeeklyDigestServiceTests: XCTestCase {
    func testBuildCountsLastSevenDays() {
        let cal = Calendar.current
        let now = Date()
        let old = cal.date(byAdding: .day, value: -10, to: now)!
        let mid = cal.date(byAdding: .day, value: -2, to: now)!
        let notes: [VoiceNotesStore.StoredVoiceNote] = [
            .init(id: UUID(), title: "a", createdAt: now, durationSec: 1, transcriptPreview: "ссылка", summary: "check", summaryConfidence: 0, summaryVersion: 0, tags: ["intent_antifake_url"], audioPath: ""),
            .init(id: UUID(), title: "b", createdAt: mid, durationSec: 1, transcriptPreview: "идея", summary: "idea line", summaryConfidence: 0, summaryVersion: 0, tags: ["intent_idea"], audioPath: ""),
            .init(id: UUID(), title: "c", createdAt: old, durationSec: 1, transcriptPreview: "old", summary: "too old", summaryConfidence: 0, summaryVersion: 0, tags: ["intent_remind"], audioPath: ""),
        ]
        let result = VoiceWeeklyDigestService.build(notes: notes, now: now, calendar: cal)
        XCTAssertEqual(result.stats.securityChecks, 1)
        XCTAssertEqual(result.stats.ideas, 1)
        XCTAssertEqual(result.stats.reminds, 0)
        XCTAssertTrue(result.topLines.contains(where: { $0.contains("check") || $0.contains("idea") }))
    }
}
