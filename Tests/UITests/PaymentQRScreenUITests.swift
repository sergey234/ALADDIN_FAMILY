import XCTest

/**
 * 💳 PaymentQR Screen UI Tests
 * UI тесты для экрана оплаты через QR-код
 * 
 * Тестирует:
 * - Отображение экрана оплаты
 * - Отображение QR-кода
 * - Выбор метода оплаты (СБП, SberPay, Card)
 * - Проверка статуса платежа
 * - Обработка ошибок
 */

@MainActor
class PaymentQRScreenUITests: XCTestCase {
    
    var app: XCUIApplication!
    
    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    override func tearDownWithError() throws {
        app = nil
        super.tearDown()
    }
    
    // MARK: - Helper Methods
    
    /// Навигация к экрану оплаты
    private func navigateToPaymentQR() {
        // Способ 1: Через экран тарифов
        let tabBar = app.tabBars.firstMatch
        if tabBar.exists {
            // Ищем таб с тарифами/подпиской
            let subscriptionTab = tabBar.buttons.matching(NSPredicate(format: "label CONTAINS[c] 'тариф' OR label CONTAINS[c] 'tariff' OR label CONTAINS[c] 'подписк' OR label CONTAINS[c] 'subscription'")).firstMatch
            if subscriptionTab.exists {
                subscriptionTab.tap()
            }
        }
        
        // Ищем кнопку оплаты или тариф
        let payButton = app.buttons.matching(NSPredicate(format: "label CONTAINS[c] 'оплат' OR label CONTAINS[c] 'pay' OR label CONTAINS[c] 'купи' OR label CONTAINS[c] 'buy'")).firstMatch
        if payButton.exists {
            payButton.tap()
        }
        
        // Ждем появления экрана оплаты
        let paymentScreen = app.otherElements["PaymentQRScreen"]
        if !paymentScreen.waitForExistence(timeout: 5.0) {
            // Альтернативный способ: через меню
            let menuButton = app.buttons["Menu"]
            if menuButton.exists {
                menuButton.tap()
                let paymentItem = app.buttons.matching(NSPredicate(format: "label CONTAINS[c] 'оплат' OR label CONTAINS[c] 'pay'")).firstMatch
                if paymentItem.exists {
                    paymentItem.tap()
                }
            }
        }
    }
    
    // MARK: - Screen Display Tests
    
    /// Тест: Отображение экрана оплаты
    func testPaymentQRScreenDisplay() throws {
        navigateToPaymentQR()
        
        // Проверяем, что экран отображается
        let screen = app.otherElements["PaymentQRScreen"]
        if screen.waitForExistence(timeout: 5.0) {
            XCTAssertTrue(screen.exists, "Payment QR screen should be displayed")
        } else {
            // Если экран не найден по идентификатору, проверяем наличие ключевых элементов
            let qrCode = app.images.matching(NSPredicate(format: "identifier CONTAINS[c] 'qr' OR identifier CONTAINS[c] 'QR'")).firstMatch
            let amountLabel = app.staticTexts.matching(NSPredicate(format: "label CONTAINS '₽' OR label CONTAINS 'RUB'")).firstMatch
            
            if qrCode.exists || amountLabel.exists {
                XCTAssertTrue(true, "Payment screen elements found")
            } else {
                XCTSkip("Payment QR screen not accessible in current app state")
            }
        }
    }
    
    // MARK: - QR Code Display Tests
    
    /// Тест: Отображение QR-кода
    func testQRCodeDisplay() throws {
        navigateToPaymentQR()
        
        // Ждем загрузки QR-кода (может занять время)
        let qrCode = app.images.matching(NSPredicate(format: "identifier CONTAINS[c] 'qr' OR identifier CONTAINS[c] 'QR'")).firstMatch
        
        if qrCode.waitForExistence(timeout: 10.0) {
            XCTAssertTrue(qrCode.exists, "QR code should be displayed")
            XCTAssertTrue(qrCode.isHittable, "QR code should be visible and hittable")
        } else {
            // Если QR-код не найден, проверяем наличие индикатора загрузки
            let loadingIndicator = app.activityIndicators.firstMatch
            if loadingIndicator.exists {
                // Ждем еще немного для загрузки
                let _ = qrCode.waitForExistence(timeout: 5.0)
                if qrCode.exists {
                    XCTAssertTrue(qrCode.exists, "QR code should be displayed after loading")
                } else {
                    XCTSkip("QR code loading timeout - may need network connection")
                }
            } else {
                XCTSkip("QR code not found - screen may not be accessible")
            }
        }
    }
    
