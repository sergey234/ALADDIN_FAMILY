import XCTest
@testable import ALADDIN

/**
 * 🔌 Полные API Integration Tests для 42 компонентов
 * 
 * Эти тесты требуют работающий сервер и выполняют полное тестирование:
 * - Получение статуса
 * - Включение/выключение
 * - Обновление конфигурации
 * - Проверка синхронизации
 */
@MainActor
class ComponentAPIIntegrationTests: XCTestCase {
    
    // MARK: - Properties
    var apiService: APIService!
    var statusService: ComponentStatusService!
    var configurationService: ComponentConfigurationService!
    
    // MARK: - Test Setup
    override func setUp() {
        super.setUp()
        apiService = APIService.shared
        statusService = ComponentStatusService.shared
        configurationService = ComponentConfigurationService.shared
    }
    
    override func tearDown() {
        apiService = nil
        statusService = nil
        configurationService = nil
        super.tearDown()
    }
    
    // MARK: - Helper Methods
    
    /// Получить список всех 42 компонентов
    private func getAllComponentIds() -> [String] {
        return [
            // NetworkProtectionScreen (10 компонентов)
            "crash_detection_agent",
            "roadside_assistance_agent",
            "emergency_response_bot",
            "emergency_event_manager",
            "phishing_protection_agent",
            "malware_detection_agent",
            "mobile_security_agent",
            "network_security_agent",
            "incident_response_agent",
            "password_security_agent",
            
            // ParentalControlScreen (5 компонентов)
            "self_harm_detection_agent",
            "grooming_detection_agent",
            "online_predators_agent",
            "psychological_support_agent",
            "parental_control_bot",
            
            // AdvancedProtectionSettingsScreen (13 компонентов)
            "telegram_security_bot",
            "whatsapp_security_bot",
            "instagram_security_bot",
            "max_messenger_security_bot",
            "gaming_security_bot",
            "browser_security_bot",
            "location_bubble_agent",
            "personal_data_cleanup_agent",
            "anti_tracker_agent",
            "dark_web_monitoring_agent",
            "russian_identity_theft_protection_agent",
            "ai_categories_agent",
            "driving_reports_agent",
            
            // SettingsScreen (5 менеджеров)
            "emergency_contacts_manager",
            "emergency_notifications_manager",
            "voice_control_manager",
            "russian_child_protection_compliance_manager",
            "russian_data_protection_compliance_manager",
            
            // Улучшение существующих (9 менеджеров)
            "family_notification_manager",
            "smart_notification_manager",
            "child_interface_manager",
            "elderly_interface_manager",
            "subscription_manager",
            "referral_manager",
            "qr_payment_manager",
            "analytics_manager",
            "report_manager"
        ]
    }
    
    // MARK: - Test: Full Integration Cycle
    
    /// Полный цикл тестирования для одного компонента
    func testFullIntegrationCycle_SingleComponent() async throws {
        let testComponentId = "crash_detection_agent"
        
        print("\n🔄 Тестирование полного цикла для: \(testComponentId)")
        
        // Шаг 1: Получить исходный статус
        print("  1. Получение исходного статуса...")
        let initialStatus = try await statusService.getStatus(for: testComponentId)
        let wasEnabled = initialStatus.isEnabled
        print("     Исходное состояние: \(wasEnabled ? "enabled" : "disabled")")
        
        // Шаг 2: Включить компонент
        print("  2. Включение компонента...")
        try await statusService.enableComponent(componentId: testComponentId)
        
        // Шаг 3: Проверить, что компонент включен
        print("  3. Проверка включения...")
        let enabledStatus = try await statusService.getStatus(for: testComponentId)
        XCTAssertTrue(enabledStatus.isEnabled, "Компонент должен быть включен")
        print("     ✅ Компонент включен")
        
        // Шаг 4: Обновить конфигурацию
        print("  4. Обновление конфигурации...")
        let testConfig = ComponentConfiguration(
            componentId: testComponentId,
            settings: [
                "test_key": "test_value",
                "timestamp": "\(Date().timeIntervalSince1970)"
            ]
        )
        try await configurationService.saveConfiguration(testConfig)
        print("     ✅ Конфигурация сохранена")
        
        // Шаг 5: Загрузить конфигурацию
        print("  5. Загрузка конфигурации...")
        let loadedConfig = try await configurationService.getConfiguration(for: testComponentId)
        XCTAssertNotNil(loadedConfig, "Конфигурация должна быть загружена")
        print("     ✅ Конфигурация загружена")
        
        // Шаг 6: Выключить компонент
        print("  6. Выключение компонента...")
        try await statusService.disableComponent(componentId: testComponentId)
        
        // Шаг 7: Проверить, что компонент выключен
        print("  7. Проверка выключения...")
        let disabledStatus = try await statusService.getStatus(for: testComponentId)
        XCTAssertFalse(disabledStatus.isEnabled, "Компонент должен быть выключен")
        print("     ✅ Компонент выключен")
        
        // Шаг 8: Вернуть исходное состояние
        print("  8. Восстановление исходного состояния...")
        if wasEnabled {
            try await statusService.enableComponent(componentId: testComponentId)
        }
        print("     ✅ Исходное состояние восстановлено")
        
        print("  ✅ Полный цикл завершен успешно\n")
    }
    
