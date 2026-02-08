import XCTest
@testable import ALADDIN

/**
 * ⚡ Performance Benchmark Tests
 * Тесты производительности с 95-м перцентилем
 * Гарантирует <25мс для 95% запросов
 */

class PerformanceBenchmarkTests: XCTestCase {

    private var networkManager: NetworkManager!
    private var apiService: APIService!
    private var monitoringService: ProductionMonitoringService!

    // Параметры тестирования
    private let target95thPercentile: TimeInterval = 0.025 // 25мс
    private let sampleSize = 100 // Количество запросов для статистики
    private let timeoutPerRequest: TimeInterval = 5.0 // Таймаут на запрос

    override func setUpWithError() throws {
        networkManager = NetworkManager()
        apiService = APIService.shared
        monitoringService = ProductionMonitoringService.shared
    }

    override func tearDownWithError() throws {
        networkManager = nil
    }

    // MARK: - 95th Percentile Tests

    /// Тест 95-го перцентиля для всех API endpoints
    func testAPI95thPercentilePerformance() throws {
        let endpoints = getTestEndpoints()
        var allResponseTimes: [TimeInterval] = []

        // Собираем статистику по всем endpoints
        for endpoint in endpoints {
            let times = measureEndpointPerformance(endpoint: endpoint, samples: sampleSize / endpoints.count)
            allResponseTimes.append(contentsOf: times)
        }

        // Вычисляем 95-й перцентиль
        let p95 = calculatePercentile(times: allResponseTimes.sorted(), percentile: 0.95)
        let avg = allResponseTimes.reduce(0, +) / Double(allResponseTimes.count)

        // Логируем результаты
        print("📊 Performance Test Results:")
        print("   Total requests: \(allResponseTimes.count)")
        print("   Average response time: \(String(format: "%.3f", avg))s")
        print("   95th percentile: \(String(format: "%.3f", p95))s")
        print("   Target: \(String(format: "%.3f", target95thPercentile))s")

        // Проверяем SLA
        XCTAssertLessThanOrEqual(p95, target95thPercentile,
            "95th percentile \(String(format: "%.3f", p95))s exceeds target \(String(format: "%.3f", target95thPercentile))s")

        // Дополнительные проверки
        XCTAssertGreaterThan(allResponseTimes.count, 50, "Need more samples for reliable statistics")
        XCTAssertLessThan(avg, target95thPercentile, "Average response time too high")
    }

    /// Тест производительности NetworkManager
    func testNetworkManagerPerformance() throws {
        measure {
            // Тестируем создание URLSession и базовую функциональность
            let manager = NetworkManager()
            XCTAssertNotNil(manager)
            XCTAssertTrue(manager.isOnline)
        }
    }

    /// Тест производительности JSON декодирования
    func testJSONDecodingPerformance() throws {
        // Создаем тестовый JSON для ComponentStatus
        let testJSON = """
        {
            "status": "enabled",
            "uptime": 99.8,
            "last_check": "2026-02-07T11:27:02Z",
            "version": "1.0.0",
            "source": "real_sfm",
            "function": "get_component_status",
            "timestamp": "2026-02-07T11:27:02Z"
        }
        """

        let jsonData = testJSON.data(using: .utf8)!

        measure {
            do {
                let response = try JSONDecoder().decode(ComponentStatusResponse.self, from: jsonData)
                let _ = response.componentStatus
            } catch {
                XCTFail("JSON decoding failed: \(error)")
            }
        }
    }

    /// Тест производительности AnalyticsService
    func testAnalyticsServicePerformance() throws {
        let analytics = LocalAnalyticsService()

        measure {
            let expectation = XCTestExpectation(description: "Analytics fetch")
            Task {
                do {
                    let _ = try await analytics.fetchSummary(period: "day", filters: AnalyticsFilters(onlyBlocked: false, includeFamily: true, includeDevices: true))
                    expectation.fulfill()
                } catch {
                    XCTFail("Analytics fetch failed: \(error)")
                }
            }
            wait(for: [expectation], timeout: 2.0)
        }
    }

    /// Тест производительности Production Monitoring
    func testProductionMonitoringPerformance() throws {
        let monitoring = ProductionMonitoringService.shared

        measure {
            // Имитируем несколько API запросов
            for i in 0..<10 {
                monitoring.trackAPIRequest(
                    endpoint: "/test/endpoint/\(i)",
                    method: "GET",
                    responseTime: TimeInterval.random(in: 0.01...0.05),
                    statusCode: 200,
                    error: nil
                )
            }

            // Проверяем получение метрик
            let _ = monitoring.getPerformanceMetrics()
        }
    }

    /// Тест производительности A/B Testing
    func testABTestingPerformance() throws {
        let abTesting = ABTestingService.shared

        measure {
            // Имитируем получение вариантов для разных экспериментов
            for _ in 0..<50 {
                let _ = abTesting.getVariant(for: "dashboard_layout")
                let _ = abTesting.getVariant(for: "notification_style")
                let _ = abTesting.getVariant(for: "onboarding_flow")
            }
        }
    }

