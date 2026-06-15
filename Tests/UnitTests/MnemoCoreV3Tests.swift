import XCTest
@testable import ALADDIN

/// MNEMO-B15-T02 — MnemoCore v3: spine unlock, lesson flow, hint ladder, technique map, micro-wins.
final class MnemoCoreV3Tests: XCTestCase {

    private var suite: UserDefaults!

    override func setUp() {
        super.setUp()
        suite = UserDefaults(suiteName: "test.mnemo.v3.\(UUID().uuidString)")!
    }

    override func tearDown() {
        UserDefaults.standard.removeObject(forKey: MnemoLessonFlow.activeAgeGroupStorageKey)
        suite = nil
        super.tearDown()
    }

    // MARK: - Curriculum spine (B9-T08)

    func testSemesterCount_andUnlockThreshold() {
        XCTAssertEqual(MnemonicCurriculumSpine.semesterCount, 8)
        XCTAssertEqual(MnemonicCurriculumSpine.unlockThreshold, 0.70, accuracy: 0.001)
    }

    func testSemesterZero_isAlwaysUnlocked() {
        let spine = MnemonicCurriculumSpine(defaults: suite)
        XCTAssertTrue(spine.isUnlocked(0))
        let gate = spine.gate(for: ChildCategoryKey.songs)
        XCTAssertTrue(gate.isAccessible)
        XCTAssertEqual(gate.requiredSemesterIndex, 0)
    }

    func testStudyItemSemesterSplit_intro_3_4_7() {
        let spine = MnemonicCurriculumSpine.shared
        XCTAssertEqual(spine.requiredSemesterIndex(forItemId: "study.01", category: ChildCategoryKey.study), 0)
        XCTAssertEqual(spine.requiredSemesterIndex(forItemId: "study.03", category: ChildCategoryKey.study), 0)
        XCTAssertEqual(spine.requiredSemesterIndex(forItemId: "study.04", category: ChildCategoryKey.study), 3)
        XCTAssertEqual(spine.requiredSemesterIndex(forItemId: "study.10", category: ChildCategoryKey.study), 3)
        XCTAssertEqual(spine.requiredSemesterIndex(forItemId: "study.11", category: ChildCategoryKey.study), 4)
        XCTAssertEqual(spine.requiredSemesterIndex(forItemId: "study.20", category: ChildCategoryKey.study), 4)
        XCTAssertEqual(spine.requiredSemesterIndex(forItemId: "study.21", category: ChildCategoryKey.study), 7)
        XCTAssertEqual(spine.requiredSemesterIndex(forItemId: "study.30", category: ChildCategoryKey.study), 7)
    }

    func testMasteryFraction_isBoundedZeroToOne() {
        let spine = MnemonicCurriculumSpine(defaults: suite)
        for index in 0..<MnemonicCurriculumSpine.semesterCount {
            let fraction = spine.masteryFraction(for: index, childId: "v3-bound-\(UUID().uuidString)")
            XCTAssertGreaterThanOrEqual(fraction, 0)
            XCTAssertLessThanOrEqual(fraction, 1)
        }
    }

    func testSemesterGate_remainingPercent_neverNegative() {
        let gate = MnemonicCurriculumSpine.SemesterGate(
            requiredSemesterIndex: 4,
            isAccessible: false,
            priorMasteryPercent: 55,
            unlockThresholdPercent: 70
        )
        XCTAssertEqual(gate.remainingPercent, 15)
        let saturated = MnemonicCurriculumSpine.SemesterGate(
            requiredSemesterIndex: 4,
            isAccessible: true,
            priorMasteryPercent: 95,
            unlockThresholdPercent: 70
        )
        XCTAssertEqual(saturated.remainingPercent, 0)
    }

    func testItemGate_study01_introOpenWithoutSemesterThree() {
        let spine = MnemonicCurriculumSpine(defaults: suite)
        let gate = spine.itemGate(forItemId: "study.01", category: ChildCategoryKey.study)
        XCTAssertEqual(gate.requiredSemesterIndex, 0)
        XCTAssertTrue(gate.isAccessible)
        XCTAssertEqual(gate.unlockThresholdPercent, 70)
    }

