import XCTest
@testable import ALADDIN

final class DecorativeMotionPolicyTests: XCTestCase {

    private func allows(
        reduceMotion: Bool = false,
        isAppActive: Bool = true,
        isLowPowerMode: Bool = false,
        thermalState: ProcessInfo.ThermalState = .nominal
    ) -> Bool {
        DecorativeMotionPolicy.allowsContinuousMotion(
            reduceMotion: reduceMotion,
            isAppActive: isAppActive,
            isLowPowerMode: isLowPowerMode,
            thermalState: thermalState
        )
    }

    func testAllowsMotionWhenActiveCoolAndNoRestrictions() {
        XCTAssertTrue(allows())
        XCTAssertTrue(allows(thermalState: .fair))
    }

    func testStopsMotionWhenSceneIsNotActive() {
        XCTAssertFalse(allows(isAppActive: false))
    }

    func testStopsMotionForReduceMotion() {
        XCTAssertFalse(allows(reduceMotion: true))
    }

    func testStopsMotionInLowPowerMode() {
        XCTAssertFalse(allows(isLowPowerMode: true))
    }

    func testStopsMotionWhenDeviceIsHot() {
        XCTAssertFalse(allows(thermalState: .serious))
        XCTAssertFalse(allows(thermalState: .critical))
    }
}
