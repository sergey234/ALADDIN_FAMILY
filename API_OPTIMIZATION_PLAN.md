# 🚀 ALADDIN API Performance Optimization Plan

## 📊 Текущая ситуация
- **Цель:** 95-й перцентиль <25ms
- **Реальность:** 95-й перцентиль = 76ms ❌
- **Средняя задержка:** 37ms
- **Максимальная задержка:** 150ms при нагрузке

## 🎯 Фазы оптимизации

### Фаза 1: Клиентские оптимизации (Немедленно - 1-2 дня)
#### 1.1 HTTP/2 и Connection Pooling
```swift
// NetworkManager.swift - добавить HTTP/2 поддержку
private var sessionConfiguration: URLSessionConfiguration = {
    let config = URLSessionConfiguration.default
    config.httpVersion = "2.0"  // Включить HTTP/2
    config.httpMaximumConnectionsPerHost = 10  // Connection pooling
    config.timeoutIntervalForRequest = 10.0
    config.timeoutIntervalForResource = 30.0
    return config
}()
```

#### 1.2 DNS Prefetching и Connection Keep-Alive
```swift
// Добавить в AppDelegate
func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    // DNS prefetching
    let dnsPrefetchURL = URL(string: "https://aladdin-ai.ru/api/health")!
    let prefetchRequest = URLRequest(url: dnsPrefetchURL, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 1.0)
    URLSession.shared.dataTask(with: prefetchRequest).resume()

    // Connection warming
    warmUpConnections()
    return true
}

private func warmUpConnections() {
    let warmupURLs = [
        "https://aladdin-ai.ru/api/health",
        "https://aladdin-ai.ru/api/components/status/crash_detection_agent"
    ]

    for urlString in warmupURLs {
        guard let url = URL(string: urlString) else { continue }
        let request = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 1.0)
        URLSession.shared.dataTask(with: request).resume()
    }
}
```

#### 1.3 Response Compression
```swift
// NetworkManager.swift - добавить Accept-Encoding
func get<T: Decodable>(
    endpoint: String,
    completion: @escaping (Result<T, Error>) -> Void
) {
    // ... existing code ...

    var request = URLRequest(url: url)
    request.httpMethod = "GET"
    request.setValue("gzip, deflate, br", forHTTPHeaderField: "Accept-Encoding")  // Включить сжатие
    request.setValue("application/json", forHTTPHeaderField: "Accept")

    // ... rest of code ...
}
```

#### 1.4 Intelligent Caching
```swift
// Добавить HTTP caching
private var sessionConfiguration: URLSessionConfiguration = {
    let config = URLSessionConfiguration.default
    config.httpVersion = "2.0"
    config.httpMaximumConnectionsPerHost = 10

    // Умное кэширование для статичных данных
    config.urlCache = URLCache(
        memoryCapacity: 10 * 1024 * 1024,    // 10MB memory
        diskCapacity: 50 * 1024 * 1024,      // 50MB disk
        diskPath: "aladdin_api_cache"
    )

    return config
}()
```

### Фаза 2: API Endpoint оптимизации (2-3 дня)

#### 2.1 Batch Requests для Component Status
```swift
// Новый endpoint для пакетных запросов
func getMultipleComponentStatuses(componentIds: [String]) async throws -> [ComponentStatus] {
    let endpoint = "/api/components/status/batch"
    let body = ["component_ids": componentIds]

    return try await withCheckedThrowingContinuation { continuation in
        networkManager.post(endpoint: endpoint, body: body) { (result: Result<APIResponse<[ComponentStatus]>, Error>) in
            // ...
        }
    }
}

// Использование в ViewModel
func loadAllComponentsOptimized() async {
    let componentIds = [
        "crash_detection_agent", "emergency_response_bot", "phishing_protection_agent",
        "mobile_security_agent", "network_security_agent", "incident_response_agent",
        "password_security_agent", "malware_detection_agent"
    ]

    do {
        let statuses = try await apiService.getMultipleComponentStatuses(componentIds: componentIds)
        // Обновить UI одним разом
    } catch {
        // Fallback to individual requests
        await loadComponentsIndividually()
    }
}
```

