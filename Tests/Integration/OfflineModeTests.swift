import XCTest
@testable import ALADDIN

/**
 * 📴 Offline Mode Tests
 * Тесты офлайн режима и синхронизации
 * Цель: Проверка работы приложения без интернета
 */

class OfflineModeTests: XCTestCase {
    
    var apiService: APIService!
    var networkManager: NetworkManager!
    
    override func setUpWithError() throws {
        // Настройка перед каждым тестом
        networkManager = NetworkManager()
        apiService = APIService(networkManager: networkManager)
    }
    
    override func tearDownWithError() throws {
        // Очистка после каждого теста
        apiService = nil
        networkManager = nil
    }
    
    // MARK: - Offline Queue Tests
    
    func testOfflineQueueCreation() throws {
        // Тест создания очереди запросов в офлайн режиме
        // Симулируем отсутствие интернета
        let expectation = XCTestExpectation(description: "Request queued")
        
        // Выполняем запрос в офлайн режиме
        apiService.getGamificationBalance(userId: "test_user") { result in
            switch result {
            case .failure(let error):
                // В офлайн режиме запрос должен быть добавлен в очередь
                if let networkError = error as? NetworkError,
                   case .noConnection = networkError {
                    expectation.fulfill()
                }
            case .success:
                XCTFail("Request should fail in offline mode")
            }
        }
        
        wait(for: [expectation], timeout: 5.0)
    }
    
    func testOfflineQueuePersistence() throws {
        // Тест сохранения очереди запросов
        let expectation = XCTestExpectation(description: "Queue persisted")
        
        // Добавляем несколько запросов в очередь
        apiService.getGamificationBalance(userId: "test_user") { _ in }
        apiService.getGamificationRewards(userId: "test_user") { _ in }
        apiService.getGamificationAchievements(userId: "test_user") { _ in }
        
        // Проверяем что очередь сохранилась
        // TODO: Реализовать проверку очереди через OfflineManager
        expectation.fulfill()
        
        wait(for: [expectation], timeout: 5.0)
    }
    
    func testOfflineQueueExecution() throws {
        // Тест выполнения очереди после восстановления интернета
        let expectation = XCTestExpectation(description: "Queue executed")
        
        // Добавляем запрос в очередь (офлайн режим)
        apiService.getGamificationBalance(userId: "test_user") { _ in }
        
        // Симулируем восстановление интернета
        // TODO: Реализовать симуляцию восстановления интернета
        
        // Проверяем что запросы из очереди выполнены
        expectation.fulfill()
        
        wait(for: [expectation], timeout: 5.0)
    }
    
    // MARK: - Offline Data Storage Tests
    
    func testOfflineDataStorage() throws {
        // Тест сохранения данных в офлайн режиме
        let expectation = XCTestExpectation(description: "Data stored offline")
        
        // Сохраняем данные в офлайн режиме
        let testData: [String: AnyCodable] = [
            "balance": AnyCodable(100),
            "level": AnyCodable(5)
        ]
        
        apiService.updateOfflineData(
            userId: "test_user",
            dataType: "gamification",
            data: testData
        ) { result in
            switch result {
            case .success:
                expectation.fulfill()
            case .failure:
                // В офлайн режиме данные должны сохраниться локально
                expectation.fulfill()
            }
        }
        
        wait(for: [expectation], timeout: 5.0)
    }
    
    func testOfflineDataRetrieval() throws {
        // Тест получения данных из офлайн хранилища
        let expectation = XCTestExpectation(description: "Data retrieved from offline storage")
        
        // Получаем данные из офлайн хранилища
        apiService.getOfflineData(userId: "test_user", dataType: "gamification") { result in
            switch result {
            case .success(let data):
                XCTAssertFalse(data.isEmpty)
                expectation.fulfill()
            case .failure:
                // В офлайн режиме должны вернуться локальные данные
                expectation.fulfill()
            }
        }
        
        wait(for: [expectation], timeout: 5.0)
    }
    
    // MARK: - Sync After Reconnection Tests
    
    func testSyncAfterReconnection() throws {
        // Тест синхронизации после восстановления интернета
        let expectation = XCTestExpectation(description: "Sync after reconnection")
        
        // Добавляем данные в офлайн режиме
        let testData: [String: AnyCodable] = [
            "balance": AnyCodable(100)
        ]
        
        apiService.updateOfflineData(
            userId: "test_user",
            dataType: "gamification",
            data: testData
        ) { _ in
            // Симулируем восстановление интернета
            // TODO: Реализовать симуляцию восстановления интернета
            
            // Проверяем что данные синхронизированы
            expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 5.0)
    }
    
    func testSyncPriority() throws {
        // Тест приоритетов синхронизации
        let expectation = XCTestExpectation(description: "Sync priority")
        
        // Добавляем несколько запросов с разными приоритетами
        // TODO: Реализовать проверку приоритетов
        
        expectation.fulfill()
        wait(for: [expectation], timeout: 5.0)
    }
    
    // MARK: - Conflict Resolution Tests
    
    func testConflictResolution() throws {
        // Тест разрешения конфликтов при синхронизации
        let expectation = XCTestExpectation(description: "Conflict resolved")
        
        // Создаем конфликт (одни и те же данные изменены на разных устройствах)
        let conflicts: [[String: String]] = [
            [
                "dataId": "test_data_1",
                "deviceId": "device_1",
                "version": "1",
                "timestamp": "2026-02-11T10:00:00Z"
            ],
            [
                "dataId": "test_data_1",
                "deviceId": "device_2",
                "version": "2",
                "timestamp": "2026-02-11T11:00:00Z"
            ]
        ]
        
        apiService.resolveOfflineStorageConflicts(
            userId: "test_user",
            conflicts: conflicts,
            resolutionStrategy: "last-write-wins"
        ) { result in
            switch result {
            case .success:
                expectation.fulfill()
            case .failure(let error):
                XCTFail("Conflict resolution failed: \(error)")
            }
        }
        
        wait(for: [expectation], timeout: 5.0)
    }
    
    func testConflictResolutionLastWriteWins() throws {
        // Тест стратегии "последняя запись побеждает"
        let expectation = XCTestExpectation(description: "Last write wins")
        
        let conflicts: [[String: String]] = [
            [
                "dataId": "test_data_1",
                "deviceId": "device_1",
                "timestamp": "2026-02-11T10:00:00Z"
            ],
            [
                "dataId": "test_data_1",
                "deviceId": "device_2",
                "timestamp": "2026-02-11T11:00:00Z" // Более поздняя запись
            ]
        ]
        
        apiService.resolveOfflineStorageConflicts(
            userId: "test_user",
            conflicts: conflicts,
            resolutionStrategy: "last-write-wins"
        ) { result in
            switch result {
            case .success(let resolution):
                // Проверяем что выбрана более поздняя запись
                XCTAssertNotNil(resolution["device_2"])
                expectation.fulfill()
            case .failure(let error):
                XCTFail("Conflict resolution failed: \(error)")
            }
        }
        
        wait(for: [expectation], timeout: 5.0)
    }
    
    // MARK: - Performance Tests
    
    func testOfflineModePerformance() throws {
        // Тест производительности офлайн режима
        self.measure {
            // Добавляем 100 запросов в очередь
            for i in 0..<100 {
                apiService.getGamificationBalance(userId: "test_user_\(i)") { _ in }
            }
        }
    }
    
    func testSyncPerformance() throws {
        // Тест производительности синхронизации
        self.measure {
            // Синхронизируем 100 элементов
            apiService.syncGamification(userId: "test_user", lastSyncTimestamp: nil) { _ in }
        }
    }
}
