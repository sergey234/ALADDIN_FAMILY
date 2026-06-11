import XCTest
@testable import ALADDIN

final class AntifakeSharePayloadStoreTests: XCTestCase {

    override func setUp() {
        super.setUp()
        AntifakeSharePayloadStore.clear()
    }

    override func tearDown() {
        AntifakeSharePayloadStore.clear()
        super.tearDown()
    }

    func testSaveLoadAndConsumeRoundTrip() {
        AntifakeSharePayloadStore.save(mode: .text, value: "Suspicious message")

        let loaded = AntifakeSharePayloadStore.load()
        XCTAssertEqual(loaded?.mode, .text)
        XCTAssertEqual(loaded?.value, "Suspicious message")

        let consumed = AntifakeSharePayloadStore.consume()
        XCTAssertEqual(consumed?.value, "Suspicious message")
        XCTAssertNil(AntifakeSharePayloadStore.load())
    }

    func testUrlPayloadPersistsInAppGroup() {
        let payload = AntifakeSharePayload(mode: .url, value: "https://example.com/phish", createdAt: Date())
        AntifakeSharePayloadStore.save(payload)

        XCTAssertEqual(AntifakeSharePayloadStore.load()?.mode, .url)
        XCTAssertEqual(AntifakeSharePayloadStore.load()?.value, "https://example.com/phish")
    }
}