#### 2.2 Pagination и Partial Responses
```swift
// Добавить параметры для частичных ответов
struct ComponentStatusRequest {
    let componentIds: [String]?
    let fields: [String]?  // ["status", "uptime"] - только нужные поля
    let since: Date?       // Только обновленные после даты
}

// API endpoint: GET /api/components/status?ids=...&fields=...&since=...
```

#### 2.3 WebSocket для Real-time Updates
```swift
// WebSocket для мгновенных обновлений статуса компонентов
class ComponentWebSocketManager {
    private var webSocket: URLSessionWebSocketTask?

    func connect() {
        let url = URL(string: "wss://aladdin-ai.ru/ws/components")!
        let request = URLRequest(url: url)
        webSocket = URLSession.shared.webSocketTask(with: request)
        webSocket?.resume()
        receiveMessages()
    }

    private func receiveMessages() {
        webSocket?.receive { [weak self] result in
            switch result {
            case .success(let message):
                switch message {
                case .string(let text):
                    if let data = text.data(using: .utf8),
                       let update = try? JSONDecoder().decode(ComponentStatusUpdate.self, from: data) {
                        // Обновить UI мгновенно
                        NotificationCenter.default.post(name: .componentStatusUpdated, object: update)
                    }
                default:
                    break
                }
                self?.receiveMessages() // Продолжить слушать
            case .failure:
                // Reconnect logic
                DispatchQueue.global().asyncAfter(deadline: .now() + 5) {
                    self?.connect()
                }
            }
        }
    }
}
```

### Фаза 3: Серверные оптимизации (Требует backend работы)

#### 3.1 Database Optimization
```sql
-- Добавить индексы для часто используемых запросов
CREATE INDEX idx_component_status_updated_at ON component_status(updated_at);
CREATE INDEX idx_component_status_component_id ON component_status(component_id);

-- Оптимизировать запросы
EXPLAIN ANALYZE
SELECT status, uptime, last_check, version
FROM component_status
WHERE component_id = $1;
```

#### 3.2 Redis Caching Layer
```python
# Добавить Redis cache для component status
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_component_status_cached(component_id: str):
    # Проверяем кэш
    cache_key = f"component_status:{component_id}"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    # Если нет в кэше - получаем из БД
    status = get_component_status_from_db(component_id)

    # Кэшируем на 30 секунд
    redis_client.setex(cache_key, 30, json.dumps(status))

    return status
```

#### 3.3 CDN и Edge Computing
- Разместить API на CDN (Cloudflare, Fastly)
- Использовать edge functions для близких регионов
- Внедрить API rate limiting с intelligent caching

#### 3.4 Connection Pooling на сервере
```python
# FastAPI с оптимизированным connection pooling
from fastapi import FastAPI
import asyncpg

app = FastAPI()

# Connection pool для PostgreSQL
@app.on_event("startup")
async def startup():
    app.state.db_pool = await asyncpg.create_pool(
        user='user',
        password='password',
        database='aladdin',
        host='localhost',
        min_size=10,      # Минимум 10 соединений
        max_size=50       # Максимум 50 соединений
    )

@app.on_event("shutdown")
async def shutdown():
    await app.state.db_pool.close()
```

### Фаза 4: Мониторинг и alerting (1 день)

