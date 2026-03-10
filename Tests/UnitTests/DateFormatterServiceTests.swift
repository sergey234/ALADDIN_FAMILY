import XCTest
@testable import ALADDIN

/**
 * 🧪 Date Formatter Service Unit Tests
 * Тесты для проверки отсутствия рекурсии и корректности работы DateFormatterService
 * 
 * ✅ BUILD 100: Unit-тесты для предотвращения рекурсии
 */
@MainActor
final class DateFormatterServiceTests: XCTestCase {
    
    var service: DateFormatterService!
    
    override func setUp() {
        super.setUp()
        service = DateFormatterService.shared
    }
    
    override func tearDown() {
        service = nil
        super.tearDown()
    }
    
    // MARK: - Recursion Prevention Tests
    
    /// Тест: Проверка отсутствия рекурсии при множественных вызовах форматирования
    func testNoRecursionOnMultipleFormatCalls() {
        let date = Date()
        var callCount = 0
        let maxCalls = 1000
        
        // Вызываем форматирование множество раз
        for _ in 0..<maxCalls {
            let formatted = service.formatDisplayDate(date)
            XCTAssertFalse(formatted.isEmpty, "Форматированная строка не должна быть пустой")
            callCount += 1
        }
        
        XCTAssertEqual(callCount, maxCalls, "Все вызовы должны быть выполнены без рекурсии")
    }
    
    /// Тест: Проверка отсутствия рекурсии при параллельных вызовах
    func testNoRecursionOnConcurrentCalls() async {
        let date = Date()
        let concurrentCalls = 100
        
        await withTaskGroup(of: String?.self) { group in
            for _ in 0..<concurrentCalls {
                group.addTask {
                    return await MainActor.run {
                        self.service.formatDisplayDate(date)
                    }
                }
            }
            
            var results: [String?] = []
            for await result in group {
                results.append(result)
            }
            
            XCTAssertEqual(results.count, concurrentCalls, "Все параллельные вызовы должны быть выполнены")
            XCTAssertTrue(results.allSatisfy { $0 != nil && !$0!.isEmpty }, "Все результаты должны быть непустыми")
        }
    }
    
    /// Тест: Проверка отсутствия рекурсии при форматировании expiration date
    func testNoRecursionOnExpirationDateFormatting() {
        let isoString = "2026-12-31T23:59:59.000Z"
        var callCount = 0
        let maxCalls = 500
        
        // Вызываем форматирование множество раз
        for _ in 0..<maxCalls {
            let formatted = service.formatExpirationDate(from: isoString)
            XCTAssertNotNil(formatted, "Форматированная строка не должна быть nil")
            callCount += 1
        }
        
        XCTAssertEqual(callCount, maxCalls, "Все вызовы должны быть выполнены без рекурсии")
    }
    
    // MARK: - Formatting Tests
    
    /// Тест: Парсинг ISO8601 строки
    func testParseISO8601() {
        let isoString = "2026-12-31T23:59:59.000Z"
        let date = service.parseISO8601(isoString)
        
        XCTAssertNotNil(date, "Дата должна быть успешно распарсена")
    }
    
    /// Тест: Парсинг ISO8601 строки без fractional seconds
    func testParseISO8601WithoutFractionalSeconds() {
        let isoString = "2026-12-31T23:59:59Z"
        let date = service.parseISO8601(isoString)
        
        XCTAssertNotNil(date, "Дата должна быть успешно распарсена")
    }
    
    /// Тест: Форматирование даты для отображения
    func testFormatDisplayDate() {
        let date = Date()
        let formatted = service.formatDisplayDate(date)
        
        XCTAssertFalse(formatted.isEmpty, "Форматированная строка не должна быть пустой")
    }
    
    /// Тест: Форматирование даты и времени
    func testFormatDateTime() {
        let date = Date()
        let formatted = service.formatDateTime(date)
        
        XCTAssertFalse(formatted.isEmpty, "Форматированная строка не должна быть пустой")
    }
    
