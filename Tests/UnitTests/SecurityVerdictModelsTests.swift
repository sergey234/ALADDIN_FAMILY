import XCTest
@testable import ALADDIN

final class SecurityVerdictModelsTests: XCTestCase {

    func testDecodeValidVerdict() throws {
        let json = """
        {
          "verdict": "likely_fake",
          "confidence": 0.91,
          "reasons": ["url_phishing_path"],
          "sources": [
            {"id": "phishing_awareness", "title_key": "antifake_source_phishing_awareness", "url": "https://example.com"}
          ],
          "source": "real_agent",
          "agent": "heuristic_url",
          "job_id": null,
          "checked_at": "2026-06-10T12:00:00.000Z",
          "premium_required": false
        }
        """
        let verdict = try SecurityVerdictParsers.decodeVerdict(from: Data(json.utf8))
        XCTAssertEqual(verdict.verdict, .likelyFake)
        XCTAssertEqual(verdict.confidence, 0.91, accuracy: 0.001)
        XCTAssertEqual(verdict.sources.count, 1)
        XCTAssertEqual(verdict.sources.first?.id, "phishing_awareness")
        XCTAssertTrue(verdict.isLikelyThreat)
    }

    func testRejectMockSource() throws {
        let json = """
        {"verdict":"likely_real","confidence":1,"reasons":[],"source":"sfm_mock","premium_required":false}
        """
        XCTAssertThrowsError(try SecurityVerdictParsers.decodeVerdict(from: Data(json.utf8))) { error in
            XCTAssertEqual(error as? SecurityVerdictValidationError, .mockSourceRejected("sfm_mock"))
        }
    }

    func testDecodeJobEnqueue() throws {
        let json = """
        {"job_id":"abc-123","status":"queued"}
        """
        let job = try SecurityVerdictParsers.decodeJobEnqueue(from: Data(json.utf8))
        XCTAssertEqual(job.jobId, "abc-123")
        XCTAssertEqual(job.status, .queued)
    }

    func testPremiumGate403DetailObject() {
        let json = """
        {"detail":{"error":"premium_required","message":"Antifake checks require Premium subscription","premium_required":true}}
        """
        let outcome = PremiumGateHandler.outcome(httpStatus: 403, data: Data(json.utf8))
        XCTAssertEqual(outcome, .premiumRequired(message: "Antifake checks require Premium subscription"))
        XCTAssertTrue(outcome.requiresUpgrade)
    }

    func testPremiumGate403GenericForbidden() {
        let json = """
        {"detail":"Access denied"}
        """
        let outcome = PremiumGateHandler.outcome(httpStatus: 403, data: Data(json.utf8))
        XCTAssertEqual(outcome, .forbidden(message: "Access denied"))
    }

    func testNetworkErrorPremiumRequired() {
        let error = NetworkError.forbidden("premium_required: upgrade plan")
        XCTAssertTrue(error.isPremiumRequired)
        XCTAssertEqual(PremiumGateHandler.outcome(from: error), .premiumRequired(message: "premium_required: upgrade plan"))
    }

    func testDecodeJobPollPending() throws {
        let json = """
        {"job_id":"abc-123","status":"queued","type":"audio"}
        """
        let outcome = try SecurityVerdictParsers.decodeJobPoll(from: Data(json.utf8))
        guard case .pending(let pending) = outcome else {
            return XCTFail("expected pending")
        }
        XCTAssertEqual(pending.jobId, "abc-123")
        XCTAssertEqual(pending.status, .queued)
    }

    func testAntifakeCheckFailureHandlerPremium403() {
        let error = NetworkError.forbidden("premium_required: Antifake checks require Premium subscription")
        let presentation = AntifakeCheckFailureHandler.present(
            error: error,
            localizationManager: LocalizationManager()
        )
        XCTAssertTrue(presentation.requiresPremiumUpgrade)
        XCTAssertNotNil(presentation.errorMessage)
    }

    func testAntifakeCheckFailureHandlerVerdictPremiumFlag() {
        let error = SecurityVerdictPremiumRequiredError(message: "Upgrade plan")
        let presentation = AntifakeCheckFailureHandler.present(
            error: error,
            localizationManager: LocalizationManager()
        )
        XCTAssertTrue(presentation.requiresPremiumUpgrade)
        XCTAssertEqual(presentation.errorMessage, "Upgrade plan")
    }