#### 4.1 Performance Monitoring
```swift
// ProductionMonitoringService - расширить метрики
class ProductionMonitoringService {
    func trackAPIPerformance(endpoint: String, responseTime: TimeInterval, success: Bool) {
        // Отправлять метрики в monitoring систему
        let metric = APIMetric(
            endpoint: endpoint,
            responseTime: responseTime,
            success: success,
            timestamp: Date(),
            userId: AppConfig.userId,
            deviceInfo: DeviceInfo.current
        )

        // Отправить в аналитику
        analytics.track("api_performance", parameters: [
            "endpoint": endpoint,
            "response_time_ms": responseTime * 1000,
            "success": success
        ])

        // Проверять SLA и алертить
        if responseTime > 0.025 { // 25ms
            alertSLAViolation(endpoint: endpoint, responseTime: responseTime)
        }
    }

    private func alertSLAViolation(endpoint: String, responseTime: TimeInterval) {
        // Отправить алерт в Slack/Discord или email
        let alert = SLAAlert(
            endpoint: endpoint,
            responseTime: responseTime,
            threshold: 0.025,
            timestamp: Date()
        )

        // В production - отправить в monitoring систему
        print("🚨 SLA VIOLATION: \(endpoint) took \(responseTime * 1000)ms")
    }
}
```

#### 4.2 Automated Testing
```swift
// PerformanceBenchmarkTests - добавить automated monitoring
class PerformanceBenchmarkTests: XCTestCase {
    func testContinuousPerformanceMonitoring() throws {
        // Запускать каждый час в CI/CD
        let expectation = XCTestExpectation(description: "Performance monitoring")

        Task {
            let results = await runPerformanceTestSuite()

            // Сохранить результаты для трендов
            savePerformanceResults(results)

            // Проверить регрессии
            checkPerformanceRegression(results)

            expectation.fulfill()
        }

        wait(for: [expectation], timeout: 300) // 5 минут на полный тест
    }
}
```

## 📈 Ожидаемые результаты оптимизации

### После Фазы 1 (клиентские оптимизации):
- **95-й перцентиль:** 60-65ms (снижение на 15-20%)
- **Средняя задержка:** 25-30ms
- **Максимальная задержка:** 120-130ms

### После Фазы 2 (batch requests):
- **95-й перцентиль:** 45-50ms (снижение на 35-40%)
- **Средняя задержка:** 18-22ms
- **UI responsiveness:** Значительно улучшится

### После Фазы 3 (серверные оптимизации):
- **95-й перцентиль:** 20-25ms ✅ (достижение цели)
- **Средняя задержка:** 12-15ms
- **Максимальная задержка:** <50ms

## 🛠️ План реализации

### День 1: Клиентские оптимизации
- [ ] Добавить HTTP/2 поддержку
- [ ] Внедрить connection pooling
- [ ] Настроить response compression
- [ ] Добавить intelligent caching

### День 2: API оптимизации
- [ ] Реализовать batch requests
- [ ] Добавить WebSocket для real-time updates
- [ ] Оптимизировать request patterns

### День 3: Мониторинг
- [ ] Расширить ProductionMonitoringService
- [ ] Добавить SLA alerting
- [ ] Настроить automated testing

### День 4-7: Серверные оптимизации (требует backend команды)
- [ ] Database indexing
- [ ] Redis caching
- [ ] CDN deployment
- [ ] Connection pooling

## 📊 Метрики успеха

| Метрика | До оптимизации | После Фазы 1 | После Фазы 2 | Цель (Фаза 3) |
|---------|----------------|---------------|---------------|----------------|
| 95-й перцентиль | 76ms | 60-65ms | 45-50ms | <25ms ✅ |
| Средняя задержка | 37ms | 25-30ms | 18-22ms | <15ms |
| UI responsiveness | Медленная | Хорошая | Отличная | Отличная |
| Server load | Высокий | Средний | Низкий | Оптимальный |

---

## 🎯 Следующие шаги

1. **Немедленно:** Начать с клиентских оптимизаций (Фаза 1)
2. **Координация:** Обсудить с backend командой серверные оптимизации
3. **Мониторинг:** Внедрить continuous performance monitoring
4. **Тестирование:** Регулярные performance тесты в CI/CD

**Ожидаемый результат:** Достижение SLA в течение 1-2 недель с постепенными улучшениями.