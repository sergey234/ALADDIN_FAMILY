import XCTest
@testable import ALADDIN

final class VoiceDayIntentStatsTests: XCTestCase {
    func testCountsByIntentTags() {
        let today = Date()
        let notes: [VoiceNotesStore.StoredVoiceNote] = [
            .init(id: UUID(), title: "a", createdAt: today, durationSec: 1, transcriptPreview: "x", summary: "", summaryConfidence: 0, summaryVersion: 0, tags: ["intent_antifake_url"], audioPath: ""),
            .init(id: UUID(), title: "b", createdAt: today, durationSec: 1, transcriptPreview: "x", summary: "", summaryConfidence: 0, summaryVersion: 0, tags: ["intent_idea"], audioPath: ""),
            .init(id: UUID(), title: "c", createdAt: today, durationSec: 1, transcriptPreview: "x", summary: "", summaryConfidence: 0, summaryVersion: 0, tags: ["intent_remind"], audioPath: ""),
            .init(id: UUID(), title: "d", createdAt: today, durationSec: 1, transcriptPreview: "x", summary: "", summaryConfidence: 0, summaryVersion: 0, tags: ["intent_note"], audioPath: ""),
        ]
        let stats = VoiceDayIntentStats.fromTodayNotes(notes)
        XCTAssertEqual(stats.securityChecks, 1)
        XCTAssertEqual(stats.ideas, 1)
        XCTAssertEqual(stats.reminds, 1)
        XCTAssertEqual(stats.notes, 1)
        XCTAssertTrue(stats.hasAny)
    }
}
