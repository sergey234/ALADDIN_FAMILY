// MARK: - КОМПЛЕКСНАЯ ДИАГНОСТИКА ALADDIN НА РЕАЛЬНОМ УСТРОЙСТВЕ
// Используйте этот код в Debug Console Xcode для диагностики проблем

import Foundation

// MARK: - 1. ПРОВЕРКА ТОКЕНОВ АВТОРИЗАЦИИ

func checkAuthTokens() {
    print("🔐 === ПРОВЕРКА ТОКЕНОВ АВТОРИЗАЦИИ ===")

    let keychain = KeychainManager.shared

    // Проверяем access token
    if let accessToken: String = keychain.load(String.self, forKey: .authToken) {
        print("✅ Access token найден (длина: \(accessToken.count))")
        if accessToken.contains(".debugsignature") || (accessToken.count == 140 && accessToken.contains("eyJhbGciOi")) {
            print("⚠️ ОБНАРУЖЕН DEBUG ACCESS TOKEN!")
        } else {
            print("✅ Access token выглядит как реальный")
        }
    } else {
        print("❌ Access token НЕ НАЙДЕН!")
    }

    // Проверяем refresh token
    if let refreshToken: String = keychain.load(String.self, forKey: .refreshToken) {
        print("✅ Refresh token найден (длина: \(refreshToken.count))")
        if refreshToken == "debug-refresh-token" {
            print("⚠️ ОБНАРУЖЕН DEBUG REFRESH TOKEN!")
        } else {
            print("✅ Refresh token выглядит как реальный")
        }
    } else {
        print("❌ Refresh token НЕ НАЙДЕН!")
    }

    // Проверяем сохраненные credentials
    let savedEmail = UserDefaults.standard.string(forKey: "saved_login_email")
    let savedPassword = UserDefaults.standard.string(forKey: "saved_login_password")
    let autoLoginEnabled = UserDefaults.standard.bool(forKey: "auto_login_enabled")

    print("📧 Сохраненные credentials:")
    print("   - Email: \(savedEmail ?? "не найден")")
    print("   - Password: \(savedPassword != nil ? "найден (\(savedPassword!.count) символов)" : "не найден")")
    print("   - Автологин: \(autoLoginEnabled ? "включен" : "выключен")")

    print("🔐 === КОНЕЦ ПРОВЕРКИ ТОКЕНОВ ===\n")
}

// MARK: - 2. ПРОВЕРКА ПОДКЛЮЧЕНИЯ К СЕРВЕРУ

func checkServerConnection() {
    print("🌐 === ПРОВЕРКА ПОДКЛЮЧЕНИЯ К СЕРВЕРУ ===")

    let testEndpoint = "/api/health"

    APIService.shared.get(endpoint: testEndpoint) { result in
        switch result {
        case .success(let data):
            print("✅ Подключение к серверу УСПЕШНО")
            if let jsonString = String(data: data, encoding: .utf8) {
                print("📄 Ответ сервера: \(jsonString)")
            }

            // Парсим JSON для анализа
            do {
                if let json = try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any] {
                    print("📊 Анализ ответа:")
                    if let status = json["status"] as? String {
                        print("   - Status: \(status)")
                    }
                    if let sfmAdapter = json["sfm_adapter"] as? String {
                        print("   - SFM Adapter: \(sfmAdapter)")
                    }
                    if let endpoints = json["endpoints"] as? Int {
                        print("   - Endpoints: \(endpoints)")
                    }
                    if let groups = json["groups"] as? [String] {
                        print("   - Groups: \(groups.joined(separator: ", "))")
                    }
                }
            } catch {
                print("⚠️ Не удалось распарсить JSON ответ")
            }

        case .failure(let error):
            print("❌ Ошибка подключения к серверу: \(error.localizedDescription)")
            print("🔍 Детали ошибки:")

            if let networkError = error as? NetworkError {
                switch networkError {
                case .invalidStatusCode(let code):
                    print("   - HTTP Status: \(code)")
                    if code == 404 {
                        print("   - ⚠️ Endpoint не найден! Проверьте правильность endpoint на сервере")
                    } else if code == 401 {
                        print("   - ⚠️ Неверные credentials (email или password)")
                    } else if code == 403 {
                        print("   - ⚠️ Доступ запрещен")
                    }
                case .timeout:
                    print("   - Timeout: сервер не отвечает")
                case .noConnection:
                    print("   - Нет подключения к интернету")
                default:
                    print("   - Тип ошибки: \(networkError)")
                }
            }
        }
    }

    print("🌐 === КОНЕЦ ПРОВЕРКИ ПОДКЛЮЧЕНИЯ ===\n")
}

// MARK: - 3. ПРОВЕРКА SFM СТАТУСА

