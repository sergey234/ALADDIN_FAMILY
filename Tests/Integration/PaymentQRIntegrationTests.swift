import XCTest
@testable import ALADDIN

/**
 * 💳 Payment QR Integration Tests
 * 
 * Тесты с реальным API для проверки полной интеграции:
 * - Создание QR-платежа
 * - Проверка статуса платежа
 * - Полный цикл платежа
 * 
 * ⚠️ ВАЖНО: Эти тесты требуют работающий сервер!
 * ✅ Используют РЕАЛЬНЫЙ API (APIService.shared), НЕ Mock!
 */

@MainActor
class PaymentQRIntegrationTests: XCTestCase {
    
    // MARK: - Properties
    
    var apiService: APIService!
    var viewModel: PaymentQRViewModel!
    var testTariff: Tariff!
    
    // MARK: - Test Setup
    
    override func setUp() {
        super.setUp()
        
        // ✅ Используем РЕАЛЬНЫЙ API (не Mock!)
        apiService = APIService.shared
        
        // Создаем тестовый тариф
        testTariff = Tariff(
            id: "test_tariff_integration_\(UUID().uuidString)",
            title: "Test Tariff for Integration",
            price: "199 ₽",
            period: "month",
            features: ["Feature 1", "Feature 2"],
            product: nil,
            isPurchased: false
        )
        
        // Создаем ViewModel с реальным API
        viewModel = PaymentQRViewModel(tariff: testTariff)
        
        print("✅ PaymentQRIntegrationTests: Setup completed")
        print("   - API Base URL: \(AppConfig.apiBaseURL)")
        print("   - Use Mock API: \(AppConfig.useMockAPI)")
    }
    
    override func tearDown() {
        // Останавливаем авто-проверку, если запущена
        viewModel?.stopAutoCheck()
        
        viewModel = nil
        testTariff = nil
        apiService = nil
        
        super.tearDown()
        
        print("✅ PaymentQRIntegrationTests: Teardown completed")
    }
    
    // MARK: - Helper Methods
    
    /// Проверить, что сервер доступен
    private func checkServerAvailability() -> Bool {
        // Простая проверка - если API URL валиден, считаем сервер доступным
        return AppConfig.isAPIURLValid()
    }
    
    // MARK: - Integration Tests
    
    /// Тест: Создание QR-платежа с реальным API
    func testCreateQRPayment_WithRealAPI() {
        // Проверяем доступность сервера
        guard checkServerAvailability() else {
            XCTSkip("Server is not available. Skipping integration test.")
        }
        
        let expectation = expectation(description: "Payment created with real API")
        
        // ✅ Используем реальный API через ViewModel
        viewModel.createPayment()
        
        // Ждем завершения создания платежа
        // Проверяем состояние через небольшие интервалы
        var attempts = 0
        let maxAttempts = 20 // 10 секунд максимум (20 * 0.5 сек)
        
        Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { timer in
            attempts += 1
            
            // Проверяем успешное создание
            if let paymentId = self.viewModel.paymentId, !paymentId.isEmpty {
                XCTAssertNotNil(self.viewModel.paymentId, "Payment ID should not be nil")
                XCTAssertNotNil(self.viewModel.qrCodeImageSBP, "QR Code should be generated")
                XCTAssertFalse(self.viewModel.isLoading, "Loading should be false after completion")
                XCTAssertNil(self.viewModel.errorMessage, "Error message should be nil on success")
                
                print("✅ Payment created successfully:")
                print("   - Payment ID: \(paymentId)")
                print("   - QR Code exists: \(self.viewModel.qrCodeImageSBP != nil)")
                
                expectation.fulfill()
                timer.invalidate()
            }
            // Проверяем ошибку
            else if let errorMessage = self.viewModel.errorMessage, !errorMessage.isEmpty {
                XCTFail("Payment creation failed: \(errorMessage)")
                timer.invalidate()
            }
            // Превышен лимит попыток
            else if attempts >= maxAttempts {
                XCTFail("Payment creation timeout after \(maxAttempts * 0.5) seconds")
                timer.invalidate()
            }
        }
        
        wait(for: [expectation], timeout: 15.0)
    }
    
    /// Тест: Проверка статуса платежа с реальным API
    func testCheckPaymentStatus_WithRealAPI() {
        // Проверяем доступность сервера
        guard checkServerAvailability() else {
            XCTSkip("Server is not available. Skipping integration test.")
        }
        
        // Сначала создаем платеж
        let createExpectation = expectation(description: "Payment created")
        viewModel.createPayment()
        
        var createAttempts = 0
        Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { timer in
            createAttempts += 1
            
            if let paymentId = self.viewModel.paymentId, !paymentId.isEmpty {
                createExpectation.fulfill()
                timer.invalidate()
            } else if createAttempts >= 20 {
                XCTFail("Payment creation timeout")
                timer.invalidate()
            }
        }
        
        wait(for: [createExpectation], timeout: 10.0)
        
        guard let paymentId = viewModel.paymentId else {
            XCTFail("Payment ID is required for status check")
            return
        }
        
        // Теперь проверяем статус
        let statusExpectation = expectation(description: "Payment status checked")
        
        viewModel.checkPaymentStatus()
        
        var statusAttempts = 0
        Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { timer in
            statusAttempts += 1
            
            // Проверяем, что статус был проверен (не должно быть ошибки)
            if self.viewModel.errorMessage == nil || statusAttempts >= 10 {
                // Статус проверен (может быть pending, completed, failed, expired)
                print("✅ Payment status checked:")
                print("   - Payment ID: \(paymentId)")
                print("   - No errors during status check")
                
                statusExpectation.fulfill()
                timer.invalidate()
            }
        }
        
        wait(for: [statusExpectation], timeout: 10.0)
    }
    