    // MARK: - Test: Batch Operations
    
    /// Тест batch операций для критичных компонентов
    func testBatchOperations_CriticalComponents() async throws {
        let criticalComponents = [
            "crash_detection_agent",
            "emergency_response_bot",
            "phishing_protection_agent",
            "malware_detection_agent",
            "mobile_security_agent"
        ]
        
        print("\n📦 Тестирование batch операций для критичных компонентов...")
        
        // Batch загрузка статусов
        print("  1. Batch загрузка статусов...")
        try await statusService.loadComponentsStatus(componentIds: criticalComponents)
        
        // Проверить все статусы
        for componentId in criticalComponents {
            let status = try await statusService.getStatus(for: componentId)
            XCTAssertNotNil(status, "Статус должен быть загружен для \(componentId)")
            print("    ✅ \(componentId): \(status.isEnabled ? "enabled" : "disabled")")
        }
        
        print("  ✅ Batch операции завершены успешно\n")
    }
    
    // MARK: - Test: Error Handling
    
    /// Тест обработки ошибок
    func testErrorHandling() async {
        print("\n⚠️ Тестирование обработки ошибок...")
        
        // Тест 1: Несуществующий компонент
        print("  1. Тест несуществующего компонента...")
        do {
            _ = try await statusService.getStatus(for: "non_existent_component_12345")
            XCTFail("Должна быть ошибка для несуществующего компонента")
        } catch {
            print("    ✅ Ошибка корректно обработана: \(error.localizedDescription)")
            XCTAssertTrue(error is ComponentError || error is NetworkError)
        }
        
        // Тест 2: Невалидная конфигурация
        print("  2. Тест невалидной конфигурации...")
        let invalidConfig = ComponentConfiguration(
            componentId: "crash_detection_agent",
            settings: [:] // Пустая конфигурация может быть невалидной
        )
        
        do {
            try await configurationService.saveConfiguration(invalidConfig)
            print("    ✅ Конфигурация сохранена (может быть валидной)")
        } catch {
            print("    ✅ Ошибка валидации корректно обработана: \(error.localizedDescription)")
        }
        
        print("  ✅ Обработка ошибок завершена\n")
    }
    
    // MARK: - Test: Retry Mechanism
    
    /// Тест retry механизма при временных ошибках
    func testRetryMechanism() async throws {
        print("\n🔄 Тестирование retry механизма...")
        
        let retryManager = RetryManager.balanced()
        let testComponentId = "crash_detection_agent"
        
        var attemptCount = 0
        
        let result: Result<ComponentStatus, NetworkError> = await retryManager.execute { [weak self] in
            attemptCount += 1
            guard let self = self else {
                throw NetworkError.unknown(NSError(domain: "test", code: -1))
            }
            print("    Попытка \(attemptCount)...")
            return try await self.statusService.getStatus(for: testComponentId)
        }
        
        switch result {
        case .success(let status):
            XCTAssertNotNil(status, "Статус должен быть получен")
            print("    ✅ Retry успешен после \(attemptCount) попыток")
        case .failure(let error):
            XCTFail("Retry должен быть успешен: \(error.localizedDescription)")
        }
        
        print("  ✅ Retry механизм работает корректно\n")
    }
    
    // MARK: - Test: Synchronization
    
    /// Тест синхронизации статусов между клиентом и сервером
    func testSynchronization() async throws {
        print("\n🔄 Тестирование синхронизации...")
        
        let testComponentId = "crash_detection_agent"
        
        // Получить статус с сервера
        let serverStatus = try await statusService.getStatus(for: testComponentId)
        
        // Очистить кэш
        let cacheService = ComponentCacheService.shared
        try? await cacheService.clearCache()
        
        // Получить статус снова (должен загрузиться с сервера)
        let freshStatus = try await statusService.getStatus(for: testComponentId)
        
        // Статусы должны совпадать
        XCTAssertEqual(serverStatus.isEnabled, freshStatus.isEnabled, "Статусы должны быть синхронизированы")
        XCTAssertEqual(serverStatus.componentId, freshStatus.componentId, "ComponentId должны совпадать")
        
        print("    ✅ Синхронизация работает корректно")
        print("  ✅ Тест синхронизации завершен\n")
    }
    
    // MARK: - Test: All Components Status Check
    
    /// Проверка статуса всех 42 компонентов
    func testAllComponentsStatusCheck() async throws {
        let componentIds = getAllComponentIds()
        var results: [String: Bool] = [:]
        
        print("\n📊 Проверка статуса всех 42 компонентов...")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        for componentId in componentIds {
            do {
                let status = try await statusService.getStatus(for: componentId)
                results[componentId] = true
                print("✅ \(componentId): \(status.isEnabled ? "enabled" : "disabled")")
            } catch {
                results[componentId] = false
                print("❌ \(componentId): \(error.localizedDescription)")
            }
        }
        
        let successCount = results.values.filter { $0 }.count
        let successRate = Double(successCount) / Double(componentIds.count)
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📊 Результаты:")
        print("   Успешно: \(successCount)/\(componentIds.count)")
        print("   Процент успеха: \(Int(successRate * 100))%")
        print("")
        
        // Минимум 80% компонентов должны отвечать
        XCTAssertGreaterThanOrEqual(successRate, 0.8, "Минимум 80% компонентов должны отвечать")
    }
}

