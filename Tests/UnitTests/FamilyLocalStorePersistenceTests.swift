import XCTest
import CoreLocation
@testable import ALADDIN

/// Smoke: family_id Keychain ↔ legacy UserDefaults (Build 198 family chat fix).
final class FamilyLocalStorePersistenceTests: XCTestCase {
    private let testFamilyId = "FAM_BUILD198_TEST"
    private let testUserId = "170"

    override func setUp() {
        super.setUp()
        FamilyLocalStore.invalidateFamilyIdMemo()
    }

    override func tearDown() {
        KeychainManager.shared.delete(forKey: .familyId)
        KeychainManager.shared.delete(scopedKey: "family_id_uid_\(testUserId)")
        UserDefaults.standard.removeObject(forKey: FamilyLocalStore.familyIdKey)
        UserDefaults.standard.removeObject(forKey: FamilyLocalStore.familyContextOwnerUserIdKey)
        FamilyLocalStore.invalidateFamilyIdMemo()
        super.tearDown()
    }

    func testLoadPersistedFamilyIdSeesRecoveryCodeWrite() {
        UserDefaults.standard.set(testUserId, forKey: FamilyLocalStore.familyContextOwnerUserIdKey)
        XCTAssertEqual(FamilyLocalStore.loadPersistedFamilyId(), "")
        XCTAssertTrue(RecoveryCodeStorageManager.shared.saveRecoveryCode("RC-TEST", familyID: testFamilyId))
        XCTAssertEqual(FamilyLocalStore.loadPersistedFamilyId(), testFamilyId)
        _ = RecoveryCodeStorageManager.shared.deleteRecoveryCode()
    }

    func testLoadPersistedFamilyIdReadsKeychainAfterPersist() {
        UserDefaults.standard.set(testUserId, forKey: FamilyLocalStore.familyContextOwnerUserIdKey)
        FamilyLocalStore.persistFamilyId(testFamilyId)

        XCTAssertNil(UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey))
        XCTAssertEqual(FamilyLocalStore.loadPersistedFamilyId(), testFamilyId)
        XCTAssertEqual(KeychainManager.shared.loadString(forKey: .familyId), testFamilyId)
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

