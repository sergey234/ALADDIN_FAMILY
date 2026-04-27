import XCTest
@testable import ALADDIN

/// Smoke tests for API wiring. Detailed mock flows belong in integration tests.
final class MockAPIServiceTests: XCTestCase {

    func testAPIServiceSharedIsReachable() {
        let service = APIService.shared
        XCTAssertNotNil(service)
    }

    #if DEBUG
    func testMockAPIServiceWhenCompileTimeMockEnabled() {
        if AppConfig.useMockAPI {
            XCTAssertTrue(APIService.shared is MockAPIService)
        }
    }
    #endif
}
