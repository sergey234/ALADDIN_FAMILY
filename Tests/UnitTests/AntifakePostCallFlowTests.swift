import XCTest
@testable import ALADDIN

final class AntifakePostCallFlowTests: XCTestCase {

    func testPostCallDeepLinkRecognized() {
        let url = URL(string: "aladdin://antifake/call-check")!
        XCTAssertTrue(AntifakeDeepLinkRouter.isPostCallCheckDeepLink(url))
        XCTAssertTrue(AntifakeDeepLinkRouter.isAntifakeCheckDeepLink(url))
    }

    func testPostCallDeepLinkParsesCallerIdHint() {
        let url = URL(string: "aladdin://antifake/call-check?caller_id=%2B79001234567")!
        XCTAssertEqual(AntifakeDeepLinkRouter.parseCallerIdHint(from: url), "+79001234567")
    }

    func testReminderToggleDefaultEnabled() {
        let defaults = UserDefaults(suiteName: "AntifakePostCallFlowTests")!
        defaults.removePersistentDomain(forName: "AntifakePostCallFlowTests")
        XCTAssertTrue(
            defaults.object(forKey: AppConfig.UserDefaultsKeys.antifakePostCallReminderEnabled) == nil
        )
    }

    func testCooldownBlocksSecondPushWithin15Minutes() {
        let now: TimeInterval = 1_700_000_000
        let lastPush = now - 60
        XCTAssertFalse(
            AntifakePostCallPolicy.shouldScheduleNotification(
                reminderEnabled: true,
                lastPushAt: lastPush,
                now: now
            )
        )
    }

    func testCooldownAllowsPushAfter15Minutes() {
        let now: TimeInterval = 1_700_000_000
        let lastPush = now - AntifakePostCallPolicy.cooldownSeconds - 1
        XCTAssertTrue(
            AntifakePostCallPolicy.shouldScheduleNotification(
                reminderEnabled: true,
                lastPushAt: lastPush,
                now: now
            )
        )
    }

    func testReminderDisabledSkipsPush() {
        XCTAssertFalse(
            AntifakePostCallPolicy.shouldScheduleNotification(
                reminderEnabled: false,
                lastPushAt: 0,
                now: 1_700_000_000
            )
        )
    }

    @MainActor
    func testLastCallContextPrefillAndConsume() {
        let cidKey = AppConfig.UserDefaultsKeys.antifakeLastCallerId
        let nameKey = AppConfig.UserDefaultsKeys.antifakeLastDisplayName
        UserDefaults.standard.set("+79990001122", forKey: cidKey)
        UserDefaults.standard.set("Bank", forKey: nameKey)
        defer {
            UserDefaults.standard.removeObject(forKey: cidKey)
            UserDefaults.standard.removeObject(forKey: nameKey)
        }

        let vm = AntifakeMediaCheckViewModel(mediaKind: .call)
        AntifakeLastCallContext.applyPrefillIfNeeded(to: vm)
        XCTAssertEqual(vm.callerId, "+79990001122")
        XCTAssertEqual(vm.displayName, "Bank")

        let vm2 = AntifakeMediaCheckViewModel(mediaKind: .call)
        AntifakeLastCallContext.applyPrefillIfNeeded(to: vm2)
        XCTAssertTrue(vm2.callerId.isEmpty)
    }

    @MainActor
    func testCallTabEnablesNumberOnlyCheckWithoutRecording() {
        let vm = AntifakeMediaCheckViewModel(mediaKind: .call)
        XCTAssertFalse(vm.canSubmit)

        vm.callerId = "   "
        XCTAssertFalse(vm.canSubmit)

        vm.callerId = "+79990001122"
        XCTAssertTrue(vm.isCallerNumberOnlyCheck)
        XCTAssertTrue(vm.canSubmit)

        vm.setSelectedFile(data: Data([0x01]), filename: "call.m4a")
        XCTAssertFalse(vm.isCallerNumberOnlyCheck)
        XCTAssertTrue(vm.canSubmit)
    }

    @MainActor
    func testNonCallMediaStillRequiresFile() {
        let vm = AntifakeMediaCheckViewModel(mediaKind: .audio)
        vm.callerId = "+79990001122"
        XCTAssertFalse(vm.isCallerNumberOnlyCheck)
        XCTAssertFalse(vm.canSubmit)
    }
}