func checkSFMStatus() {
    print("🤖 === ПРОВЕРКА SFM СТАТУСА ===")

    APIService.shared.get(endpoint: "/api/health") { result in
        switch result {
        case .success(let data):
            do {
                if let json = try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any],
                   let sfmStatus = json["sfm_adapter"] as? String {
                    print("📊 SFM Adapter статус: \(sfmStatus)")

                    switch sfmStatus {
                    case "available":
                        print("✅ SFM работает корректно!")
                    case "initializing":
                        print("⏳ SFM инициализируется...")
                    case "fallback":
                        print("⚠️ SFM работает в режиме fallback (mock данные)")
                        print("🔧 Возможные причины:")
                        print("   - SFM медленно загружается (60+ сек)")
                        print("   - Ошибки в инициализации компонентов")
                        print("   - Недостаточно ресурсов сервера")
                    case "error":
                        print("❌ SFM в состоянии ошибки")
                    default:
                        print("❓ Неизвестный статус SFM")
                    }
                } else {
                    print("⚠️ Не удалось получить статус SFM")
                }
            } catch {
                print("❌ Ошибка парсинга ответа SFM")
            }

        case .failure(let error):
            print("❌ Не удалось проверить статус SFM: \(error.localizedDescription)")
        }
    }

    print("🤖 === КОНЕЦ ПРОВЕРКИ SFM ===\n")
}

// MARK: - 4. ПРОВЕРКА ОСНОВНЫХ API ЭНДПОИНТОВ

func testMainAPIEndpoints() {
    print("🔗 === ТЕСТИРОВАНИЕ ОСНОВНЫХ API ЭНДПОИНТОВ ===")

    let endpoints = [
        "/api/phishing/sensitivity",
        "/api/malware/scan_scheduled",
        "/api/network/firewall_rules",
        "/api/components/status/crash_detection_agent",
        "/api/analytics/overview",
        "/api/notifications/list"
    ]

    for endpoint in endpoints {
        print("🔍 Тестируем: \(endpoint)")
        APIService.shared.get(endpoint: endpoint) { result in
            switch result {
            case .success(let data):
                print("   ✅ \(endpoint): УСПЕХ")
                if let jsonString = String(data: data, encoding: .utf8) {
                    // Проверяем, содержит ли ответ "mock" или "real"
                    if jsonString.contains("\"source\": \"mock\"") {
                        print("   ⚠️ Данные из MOCK (не реальные)")
                    } else if jsonString.contains("\"source\": \"sfm_real\"") {
                        print("   ✅ Данные из SFM (реальные)")
                    } else {
                        print("   ℹ️ Данные без указания источника")
                    }
                }
            case .failure(let error):
                print("   ❌ \(endpoint): ОШИБКА - \(error.localizedDescription)")
            }
        }
    }

    print("🔗 === КОНЕЦ ТЕСТИРОВАНИЯ API ===\n")
}

// MARK: - 5. ПРОВЕРКА УВЕДОМЛЕНИЙ

func checkNotificationsSystem() {
    print("🔔 === ПРОВЕРКА СИСТЕМЫ УВЕДОМЛЕНИЙ ===")

    // Проверяем разрешения
    NotificationManager.shared.requestAuthorization { granted in
        print("📱 Разрешения на уведомления: \(granted ? "✅ предоставлены" : "❌ отклонены")")

        if !granted {
            print("⚠️ Уведомления не будут приходить - разрешения не предоставлены!")
            print("🔧 Как исправить:")
            print("   1. Настройки → ALADDIN → Уведомления")
            print("   2. Включить 'Разрешить уведомления'")
            return
        }

        // Отправляем тестовое уведомление
        print("📤 Отправляем тестовое уведомление...")
        APIService.shared.testNotification { result in
            switch result {
            case .success:
                print("✅ Тестовое уведомление отправлено успешно")
                print("⏳ Проверьте, пришло ли уведомление на устройство в течение 10 секунд")
            case .failure(let error):
                print("❌ Ошибка отправки тестового уведомления: \(error.localizedDescription)")
            }
        }
    }

    print("🔔 === КОНЕЦ ПРОВЕРКИ УВЕДОМЛЕНИЙ ===\n")
}

// MARK: - 6. АНАЛИЗ ДАННЫХ АНАЛИТИКИ

