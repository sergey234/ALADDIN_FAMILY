import XCTest
@testable import ALADDIN

final class SubscriptionFamilyLimitsTests: XCTestCase {
    
    var subscriptionManager: SubscriptionManager!
    
    override func setUpWithError() throws {
        try super.setUpWithError()
        subscriptionManager = SubscriptionManager.shared
        // Reset for clean tests
        UserDefaults.standard.removeObject(forKey: "family_limit")
        UserDefaults.standard.removeObject(forKey: "family_remaining")
        UserDefaults.standard.removeObject(forKey: "family_roster_used_last")
        UserDefaults.standard.removeObject(forKey: "family_quota_source_last")
        UserDefaults.standard.removeObject(forKey: "family_quota_family_id_last")
        UserDefaults.standard.removeObject(forKey: FamilyLocalStore.familyIdKey)
        UserDefaults.standard.removeObject(forKey: FamilyLocalStore.lastResolvedFamilyIdKey)
        UserDefaults.standard.removeObject(forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        UserDefaults.standard.removeObject(forKey: "current_user_role")
    }
    
    override func tearDownWithError() throws {
        UserDefaults.standard.removeObject(forKey: "family_limit")
        UserDefaults.standard.removeObject(forKey: "family_remaining")
        UserDefaults.standard.removeObject(forKey: "family_roster_used_last")
        UserDefaults.standard.removeObject(forKey: "family_quota_source_last")
        UserDefaults.standard.removeObject(forKey: "family_quota_family_id_last")
        UserDefaults.standard.removeObject(forKey: FamilyLocalStore.familyIdKey)
        UserDefaults.standard.removeObject(forKey: FamilyLocalStore.lastResolvedFamilyIdKey)
        UserDefaults.standard.removeObject(forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        UserDefaults.standard.removeObject(forKey: "current_user_role")
        subscriptionManager = nil
        try super.tearDownWithError()
    }
    
    func testFamilyMemberLimitForAllTiers() {
        XCTAssertEqual(subscriptionManager.familyMemberLimit(for: .free), 1)
        XCTAssertEqual(subscriptionManager.familyMemberLimit(for: .trial), 3)
        XCTAssertEqual(subscriptionManager.familyMemberLimit(for: .personal), 2)
        XCTAssertEqual(subscriptionManager.familyMemberLimit(for: .family), 6)
        XCTAssertEqual(subscriptionManager.familyMemberLimit(for: .premium), 10)
    }
    
    func testCanAddFamilyMemberUnderLimit() {
        // Use direct method without full status (to avoid initializer issues)
        // Simulate by calling update (it sets limit to 3 for .trial)
        let testStatus = SubscriptionStatus(
            level: .trial,
            isActive: true,
            expiresAt: Date().addingTimeInterval(86400),
            trialInfo: nil,
            limits: SubscriptionLimits.trialLimits,
            components: [],
            lastUpdated: Date()
        )
        subscriptionManager.updateSubscriptionStatus(testStatus)
        
        let (allowed, message, upgradeSuggested) = subscriptionManager.canAddFamilyMember(currentCount: 2)
        XCTAssertTrue(allowed, "Should allow adding when under limit")
        XCTAssertNil(message)
        XCTAssertFalse(upgradeSuggested)
    }
    
    func testCanAddFamilyMemberAtLimit() {
        let testStatus = SubscriptionStatus(
            level: .trial,
            isActive: true,
            expiresAt: nil,
            trialInfo: nil,
            limits: SubscriptionLimits.trialLimits,
            components: [],
            lastUpdated: Date()
        )
        subscriptionManager.updateSubscriptionStatus(testStatus)
        
        let (allowed, message, upgrade) = subscriptionManager.canAddFamilyMember(currentCount: 3)
        XCTAssertFalse(allowed)
        XCTAssertNotNil(message)
        XCTAssertTrue(upgrade)
        XCTAssertTrue(message!.contains("3"))
    }
    
    func testCanAddFamilyMemberFreeTier() {
        let testStatus = SubscriptionStatus(
            level: .free,
            isActive: true,
            expiresAt: nil,
            trialInfo: nil,
            limits: SubscriptionLimits.freeLimits,
            components: [],
            lastUpdated: Date()
        )
        subscriptionManager.updateSubscriptionStatus(testStatus)
        
        let (allowed, _, _) = subscriptionManager.canAddFamilyMember(currentCount: 1)
        XCTAssertFalse(allowed) // At limit for free
    }

    /// JWT may still report `free` while trial dates are active — roster cap must be 3, not 1.
    func testFreePlanWithActiveTrialInfoUsesTrialFamilyCap() {
        let trial = TrialInfo(
            startDate: Date().addingTimeInterval(-86_400),
            endDate: Date().addingTimeInterval(86_400 * 7),
            durationDays: 14
        )
        XCTAssertTrue(trial.isActive)
        let testStatus = SubscriptionStatus(
            level: .free,
            isActive: true,
            expiresAt: nil,
            trialInfo: trial,
            limits: SubscriptionLimits.freeLimits,
            components: [],
            lastUpdated: Date()
        )
        subscriptionManager.updateSubscriptionStatus(testStatus)
        XCTAssertEqual(subscriptionManager.currentFamilyLimit, 3)
        let (allowed, _, _) = subscriptionManager.canAddFamilyMember(currentCount: 2)
        XCTAssertTrue(allowed)
    }
    
    func testPublishedPropertiesUpdateOnSubscriptionChange() {
        let testStatus = SubscriptionStatus(
            level: .family,
            isActive: true,
            expiresAt: nil,
            trialInfo: nil,
            limits: SubscriptionLimits.familyLimits,
            components: [],
            lastUpdated: Date()
        )
        
        subscriptionManager.updateSubscriptionStatus(testStatus)
        
        XCTAssertEqual(subscriptionManager.currentFamilyLimit, 6)
        XCTAssertGreaterThanOrEqual(subscriptionManager.currentFamilyRemaining, 5)
    }

    func testCanAddFamilyMemberIgnoresStalePersistedUsedWhenCurrentCountIsLower() {
        let testStatus = SubscriptionStatus(
            level: .trial,
            isActive: true,
            expiresAt: nil,
            trialInfo: nil,
            limits: SubscriptionLimits.trialLimits,
            components: [],
            lastUpdated: Date()
        )
        subscriptionManager.updateSubscriptionStatus(testStatus)
        XCTAssertEqual(subscriptionManager.currentFamilyLimit, 3)

        UserDefaults.standard.set(3, forKey: "family_roster_used_last")
        UserDefaults.standard.set(FamilyQuotaSource.persistedCache.rawValue, forKey: "family_quota_source_last")
        UserDefaults.standard.synchronize()

        let (allowed, message, upgrade) = subscriptionManager.canAddFamilyMember(currentCount: 0)
        XCTAssertTrue(allowed, "Persisted stale used should not block add when current roster is empty")
        XCTAssertNil(message)
        XCTAssertFalse(upgrade)
    }

    func testClearLocalFamilyRosterCacheForManualResetKeepsAuthAndTrialDataIntact() {
        UserDefaults.standard.set("FAM_123", forKey: FamilyLocalStore.familyIdKey)
        UserDefaults.standard.set("MEM_123", forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        UserDefaults.standard.set(3, forKey: "family_limit")
        UserDefaults.standard.set(0, forKey: "family_remaining")
        UserDefaults.standard.set(3, forKey: "family_roster_used_last")
        UserDefaults.standard.set(FamilyQuotaSource.persistedCache.rawValue, forKey: "family_quota_source_last")
        UserDefaults.standard.set("FAM_123", forKey: "family_quota_family_id_last")
        UserDefaults.standard.set("token-placeholder", forKey: "auth_token")
        UserDefaults.standard.set("trial-placeholder", forKey: "trial_status")
        UserDefaults.standard.synchronize()

        FamilyLocalStore.clearLocalFamilyRosterCacheForManualReset()

        XCTAssertEqual(UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey), "FAM_123")
        XCTAssertEqual(UserDefaults.standard.string(forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey), "MEM_123")
        XCTAssertEqual(UserDefaults.standard.string(forKey: "auth_token"), "token-placeholder")
        XCTAssertEqual(UserDefaults.standard.string(forKey: "trial_status"), "trial-placeholder")
        XCTAssertEqual(UserDefaults.standard.integer(forKey: "family_roster_used_last"), 0)
    }

    func testClearLocalFamilyContextForManualResetDoesNotTouchAuthAndTrialData() {
        UserDefaults.standard.set("FAM_999", forKey: FamilyLocalStore.familyIdKey)
        UserDefaults.standard.set("MEM_999", forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey)
        UserDefaults.standard.set("parent", forKey: "current_user_role")
        UserDefaults.standard.set("jwt-keep", forKey: "auth_token")
        UserDefaults.standard.set("trial-keep", forKey: "trial_status")
        UserDefaults.standard.synchronize()

        FamilyLocalStore.clearLocalFamilyContextForManualReset()

        XCTAssertNil(UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey))
        XCTAssertNil(UserDefaults.standard.string(forKey: FamilyLocalStore.yourMemberIdUserDefaultsKey))
        XCTAssertNil(UserDefaults.standard.string(forKey: "current_user_role"))
        XCTAssertEqual(UserDefaults.standard.string(forKey: "auth_token"), "jwt-keep")
        XCTAssertEqual(UserDefaults.standard.string(forKey: "trial_status"), "trial-keep")
    }
}