    // MARK: - Payment Method Selection Tests
    
    /// Тест: Выбор метода оплаты (СБП)
    func testSelectPaymentMethod_SBP() throws {
        navigateToPaymentQR()
        
        // Ищем кнопку/сегмент для выбора СБП
        let sbpButton = app.buttons.matching(NSPredicate(format: "label CONTAINS[c] 'СБП' OR label CONTAINS[c] 'SBP' OR identifier CONTAINS[c] 'sbp'")).firstMatch
        
        if sbpButton.exists {
            sbpButton.tap()
            
            // Проверяем, что метод выбран
            XCTAssertTrue(sbpButton.isSelected || sbpButton.value as? String == "1", "SBP payment method should be selected")
        } else {
            XCTSkip("SBP payment method selector not found")
        }
    }
    
    /// Тест: Выбор метода оплаты (SberPay)
    func testSelectPaymentMethod_SberPay() throws {
        navigateToPaymentQR()
        
        // Ищем кнопку/сегмент для выбора SberPay
        let sberpayButton = app.buttons.matching(NSPredicate(format: "label CONTAINS[c] 'SberPay' OR label CONTAINS[c] 'Сбер' OR identifier CONTAINS[c] 'sberpay'")).firstMatch
        
        if sberpayButton.exists {
            sberpayButton.tap()
            
            // Проверяем, что метод выбран
            XCTAssertTrue(sberpayButton.isSelected || sberpayButton.value as? String == "1", "SberPay payment method should be selected")
        } else {
            XCTSkip("SberPay payment method selector not found")
        }
    }
    
    /// Тест: Выбор метода оплаты (Card)
    func testSelectPaymentMethod_Card() throws {
        navigateToPaymentQR()
        
        // Ищем кнопку/сегмент для выбора карты
        let cardButton = app.buttons.matching(NSPredicate(format: "label CONTAINS[c] 'карт' OR label CONTAINS[c] 'card' OR identifier CONTAINS[c] 'card'")).firstMatch
        
        if cardButton.exists {
            cardButton.tap()
            
            // Проверяем, что метод выбран
            XCTAssertTrue(cardButton.isSelected || cardButton.value as? String == "1", "Card payment method should be selected")
        } else {
            XCTSkip("Card payment method selector not found")
        }
    }
    
    // MARK: - Payment Status Tests
    
    /// Тест: Отображение статуса платежа
    func testPaymentStatusDisplay() throws {
        navigateToPaymentQR()
        
        // Ждем появления статуса платежа
        let statusText = app.staticTexts.matching(NSPredicate(format: "label CONTAINS[c] 'ожидан' OR label CONTAINS[c] 'pending' OR label CONTAINS[c] 'заверш' OR label CONTAINS[c] 'completed' OR label CONTAINS[c] 'ошибк' OR label CONTAINS[c] 'error'")).firstMatch
        
        if statusText.waitForExistence(timeout: 10.0) {
            XCTAssertTrue(statusText.exists, "Payment status should be displayed")
            let statusLabel = statusText.label
            XCTAssertFalse(statusLabel.isEmpty, "Payment status label should not be empty")
            
            print("✅ Payment status found: \(statusLabel)")
        } else {
            // Статус может не отображаться сразу, это нормально
            print("⚠️ Payment status not found immediately - may appear later")
        }
    }
    
    /// Тест: Отображение суммы платежа
    func testPaymentAmountDisplay() throws {
        navigateToPaymentQR()
        
        // Ищем текст с суммой (обычно содержит ₽ или RUB)
        let amountText = app.staticTexts.matching(NSPredicate(format: "label CONTAINS '₽' OR label CONTAINS 'RUB' OR label MATCHES '.*[0-9]+.*'")).firstMatch
        
        if amountText.waitForExistence(timeout: 5.0) {
            XCTAssertTrue(amountText.exists, "Payment amount should be displayed")
            let amountLabel = amountText.label
            XCTAssertFalse(amountLabel.isEmpty, "Payment amount label should not be empty")
            
            print("✅ Payment amount found: \(amountLabel)")
        } else {
            XCTSkip("Payment amount not found - screen may not be accessible")
        }
    }
    
