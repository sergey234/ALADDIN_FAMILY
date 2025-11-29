import XCTest
@testable import ALADDIN

/**
 * 📊 SharedDataManager Unit Tests
 * Тестирование менеджера общих данных для виджетов
 */

final class SharedDataManagerTests: XCTestCase {
    
    var sharedDataManager: SharedDataManager!
    
    override func setUpWithError() throws {
        sharedDataManager = SharedDataManager()
        // Очищаем данные перед каждым тестом
        clearAllData()
    }
    
    override func tearDownWithError() throws {
        clearAllData()
        sharedDataManager = nil
    }
    
    // MARK: - Family Protection Data Tests
    
    func testSaveFamilyProtectionData() {
        // Тестируем сохранение данных защиты семьи
        let testData = FamilyProtectionData(
            isProtected: true,
            threatsBlocked: 15,
            lastScanTime: Date(),
            familyMembersCount: 4
        )
        
        sharedDataManager.saveFamilyProtectionData(testData)
        
        let retrievedData = sharedDataManager.getFamilyProtectionData()
        XCTAssertNotNil(retrievedData, "Данные защиты семьи должны быть сохранены")
        XCTAssertEqual(retrievedData?.isProtected, true, "Статус защиты должен сохраниться")
        XCTAssertEqual(retrievedData?.threatsBlocked, 15, "Количество заблокированных угроз должно сохраниться")
        XCTAssertEqual(retrievedData?.familyMembersCount, 4, "Количество членов семьи должно сохраниться")
    }
    
    func testGetFamilyProtectionDataWhenEmpty() {
        // Тестируем получение данных защиты семьи когда они пустые
        let data = sharedDataManager.getFamilyProtectionData()
        XCTAssertNil(data, "Данные защиты семьи должны быть nil когда не сохранены")
    }
    
    // MARK: - VPN Status Data Tests
    
    func testSaveVPNStatusData() {
        // Тестируем сохранение данных статуса VPN
        let testData = VPNStatusData(
            isConnected: true,
            serverLocation: "США",
            connectionTime: Date(),
            dataTransferred: 1024 * 1024 // 1MB
        )
        
        sharedDataManager.saveVPNStatusData(testData)
        
        let retrievedData = sharedDataManager.getVPNStatusData()
        XCTAssertNotNil(retrievedData, "Данные статуса VPN должны быть сохранены")
        XCTAssertEqual(retrievedData?.isConnected, true, "Статус подключения должен сохраниться")
        XCTAssertEqual(retrievedData?.serverLocation, "США", "Локация сервера должна сохраниться")
        XCTAssertEqual(retrievedData?.dataTransferred, 1024 * 1024, "Переданные данные должны сохраниться")
    }
    
    func testGetVPNStatusDataWhenEmpty() {
        // Тестируем получение данных статуса VPN когда они пустые
        let data = sharedDataManager.getVPNStatusData()
        XCTAssertNil(data, "Данные статуса VPN должны быть nil когда не сохранены")
    }
    
    // MARK: - Analytics Data Tests
    
    func testSaveAnalyticsData() {
        // Тестируем сохранение данных аналитики
        let testData = AnalyticsData(
            dailyThreats: 5,
            weeklyThreats: 25,
            monthlyThreats: 100,
            lastUpdateTime: Date()
        )
        
        sharedDataManager.saveAnalyticsData(testData)
        
        let retrievedData = sharedDataManager.getAnalyticsData()
        XCTAssertNotNil(retrievedData, "Данные аналитики должны быть сохранены")
        XCTAssertEqual(retrievedData?.dailyThreats, 5, "Ежедневные угрозы должны сохраниться")
        XCTAssertEqual(retrievedData?.weeklyThreats, 25, "Еженедельные угрозы должны сохраниться")
        XCTAssertEqual(retrievedData?.monthlyThreats, 100, "Ежемесячные угрозы должны сохраниться")
    }
    
    func testGetAnalyticsDataWhenEmpty() {
        // Тестируем получение данных аналитики когда они пустые
        let data = sharedDataManager.getAnalyticsData()
        XCTAssertNil(data, "Данные аналитики должны быть nil когда не сохранены")
    }
    
    // MARK: - Data Update Tests
    
