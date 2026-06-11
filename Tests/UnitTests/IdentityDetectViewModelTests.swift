import XCTest
@testable import ALADDIN

@MainActor
final class IdentityDetectViewModelTests: XCTestCase {

    private var viewModel: IdentityDetectViewModel!

    override func setUpWithError() throws {
        try super.setUpWithError()
        viewModel = IdentityDetectViewModel()
    }

    override func tearDownWithError() throws {
        AppConfig.authToken = nil
        viewModel = nil
        try super.tearDownWithError()
    }

    func testSNILSNormalizerStripsFormatting() {
        XCTAssertEqual(IdentitySNILSNormalizer.digits(from: "123-456-789 01"), "12345678901")
        XCTAssertTrue(IdentitySNILSNormalizer.isValid("123-456-789 01"))
        XCTAssertFalse(IdentitySNILSNormalizer.isValid("123-456-789"))
    }

    func testCanSubmitRequiresElevenDigits() {
        viewModel.snilsInput = "123"
        XCTAssertFalse(viewModel.canSubmit)

        viewModel.snilsInput = "123-456-789 01"
        XCTAssertTrue(viewModel.canSubmit)
    }

    func testSubmitWithoutAuthShowsUnauthorizedError() async {
        AppConfig.authToken = nil
        viewModel.snilsInput = "123-456-789 01"

        let ok = await viewModel.submitDetect()

        XCTAssertFalse(ok)
        XCTAssertNotNil(viewModel.errorMessage)
        XCTAssertNil(viewModel.verdict)
    }

    func testSubmitWithInvalidSnilsShowsValidationError() async {
        AppConfig.authToken = "test-token"
        viewModel.snilsInput = "12345"

        let ok = await viewModel.submitDetect()

        XCTAssertFalse(ok)
        XCTAssertNotNil(viewModel.errorMessage)
        XCTAssertNil(viewModel.verdict)
    }
}