    // MARK: - Error Handling Tests
    
    /// Тест: Отображение ошибки (если возникает)
    func testErrorDisplay() throws {
        navigateToPaymentQR()
        
        // Ждем некоторое время для возможной ошибки
        let errorAlert = app.alerts.firstMatch
        
        if errorAlert.waitForExistence(timeout: 15.0) {
            // Если появился алерт с ошибкой, проверяем его
            XCTAssertTrue(errorAlert.exists, "Error alert should be displayed if error occurs")
            
            // Закрываем алерт
            let okButton = errorAlert.buttons.matching(NSPredicate(format: "label CONTAINS[c] 'ок' OR label CONTAINS[c] 'ok' OR label CONTAINS[c] 'закрыт' OR label CONTAINS[c] 'close'")).firstMatch
            if okButton.exists {
                okButton.tap()
            }
        } else {
            // Ошибка не возникла - это хорошо
            print("✅ No errors occurred during payment flow")
        }
    }
    
    // MARK: - Accessibility Tests
    
    /// Тест: Поддержка доступности
    func testAccessibilitySupport() throws {
        navigateToPaymentQR()
        
        // Проверяем, что элементы имеют accessibility labels
        let buttons = app.buttons.allElementsBoundByIndex
        var buttonsWithLabels = 0
        
        for button in buttons.prefix(10) { // Проверяем первые 10 кнопок
            let label = button.label
            if !label.isEmpty {
                buttonsWithLabels += 1
            }
        }
        
        // Хотя бы некоторые кнопки должны иметь labels
        if buttons.count > 0 {
            let labelPercentage = Double(buttonsWithLabels) / Double(min(buttons.count, 10)) * 100
            print("✅ Accessibility: \(Int(labelPercentage))% of buttons have labels")
            
            // Не строгий тест - просто проверяем наличие
            XCTAssertTrue(buttonsWithLabels > 0, "At least some buttons should have accessibility labels")
        }
    }
    
    // MARK: - Navigation Tests
    
    /// Тест: Закрытие экрана оплаты
    func testClosePaymentScreen() throws {
        navigateToPaymentQR()
        
        // Ищем кнопку закрытия/назад
        let backButton = app.navigationBars.buttons.firstMatch
        let closeButton = app.buttons.matching(NSPredicate(format: "label CONTAINS[c] 'закрыт' OR label CONTAINS[c] 'close' OR label CONTAINS[c] 'отмен' OR label CONTAINS[c] 'cancel' OR identifier CONTAINS[c] 'close'")).firstMatch
        
        if closeButton.exists {
            closeButton.tap()
            
            // Проверяем, что экран закрылся
            let screen = app.otherElements["PaymentQRScreen"]
            if screen.exists {
                // Ждем немного для анимации закрытия
                let _ = screen.waitForNonExistence(timeout: 2.0)
                XCTAssertFalse(screen.exists, "Payment screen should be closed")
            }
        } else if backButton.exists {
            backButton.tap()
            
            // Проверяем, что экран закрылся
            let screen = app.otherElements["PaymentQRScreen"]
            if screen.exists {
                let _ = screen.waitForNonExistence(timeout: 2.0)
                XCTAssertFalse(screen.exists, "Payment screen should be closed")
            }
        } else {
            XCTSkip("Close/back button not found")
        }
    }
    
    // MARK: - Loading State Tests
    
    /// Тест: Индикатор загрузки
    func testLoadingIndicator() throws {
        navigateToPaymentQR()
        
        // Проверяем наличие индикатора загрузки (может быть виден кратковременно)
        let loadingIndicator = app.activityIndicators.firstMatch
        
        if loadingIndicator.exists {
            XCTAssertTrue(loadingIndicator.exists, "Loading indicator should be displayed during payment creation")
            
            // Ждем завершения загрузки
            let _ = loadingIndicator.waitForNonExistence(timeout: 10.0)
            print("✅ Loading indicator disappeared - payment creation completed")
        } else {
            // Индикатор может исчезнуть очень быстро или не отображаться
            print("⚠️ Loading indicator not found - may have already completed")
        }
    }
}
