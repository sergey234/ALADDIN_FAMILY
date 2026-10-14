import XCTest
@testable import ALADDIN

final class UX36W6RegistrationDateTests: XCTestCase {

    func testCapture_freezesFirstDate_andIgnoresLater() {
        let suite = "ux36_w6_reg_\(UUID().uuidString)"
        let defaults = UserDefaults(suiteName: suite)!
        defer { defaults.removePersistentDomain(forName: suite) }

        let day1 = date(2026, 9, 1)
        let day2 = date(2026, 10, 14)
        XCTAssertEqual(
            AccountRegistrationDateStore.captureIfNeeded(day1, defaults: defaults),
            Calendar.current.startOfDay(for: day1)
        )
        XCTAssertEqual(
            AccountRegistrationDateStore.captureIfNeeded(day2, defaults: defaults),
            Calendar.current.startOfDay(for: day1)
        )
        XCTAssertEqual(
            AccountRegistrationDateStore.resolvedDate(defaults: defaults),
            Calendar.current.startOfDay(for: day1)
        )
    }

    func testCapture_earlierServerDate_wins() {
        let suite = "ux36_w6_reg2_\(UUID().uuidString)"
        let defaults = UserDefaults(suiteName: suite)!
        defer { defaults.removePersistentDomain(forName: suite) }

        let later = date(2026, 10, 14)
        let earlier = date(2026, 8, 1)
        _ = AccountRegistrationDateStore.captureIfNeeded(later, defaults: defaults)
        XCTAssertEqual(
            AccountRegistrationDateStore.captureIfNeeded(earlier, defaults: defaults),
            Calendar.current.startOfDay(for: earlier)
        )
    }

    func testDisplay_nilWhenUnknown_doesNotInventToday() {
        let suite = "ux36_w6_reg3_\(UUID().uuidString)"
        let defaults = UserDefaults(suiteName: suite)!
        defer { defaults.removePersistentDomain(forName: suite) }

        XCTAssertNil(AccountRegistrationDateStore.displayString(isRussian: true, defaults: defaults))
        XCTAssertNil(AccountRegistrationDateStore.resolvedDate(defaults: defaults))
    }

    func testCaptureFromISO() {
        let suite = "ux36_w6_reg4_\(UUID().uuidString)"
        let defaults = UserDefaults(suiteName: suite)!
        defer { defaults.removePersistentDomain(forName: suite) }

        let captured = AccountRegistrationDateStore.captureFromServerString(
            "2026-09-15T12:00:00Z",
            defaults: defaults
        )
        XCTAssertNotNil(captured)
        XCTAssertEqual(
            Calendar.current.component(.day, from: captured!),
            15
        )
    }

    private func date(_ y: Int, _ m: Int, _ d: Int) -> Date {
        var c = DateComponents()
        c.year = y
        c.month = m
        c.day = d
        return Calendar.current.date(from: c)!
    }
}
