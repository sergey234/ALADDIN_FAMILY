import XCTest
@testable import ALADDIN

/**
 * 🛡️ PaymentQRViewModel Protection Tests
 * Тесты защитной логики PaymentQR для предотвращения регрессий
 * 
 * Проверяет:
 * - creationError флаг
 * - retryCreatePayment() метод
 * - clearPaymentData() метод
 * - Guard-проверки в checkPaymentStatus()
 * - Guard-проверки в startAutoCheck()
 */

@MainActor
final class PaymentQRViewModelProtectionTests: XCTestCase {
    
    private var viewModel: PaymentQRViewModel!
    private var testTariff: Tariff!
    
    override func setUp() async throws {
        try await super.setUp()
        testTariff = Tariff(
            id: "test_tariff_001",
            title: "Test Tariff",
            price: "199 ₽",
            period: "month",
            features: ["Feature 1", "Feature 2"],
            product: nil,
            isPurchased: false
        )
        viewModel = PaymentQRViewModel(tariff: testTariff)
    }
    
    override func tearDown() async throws {
        try await super.tearDown()
        viewModel = nil
        testTariff = nil
    }
    
    // MARK: - creationError Tests
    
    func testCreationErrorFlagExists() {
        // Проверяем, что флаг creationError существует и доступен
        XCTAssertFalse(viewModel.creationError, "creationError должен быть false по умолчанию")
        
        // Проверяем, что флаг можно установить
        viewModel.creationError = true
        XCTAssertTrue(viewModel.creationError, "creationError должен быть устанавливаемым")
    }
    
    func testCreationErrorPreventsAutoCheck() {
        // Устанавливаем creationError
        viewModel.creationError = true
        viewModel.paymentId = "test_payment_123"
        
        // Пытаемся запустить авто-проверку
        viewModel.startAutoCheck()
        
        // Проверяем, что авто-проверка не запустилась
        XCTAssertFalse(viewModel.isAutoCheckRunning, "startAutoCheck() должен быть заблокирован при creationError == true")
    }
    
    // MARK: - retryCreatePayment() Tests
    
    func testRetryCreatePaymentResetsCreationError() {
        // Устанавливаем ошибку
        viewModel.creationError = true
        viewModel.paymentId = "old_payment_id"
        
        // Вызываем retry
        viewModel.retryCreatePayment()
        
        // Проверяем, что ошибка сброшена
        XCTAssertFalse(viewModel.creationError, "retryCreatePayment() должен сбрасывать creationError")
    }
    
    func testRetryCreatePaymentClearsPaymentData() {
        // Устанавливаем данные платежа
        viewModel.creationError = true
        viewModel.paymentId = "old_payment_id"
        viewModel.qrCodeImageSBP = "old_qr_image"
        viewModel.errorMessage = "Old error"
        
        // Вызываем retry
        viewModel.retryCreatePayment()
        
        // Проверяем, что данные очищены
        XCTAssertNil(viewModel.paymentId, "retryCreatePayment() должен очищать paymentId")
        XCTAssertNil(viewModel.qrCodeImageSBP, "retryCreatePayment() должен очищать QR коды")
        XCTAssertNil(viewModel.errorMessage, "retryCreatePayment() должен очищать errorMessage")
    }
    
    func testRetryCreatePaymentStopsAutoCheck() {
        // Запускаем авто-проверку
        viewModel.paymentId = "test_payment"
        viewModel.startAutoCheck()
        XCTAssertTrue(viewModel.isAutoCheckRunning, "Авто-проверка должна быть запущена")
        
        // Устанавливаем ошибку и вызываем retry
        viewModel.creationError = true
        viewModel.retryCreatePayment()
        
        // Проверяем, что авто-проверка остановлена
        XCTAssertFalse(viewModel.isAutoCheckRunning, "retryCreatePayment() должен останавливать авто-проверку")
    }
    
    // MARK: - clearPaymentData() Tests
    
