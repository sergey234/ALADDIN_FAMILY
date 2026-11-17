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

/// Build 34 — trip metrics from real fix time/speed (Life360-style trip card + push).
final class DrivingTripAnalyzerTests: XCTestCase {
    private let t0 = Date(timeIntervalSince1970: 1_800_000_000)

    /// ~100 m north per step.
    private func point(_ i: Int, seconds: TimeInterval, v: Double? = nil, timed: Bool = true) -> DrivingRoutePoint {
        DrivingRoutePoint(
            latitude: 53.0 + Double(i) * 0.0009,
            longitude: 50.0,
            t: timed ? t0.addingTimeInterval(seconds) : nil,
            v: v
        )
    }

    func testMaxSpeedUsesRealFixSpacingNotFixed30s() {
        let pts = (0..<6).map { point($0, seconds: Double($0) * 5) }
        let m = DrivingTripAnalyzer.analyze(points: pts)
        XCTAssertEqual(m.maxSpeedKmh, 72, accuracy: 4, "100 m / 5 s ≈ 72 km/h (legacy 30 s rule gave ~12)")
        XCTAssertEqual(m.distanceKm, 0.5, accuracy: 0.02)
        XCTAssertTrue(m.events.isEmpty)
    }

    func testHardBrakingFromDopplerSpeedBecomesEventAndRisk() {
        let pts = [
            point(0, seconds: 0, v: 16.7),
            point(1, seconds: 4, v: 16.7),
            point(2, seconds: 6, v: 5.0)
        ]
        let m = DrivingTripAnalyzer.analyze(points: pts)
        XCTAssertEqual(m.events.map(\.type), [.braking])
        XCTAssertEqual(m.harshViolations.map(\.type), [.harshBraking])
        XCTAssertEqual(m.harshViolations.first?.severity, .high)
    }

    func testHardAccelerationDetected() {
        let pts = [point(0, seconds: 0, v: 3), point(1, seconds: 3, v: 13)]
        let m = DrivingTripAnalyzer.analyze(points: pts)
        XCTAssertEqual(m.events.map(\.type), [.acceleration])
    }

    func testLegacyUntimedTripKeepsOldMathAndNoEvents() {
        let pts = (0..<3).map { point($0, seconds: 0, timed: false) }
        let m = DrivingTripAnalyzer.analyze(points: pts)
        XCTAssertEqual(m.maxSpeedKmh, 12, accuracy: 1)
        XCTAssertTrue(m.events.isEmpty)
    }

    func testRoutePointDecodesWithoutTimeFields() throws {
        let data = Data(#"[{"latitude":53.1,"longitude":50.1}]"#.utf8)
        let pts = try JSONDecoder().decode([DrivingRoutePoint].self, from: data)
        XCTAssertNil(pts.first?.t)
        XCTAssertNil(pts.first?.v)
    }

    func testMotionClassifierDropsBikeKeepsCarAndUnknown() {
        let end = t0.addingTimeInterval(600)
        let bike = [DriveActivityClassifier.Segment(start: t0, automotive: false, nonCar: true)]
        let car = [DriveActivityClassifier.Segment(start: t0, automotive: true, nonCar: false)]
        XCTAssertTrue(DriveActivityClassifier.isNotDriving(bike, end: end))
        XCTAssertFalse(DriveActivityClassifier.isNotDriving(car, end: end))
        XCTAssertFalse(DriveActivityClassifier.isNotDriving([], end: end), "No motion data → keep the trip")
    }
}
