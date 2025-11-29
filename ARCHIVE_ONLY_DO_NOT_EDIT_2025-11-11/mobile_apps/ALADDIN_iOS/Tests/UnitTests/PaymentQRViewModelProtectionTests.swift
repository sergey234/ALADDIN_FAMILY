import XCTest
@testable import ALADDIN

@MainActor
final class PaymentQRViewModelProtectionTests: XCTestCase {
    func testRetryCreatePaymentResetsStateAndInvokesCreate() {
        let tariff = Tariff(
            id: "test_tariff",
            title: "Test",
            price: "199 ₽",
            period: "month",
            features: ["Feature"],
            product: nil,
            isPurchased: false
        )
        let viewModel = PaymentQRViewModelSpy(tariff: tariff)
        viewModel.creationError = true
        viewModel.paymentId = "existing_payment"
        viewModel.qrCodeImageSBP = "old"

        viewModel.retryCreatePayment()

        XCTAssertFalse(viewModel.creationError, "retryCreatePayment() должно сбрасывать creationError")
        XCTAssertNil(viewModel.paymentId, "retryCreatePayment() должно очищать старый paymentId")
        XCTAssertEqual(viewModel.createPaymentCallCount, 1, "retryCreatePayment() должен вызвать createPayment один раз")
    }
}

@MainActor
private final class PaymentQRViewModelSpy: PaymentQRViewModel {
    private(set) var createPaymentCallCount = 0

    override func createPayment() {
        createPaymentCallCount += 1
    }
}
import XCTest
@testable import ALADDIN

@MainActor
final class PaymentQRViewModelProtectionTests: XCTestCase {
    func testRetryCreatePaymentResetsStateAndInvokesCreate() {
        let tariff = Tariff(
            id: "test_tariff",
            title: "Test",
            price: "199 ₽",
            period: "month",
            features: ["Feature"],
            product: nil,
            isPurchased: false
        )
        let viewModel = PaymentQRViewModelSpy(tariff: tariff)
        viewModel.creationError = true
        viewModel.paymentId = "payment_old"
        viewModel.qrCodeImageSBP = "old"

        viewModel.retryCreatePayment()

        XCTAssertFalse(viewModel.creationError, "retryCreatePayment() should reset creationError flag")
        XCTAssertNil(viewModel.paymentId, "retryCreatePayment() must clear previous payment identifier")
        XCTAssertEqual(viewModel.createPaymentCallCount, 1, "retryCreatePayment() should trigger a new payment creation once")
    }
}

@MainActor
private final class PaymentQRViewModelSpy: PaymentQRViewModel {
    private(set) var createPaymentCallCount = 0

    override func createPayment() {
        createPaymentCallCount += 1
    }
}
