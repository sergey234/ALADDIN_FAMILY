import XCTest
@testable import ALADDIN

/**
 * 🔌 API Integration Tests для 42 компонентов
 * 
 * Тесты требуют работающий сервер по адресу из AppConfig
 * Для запуска тестов необходимо:
 * 1. Убедиться, что сервер доступен
 * 2. Настроить правильный baseURL в AppConfig
 * 3. Иметь валидные credentials для API
 */
@MainActor
class ComponentAPITests: XCTestCase {
    
    // MARK: - Properties
    var apiService: APIService!
    var statusService: ComponentStatusService!
    
    // MARK: - Test Setup
    override func setUp() {
        super.setUp()
        apiService = APIService.shared
        statusService = ComponentStatusService.shared
    }
    
    override func tearDown() {
        apiService = nil
        statusService = nil
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
    
    // MARK: - Test: Get Component Status
    
    /// Тест получения статуса для всех 42 компонентов
    func testGetComponentStatus_AllComponents() async throws {
        let componentIds = getAllComponentIds()
        var successCount = 0
        var failureCount = 0
        var errors: [String] = []
        
        for componentId in componentIds {
            do {
                let status = try await statusService.getStatus(for: componentId)
                XCTAssertNotNil(status, "Статус должен быть получен для \(componentId)")
                XCTAssertEqual(status.componentId, componentId, "ComponentId должен совпадать")
                print("✅ \(componentId): \(status.isEnabled ? "enabled" : "disabled")")
                successCount += 1
            } catch {
                print("❌ \(componentId): \(error.localizedDescription)")
                errors.append("\(componentId): \(error.localizedDescription)")
                failureCount += 1
            }
        }
        
        print("\n📊 Результаты:")
        print("✅ Успешно: \(successCount)/\(componentIds.count)")
        print("❌ Ошибок: \(failureCount)/\(componentIds.count)")
        
        if !errors.isEmpty {
            print("\n⚠️ Ошибки:")
            for error in errors {
                print("  - \(error)")
            }
        }
        
        // Минимум 80% компонентов должны отвечать
        let successRate = Double(successCount) / Double(componentIds.count)
        XCTAssertGreaterThanOrEqual(successRate, 0.8, "Минимум 80% компонентов должны отвечать")
    }
    
    // MARK: - Test: Enable Component
    
    /// Тест включения компонента
    func testEnableComponent() async throws {
        let testComponentId = "crash_detection_agent"
        
        // Получить текущий статус
        let initialStatus = try await statusService.getStatus(for: testComponentId)
        let wasEnabled = initialStatus.isEnabled
        
        // Включить компонент
        try await statusService.enableComponent(componentId: testComponentId)
        
        // Проверить, что компонент включен
        let newStatus = try await statusService.getStatus(for: testComponentId)
        XCTAssertTrue(newStatus.isEnabled, "Компонент должен быть включен")
        
        // Вернуть исходное состояние
        if !wasEnabled {
            try await statusService.disableComponent(componentId: testComponentId)
        }
    }
    
    // MARK: - Test: Disable Component
    
    /// Тест выключения компонента
    func testDisableComponent() async throws {
        let testComponentId = "crash_detection_agent"
        
        // Получить текущий статус
        let initialStatus = try await statusService.getStatus(for: testComponentId)
        let wasEnabled = initialStatus.isEnabled
        
        // Включить компонент сначала (если был выключен)
        if !wasEnabled {
            try await statusService.enableComponent(componentId: testComponentId)
        }
        
        // Выключить компонент
        try await statusService.disableComponent(componentId: testComponentId)
        
        // Проверить, что компонент выключен
        let newStatus = try await statusService.getStatus(for: testComponentId)
        XCTAssertFalse(newStatus.isEnabled, "Компонент должен быть выключен")
        
        // Вернуть исходное состояние
        if wasEnabled {
            try await statusService.enableComponent(componentId: testComponentId)
        }
    }
    
    // MARK: - Test: Batch Load Critical Components
    
    /// Тест batch загрузки критичных компонентов
    func testLoadCriticalComponentsStatus() async throws {
        let criticalComponents = [
            "crash_detection_agent",
            "emergency_response_bot",
            "phishing_protection_agent",
            "malware_detection_agent",
            "mobile_security_agent"
        ]
        
        try await statusService.loadComponentsStatus(componentIds: criticalComponents)
        
        // Проверить, что все статусы загружены
        for componentId in criticalComponents {
            let status = try await statusService.getStatus(for: componentId)
            XCTAssertNotNil(status, "Статус должен быть загружен для \(componentId)")
        }
    }
    
    // MARK: - Test: Update Component Configuration
    
    /// Тест обновления конфигурации компонента
    func testUpdateComponentConfiguration() async throws {
        let testComponentId = "password_security_agent"
        let configurationService = ComponentConfigurationService.shared
        
        // Создать тестовую конфигурацию
        let testConfig = ComponentConfiguration(
            componentId: testComponentId,
            settings: [
                "minLength": "12",
                "requireUppercase": "true",
                "requireNumbers": "true"
            ]
        )
        
        // Сохранить конфигурацию
        try await configurationService.saveConfiguration(testConfig)
        
        // Загрузить конфигурацию
        let loadedConfig = try await configurationService.getConfiguration(for: testComponentId)
        XCTAssertNotNil(loadedConfig, "Конфигурация должна быть загружена")
        XCTAssertEqual(loadedConfig?.componentId, testComponentId, "ComponentId должен совпадать")
    }
    
    // MARK: - Test: Network Error Handling
    
    /// Тест обработки сетевых ошибок
    func testNetworkErrorHandling() async {
        // Попытка получить статус несуществующего компонента
        let invalidComponentId = "non_existent_component_12345"
        
        do {
            _ = try await statusService.getStatus(for: invalidComponentId)
            XCTFail("Должна быть ошибка для несуществующего компонента")
        } catch {
            // Ожидаем ошибку
            XCTAssertTrue(error is ComponentError || error is NetworkError, "Должна быть ComponentError или NetworkError")
            print("✅ Ошибка корректно обработана: \(error.localizedDescription)")
        }
    }
    
    // MARK: - Test: Retry Mechanism
    
    /// Тест retry механизма
    func testRetryMechanism() async throws {
        let retryManager = RetryManager.balanced()
        let testComponentId = "crash_detection_agent"
        
        var attemptCount = 0
        
        let result: Result<ComponentStatus, NetworkError> = await retryManager.execute { [weak self] in
            attemptCount += 1
            guard let self = self else {
                throw NetworkError.unknown(NSError(domain: "test", code: -1))
            }
            return try await self.statusService.getStatus(for: testComponentId)
        }
        
        switch result {
        case .success(let status):
            XCTAssertNotNil(status, "Статус должен быть получен")
            print("✅ Retry успешен после \(attemptCount) попыток")
        case .failure(let error):
            XCTFail("Retry должен быть успешен: \(error.localizedDescription)")
        }
    }
    
    // MARK: - Test: All Components Toggle Cycle
    
    /// Тест полного цикла включения/выключения для всех компонентов
    func testAllComponentsToggleCycle() async throws {
        let componentIds = getAllComponentIds()
        var successCount = 0
        var failureCount = 0
        
        for componentId in componentIds {
            do {
                // Получить исходный статус
                let initialStatus = try await statusService.getStatus(for: componentId)
                let wasEnabled = initialStatus.isEnabled
                
                // Переключить состояние
                if wasEnabled {
                    try await statusService.disableComponent(componentId: componentId)
                    let disabledStatus = try await statusService.getStatus(for: componentId)
                    XCTAssertFalse(disabledStatus.isEnabled, "Компонент должен быть выключен")
                    
                    // Вернуть исходное состояние
                    try await statusService.enableComponent(componentId: componentId)
                } else {
                    try await statusService.enableComponent(componentId: componentId)
                    let enabledStatus = try await statusService.getStatus(for: componentId)
                    XCTAssertTrue(enabledStatus.isEnabled, "Компонент должен быть включен")
                    
                    // Вернуть исходное состояние
                    try await statusService.disableComponent(componentId: componentId)
                }
                
                successCount += 1
                print("✅ \(componentId): toggle успешен")
            } catch {
                failureCount += 1
                print("❌ \(componentId): \(error.localizedDescription)")
            }
        }
        
        print("\n📊 Результаты toggle цикла:")
        print("✅ Успешно: \(successCount)/\(componentIds.count)")
        print("❌ Ошибок: \(failureCount)/\(componentIds.count)")
        
        // Минимум 80% компонентов должны поддерживать toggle
        let successRate = Double(successCount) / Double(componentIds.count)
        XCTAssertGreaterThanOrEqual(successRate, 0.8, "Минимум 80% компонентов должны поддерживать toggle")
    }
}