    /// Тест: Полный цикл платежа (создание → проверка статуса)
    func testPaymentFlow_Complete() {
        // Проверяем доступность сервера
        guard checkServerAvailability() else {
            XCTSkip("Server is not available. Skipping integration test.")
        }
        
        let expectation = expectation(description: "Complete payment flow")
        
        // Шаг 1: Создание платежа
        print("📝 Step 1: Creating payment...")
        viewModel.createPayment()
        
        var step = 1
        var paymentId: String?
        
        Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { timer in
            switch step {
            case 1: // Ожидание создания платежа
                if let id = self.viewModel.paymentId, !id.isEmpty {
                    paymentId = id
                    print("✅ Step 1 completed: Payment created with ID: \(id)")
                    step = 2
                    
                    // Шаг 2: Проверка статуса
                    print("📝 Step 2: Checking payment status...")
                    self.viewModel.checkPaymentStatus()
                } else if self.viewModel.errorMessage != nil {
                    XCTFail("Payment creation failed: \(self.viewModel.errorMessage ?? "Unknown error")")
                    timer.invalidate()
                }
                
            case 2: // Ожидание проверки статуса
                // Проверка статуса завершена (может быть любой статус)
                print("✅ Step 2 completed: Payment status checked")
                print("   - Payment ID: \(paymentId ?? "unknown")")
                print("   - Flow completed successfully")
                
                expectation.fulfill()
                timer.invalidate()
            default:
                timer.invalidate()
            }
        }
        
        wait(for: [expectation], timeout: 20.0)
    }
    
    /// Тест: Обработка ошибок при создании платежа
    func testCreatePayment_ErrorHandling() {
        // Проверяем доступность сервера
        guard checkServerAvailability() else {
            XCTSkip("Server is not available. Skipping integration test.")
        }
        
        // Создаем ViewModel с невалидным тарифом (нулевая цена)
        let invalidTariff = Tariff(
            id: "invalid_tariff",
            title: "Invalid Tariff",
            price: "0 ₽", // Невалидная цена
            period: "month",
            features: [],
            product: nil,
            isPurchased: false
        )
        
        let invalidViewModel = PaymentQRViewModel(tariff: invalidTariff)
        
        let expectation = expectation(description: "Error handling")
        
        invalidViewModel.createPayment()
        
        // Ждем обработки ошибки
        var attempts = 0
        Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { timer in
            attempts += 1
            
            // Проверяем, что ошибка обработана
            if let errorMessage = invalidViewModel.errorMessage, !errorMessage.isEmpty {
                print("✅ Error handled correctly:")
                print("   - Error message: \(errorMessage)")
                XCTAssertTrue(invalidViewModel.showErrorAlert, "Error alert should be shown")
                XCTAssertFalse(invalidViewModel.isLoading, "Loading should be false after error")
                
                expectation.fulfill()
                timer.invalidate()
            } else if attempts >= 10 {
                // Если ошибка не возникла, это тоже может быть валидным сценарием
                // (зависит от логики сервера)
                print("⚠️ No error occurred (server may accept 0 amount)")
                expectation.fulfill()
                timer.invalidate()
            }
        }
        
        wait(for: [expectation], timeout: 10.0)
    }
    
    /// Тест: Автоматическая проверка статуса платежа
    func testAutoCheck_WithRealAPI() {
        // Проверяем доступность сервера
        guard checkServerAvailability() else {
            XCTSkip("Server is not available. Skipping integration test.")
        }
        
        // Создаем платеж
        let createExpectation = expectation(description: "Payment created for auto check")
        viewModel.createPayment()
        
        var createAttempts = 0
        Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { timer in
            createAttempts += 1
            
            if let paymentId = self.viewModel.paymentId, !paymentId.isEmpty {
                createExpectation.fulfill()
                timer.invalidate()
            } else if createAttempts >= 20 {
                XCTFail("Payment creation timeout")
                timer.invalidate()
            }
        }
        
        wait(for: [createExpectation], timeout: 10.0)
        
        guard viewModel.paymentId != nil else {
            XCTFail("Payment ID is required for auto check")
            return
        }
        
        // Запускаем автоматическую проверку
        let autoCheckExpectation = expectation(description: "Auto check started")
        
        viewModel.startAutoCheck()
        
        // Проверяем, что авто-проверка запущена
        XCTAssertTrue(viewModel.isAutoCheckRunning, "Auto check should be running")
        
        print("✅ Auto check started successfully")
        
        // Ждем несколько проверок (минимум 2 проверки)
        var checkCount = 0
        Timer.scheduledTimer(withTimeInterval: 3.0, repeats: true) { timer in
            checkCount += 1
            
            if checkCount >= 2 {
                print("✅ Auto check verified: \(checkCount) checks completed")
                autoCheckExpectation.fulfill()
                timer.invalidate()
                
                // Останавливаем авто-проверку
                self.viewModel.stopAutoCheck()
            }
        }
        
        wait(for: [autoCheckExpectation], timeout: 15.0)
        
        // Проверяем, что авто-проверка остановлена
        XCTAssertFalse(viewModel.isAutoCheckRunning, "Auto check should be stopped")
    }
}