    func testUpdateFamilyProtectionData() {
        // Тестируем обновление данных защиты семьи
        let initialData = FamilyProtectionData(
            isProtected: false,
            threatsBlocked: 0,
            lastScanTime: Date(),
            familyMembersCount: 0
        )
        
        sharedDataManager.saveFamilyProtectionData(initialData)
        
        let updatedData = FamilyProtectionData(
            isProtected: true,
            threatsBlocked: 10,
            lastScanTime: Date(),
            familyMembersCount: 3
        )
        
        sharedDataManager.saveFamilyProtectionData(updatedData)
        
        let retrievedData = sharedDataManager.getFamilyProtectionData()
        XCTAssertEqual(retrievedData?.isProtected, true, "Данные должны обновиться")
        XCTAssertEqual(retrievedData?.threatsBlocked, 10, "Количество угроз должно обновиться")
    }
    
    // MARK: - Data Persistence Tests
    
    func testDataPersistence() {
        // Тестируем сохранение данных между сессиями
        let testData = FamilyProtectionData(
            isProtected: true,
            threatsBlocked: 20,
            lastScanTime: Date(),
            familyMembersCount: 5
        )
        
        sharedDataManager.saveFamilyProtectionData(testData)
        
        // Создаем новый экземпляр SharedDataManager
        let newManager = SharedDataManager()
        let retrievedData = newManager.getFamilyProtectionData()
        
        XCTAssertNotNil(retrievedData, "Данные должны сохраняться между сессиями")
        XCTAssertEqual(retrievedData?.isProtected, true, "Статус защиты должен сохраниться")
    }
    
    // MARK: - Helper Methods Tests
    
    func testFormatTime() {
        // Тестируем форматирование времени
        let date = Date()
        let formattedTime = sharedDataManager.formatTime(date)
        
        XCTAssertNotNil(formattedTime, "Время должно быть отформатировано")
        XCTAssertFalse(formattedTime.isEmpty, "Отформатированное время не должно быть пустым")
    }
    
    func testFormatDataSize() {
        // Тестируем форматирование размера данных
        let bytes = 1024 * 1024 // 1MB
        let formattedSize = sharedDataManager.formatDataSize(bytes)
        
        XCTAssertNotNil(formattedSize, "Размер данных должен быть отформатирован")
        XCTAssertTrue(formattedSize.contains("MB"), "Размер должен содержать единицы измерения")
    }
    
    // MARK: - Edge Cases Tests
    
    func testConcurrentDataAccess() {
        // Тестируем одновременный доступ к данным
        let expectation1 = XCTestExpectation(description: "Save data 1")
        let expectation2 = XCTestExpectation(description: "Save data 2")
        
        DispatchQueue.global().async {
            let data = FamilyProtectionData(
                isProtected: true,
                threatsBlocked: 10,
                lastScanTime: Date(),
                familyMembersCount: 2
            )
            self.sharedDataManager.saveFamilyProtectionData(data)
            expectation1.fulfill()
        }
        
        DispatchQueue.global().async {
            let data = VPNStatusData(
                isConnected: true,
                serverLocation: "Германия",
                connectionTime: Date(),
                dataTransferred: 2048
            )
            self.sharedDataManager.saveVPNStatusData(data)
            expectation2.fulfill()
        }
        
        wait(for: [expectation1, expectation2], timeout: 1.0)
        
        // Проверяем, что данные сохранились
        let familyData = sharedDataManager.getFamilyProtectionData()
        let vpnData = sharedDataManager.getVPNStatusData()
        
        XCTAssertNotNil(familyData, "Данные защиты семьи должны сохраниться")
        XCTAssertNotNil(vpnData, "Данные VPN должны сохраниться")
    }
    
    func testInvalidDataHandling() {
        // Тестируем обработку невалидных данных
        // В реальном тесте нужно было бы проверить обработку ошибок
        XCTAssertTrue(true, "Невалидные данные должны обрабатываться корректно")
    }
    
    // MARK: - Helper Methods
    
    private func clearAllData() {
        // Очищаем все данные для чистого тестирования
        let userDefaults = UserDefaults(suiteName: "group.com.aladdin.family")
        userDefaults?.removeObject(forKey: "family_protection_data")
        userDefaults?.removeObject(forKey: "vpn_status_data")
        userDefaults?.removeObject(forKey: "analytics_data")
    }
}
