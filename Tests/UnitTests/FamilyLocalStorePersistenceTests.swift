import XCTest
@testable import ALADDIN

/// Smoke: family_id Keychain ↔ legacy UserDefaults (Build 198 family chat fix).
final class FamilyLocalStorePersistenceTests: XCTestCase {
    private let testFamilyId = "FAM_BUILD198_TEST"

    override func tearDown() {
        KeychainManager.shared.delete(forKey: .familyId)
        UserDefaults.standard.removeObject(forKey: FamilyLocalStore.familyIdKey)
        super.tearDown()
    }

    func testLoadPersistedFamilyIdReadsKeychainAfterPersist() {
        FamilyLocalStore.persistFamilyId(testFamilyId)

        XCTAssertNil(UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey))
        XCTAssertEqual(FamilyLocalStore.loadPersistedFamilyId(), testFamilyId)
    }

    func testLoadPersistedFamilyIdMigratesLegacyUserDefaults() {
        UserDefaults.standard.set(testFamilyId, forKey: FamilyLocalStore.familyIdKey)

        XCTAssertEqual(FamilyLocalStore.loadPersistedFamilyId(), testFamilyId)
        XCTAssertNil(UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey))
        XCTAssertEqual(KeychainManager.shared.loadString(forKey: .familyId), testFamilyId)
    }
}