func analyzeAnalyticsData() {
    print("📊 === АНАЛИЗ ДАННЫХ АНАЛИТИКИ ===")

    APIService.shared.get(endpoint: "/api/analytics/overview") { result in
        switch result {
        case .success(let data):
            print("✅ Данные аналитики получены")

            do {
                if let json = try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any] {
                    print("📈 Анализ данных:")

                    // Проверяем на старые данные
                    if let webThreats = json["web_threats"] as? Int {
                        print("   - Web threats: \(webThreats)")
                        if webThreats == 542 {
                            print("   ⚠️ ВНИМАНИЕ: Данные выглядят устаревшими (542 - фиксированное значение)")
                        }
                    }

                    if let fileThreats = json["file_threats"] as? Int {
                        print("   - File threats: \(fileThreats)")
                        if fileThreats == 318 {
                            print("   ⚠️ ВНИМАНИЕ: Данные выглядят устаревшими (318 - фиксированное значение)")
                        }
                    }

                    if let lastUpdate = json["last_update"] as? String {
                        print("   - Last update: \(lastUpdate)")
                        // Проверяем, не старше ли недели
                        if let date = ISO8601DateFormatter().date(from: lastUpdate) {
                            let timeInterval = Date().timeIntervalSince(date)
                            let days = Int(timeInterval / (24 * 60 * 60))
                            if days > 7 {
                                print("   ⚠️ Данные старше \(days) дней!")
                            } else {
                                print("   ✅ Данные свежие (\(days) дней назад)")
                            }
                        }
                    }

                    if let source = json["source"] as? String {
                        print("   - Source: \(source)")
                        if source == "mock" {
                            print("   ⚠️ Данные из MOCK - аналитика не работает!")
                        } else if source == "real" {
                            print("   ✅ Данные реальные")
                        }
                    }

                } else {
                    print("⚠️ Не удалось распарсить данные аналитики")
                }
            } catch {
                print("❌ Ошибка парсинга данных аналитики")
            }

        case .failure(let error):
            print("❌ Ошибка получения данных аналитики: \(error.localizedDescription)")
        }
    }

    print("📊 === КОНЕЦ АНАЛИЗА АНАЛИТИКИ ===\n")
}

// MARK: - 7. ПРОВЕРКА ТУМБЛЕРОВ КОМПОНЕНТОВ

func checkComponentToggles() {
    print("🔄 === ПРОВЕРКА ТУМБЛЕРОВ КОМПОНЕНТОВ ===")

    let components = [
        "crash_detection_agent",
        "phishing_protection_agent",
        "malware_detection_agent",
        "emergency_response_agent"
    ]

    for componentId in components {
        print("🔍 Проверяем компонент: \(componentId)")

        APIService.shared.getComponentStatus(componentId: componentId) { result in
            switch result {
            case .success(let status):
                print("   ✅ \(componentId): статус получен - \(status)")
                if status {
                    print("   🔄 Компонент ВКЛЮЧЕН")
                } else {
                    print("   ⭕ Компонент ВЫКЛЮЧЕН")
                }
            case .failure(let error):
                print("   ❌ \(componentId): ошибка - \(error.localizedDescription)")
            }
        }
    }

    print("🔄 === КОНЕЦ ПРОВЕРКИ ТУМБЛЕРОВ ===\n")
}

// MARK: - ГЛАВНАЯ ФУНКЦИЯ ДИАГНОСТИКИ

func runFullDiagnostic() {
    print("🚀 === НАЧАЛО ПОЛНОЙ ДИАГНОСТИКИ ALADDIN ===\n")

    // Выполняем все проверки последовательно с задержками
    checkAuthTokens()

    DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
        checkServerConnection()

        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            checkSFMStatus()

            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                testMainAPIEndpoints()

                DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
                    checkNotificationsSystem()

                    DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                        analyzeAnalyticsData()

                        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                            checkComponentToggles()

                            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                                print("🏁 === ДИАГНОСТИКА ЗАВЕРШЕНА ===")
                                print("📋 РЕЗУЛЬТАТЫ:")
                                print("   - Проверьте логи выше на наличие ошибок")
                                print("   - Исправьте найденные проблемы")
                                print("   - Повторите тестирование")
                            }
                        }
                    }
                }
            }
        }
    }
}

// MARK: - ДОСТУПНЫЕ КОМАНДЫ ДЛЯ DEBUG CONSOLE

/*
КОМАНДЫ ДЛЯ ИСПОЛЬЗОВАНИЯ В DEBUG CONSOLE XCODE:

1. ПОЛНАЯ ДИАГНОСТИКА:
runFullDiagnostic()

2. ОТДЕЛЬНЫЕ ПРОВЕРКИ:
checkAuthTokens()           // Проверка токенов
checkServerConnection()     // Проверка сервера
checkSFMStatus()           // Проверка SFM
testMainAPIEndpoints()     // Тестирование API
checkNotificationsSystem() // Проверка уведомлений
analyzeAnalyticsData()     // Анализ аналитики
checkComponentToggles()    // Проверка тумблеров

3. ДОПОЛНИТЕЛЬНЫЕ КОМАНДЫ:
performRealLogin(email: "ваш_email@test.com", password: "ваш_пароль") { _ in } // Авторизация
clearDebugTokens()         // Очистка debug токенов
checkIfTokensAreDebug()    // Проверка типа токенов

ПРИМЕР ИСПОЛЬЗОВАНИЯ:
1. В Xcode откройте Debug Console (View → Debug Area → Activate Console)
2. Выполните: runFullDiagnostic()
3. Дождитесь завершения всех проверок
4. Проанализируйте результаты
*/