    func testDecodeJobEnqueueCompleted() throws {
        let json = """
        {
          "job_id": "abc-123",
          "status": "completed",
          "verdict": "likely_real",
          "confidence": 0.88,
          "reasons": ["natural voice"],
          "source": "real_agent",
          "premium_required": false
        }
        """
        let result = try SecurityVerdictParsers.decodeJobEnqueueResult(from: Data(json.utf8))
        guard case .completed(let verdict) = result else {
            return XCTFail("expected completed")
        }
        XCTAssertEqual(verdict.verdict, .likelyReal)
    }

    func testDecodeInsufficientDataVerdict() throws {
        let json = """
        {
          "verdict": "insufficient_data",
          "confidence": 0.0,
          "fake_risk": 0.0,
          "reasons": ["text_too_short"],
          "source": "real_agent",
          "agent": "fake_news_detection_agent",
          "premium_required": false
        }
        """
        let verdict = try SecurityVerdictParsers.decodeVerdict(from: Data(json.utf8))
        XCTAssertEqual(verdict.verdict, .insufficientData)
        XCTAssertEqual(verdict.confidence, 0, accuracy: 0.001)
        XCTAssertEqual(verdict.fakeRisk, 0, accuracy: 0.001)
    }

    // MARK: - Antifake / trial access (G-03 + 14-day trial)

    func testTrialFeatureAccessTierMatchesPremium() {
        XCTAssertEqual(TariffType.trial.featureAccessTier, TariffType.premium.featureAccessTier)
        XCTAssertGreaterThan(TariffType.trial.featureAccessTier, TariffType.family.featureAccessTier)
    }

    @MainActor
    func testTrialTariffUnlocksDeepfakesForAntifakeHub() {
        let settings = ProtectionSettingsManager.shared
        XCTAssertTrue(settings.isCategoryAvailable(.deepfakes, in: .trial))
        XCTAssertTrue(settings.isCategoryAvailable(.deepfakes, in: .premium))
        XCTAssertFalse(settings.isCategoryAvailable(.deepfakes, in: .free))
        XCTAssertFalse(settings.isCategoryAvailable(.deepfakes, in: .personal))
    }

    @MainActor
    func testTariffManagerTrialAllowsDeepfakesCategory() {
        let tariffManager = TariffManager.shared
        tariffManager.saveTariff(.trial, pullServerAfterSave: false)
        XCTAssertTrue(tariffManager.isCategoryAvailable(.deepfakes))
        tariffManager.saveTariff(.free, pullServerAfterSave: false)
        XCTAssertFalse(tariffManager.isCategoryAvailable(.deepfakes))
    }

    func testTrialParentalControlFeatureAccessMatchesPremium() {
        let premiumRewards = ParentalControlModule.rewards.features(for: .premium)
        let trialRewards = ParentalControlModule.rewards.features(for: .trial)
        XCTAssertEqual(trialRewards.count, premiumRewards.count)
        XCTAssertTrue(
            ParentalControlFeature(
                id: "rewards_premium",
                titleKey: "tariff_parental_rewards_premium_premium",
                descriptionKey: nil,
                module: .rewards,
                requiredTariff: .premium
            ).isAvailable(for: .trial)
        )
        XCTAssertFalse(
            ParentalControlFeature(
                id: "rewards_premium",
                titleKey: "tariff_parental_rewards_premium_premium",
                descriptionKey: nil,
                module: .rewards,
                requiredTariff: .premium
            ).isAvailable(for: .free)
        )
    }

    func testCompanionHeroRiveHostHasRasterFallbackForBundledMasters() {
        XCTAssertTrue(CompanionHeroRiveHost.hasRasterFallback(characterId: "unicorn"))
        XCTAssertTrue(CompanionHeroRiveHost.hasRasterFallback(characterId: "aladdin"))
        XCTAssertTrue(CompanionHeroRiveHost.hasRasterFallback(characterId: "genie"))
    }

    func testCompanionHeroStateMachineContract() {
        XCTAssertEqual(CompanionHeroRiveHost.stateMachineName, "HeroSM")
    }
}