    /// Тест: Форматирование только времени
    func testFormatTime() {
        let date = Date()
        let formatted = service.formatTime(date)
        
        XCTAssertFalse(formatted.isEmpty, "Форматированная строка не должна быть пустой")
    }
    
    /// Тест: Полное форматирование
    func testFormatFull() {
        let date = Date()
        let formatted = service.formatFull(date)
        
        XCTAssertFalse(formatted.isEmpty, "Форматированная строка не должна быть пустой")
    }
    
    /// Тест: Форматирование expiration date из ISO строки
    func testFormatExpirationDate() {
        let isoString = "2026-12-31T23:59:59.000Z"
        let formatted = service.formatExpirationDate(from: isoString)
        
        XCTAssertNotNil(formatted, "Форматированная строка не должна быть nil")
        XCTAssertFalse(formatted!.isEmpty, "Форматированная строка не должна быть пустой")
    }
    
    // MARK: - Calendar Helper Tests
    
    /// Тест: Проверка isDateInToday
    func testIsDateInToday() {
        let today = Date()
        XCTAssertTrue(service.isDateInToday(today), "Сегодняшняя дата должна быть определена как сегодня")
        
        let yesterday = service.date(byAdding: -1, to: today)!
        XCTAssertFalse(service.isDateInToday(yesterday), "Вчерашняя дата не должна быть определена как сегодня")
    }
    
    /// Тест: Проверка isDateInYesterday
    func testIsDateInYesterday() {
        let today = Date()
        let yesterday = service.date(byAdding: -1, to: today)!
        
        XCTAssertTrue(service.isDateInYesterday(yesterday), "Вчерашняя дата должна быть определена как вчера")
        XCTAssertFalse(service.isDateInYesterday(today), "Сегодняшняя дата не должна быть определена как вчера")
    }
    
    /// Тест: Добавление дней к дате
    func testDateByAddingDays() {
        let date = Date()
        let futureDate = service.date(byAdding: 7, to: date)
        
        XCTAssertNotNil(futureDate, "Будущая дата должна быть создана")
        if let futureDate = futureDate {
            let daysDifference = Calendar.current.dateComponents([.day], from: date, to: futureDate).day
            XCTAssertEqual(daysDifference, 7, "Разница должна быть 7 дней")
        }
    }
    
    /// Тест: Получение компонента даты
    func testComponent() {
        let date = Date()
        let month = service.component(.month, from: date)
        
        XCTAssertGreaterThan(month, 0, "Месяц должен быть больше 0")
        XCTAssertLessThanOrEqual(month, 12, "Месяц должен быть не больше 12")
    }
    
    // MARK: - Thread Safety Tests
    
    /// Тест: Проверка thread-safety при множественных вызовах
    func testThreadSafety() async {
        let date = Date()
        let concurrentCalls = 50
        
        await withTaskGroup(of: Void.self) { group in
            for _ in 0..<concurrentCalls {
                group.addTask {
                    await MainActor.run {
                        let formatted = self.service.formatDisplayDate(date)
                        XCTAssertFalse(formatted.isEmpty)
                    }
                }
            }
            
            for await _ in group {
                // Все задачи должны выполниться без ошибок
            }
        }
    }
    
    // MARK: - Edge Cases Tests
    
    /// Тест: Обработка пустой ISO строки
    func testEmptyISOString() {
        let formatted = service.formatExpirationDate(from: "")
        XCTAssertNil(formatted, "Пустая строка должна вернуть nil")
    }
    
    /// Тест: Обработка невалидной ISO строки
    func testInvalidISOString() {
        let formatted = service.formatExpirationDate(from: "invalid-date")
        XCTAssertNil(formatted, "Невалидная строка должна вернуть nil")
    }
    
    /// Тест: Обработка nil при парсинге
    func testNilParsing() {
        let date = service.parseISO8601("invalid")
        XCTAssertNil(date, "Невалидная строка должна вернуть nil")
    }
}