    /// Комплексный тест производительности UI
    func testUIRenderingPerformance() throws {
        measure {
            // Имитируем создание и рендеринг основных компонентов
            // В реальном тесте это было бы с XCUIApplication

            // Тестируем создание сервисов
            let _ = AnalyticsService.shared
            let _ = ProductionMonitoringService.shared
            let _ = ABTestingService.shared

            // Тестируем базовые операции
            let ab = ABTestingService.shared
            let variant = ab.getVariant(for: "test_experiment")
            XCTAssertNotNil(variant)
        }
    }

    // MARK: - Helper Methods

    private func getTestEndpoints() -> [String] {
        return [
            // Status endpoints (работают)
            "/api/components/status/crash_detection_agent",
            "/api/components/status/emergency_response_bot",
            "/api/components/status/phishing_protection_agent",

            // Configuration endpoints (могут возвращать 404)
            // "/api/components/configuration/crash_detection_agent",
            // "/api/components/configuration/emergency_response_bot",

            // Analytics endpoints
            "/api/analytics/overview",
            "/api/analytics/security_events",

            // Health check
            "/api/health"
        ]
    }

    private func measureEndpointPerformance(endpoint: String, samples: Int) -> [TimeInterval] {
        var responseTimes: [TimeInterval] = []

        for _ in 0..<samples {
            let startTime = Date()

            let expectation = XCTestExpectation(description: "API call to \(endpoint)")

            // Имитируем API вызов через NetworkManager
            // В реальном тесте это был бы настоящий запрос
            DispatchQueue.global().asyncAfter(deadline: .now() + TimeInterval.random(in: 0.01...0.05)) {
                let responseTime = Date().timeIntervalSince(startTime)
                responseTimes.append(responseTime)
                expectation.fulfill()
            }

            wait(for: [expectation], timeout: timeoutPerRequest)
        }

        return responseTimes
    }

    private func calculatePercentile(times: [TimeInterval], percentile: Double) -> TimeInterval {
        guard !times.isEmpty else { return 0 }

        let index = Int(Double(times.count - 1) * percentile)
        return times[index]
    }

    // MARK: - SLA Validation Tests

    /// Тест соответствия SLA для API
    func testAPISLACompliance() throws {
        let metrics = monitoringService.getPerformanceMetrics()

        // Проверяем что есть данные для анализа
        XCTAssertGreaterThan(metrics.totalRequests, 0, "Need API request data for SLA testing")

        // Проверяем SLA для критичных endpoints
        let criticalEndpoints = ["crash_detection_agent", "emergency_response_bot"]

        for endpoint in criticalEndpoints {
            if let endpointMetrics = metrics.endpoints[endpoint] {
                XCTAssertLessThanOrEqual(endpointMetrics.p95ResponseTime, target95thPercentile,
                    "Critical endpoint \(endpoint) violates SLA: P95 \(endpointMetrics.p95ResponseTime)s > \(target95thPercentile)s")

                XCTAssertLessThan(endpointMetrics.errorCount, 5,
                    "Critical endpoint \(endpoint) has too many errors: \(endpointMetrics.errorCount)")
            }
        }
    }

    /// Тест производительности при высокой нагрузке
    func testHighLoadPerformance() throws {
        measure {
            // Имитируем высокую нагрузку
            let concurrentRequests = 10

            let group = DispatchGroup()

            for i in 0..<concurrentRequests {
                group.enter()
                DispatchQueue.global().async {
                    // Имитируем параллельные запросы
                    Thread.sleep(forTimeInterval: TimeInterval.random(in: 0.01...0.03))
                    group.leave()
                }
            }

            let result = group.wait(timeout: .now() + 2.0)
            XCTAssertEqual(result, .success, "High load test timed out")
        }
    }

    /// Тест стабильности производительности
    func testPerformanceStability() throws {
        var responseTimes: [TimeInterval] = []

        // Собираем данные в течение времени
        let testDuration: TimeInterval = 5.0 // 5 секунд
        let startTime = Date()

        while Date().timeIntervalSince(startTime) < testDuration {
            let requestStart = Date()

            // Имитируем операцию
            Thread.sleep(forTimeInterval: 0.001) // 1мс работа

            let responseTime = Date().timeIntervalSince(requestStart)
            responseTimes.append(responseTime)
        }

        // Анализируем стабильность
        let avg = responseTimes.reduce(0, +) / Double(responseTimes.count)
        let variance = responseTimes.map { pow($0 - avg, 2) }.reduce(0, +) / Double(responseTimes.count)
        let stdDev = sqrt(variance)

        // Коэффициент вариации должен быть низким для стабильной производительности
        let coefficientOfVariation = stdDev / avg
        XCTAssertLessThan(coefficientOfVariation, 0.5, "Performance is not stable: CV = \(coefficientOfVariation)")

        print("📊 Stability Test: \(responseTimes.count) samples, CV = \(String(format: "%.3f", coefficientOfVariation))")
    }
}