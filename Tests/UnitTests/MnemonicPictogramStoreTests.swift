import XCTest
import UIKit
@testable import ALADDIN

final class MnemonicPictogramStoreTests: XCTestCase {

    private var tempRoot: URL!

    override func setUp() {
        super.setUp()
        tempRoot = FileManager.default.temporaryDirectory
            .appendingPathComponent("mnemo-pictogram-tests-\(UUID().uuidString)", isDirectory: true)
        try? FileManager.default.createDirectory(at: tempRoot, withIntermediateDirectories: true)
    }

    override func tearDown() {
        try? FileManager.default.removeItem(at: tempRoot)
        super.tearDown()
    }

    func testSaveAndLoad_roundTripPNG() throws {
        let store = MnemonicPictogramStore(fileManager: .default, rootURL: tempRoot)
        let size = CGSize(width: 8, height: 8)
        UIGraphicsBeginImageContext(size)
        UIColor.cyan.setFill()
        UIRectFill(CGRect(origin: .zero, size: size))
        let image = UIGraphicsGetImageFromCurrentImageContext()!
        UIGraphicsEndImageContext()

        let url = try store.saveImage(image, itemId: "study.09", childId: "child-a")
        XCTAssertTrue(FileManager.default.fileExists(atPath: url.path))
        XCTAssertTrue(url.path.contains("MnemoPictograms") || url.path.contains(tempRoot.lastPathComponent))
        XCTAssertTrue(store.hasPictogram(itemId: "study.09", childId: "child-a"))
        XCTAssertNotNil(store.loadImage(itemId: "study.09", childId: "child-a"))
        XCTAssertEqual(store.pictogramCount(childId: "child-a"), 1)
    }

    func testDelete_removesFileAndIndexEntry() throws {
        let store = MnemonicPictogramStore(fileManager: .default, rootURL: tempRoot)
        let png = Data([0x89, 0x50, 0x4E, 0x47]) // minimal header stub; UIImage load may fail but file exists
        _ = try store.savePNG(png, itemId: "games.05", childId: nil)
        XCTAssertTrue(store.hasPictogram(itemId: "games.05"))
        store.delete(itemId: "games.05")
        XCTAssertFalse(store.hasPictogram(itemId: "games.05"))
        XCTAssertEqual(store.pictogramCount(), 0)
    }

    func testSanitizedFileName_replacesUnsafeCharacters() {
        let store = MnemonicPictogramStore(fileManager: .default, rootURL: tempRoot)
        XCTAssertEqual(store.sanitizedFileName(for: "study.01"), "study.01")
        XCTAssertFalse(store.sanitizedFileName(for: "bad/id").contains("/"))
    }
}
