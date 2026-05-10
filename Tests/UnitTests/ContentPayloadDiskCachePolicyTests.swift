import XCTest
@testable import ALADDIN

@MainActor
final class ContentPayloadDiskCachePolicyTests: XCTestCase {

    func testEnforceBudgetEvictsOldestByPayloadMtime() throws {
        let root = FileManager.default.temporaryDirectory
            .appendingPathComponent("ContentPayloadsTest-\(UUID().uuidString)", isDirectory: true)
        defer { try? FileManager.default.removeItem(at: root) }

        try FileManager.default.createDirectory(at: root, withIntermediateDirectories: true)

        func writePayload(dirName: String, bytes: Int, mtime: Date) throws {
            let dir = root.appendingPathComponent(dirName, isDirectory: true)
            try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
            let bin = dir.appendingPathComponent("payload.bin", isDirectory: false)
            try Data(repeating: 0xAB, count: bytes).write(to: bin, options: .atomic)
            try FileManager.default.setAttributes([.modificationDate: mtime], ofItemAtPath: bin.path)
        }

        let old = Date(timeIntervalSince1970: 1_000_000)
        let mid = Date(timeIntervalSince1970: 2_000_000)
        let young = Date(timeIntervalSince1970: 3_000_000)

        try writePayload(dirName: "a-old", bytes: 100, mtime: old)
        try writePayload(dirName: "b-mid", bytes: 100, mtime: mid)
        try writePayload(dirName: "c-young", bytes: 100, mtime: young)

        try ContentPayloadDiskCachePolicy.enforceBudget(root: root, maxTotalBytes: 250)

        XCTAssertTrue(FileManager.default.fileExists(atPath: root.appendingPathComponent("b-mid").path))
        XCTAssertTrue(FileManager.default.fileExists(atPath: root.appendingPathComponent("c-young").path))
        XCTAssertFalse(FileManager.default.fileExists(atPath: root.appendingPathComponent("a-old").path))
    }

    func testTotalPayloadBytesSumsOnlyPayloadBin() throws {
        let root = FileManager.default.temporaryDirectory
            .appendingPathComponent("ContentPayloadsSum-\(UUID().uuidString)", isDirectory: true)
        defer { try? FileManager.default.removeItem(at: root) }
        try FileManager.default.createDirectory(at: root, withIntermediateDirectories: true)

        let d1 = root.appendingPathComponent("x", isDirectory: true)
        try FileManager.default.createDirectory(at: d1, withIntermediateDirectories: true)
        try Data(count: 40).write(to: d1.appendingPathComponent("payload.bin"), options: .atomic)

        let total = try ContentPayloadDiskCachePolicy.totalPayloadBytes(under: root)
        XCTAssertEqual(total, 40)
    }
}
