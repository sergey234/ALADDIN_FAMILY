import XCTest
@testable import ALADDIN

final class ClipboardSafetyServiceTests: XCTestCase {

    func testStripUTMParams() {
        let raw = "https://example.com/a?utm_source=ig&utm_medium=social&id=1&fbclid=abc"
        let result = ClipboardSafetyService.process(raw)
        guard case .ok(let cleaned) = result else {
            return XCTFail("expected ok")
        }
        XCTAssertTrue(cleaned.contains("example.com"))
        XCTAssertTrue(cleaned.contains("id=1"))
        XCTAssertFalse(cleaned.lowercased().contains("utm_"))
        XCTAssertFalse(cleaned.lowercased().contains("fbclid"))
    }

    func testBearerTokenBlocked() {
        let raw = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.aaa.bbb"
        let result = ClipboardSafetyService.process(raw)
        guard case .blockedSecret(let kind) = result else {
            return XCTFail("expected blockedSecret")
        }
        XCTAssertEqual(kind, .authToken)
    }

    func testOpenAIKeyBlocked() {
        let raw = "sk-abcdefghijklmnopqrstuvwxyz0123456789ABCD"
        guard case .blockedSecret = ClipboardSafetyService.process(raw) else {
            return XCTFail("expected blockedSecret")
        }
    }

    func testPhoneNotTreatedAsOTP() {
        let raw = "+7 (900) 123-45-67"
        let result = ClipboardSafetyService.process(raw)
        guard case .ok(let cleaned) = result else {
            return XCTFail("expected ok for phone, got \(result)")
        }
        XCTAssertTrue(cleaned.contains("900"))
    }

    func testShortOTPBlockedWhenOnlyDigits() {
        let raw = "483920"
        guard case .blockedSecret(let kind) = ClipboardSafetyService.process(raw) else {
            return XCTFail("expected OTP block")
        }
        XCTAssertEqual(kind, .otp)
    }

    func testPlainTextPassthrough() {
        let raw = "Мама прислала странное сообщение про выигрыш"
        guard case .ok(let cleaned) = ClipboardSafetyService.process(raw) else {
            return XCTFail("expected ok")
        }
        XCTAssertEqual(cleaned, raw)
    }

    func testEmpty() {
        guard case .ok(let cleaned) = ClipboardSafetyService.process("   ") else {
            return XCTFail("expected ok empty")
        }
        XCTAssertTrue(cleaned.isEmpty)
    }

    func testCardLikeLuhnBlocked() {
        // Visa test PAN that passes Luhn: 4111111111111111
        let raw = "4111111111111111"
        guard case .blockedSecret(let kind) = ClipboardSafetyService.process(raw) else {
            return XCTFail("expected card block")
        }
        XCTAssertEqual(kind, .paymentCard)
    }

    /// C-2: looksLikeURL true but no single extractable URL → keep plain text (no force-normalize).
    func testLooksLikeURLWithoutSingleExtractLeavesPlainText() {
        let raw = "Line one\nSee youtube.com and also vk.com together"
        guard case .ok(let cleaned) = ClipboardSafetyService.process(raw) else {
            return XCTFail("expected ok")
        }
        XCTAssertEqual(cleaned, raw)
        XCTAssertFalse(cleaned.lowercased().hasPrefix("https://"))
    }

    func testBareHostStillNormalizedWhenExtractable() {
        let raw = "youtube.com/watch?v=1&utm_source=x"
        guard case .ok(let cleaned) = ClipboardSafetyService.process(raw) else {
            return XCTFail("expected ok")
        }
        XCTAssertTrue(cleaned.lowercased().hasPrefix("https://"))
        XCTAssertTrue(cleaned.contains("v=1") || cleaned.contains("watch"))
        XCTAssertFalse(cleaned.lowercased().contains("utm_"))
    }
}