    func testNextSemesterUnlockProgress_reportsActiveAndNext() {
        let spine = MnemonicCurriculumSpine(defaults: suite)
        let progress = spine.nextSemesterUnlockProgress(childId: "v3-progress-\(UUID().uuidString)")
        XCTAssertGreaterThanOrEqual(progress.activeSemesterIndex, 0)
        XCTAssertLessThanOrEqual(progress.activeSemesterIndex, 7)
        XCTAssertEqual(progress.gate.unlockThresholdPercent, 70)
        if progress.allSemestersUnlocked {
            XCTAssertEqual(progress.nextSemesterIndex, progress.activeSemesterIndex)
        } else {
            XCTAssertEqual(progress.nextSemesterIndex, progress.activeSemesterIndex + 1)
        }
    }

    // MARK: - Lesson flow (B14)

    func testLessonFlow_ageGates() {
        XCTAssertFalse(MnemoLessonFlow.supportsWarmup(for: .kids))
        XCTAssertTrue(MnemoLessonFlow.supportsWarmup(for: .school))
        XCTAssertFalse(MnemoLessonFlow.supportsTechniquePicker(for: .school))
        XCTAssertTrue(MnemoLessonFlow.supportsTechniquePicker(for: .teen))
        XCTAssertTrue(MnemoLessonFlow.supportsReflect(for: .youngAdult))
        XCTAssertFalse(MnemoLessonFlow.supportsReflect(for: .kids))
    }

    func testLessonFlow_teenPhaseIndicators_includePickerWarmupReflect() {
        let phases = MnemoLessonFlow.lessonPhaseIndicators(for: .teen)
        XCTAssertEqual(phases.first, .techniquePick)
        XCTAssertTrue(phases.contains(.warmup))
        XCTAssertEqual(phases.filter { MnemoAcademyPhase.catalogPhases.contains($0) }.count, 4)
        XCTAssertEqual(phases.last, .reflect)
    }

    func testLessonFlow_kidsStartAtEncode_withoutWarmup() {
        MnemoLessonFlow.persistActiveAgeGroup(.kids)
        XCTAssertEqual(MnemoLessonFlow.initialLessonPhase(), .encode)
        let phases = MnemoLessonFlow.lessonPhaseIndicators(for: .kids)
        XCTAssertFalse(phases.contains(.warmup))
        XCTAssertFalse(phases.contains(.techniquePick))
        XCTAssertFalse(phases.contains(.reflect))
    }

    func testLessonFlow_initialPhase_teenStartsTechniquePick() {
        MnemoLessonFlow.persistActiveAgeGroup(.teen)
        XCTAssertEqual(MnemoLessonFlow.initialLessonPhase(), .techniquePick)
    }

    // MARK: - Hint ladder + technique map (B14)

    func testHintLadder_firstLetter_uppercasesAndHandlesEmpty() {
        XCTAssertEqual(MnemonicHintLadder.firstLetter(from: "образ"), "О")
        XCTAssertEqual(MnemonicHintLadder.firstLetter(from: "  answer "), "A")
        XCTAssertEqual(MnemonicHintLadder.firstLetter(from: "   "), "?")
    }

    func testHintLadder_levelsProgressImageToChoice() {
        XCTAssertEqual(MnemonicHintLadder.Level.image.next, .letter)
        XCTAssertEqual(MnemonicHintLadder.Level.letter.next, .threeChoice)
        XCTAssertNil(MnemonicHintLadder.Level.threeChoice.next)
    }

    func testStudyTechniqueMap_knownStudyItems() {
        XCTAssertEqual(MnemonicStudyTechniqueMap.technique(for: "study.09"), .storyLink)
        XCTAssertEqual(MnemonicStudyTechniqueMap.technique(for: "study.24"), .spacedReview)
        XCTAssertEqual(MnemonicStudyTechniqueMap.journeyStop(for: "study.12"), 12)
    }

    func testStudyTechniqueMap_pickerOptions_includeRecommended() {
        let options = MnemonicStudyTechniqueMap.pickerOptions(for: "study.02")
        XCTAssertEqual(options.count, 3)
        XCTAssertTrue(options.contains(.chunking))
        XCTAssertFalse(options.contains(.spacedReview))
    }

    func testStudyTechniqueMap_pickerContextKey_vocabFormulaDates() {
        XCTAssertEqual(
            MnemonicStudyTechniqueMap.pickerContextKey(for: "study.01"),
            "child_mnemo_technique_picker_context_vocab"
        )
        XCTAssertEqual(
            MnemonicStudyTechniqueMap.pickerContextKey(for: "study.02"),
            "child_mnemo_technique_picker_context_formula"
        )
        XCTAssertEqual(
            MnemonicStudyTechniqueMap.pickerContextKey(for: "study.04"),
            "child_mnemo_technique_picker_context_dates"
        )
    }