    func testIsCurrentAccountFamilyCreatorRequiresMatchingMemberId() {
        let suite = "FamilyLocalStoreCreatorTests"
        let defaults = UserDefaults(suiteName: suite)!
        defaults.removePersistentDomain(forName: suite)
        defer { defaults.removePersistentDomain(forName: suite) }

        XCTAssertFalse(FamilyLocalStore.isCurrentAccountFamilyCreator(defaults: defaults))

        defaults.set("MEM_AAAA1111", forKey: FamilyLocalStore.familyCreatorMemberIdKey)
        defaults.set("MEM_BBBB2222", forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        XCTAssertFalse(FamilyLocalStore.isCurrentAccountFamilyCreator(defaults: defaults))

        defaults.set("MEM_AAAA1111", forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        XCTAssertTrue(FamilyLocalStore.isCurrentAccountFamilyCreator(defaults: defaults))
    }

    func testUserIdFromJWTPayloadAcceptsIntAndString() {
        XCTAssertEqual(FamilyLocalStore.userId(fromJWTPayload: ["user_id": 884]), "884")
        XCTAssertEqual(FamilyLocalStore.userId(fromJWTPayload: ["user_id": "1521"]), "1521")
        XCTAssertNil(FamilyLocalStore.userId(fromJWTPayload: ["sub": "1521"]))
    }

    func testStableDeviceIdentityIsStableAcrossCalls() {
        let first = StableDeviceIdentity.current()
        XCTAssertFalse(first.isEmpty)
        XCTAssertEqual(StableDeviceIdentity.current(), first)
        XCTAssertFalse(
            KeychainManager.Key.allCases.map(\.rawValue).contains("aladdin_stable_device_id_v1"),
            "KeychainManager.clearAll (logout) must not reset device identity"
        )
    }
}

/// Map setup card: one next step so the user's avatar appears on the family map.
final class FamilyMapSetupStepTests: XCTestCase {
    func testNotDeterminedAsksForAccess() {
        XCTAssertEqual(
            FamilyMapSetupStep.resolve(auth: .notDetermined, preciseEnabled: true, entitled: true, alwaysCardDismissed: false),
            .allowAccess
        )
    }

    func testDeniedGoesToSettings() {
        XCTAssertEqual(
            FamilyMapSetupStep.resolve(auth: .denied, preciseEnabled: true, entitled: true, alwaysCardDismissed: false),
            .openSettings
        )
    }

    func testPreciseOffWinsOverAlways() {
        XCTAssertEqual(
            FamilyMapSetupStep.resolve(auth: .authorizedWhenInUse, preciseEnabled: false, entitled: true, alwaysCardDismissed: false),
            .preciseLocation
        )
        XCTAssertEqual(
            FamilyMapSetupStep.resolve(auth: .authorizedAlways, preciseEnabled: false, entitled: true, alwaysCardDismissed: true),
            .preciseLocation
        )
    }

    func testWhenInUseOffersAlwaysOnlyForEntitledAndNotDismissed() {
        XCTAssertEqual(
            FamilyMapSetupStep.resolve(auth: .authorizedWhenInUse, preciseEnabled: true, entitled: true, alwaysCardDismissed: false),
            .alwaysAllow
        )
        XCTAssertNil(
            FamilyMapSetupStep.resolve(auth: .authorizedWhenInUse, preciseEnabled: true, entitled: true, alwaysCardDismissed: true)
        )
        XCTAssertNil(
            FamilyMapSetupStep.resolve(auth: .authorizedWhenInUse, preciseEnabled: true, entitled: false, alwaysCardDismissed: false)
        )
    }

    func testAlwaysAndPreciseNeedsNoCard() {
        XCTAssertNil(
            FamilyMapSetupStep.resolve(auth: .authorizedAlways, preciseEnabled: true, entitled: true, alwaysCardDismissed: false)
        )
    }

    func testAccuracyLabelUsesKilometresForCityGrade() {
        let loc = LocalizationManager.shared
        let km = FamilyMapSetupStep.accuracyLabel(meters: 5155, localization: loc)
        XCTAssertTrue(km.hasPrefix("5"), km)
        XCTAssertFalse(km.contains("5155"), km)
        let m = FamilyMapSetupStep.accuracyLabel(meters: 784, localization: loc)
        XCTAssertTrue(m.hasPrefix("780"), m)
        XCTAssertEqual(FamilyMapSetupStep.accuracyLabel(meters: -1, localization: loc), "")
    }

    func testShareConsentComesAfterPreciseAndBeforeAlways() {
        XCTAssertEqual(
            FamilyMapSetupStep.resolve(
                auth: .authorizedWhenInUse, preciseEnabled: true, entitled: true,
                alwaysCardDismissed: false, familySharingDecided: false
            ),
            .shareWithFamily
        )
        XCTAssertEqual(
            FamilyMapSetupStep.resolve(
                auth: .authorizedWhenInUse, preciseEnabled: false, entitled: true,
                alwaysCardDismissed: false, familySharingDecided: false
            ),
            .preciseLocation
        )
        XCTAssertNil(
            FamilyMapSetupStep.resolve(
                auth: .authorizedAlways, preciseEnabled: true, entitled: false,
                alwaysCardDismissed: false, familySharingDecided: false
            )
        )
    }
}

final class FamilyMapAutoShareTests: XCTestCase {
    func testFirstPreciseFixIsPublished() {
        XCTAssertTrue(FamilyMapAutoShare.shouldPublish(accuracy: 30, distanceFromLast: nil, secondsSinceLast: nil))
    }

    func testApproximateFixIsNeverPublished() {
        XCTAssertFalse(FamilyMapAutoShare.shouldPublish(accuracy: 3000, distanceFromLast: nil, secondsSinceLast: nil))
        XCTAssertFalse(FamilyMapAutoShare.shouldPublish(accuracy: -1, distanceFromLast: nil, secondsSinceLast: nil))
    }

    func testThrottleRespectsServerRateLimit() {
        XCTAssertFalse(FamilyMapAutoShare.shouldPublish(accuracy: 20, distanceFromLast: 5000, secondsSinceLast: 60))
        XCTAssertTrue(FamilyMapAutoShare.shouldPublish(accuracy: 20, distanceFromLast: 250, secondsSinceLast: 160))
        XCTAssertFalse(FamilyMapAutoShare.shouldPublish(accuracy: 20, distanceFromLast: 50, secondsSinceLast: 200))
        XCTAssertTrue(FamilyMapAutoShare.shouldPublish(accuracy: 20, distanceFromLast: 0, secondsSinceLast: 301))
    }

    func testOwnerTierGrantsLiveMapToMembers() {
        XCTAssertTrue(FamilyMapLiveAccess.ownerTierGrantsLiveMap("family"))
        XCTAssertTrue(FamilyMapLiveAccess.ownerTierGrantsLiveMap(" Premium "))
        XCTAssertTrue(FamilyMapLiveAccess.ownerTierGrantsLiveMap("trial"))
        XCTAssertFalse(FamilyMapLiveAccess.ownerTierGrantsLiveMap("free"))
        XCTAssertFalse(FamilyMapLiveAccess.ownerTierGrantsLiveMap("personal"))
        XCTAssertFalse(FamilyMapLiveAccess.ownerTierGrantsLiveMap(nil))
    }

    func testMemberPinsSkipSelfMainAndSamePlace() {
        let main = CLLocationCoordinate2D(latitude: 55.75, longitude: 37.62)
        let pins = FamilyMapMemberPin.extras(
            from: [
                ("MEM_SELF", "Я", CLLocationCoordinate2D(latitude: 55.70, longitude: 37.50)),
                ("MEM_MAIN", "Мама", CLLocationCoordinate2D(latitude: 55.71, longitude: 37.51)),
                ("MEM_NEAR", "Папа", CLLocationCoordinate2D(latitude: 55.75005, longitude: 37.62)),
                ("MEM_KID", "Аня", CLLocationCoordinate2D(latitude: 55.80, longitude: 37.70)),
                ("MEM_KID", "Аня", CLLocationCoordinate2D(latitude: 55.80, longitude: 37.70)),
                ("MEM_NOGEO", "Бабушка", nil)
            ],
            selfMemberId: "MEM_SELF",
            mainMemberId: "MEM_MAIN",
            mainCoordinate: main
        )
        XCTAssertEqual(pins.map(\.memberId), ["MEM_KID"])
        XCTAssertEqual(pins.first?.name, "Аня")
    }
}
