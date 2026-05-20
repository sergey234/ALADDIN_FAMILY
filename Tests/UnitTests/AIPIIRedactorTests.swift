import XCTest
@testable import ALADDIN

final class AIPIIRedactorTests: XCTestCase {

    func testRedactsEmailPhoneAndCard() {
        let input = "Пишите на user@example.com или +79991234567, карта 4111111111111111"
        let result = AIPIIRedactor.redact(input)
        XCTAssertFalse(result.text.contains("user@example.com"))
        XCTAssertFalse(result.text.contains("+79991234567"))
        XCTAssertFalse(result.text.contains("4111111111111111"))
        XCTAssertTrue(result.text.contains("[REDACTED_EMAIL]"))
        XCTAssertTrue(result.text.contains("[REDACTED_PHONE]"))
        XCTAssertTrue(result.text.contains("[REDACTED_CARD]"))
        XCTAssertGreaterThan(result.replacementCount, 0)
    }

    func testRedactsJWT() {
        let jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        let result = AIPIIRedactor.redact("token \(jwt)")
        XCTAssertFalse(result.text.contains("eyJhbGci"))
        XCTAssertTrue(result.text.contains("[REDACTED_JWT]"))
    }

    func testOutboundGateRequiresOptIn() {
        let key = AppConfig.UserDefaultsKeys.aiDataSharingEnabled
        let previous = UserDefaults.standard.object(forKey: key) as? Bool
        defer {
            if let previous {
                UserDefaults.standard.set(previous, forKey: key)
            } else {
                UserDefaults.standard.removeObject(forKey: key)
            }
        }
        UserDefaults.standard.set(false, forKey: key)
        XCTAssertThrowsError(try AIOutboundTextGate.prepareUserMessage("Привет")) { error in
            XCTAssertTrue(error is AIOutboundTextGate.GateError)
        }
    }

    func testOutboundGateRedactsForCloud() throws {
        let key = AppConfig.UserDefaultsKeys.aiDataSharingEnabled
        UserDefaults.standard.set(true, forKey: key)
        defer { UserDefaults.standard.set(false, forKey: key) }

        let prepared = try AIOutboundTextGate.prepareUserMessage("Мой email test@mail.ru и всё")
        XCTAssertEqual(prepared.displayText, "Мой email test@mail.ru и всё")
        XCTAssertFalse(prepared.cloudText.contains("test@mail.ru"))
        XCTAssertTrue(prepared.cloudText.contains("[REDACTED_EMAIL]"))
    }
}
