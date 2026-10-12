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

    func testDocumentInboxRoundTrip() throws {
        let bytes = Data("fake-pdf-bytes".utf8)
        try AntifakeSharePayloadStore.saveDocument(data: bytes, filename: "bill.pdf")

        let payload = AntifakeSharePayloadStore.consume()
        XCTAssertEqual(payload?.mode, .document)
        XCTAssertEqual(payload?.value, "bill.pdf")

        let file = AntifakeSharePayloadStore.consumeDocumentFile(relativeName: "bill.pdf")
        XCTAssertEqual(file?.data, bytes)
        XCTAssertEqual(file?.filename, "bill.pdf")
        XCTAssertNil(AntifakeShareFileInbox.loadData(relativeName: "bill.pdf"))
    }

    func testDocumentRejectsOversizedFile() {
        let oversized = Data(repeating: 0x41, count: AntifakeShareConstants.maxDocumentBytes + 1)
        XCTAssertThrowsError(try AntifakeSharePayloadStore.saveDocument(data: oversized, filename: "big.pdf"))
    }
}