    func testJourneyPath_stopKeyUsesZeroPaddedIndex() {
        XCTAssertEqual(MnemonicJourneyPath.stopLocalizationKey(index: 1), "child_mnemo_journey_stop_01")
        XCTAssertEqual(MnemonicJourneyPath.stopLocalizationKey(index: 40), "child_mnemo_journey_stop_40")
    }

    func testMnemoItemProgress_recallPercentFromSRSBox() {
        let suite = UserDefaults(suiteName: "test.mnemo.item.progress.\(UUID().uuidString)")!
        let store = MnemonicSRSStore(defaults: suite)
        let now = Date(timeIntervalSince1970: 1_700_000_000)
        let itemId = "games.05"
        XCTAssertEqual(MnemoItemProgress.recallPercent(for: itemId, store: store), 0)
        store.scheduleInitial(itemId: itemId, now: now)
        store.recordSuccess(itemId: itemId, now: now)
        XCTAssertEqual(MnemoItemProgress.recallPercent(for: itemId, store: store), 25)
        XCTAssertFalse(MnemoItemProgress.hasOpened(progress: nil))
        let opened = ContentProgress(
            contentId: itemId,
            completionPercent: 0,
            attempts: 1,
            lastOpenedAt: now,
            completedAt: nil
        )
        XCTAssertTrue(MnemoItemProgress.hasOpened(progress: opened))
    }

    // MARK: - Catalog manifest (PlanItem275 v4)

    func testCatalogManifestBuilder_games05FirstAndFullStudyCount() {
        let categories = [
            ContentCategory(
                id: ChildCategoryKey.games,
                titleKey: "child_interface_category_games",
                icon: "gamecontroller.fill",
                ageBand: .school_7_12
            ),
            ContentCategory(
                id: ChildCategoryKey.study,
                titleKey: "child_interface_category_study",
                icon: "book.fill",
                ageBand: .school_7_12
            )
        ]
        let games = MnemoCatalogManifestBuilder.items(for: ChildCategoryKey.games, ageBand: .school_7_12)
        XCTAssertEqual(games.first?.id, "games.05")
        XCTAssertEqual(games.count, 20)
        let study = MnemoCatalogManifestBuilder.items(for: ChildCategoryKey.study, ageBand: .school_7_12)
        XCTAssertEqual(study.count, 30)
        let all = MnemoCatalogManifestBuilder.allMnemoItems(categories: categories)
        XCTAssertEqual(all.filter { $0.categoryId == ChildCategoryKey.games }.count, 20)
        XCTAssertEqual(all.filter { $0.categoryId == ChildCategoryKey.study }.count, 30)
    }

    // MARK: - Technique mastery + micro-wins (B14-T09)

    func testTechniqueMastery_stageThresholds() {
        let mastery = MnemonicTechniqueMastery(defaults: suite)
        let childId = "v3-mastery-\(UUID().uuidString)"
        XCTAssertEqual(mastery.stage(for: .acronym, childId: childId), .awareness)
        mastery.recordSuccess(technique: .acronym, childId: childId)
        XCTAssertEqual(mastery.stage(for: .acronym, childId: childId), .awareness)
        mastery.recordSuccess(technique: .acronym, childId: childId)
        mastery.recordSuccess(technique: .acronym, childId: childId)
        mastery.recordSuccess(technique: .acronym, childId: childId)
        mastery.recordSuccess(technique: .acronym, childId: childId)
        XCTAssertEqual(mastery.stage(for: .acronym, childId: childId), .practice)
    }

    func testAwardRecallAttempt_deduplicatesPerQuestion() {
        let itemId = "v3.micro.\(UUID().uuidString)"
        XCTAssertTrue(MnemonicRewardBridge.awardRecallAttempt(itemId: itemId, attemptKey: "q0"))
        XCTAssertFalse(MnemonicRewardBridge.awardRecallAttempt(itemId: itemId, attemptKey: "q0"))
        XCTAssertTrue(MnemonicRewardBridge.awardRecallAttempt(itemId: itemId, attemptKey: "q1"))
    }

    func testRewardEvent_recallAttemptAmountIsOne() {
        XCTAssertEqual(MnemonicRewardEvent.recallAttempt.unicornAmount, 1)
        XCTAssertEqual(MnemonicRewardEvent.recallAttempt.localizationKey, "child_mnemo_reward_micro_win")
    }
}
