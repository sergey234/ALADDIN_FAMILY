import XCTest
@testable import ALADDIN

/// Smoke: family_id Keychain ↔ legacy UserDefaults (Build 198 family chat fix).
final class FamilyLocalStorePersistenceTests: XCTestCase {
    private let testFamilyId = "FAM_BUILD198_TEST"
    private let testUserId = "170"

    override func tearDown() {
        KeychainManager.shared.delete(forKey: .familyId)
        KeychainManager.shared.delete(scopedKey: "family_id_uid_\(testUserId)")
        UserDefaults.standard.removeObject(forKey: FamilyLocalStore.familyIdKey)
        UserDefaults.standard.removeObject(forKey: FamilyLocalStore.familyContextOwnerUserIdKey)
        super.tearDown()
    }

    func testLoadPersistedFamilyIdReadsKeychainAfterPersist() {
        UserDefaults.standard.set(testUserId, forKey: FamilyLocalStore.familyContextOwnerUserIdKey)
        FamilyLocalStore.persistFamilyId(testFamilyId)

        XCTAssertNil(UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey))
        XCTAssertEqual(FamilyLocalStore.loadPersistedFamilyId(), testFamilyId)
    }

    func testLoadPersistedFamilyIdMigratesLegacyUserDefaults() {
        UserDefaults.standard.set(testUserId, forKey: FamilyLocalStore.familyContextOwnerUserIdKey)
        UserDefaults.standard.set(testFamilyId, forKey: FamilyLocalStore.familyIdKey)

        XCTAssertEqual(FamilyLocalStore.loadPersistedFamilyId(), testFamilyId)
        XCTAssertNil(UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey))
        XCTAssertEqual(
            KeychainManager.shared.loadString(scopedKey: "family_id_uid_\(testUserId)"),
            testFamilyId
        )
    }

    func testScopedFamilyIdIsolatedPerUserId() {
        UserDefaults.standard.set(testUserId, forKey: FamilyLocalStore.familyContextOwnerUserIdKey)
        FamilyLocalStore.persistFamilyId(testFamilyId)

        UserDefaults.standard.set("169", forKey: FamilyLocalStore.familyContextOwnerUserIdKey)
        XCTAssertEqual(FamilyLocalStore.loadPersistedFamilyId(), "")

        UserDefaults.standard.set(testUserId, forKey: FamilyLocalStore.familyContextOwnerUserIdKey)
        XCTAssertEqual(FamilyLocalStore.loadPersistedFamilyId(), testFamilyId)
    }

    func testClearPersistedFamilyContextRemovesKeychainFamilyId() {
        UserDefaults.standard.set(testUserId, forKey: FamilyLocalStore.familyContextOwnerUserIdKey)
        FamilyLocalStore.persistFamilyId(testFamilyId)
        FamilyLocalStore.clearPersistedFamilyContextWhenServerReportsNoFamily()

        XCTAssertEqual(FamilyLocalStore.loadPersistedFamilyId(), "")
        XCTAssertNil(KeychainManager.shared.loadString(forKey: .familyId))
        XCTAssertNil(KeychainManager.shared.loadString(scopedKey: "family_id_uid_\(testUserId)"))
    }

    func testNeedsServerFamilyCreationWithoutJWT() {
        KeychainManager.shared.delete(forKey: .authToken)
        XCTAssertFalse(FamilyLocalStore.needsServerFamilyCreation())
    }

    func testNeedsServerFamilyCreationWithJWTAndNoFamily() {
        KeychainManager.shared.save("test.jwt.token", forKey: .authToken)
        FamilyLocalStore.clearPersistedFamilyContextWhenServerReportsNoFamily()
        XCTAssertTrue(FamilyLocalStore.needsServerFamilyCreation())
        KeychainManager.shared.delete(forKey: .authToken)
    }

    func testPrepareCreateFamilyFlowClearsAdminAddMode() {
        UserDefaults.standard.set(true, forKey: "admin_add_mode")
        FamilyLocalStore.prepareCreateFamilyFlow()
        XCTAssertFalse(UserDefaults.standard.bool(forKey: "admin_add_mode"))
    }
}