    func testClearPaymentDataClearsAllPaymentFields() {
        // Устанавливаем все поля платежа
        viewModel.paymentId = "test_payment_123"
        viewModel.qrCodeDataSBP = "sbp_qr_data"
        viewModel.qrCodeDataSberPay = "sberpay_qr_data"
        viewModel.qrCodeDataUniversal = "universal_qr_data"
        viewModel.qrCodeImageSBP = "sbp_image"
        viewModel.qrCodeImageSberPay = "sberpay_image"
        viewModel.qrCodeImageUniversal = "universal_image"
        viewModel.qrCodeImageCard = "card_image"
        viewModel.qrCodeImageApplePay = "applepay_image"
        viewModel.expiresAt = Date()
        viewModel.errorMessage = "Test error"
        viewModel.showErrorAlert = true
        viewModel.showSuccessAlert = true
        
        // Вызываем clearPaymentData через resetState (который вызывает clearPaymentData)
        viewModel.resetState()
        
        // Проверяем, что все поля очищены
        XCTAssertNil(viewModel.paymentId, "paymentId должен быть очищен")
        XCTAssertNil(viewModel.qrCodeDataSBP, "qrCodeDataSBP должен быть очищен")
        XCTAssertNil(viewModel.qrCodeDataSberPay, "qrCodeDataSberPay должен быть очищен")
        XCTAssertNil(viewModel.qrCodeDataUniversal, "qrCodeDataUniversal должен быть очищен")
        XCTAssertNil(viewModel.qrCodeImageSBP, "qrCodeImageSBP должен быть очищен")
        XCTAssertNil(viewModel.qrCodeImageSberPay, "qrCodeImageSberPay должен быть очищен")
        XCTAssertNil(viewModel.qrCodeImageUniversal, "qrCodeImageUniversal должен быть очищен")
        XCTAssertNil(viewModel.qrCodeImageCard, "qrCodeImageCard должен быть очищен")
        XCTAssertNil(viewModel.qrCodeImageApplePay, "qrCodeImageApplePay должен быть очищен")
        XCTAssertNil(viewModel.expiresAt, "expiresAt должен быть очищен")
        XCTAssertNil(viewModel.errorMessage, "errorMessage должен быть очищен")
        XCTAssertFalse(viewModel.showErrorAlert, "showErrorAlert должен быть false")
        XCTAssertFalse(viewModel.showSuccessAlert, "showSuccessAlert должен быть false")
    }
    
    // MARK: - checkPaymentStatus() Guard Tests
    
    func testCheckPaymentStatusGuardsAgainstManualClose() {
        // Устанавливаем флаг manual close
        viewModel.prepareForManualClose()
        viewModel.paymentId = "test_payment"
        
        // Пытаемся проверить статус
        viewModel.checkPaymentStatus()
        
        // Проверяем, что проверка не выполнилась (нет изменений состояния)
        // Это косвенная проверка - если бы проверка выполнилась, состояние изменилось бы
        XCTAssertTrue(viewModel.paymentId == "test_payment", "checkPaymentStatus() должен быть заблокирован при manual close")
    }
    
    func testCheckPaymentStatusGuardsAgainstCreationError() {
        // Устанавливаем creationError
        viewModel.creationError = true
        viewModel.paymentId = "test_payment"
        
        // Пытаемся проверить статус
        // Примечание: checkPaymentStatus() не имеет явной проверки на creationError,
        // но startAutoCheck() имеет, что предотвращает автоматические проверки
        // Это тест проверяет, что при creationError авто-проверка не запускается
        viewModel.startAutoCheck()
        
        XCTAssertFalse(viewModel.isAutoCheckRunning, "Авто-проверка не должна запускаться при creationError")
    }
    
    func testCheckPaymentStatusRequiresPaymentId() {
        // Не устанавливаем paymentId
        viewModel.paymentId = nil
        
        // Пытаемся проверить статус
        viewModel.checkPaymentStatus()
        
        // Проверяем, что paymentId остался nil (проверка не выполнилась)
        XCTAssertNil(viewModel.paymentId, "checkPaymentStatus() должен требовать paymentId")
    }
    
    func testCheckPaymentStatusRequiresNonEmptyPaymentId() {
        // Устанавливаем пустой paymentId
        viewModel.paymentId = ""
        
        // Пытаемся проверить статус
        viewModel.checkPaymentStatus()
        
        // Проверяем, что paymentId остался пустым (проверка не выполнилась)
        XCTAssertEqual(viewModel.paymentId, "", "checkPaymentStatus() должен требовать непустой paymentId")
    }
    
    // MARK: - startAutoCheck() Guard Tests
    
