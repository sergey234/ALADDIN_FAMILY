import XCTest
@testable import ALADDIN

final class CallSessionsStoreTests: XCTestCase {
    func testUpsertAndLoad() {
        let store = CallSessionsStore()
        let session = CallSession(
            goal: "Банк",
            mode: .postOnly,
            source: .postCallPush,
            transcript: "Перезвонят завтра",
            summary: CallSummaryService.summarize(goal: "Банк", transcriptOrNote: "Перезвонят завтра")
        )
        store.upsert(session)
        let loaded = store.load()
        XCTAssertTrue(loaded.contains(where: { $0.id == session.id }))
        XCTAssertFalse(loaded.first(where: { $0.id == session.id })?.summary.isEmpty ?? true)
        store.delete(id: session.id)
        XCTAssertFalse(store.load().contains(where: { $0.id == session.id }))
    }

    func testSummaryRiskHint() {
        let s = CallSummaryService.summarize(goal: "", transcriptOrNote: "Просили назвать пароль от банка")
        XCTAssertFalse(s.risks.isEmpty)
    }
}