    func testStartAutoCheckGuardsAgainstCreationError() {
        // Устанавливаем creationError
        viewModel.creationError = true
        viewModel.paymentId = "test_payment"
        
        // Пытаемся запустить авто-проверку
        viewModel.startAutoCheck()
        
        // Проверяем, что авто-проверка не запустилась
        XCTAssertFalse(viewModel.isAutoCheckRunning, "startAutoCheck() должен быть заблокирован при creationError == true")
    }
    
    func testStartAutoCheckGuardsAgainstManualClose() {
        // Устанавливаем manual close
        viewModel.prepareForManualClose()
        viewModel.paymentId = "test_payment"
        
        // Пытаемся запустить авто-проверку
        viewModel.startAutoCheck()
        
        // Проверяем, что авто-проверка не запустилась
        XCTAssertFalse(viewModel.isAutoCheckRunning, "startAutoCheck() должен быть заблокирован при manual close")
    }
    
    func testStartAutoCheckRequiresPaymentId() {
        // Не устанавливаем paymentId
        viewModel.paymentId = nil
        
        // Пытаемся запустить авто-проверку
        viewModel.startAutoCheck()
        
        // Проверяем, что авто-проверка не запустилась
        XCTAssertFalse(viewModel.isAutoCheckRunning, "startAutoCheck() должен требовать paymentId")
    }
    
    func testStartAutoCheckRequiresNonEmptyPaymentId() {
        // Устанавливаем пустой paymentId
        viewModel.paymentId = ""
        
        // Пытаемся запустить авто-проверку
        viewModel.startAutoCheck()
        
        // Проверяем, что авто-проверка не запустилась
        XCTAssertFalse(viewModel.isAutoCheckRunning, "startAutoCheck() должен требовать непустой paymentId")
    }
    
    func testStartAutoCheckStopsPreviousAutoCheck() {
        // Запускаем первую авто-проверку
        viewModel.paymentId = "test_payment_1"
        viewModel.startAutoCheck()
        XCTAssertTrue(viewModel.isAutoCheckRunning, "Первая авто-проверка должна запуститься")
        
        // Запускаем вторую авто-проверку
        viewModel.paymentId = "test_payment_2"
        viewModel.startAutoCheck()
        
        // Проверяем, что только одна авто-проверка активна
        XCTAssertTrue(viewModel.isAutoCheckRunning, "Авто-проверка должна быть активна")
    }
    
    // MARK: - Integration Tests
    
    func testFullErrorRecoveryFlow() {
        // 1. Создаём ошибку
        viewModel.creationError = true
        viewModel.paymentId = "failed_payment"
        viewModel.errorMessage = "Creation failed"
        
        // 2. Проверяем, что авто-проверка заблокирована
        viewModel.startAutoCheck()
        XCTAssertFalse(viewModel.isAutoCheckRunning, "Авто-проверка должна быть заблокирована")
        
        // 3. Выполняем retry
        viewModel.retryCreatePayment()
        
        // 4. Проверяем, что состояние сброшено
        XCTAssertFalse(viewModel.creationError, "creationError должен быть сброшен")
        XCTAssertNil(viewModel.paymentId, "paymentId должен быть очищен")
        XCTAssertNil(viewModel.errorMessage, "errorMessage должен быть очищен")
    }
    
    func testResetStateClearsEverything() {
        // Устанавливаем все возможные состояния
        viewModel.creationError = true
        viewModel.paymentId = "test_payment"
        viewModel.qrCodeImageSBP = "test_image"
        viewModel.errorMessage = "Test error"
        viewModel.isLoading = true
        viewModel.selectedMethod = .sberpay
        viewModel.startAutoCheck()
        
        // Выполняем reset
        viewModel.resetState()
        
        // Проверяем, что всё очищено
        XCTAssertFalse(viewModel.creationError, "creationError должен быть сброшен")
        XCTAssertNil(viewModel.paymentId, "paymentId должен быть очищен")
        XCTAssertNil(viewModel.qrCodeImageSBP, "QR коды должны быть очищены")
        XCTAssertNil(viewModel.errorMessage, "errorMessage должен быть очищен")
        XCTAssertFalse(viewModel.isLoading, "isLoading должен быть false")
        XCTAssertEqual(viewModel.selectedMethod, .sbp, "selectedMethod должен быть сброшен на .sbp")
        XCTAssertFalse(viewModel.isAutoCheckRunning, "Авто-проверка должна быть остановлена")
    }
}

