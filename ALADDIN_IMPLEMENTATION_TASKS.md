# 🎯 **ALADDIN iOS - ПОЛНЫЙ СПИСОК ЗАДАЧ (60) С ПОДРОБНЫМ ОПИСАНИЕМ**

*Дата создания: 10 февраля 2026 г.*
*Версия: 1.0*
*Для ML системы: подробная инструкция по выполнению всех задач*

---

## 📋 **ПОЛНЫЙ СПИСОК ВСЕХ 60 ЗАДАЧ**

**Каждая задача имеет:**
- 🎯 **Цель** - что нужно достичь
- 📋 **Действия** - пошаговый план выполнения
- 🧪 **Тестирование** - как проверить результат
- ⚠️ **Риски** - что может пойти не так

---

### **🚨 АВАРИЙНЫЙ ЭТАП: AI ASSISTANT (Задачи 1-5)**

#### **1. `ai_server_endpoints` - Добавить 8 AI Assistant endpoint'ов на сервер**
**Цель:** Создать API endpoints для чата с ИИ

**Действия:**
- Подключиться к серверу по SSH: `ssh user@149.154.65.180`
- Открыть файл `api_gateway_server_current.py`
- Добавить следующие endpoints:
  ```python
  @app.post("/api/ai/assistant/chat")        # отправка сообщения
  @app.get("/api/ai/assistant/history")       # история чата
  @app.post("/api/ai/assistant/feedback")     # обратная связь
  @app.get("/api/ai/assistant/capabilities")  # возможности ИИ
  @app.post("/api/ai/assistant/analyze_threat") # анализ угрозы
  @app.get("/api/ai/assistant/recommendations") # рекомендации
  @app.post("/api/ai/assistant/report_incident") # отчет об инциденте
  @app.get("/api/ai/assistant/security_tips") # советы по безопасности
  ```
- Реализовать логику обработки для каждого endpoint'а
- Протестировать через curl/Postman

**Тестирование:** Каждый endpoint возвращает корректный JSON ответ
**Риски:** Неправильные пути endpoint'ов, ошибки в логике

#### **2. `ai_ios_endpoints` - Добавить AI endpoint'ы в AppConfig.swift и исправить APIService**
**Цель:** Настроить клиентскую часть AI API

**Действия:**
- В `AppConfig.swift` добавить:
  ```swift
  static let aiAssistantChat = "/api/ai/assistant/chat"
  static let aiAssistantHistory = "/api/ai/assistant/history"
  static let aiAssistantFeedback = "/api/ai/assistant/feedback"
  static let aiAssistantCapabilities = "/api/ai/assistant/capabilities"
  static let aiAssistantAnalyzeThreat = "/api/ai/assistant/analyze_threat"
  static let aiAssistantRecommendations = "/api/ai/assistant/recommendations"
  static let aiAssistantReportIncident = "/api/ai/assistant/report_incident"
  static let aiAssistantSecurityTips = "/api/ai/assistant/security_tips"
  ```
- В `APIService.swift` добавить методы:
  ```swift
  func sendAIChatMessage(message: String, completion: @escaping (Result<AIChatResponse, Error>) -> Void)
  func getAIChatHistory(completion: @escaping (Result<[AIChatMessage], Error>) -> Void)
  func sendAIFeedback(rating: Int, comment: String, completion: @escaping (Result<AIFeedbackResponse, Error>) -> Void)
  // + остальные методы
  ```
- Использовать `AppConfig.Endpoint.*` вместо жестких строк

**Тестирование:** Методы компилируются, endpoint'ы правильные
**Риски:** Ошибки типизации, неправильные пути

#### **3. `ai_localization` - Добавить все feedback ключи локализации**
**Цель:** Перевести интерфейс обратной связи AI

**Действия:**
- В `LocalizedVersions/Russian.json` добавить:
  ```json
  "ai_assistant_feedback_title": "Обратная связь",
  "ai_assistant_feedback_description": "Расскажите, как улучшить AI помощника",
  "ai_assistant_feedback_rating": "Оценка",
  "ai_assistant_feedback_comment": "Комментарий",
  "ai_assistant_feedback_submit": "Отправить",
  "ai_assistant_feedback_success": "Спасибо за отзыв!"
  ```
- В `LocalizedVersions/English.json` добавить соответствующие английские переводы
- Проверить что ключи используются в `AIAssistantViewModel`
- Протестировать отображение на русском и английском

**Тестирование:** Все тексты отображаются корректно на обоих языках
**Риски:** Ошибки в JSON синтаксисе, отсутствие ключей

#### **4. `ai_speech_fix` - Добавить NSSpeechRecognitionUsageDescription в Info.plist**
**Цель:** Исправить краш при голосовом вводе

**Действия:**
- Открыть `Info.plist`
- Добавить ключ:
  ```xml
  <key>NSSpeechRecognitionUsageDescription</key>
  <string>AI Assistant использует распознавание речи для голосовых команд</string>
  ```
- Проверить что `Info.plist` валиден (Xcode не показывает ошибки)
- Протестировать голосовой ввод в AI Assistant
- Убедиться что нет краша при активации микрофона

**Тестирование:** Голосовой ввод работает без крашей
**Риски:** Неправильный формат Info.plist, отсутствие описания

#### **5. `ai_real_integration` - Интегрировать настоящий AI вместо симуляции**
**Цель:** Заменить фейковые ответы на реальный ИИ

**Действия:**
- В `AIAssistantViewModel` заменить:
  ```swift
  // УБРАТЬ:
  DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { [weak self] in
      let aiResponse = ChatMessage(text: "Понял ваш запрос! Обрабатываю... 🤖", isUser: false, timestamp: Date())
      self?.messages.append(aiResponse)
      self?.isAITyping = false
  }

  // ДОБАВИТЬ:
  apiService.sendAIChatMessage(message: currentMessage) { [weak self] result in
      switch result {
      case .success(let response):
          let aiMessage = ChatMessage(text: response.message, isUser: false, timestamp: Date())
          self?.messages.append(aiMessage)
      case .failure(let error):
          let errorMessage = ChatMessage(text: "Ошибка: \(error.localizedDescription)", isUser: false, timestamp: Date())
          self?.messages.append(errorMessage)
      }
      self?.isAITyping = false
  }
  ```
- Протестировать отправку сообщений на сервер
- Проверить обработку ответов AI
- Добавить индикатор загрузки при ожидании ответа

**Тестирование:** Сообщения отправляются на сервер, приходят реальные ответы
**Риски:** Сетевые ошибки, неправильная обработка ответов

---

### **🔧 ЭТАП 0: ИСПРАВЛЕНИЕ MOCK (Задачи 6-22)**

#### **6. `fix_appconfig_mockapi` - ИСПРАВИТЬ useMockAPI = true в AppConfig.swift (КРИТИЧНО!)**
**Цель:** Включить реальный API вместо mock в продакшене

**Действия:**
- В `Core/Config/AppConfig.swift` найти:
  ```swift
  static let useMockAPI: Bool = true  // ❌ ПРОДАКШЕН НЕ РАБОТАЕТ!
  ```
- Заменить на:
  ```swift
  static let useMockAPI: Bool = {
      #if DEBUG && USE_MOCK_FOR_DEVELOPMENT
      return true  // Только для разработки
      #else
      return false // Продакшен использует реальный API
      #endif
  }()
  ```
- Пересобрать проект (cmd+B)
- Проверить что приложение запускается
- Убедиться что API запросы идут на реальный сервер

**Тестирование:** Приложение компилируется, запускается, API запросы идут на сервер
**Риски:** Крах при запуске, неправильная конфигурация

#### **7. `fix_hardcoded_endpoints` - Добавить 25 недостающих endpoint'ов в AppConfig.swift**
**Цель:** Централизовать все API endpoints

**Действия:**
- В `AppConfig.Endpoint` добавить:
  ```swift
  // AI Assistant (8)
  static let aiAssistantChat = "/api/ai/assistant/chat"
  static let aiAssistantHistory = "/api/ai/assistant/history"
  static let aiAssistantFeedback = "/api/ai/assistant/feedback"
  static let aiAssistantCapabilities = "/api/ai/assistant/capabilities"
  static let aiAssistantAnalyzeThreat = "/api/ai/assistant/analyze_threat"
  static let aiAssistantRecommendations = "/api/ai/assistant/recommendations"
  static let aiAssistantReportIncident = "/api/ai/assistant/report_incident"
  static let aiAssistantSecurityTips = "/api/ai/assistant/security_tips"

  // Network Protection (2)
  static let networkProtectionConfig = "/network-protection/config"
  static let networkProtectionStats = "/network-protection/stats"

  // IoT Security (6)
  static let iotStatus = "/iot/status/{homeId}"
  static let iotDevices = "/iot/devices/{homeId}"
  static let iotThreats = "/iot/threats/{homeId}"
  static let iotDeviceBlock = "/iot/device/{deviceId}/block"
  static let iotScan = "/iot/scan/{homeId}"
  static let iotFix = "/iot/fix/{threatId}"

  // Payments (2)
  static let paymentsQRCreate = "/payments/qr/create"
  static let paymentsQRStatus = "/payments/qr/status/{paymentId}"

  // Auth (1)
  static let authRefresh = "/auth/refresh"
  ```
- Проверить что все endpoints уникальны
- Убедиться что пути соответствуют серверным

**Тестирование:** Все endpoints добавлены, компиляция успешна
**Риски:** Дублирование endpoints, ошибки в путях

#### **8. `replace_hardcoded_strings` - Заменить все жесткие строки в APIService.swift на AppConfig**
**Цель:** Убрать все жестко закодированные "/api/..." строки

**Действия:**
- В `Core/Network/APIService.swift` найти все строки типа:
  ```swift
  networkManager.post(endpoint: "/api/ai/assistant/chat", ...)
  ```
- Заменить на:
  ```swift
  networkManager.post(endpoint: AppConfig.Endpoint.aiAssistantChat, ...)
  ```
- Найти и заменить ВСЕ жесткие строки (25+ замен)
- Проверить компиляцию после каждой замены
- Убедиться что все методы `APIService` используют `AppConfig.Endpoint.*`

**Тестирование:** Нет жестких строк, все через AppConfig, компиляция успешна
**Риски:** Пропуск некоторых строк, ошибки компиляции

#### **9. `fix_mock_notifications` - Заменить loadMockNotifications() на реальные API вызовы**
**Цель:** Показывать реальные уведомления вместо фейковых

**Действия:**
- В `ViewModels/NotificationsViewModel` найти:
  ```swift
  private func loadMockNotifications() { ... } // УДАЛИТЬ
  ```
- Добавить реальный API вызов:
  ```swift
  apiService.getNotifications { [weak self] result in
      switch result {
      case .success(let notifications):
          self?.notifications = notifications.map { notification in
              AppNotification(
                  id: notification.id,
                  icon: self?.getIconForType(notification.type) ?? "🔔",
                  title: notification.title,
                  message: notification.message,
                  timestamp: notification.timestamp,
                  isRead: notification.isRead,
                  kind: self?.getKindForType(notification.type) ?? .info,
                  priority: self?.getPriorityForType(notification.type) ?? .low
              )
          }
          self?.unreadCount = notifications.filter { !$0.isRead }.count
      case .failure(let error):
          self?.errorMessage = "Ошибка загрузки уведомлений: \(error.localizedDescription)"
      }
      self?.isLoading = false
  }
  ```
- Удалить всю mock логику генерации уведомлений
- Протестировать получение уведомлений с сервера

**Тестирование:** Уведомления загружаются с сервера, отображаются корректно
**Риски:** Ошибки API, неправильное маппинг данных

#### **10. `fix_mock_ai_assistant` - Заменить симуляцию AI на реальные API вызовы**
**Цель:** Реальный чат с AI вместо фейковых ответов

**Действия:**
- В `ViewModels/AIAssistantViewModel` найти:
  ```swift
  DispatchQueue.main.asyncAfter { ... } // УДАЛИТЬ
  ```
- Заменить на:
  ```swift
  apiService.sendAIChatMessage(message: currentMessage) { [weak self] result in
      self?.isAITyping = false
      switch result {
      case .success(let response):
          let aiMessage = ChatMessage(text: response.message, isUser: false, timestamp: Date())
          self?.messages.append(aiMessage)
          self?.currentMessage = ""
      case .failure(let error):
          let errorMessage = ChatMessage(text: "Извините, произошла ошибка. Попробуйте позже.", isUser: false, timestamp: Date())
          self?.messages.append(errorMessage)
      }
  }
  ```
- Удалить все симуляции ответов
- Добавить индикатор "AI печатает..."
- Протестировать реальный чат с сервером

**Тестирование:** Сообщения отправляются, приходят реальные ответы AI
**Риски:** Сетевые ошибки, неправильная обработка ответов

#### **11. `fix_mock_device_detail` - Убрать mock данные из DeviceDetailScreen**
**Цель:** Показывать реальную информацию об устройстве

**Действия:**
- В `Screens/22_DeviceDetailScreen` найти:
  ```swift
  // Mock данные - в реальном приложении будут приходить из API
  InfoRow(icon: "phone.fill", title: "Модель", value: "iPhone 13 Pro", color: .green)
  ```
- Заменить на реальный API вызов:
  ```swift
  apiService.getDeviceDetails(deviceId: deviceId) { [weak self] result in
      switch result {
      case .success(let device):
          // Обновить UI с реальными данными
          self?.deviceModel = device.model
          self?.deviceStatus = device.status
          // ...
      case .failure(let error):
          self?.errorMessage = error.localizedDescription
      }
  }
  ```
- Добавить обработку загрузки и ошибок
- Удалить все hardcoded значения
- Протестировать отображение реальных данных

**Тестирование:** Данные устройства загружаются с сервера
**Риски:** Отсутствие API метода, ошибки загрузки

#### **12. `fix_mock_protection_stats` - Убрать mock данные из ProtectionStatsScreen**
**Цель:** Показывать реальную статистику защиты

**Действия:**
- В `Screens/27_ProtectionStatsScreen` найти:
  ```swift
  // Mock data для демонстрации
  protectionStats = ProtectionStatsResponse(
      isActive: true,
      functionsActive: 187,
      threatsBlocked: 2847,
      lastScan: "2026-02-04T12:00:00Z",
      securityScore: 95,
      protectionLevel: "high",
      activeComponents: [
          "VPN", "Антивирус", "Антифишинг", "Родительский контроль",
          "Защита от трекеров", "Мониторинг даркнета", "Защита от мошенничества"
      ]
  )
  ```
- Заменить на реальный API вызов:
  ```swift
  apiService.getProtectionStats { [weak self] result in
      switch result {
      case .success(let stats):
          self?.protectionStats = stats
      case .failure(let error):
          self?.errorMessage = "Ошибка загрузки статистики: \(error.localizedDescription)"
      }
      self?.isLoading = false
  }
  ```
- Удалить все hardcoded статистику
- Добавить локализацию для текстов

**Тестирование:** Статистика загружается с сервера, отображается корректно
**Риски:** Ошибки API, неправильная локализация

#### **13. `fix_mock_family_registration` - Убрать DispatchQueue симуляции из FamilyRegistrationViewModel**
**Цель:** Убрать фейковые задержки в регистрации семьи

**Действия:**
- Найти все `DispatchQueue.main.asyncAfter` в `FamilyRegistrationViewModel`
- Проанализировать нужны ли эти задержки
- Если задержки искусственные - убрать
- Если нужны для UX - заменить на реальные операции
- Проверить что регистрация работает без искусственных задержек
- Убедиться что UI не "замирает" во время операций

**Тестирование:** Регистрация семьи работает плавно без задержек
**Риски:** Нарушение UX, слишком быстрые операции

#### **14. `fix_mock_family_view` - Убрать DispatchQueue симуляции из FamilyViewModel**
**Цель:** Убрать фейковые задержки в управлении семьей

**Действия:**
- Найти `DispatchQueue.main.asyncAfter` в `FamilyViewModel`
- Проанализировать назначение задержки
- Заменить на реальные операции или убрать
- Проверить работу всех семейных функций
- Убедиться что нет искусственных задержек

**Тестирование:** Все семейные операции работают без задержек
**Риски:** Проблемы с синхронизацией UI

#### **15. `fix_mock_main_view` - Убрать DispatchQueue симуляции из MainViewModel**
**Цель:** Убрать фейковые задержки в главном экране

**Действия:**
- Найти все `DispatchQueue.main.asyncAfter` в `MainViewModel`
- Проанализировать нужны ли эти задержки для timeout операций
- Если задержки для timeout - оставить с правильной логикой
- Если искусственные - убрать
- Проверить быстродействие главного экрана

**Тестирование:** Главный экран работает без искусственных задержек
**Риски:** Проблемы с timeout операциями

#### **16. `create_remote_analytics` - Создать RemoteAnalyticsService для реальных данных**
**Цель:** Получать реальную аналитику вместо фейковых цифр

**Действия:**
- Создать `Core/Analytics/RemoteAnalyticsService.swift`:
  ```swift
  final class RemoteAnalyticsService: AnalyticsService {
      private let apiService: APIService

      init(apiService: APIService = .shared) {
          self.apiService = apiService
      }

      func fetchSummary(period: String, filters: AnalyticsFilters) async throws -> AnalyticsSummary {
          // Реальный API вызов
          return try await withCheckedThrowingContinuation { continuation in
              apiService.getAnalyticsSummary(period: period, filters: filters) { result in
                  switch result {
                  case .success(let summary):
                      continuation.resume(returning: summary)
                  case .failure(let error):
                      continuation.resume(throwing: error)
                  }
              }
          }
      }

      // Реализовать остальные методы аналогично
      func fetchSecurityAnalytics(period: String) async throws -> SecurityAnalytics { ... }
      func fetchFamilyAnalytics(period: String) async throws -> FamilyAnalytics { ... }
      func fetchUsageAnalytics(period: String) async throws -> UsageAnalytics { ... }
      func fetchDevicesAnalytics(period: String) async throws -> DevicesAnalytics { ... }
  }
  ```
- Протестировать получение данных с сервера

**Тестирование:** Аналитика загружается с сервера, показывает реальные данные
**Риски:** Ошибки API, неправильная типизация данных

#### **17. `add_service_switching` - Добавить переключение Local/Remote для Analytics**
**Цель:** Использовать LocalAnalyticsService в DEBUG, RemoteAnalyticsService в продакшене

**Действия:**
- В `AnalyticsViewModel` или AppDelegate добавить:
  ```swift
  let analyticsService: AnalyticsService = {
      #if DEBUG && USE_MOCK_ANALYTICS
      return LocalAnalyticsService() // Для разработки
      #else
      return RemoteAnalyticsService() // Для продакшена
      #endif
  }()
  ```
- Протестировать переключение между режимами
- Убедиться что в продакшене используются реальные данные

**Тестирование:** Правильное переключение сервисов в зависимости от режима
**Риски:** Неправильная логика переключения

---

### **🔥 ЭТАП 1: NOTIFICATIONS (Задачи 18-20)**

#### **18. `notifications_apns_setup` - Настроить APNs инфраструктуру (сертификаты)**
**Цель:** Включить push-уведомления через Apple

**Действия:**
- Войти в Apple Developer Account
- Создать App ID с Push Notifications capability
- Сгенерировать development и production сертификаты:
  - Development: для тестирования на устройствах разработчиков
  - Production: для App Store и TestFlight
- Скачать .p12 файлы сертификатов
- Установить сертификаты на сервер (149.154.65.180)
- Настроить provisioning profile с Push Notifications
- Протестировать отправку тестового push через curl:
  ```bash
  curl -v -d '{"aps":{"alert":"Test"}}' \
       -H "apns-topic: com.your.bundle.id" \
       -H "apns-expiration: 1" \
       --cert cert.pem --key key.pem \
       --http2 https://api.sandbox.push.apple.com/3/device/DEVICE_TOKEN
  ```

**Тестирование:** Тестовое push-уведомление приходит на устройство
**Риски:** Неправильные сертификаты, ошибки в настройке сервера

#### **19. `notifications_server_implementation` - Реализовать 16 Notifications endpoint'ов на сервере**
**Цель:** Создать полный API для управления уведомлениями

**Действия:**
- В `api_gateway_server_current.py` добавить:
  ```python
  @app.get("/api/notifications/list")
  async def get_notifications(user_id: str = Depends(get_current_user)):
      # Получить список уведомлений пользователя

  @app.get("/api/notifications/stats")
  async def get_notifications_stats(user_id: str = Depends(get_current_user)):
      # Получить статистику уведомлений

  @app.get("/api/notifications/unread_count")
  async def get_unread_count(user_id: str = Depends(get_current_user)):
      # Получить количество непрочитанных

  @app.post("/api/notifications/mark_read/{notification_id}")
  async def mark_as_read(notification_id: str, user_id: str = Depends(get_current_user)):
      # Отметить уведомление как прочитанное

  @app.delete("/api/notifications/delete/{notification_id}")
  async def delete_notification(notification_id: str, user_id: str = Depends(get_current_user)):
      # Удалить уведомление

  @app.post("/api/notifications/bulk_mark_read")
  async def bulk_mark_read(notification_ids: List[str], user_id: str = Depends(get_current_user)):
      # Массовое прочтение уведомлений

  @app.post("/api/notifications/test")
  async def send_test_notification(user_id: str = Depends(get_current_user)):
      # Отправить тестовое уведомление

  # + остальные 9 endpoint'ов для различных типов уведомлений
  ```
- Реализовать логику для каждого endpoint'а
- Подключить к базе данных уведомлений
- Добавить валидацию прав доступа
- Протестировать все endpoint'ы через Postman

**Тестирование:** Все 16 endpoint'ов работают, возвращают корректные данные
**Риски:** Ошибки в логике, проблемы с базой данных, неправильная аутентификация

#### **20. `notifications_localization` - Добавить локализацию для типов уведомлений**
**Цель:** Перевести типы уведомлений

**Действия:**
- В `LocalizedVersions/Russian.json` добавить:
  ```json
  "notification_type_threat": "Угроза безопасности",
  "notification_type_success": "Успешная защита",
  "notification_type_warning": "Предупреждение",
  "notification_type_info": "Информация",
  "notification_threat_detected": "Обнаружена угроза: {{threat}}",
  "notification_protection_activated": "Защита активирована",
  "notification_scan_completed": "Сканирование завершено",
  "notification_update_available": "Доступно обновление"
  ```
- В `LocalizedVersions/English.json` добавить соответствующие переводы
- Использовать ключи в коде уведомлений:
  ```swift
  let title = localizationManager.localized("notification_type_\(notification.kind.rawValue)")
  ```
- Протестировать отображение на разных языках

**Тестирование:** Все типы уведомлений отображаются на правильном языке
**Риски:** Отсутствие ключей, ошибки в локализации

---

### **🟡 ЭТАП 2: COMPONENTS (Задачи 21-22)**

#### **21. `components_server_implementation` - Реализовать 14 Components endpoint'ов на сервере**
**Цель:** Создать API для управления системными компонентами

**Действия:**
- Добавить 14 endpoint'ов в `api_gateway_server_current.py`:
  ```python
  @app.get("/api/components/health")
  async def get_components_health():
      # Общее здоровье всех компонентов

  @app.get("/api/components/status/{component_id}")
  async def get_component_status(component_id: str):
      # Статус конкретного компонента

  @app.get("/api/components/config/{component_id}")
  async def get_component_config(component_id: str):
      # Конфигурация компонента

  @app.post("/api/components/enable/{component_id}")
  async def enable_component(component_id: str):
      # Включить компонент

  @app.post("/api/components/disable/{component_id}")
  async def disable_component(component_id: str):
      # Отключить компонент

  @app.post("/api/components/restart/{component_id}")
  async def restart_component(component_id: str):
      # Перезапустить компонент

  # + остальные 8 endpoint'ов
  ```
- Реализовать логику управления компонентами
- Добавить аутентификацию для админских функций
- Подключить к системе мониторинга компонентов
- Добавить логирование операций

**Тестирование:** Все endpoint'ы работают, компоненты управляются корректно
**Риски:** Сбои в работе компонентов, неправильная аутентификация

#### **22. `system_components_ui` - Добавить секцию "Системные компоненты" в SettingsScreen**
**Цель:** Создать UI для администрирования компонентов

**Действия:**
- В `SettingsScreen` добавить новую секцию:
  ```swift
  Section(header: Text("system_components_title".localized)) {
      if isAdmin {
          ForEach(components, id: \.id) { component in
              ComponentRow(component: component) {
                  toggleComponent(component)
              }
          }
      }
  }
  ```
- Показывать только для пользователей с ролью admin:
  ```swift
  @AppStorage("user_role") private var userRole = "user"
  var isAdmin: Bool { userRole == "admin" }
  ```
- Добавить toggles для включения/отключения компонентов
- Показывать статус каждого компонента (зеленый/красный индикатор)
- Реализовать вызовы API для управления:
  ```swift
  func toggleComponent(_ component: Component) {
      let endpoint = component.enabled ?
          AppConfig.Endpoint.componentDisable :
          AppConfig.Endpoint.componentEnable

      apiService.post(endpoint: endpoint, body: ["component_id": component.id]) { result in
          // Обработать результат
      }
  }
  ```
- Добавить обработку ошибок и loading состояния
- Добавить pull-to-refresh для обновления статусов

**Тестирование:** Админы видят секцию компонентов, toggles работают, статусы обновляются
**Риски:** Отсутствие проверки прав, ошибки API, неправильное отображение статусов

---

### **🟢 ЭТАП 3: SYSTEM MANAGEMENT (Задача 23)**

#### **23. `system_server_implementation` - Реализовать 11 System Management endpoint'ов на сервере**
**Цель:** Создать API для управления всей системой

**Действия:**
- Добавить 11 endpoint'ов в `api_gateway_server_current.py`:
  ```python
  @app.get("/api/system/health")
  async def get_system_health():
      # Общее здоровье системы

  @app.get("/api/system/info")
  async def get_system_info():
      # Информация о системе (версия, uptime, etc.)

  @app.get("/api/system/logs")
  async def get_system_logs(level: str = "info", limit: int = 100):
      # Системные логи

  @app.post("/api/system/maintenance")
  async def set_maintenance_mode(enabled: bool):
      # Включить/выключить режим обслуживания

  @app.get("/api/system/metrics")
  async def get_system_metrics():
      # Метрики производительности

  @app.post("/api/system/backup")
  async def create_backup():
      # Создать резервную копию

  @app.get("/api/system/backup/status")
  async def get_backup_status():
      # Статус резервного копирования

  # + остальные 4 endpoint'а
  ```
- Реализовать enterprise функции управления
- Добавить мониторинг и алерты
- Обеспечить безопасность админских функций
- Подключить к системам логирования и мониторинга

**Тестирование:** Все endpoint'ы работают, система управляется корректно
**Риски:** Сбои в работе системы, неправильная аутентификация, потеря данных

---

### **🟢 ЭТАП 4: ROADSIDE ASSISTANCE IOS (Задачи 24-27)**

#### **24. `roadside_ios_api` - Добавить 4 Roadside Assistance метода в APIService.swift**
**Цель:** Создать клиентские методы для помощи на дороге

**Действия:**
- В `APIService` добавить методы:
  ```swift
  func callRoadsideAssistance(
      location: CLLocationCoordinate2D,
      vehicleInfo: String,
      completion: @escaping (Result<RoadsideRequest, Error>) -> Void
  ) {
      let request = RoadsideCallRequest(
          latitude: location.latitude,
          longitude: location.longitude,
          vehicleInfo: vehicleInfo
      )
      networkManager.post(
          endpoint: AppConfig.Endpoint.roadsideCall,
          body: request,
          completion: completion
      )
  }

  func getRoadsideAssistanceStatus(
      requestId: String,
      completion: @escaping (Result<RoadsideStatus, Error>) -> Void
  ) {
      networkManager.get(
          endpoint: AppConfig.Endpoint.roadsideStatus.replacingOccurrences(of: "{request_id}", with: requestId),
          completion: completion
      )
  }

  func cancelRoadsideAssistance(
      requestId: String,
      completion: @escaping (Result<Bool, Error>) -> Void
  ) {
      networkManager.post(
          endpoint: AppConfig.Endpoint.roadsideCancel.replacingOccurrences(of: "{request_id}", with: requestId),
          body: EmptyBody(),
          completion: completion
      )
  }

  func getRoadsideAssistanceHistory(
      completion: @escaping (Result<[RoadsideRequest], Error>) -> Void
  ) {
      networkManager.get(
          endpoint: AppConfig.Endpoint.roadsideHistory,
          completion: completion
      )
  }
  ```
- Использовать `AppConfig.Endpoint.roadside*`
- Добавить обработку ошибок
- Протестировать методы

**Тестирование:** Все методы компилируются, работают корректно
**Риски:** Ошибки типизации, неправильные endpoint'ы

#### **25. `roadside_ios_config` - Добавить 4 Roadside Assistance endpoint'а в AppConfig.swift**
**Цель:** Настроить endpoints для помощи на дороге

**Действия:**
- В `AppConfig.Endpoint` добавить:
  ```swift
  static let roadsideCall = "/api/roadside-assistance/call"
  static let roadsideStatus = "/api/roadside-assistance/status/{request_id}"
  static let roadsideCancel = "/api/roadside-assistance/cancel/{request_id}"
  static let roadsideHistory = "/api/roadside-assistance/history"
  ```
- Проверить что пути соответствуют серверным
- Убедиться что endpoints уникальны
- Добавить необходимые модели данных:
  ```swift
  struct RoadsideCallRequest: Codable {
      let latitude: Double
      let longitude: Double
      let vehicleInfo: String
  }

  struct RoadsideRequest: Codable {
      let id: String
      let status: String
      let eta: String?
      let provider: String
  }
  ```

**Тестирование:** Endpoints добавлены, модели созданы
**Риски:** Конфликты с существующими endpoint'ами

#### **26. `roadside_ui` - Добавить Roadside Assistance экран/секцию**
**Цель:** Создать UI для вызова помощи на дороге

**Действия:**
- Создать `RoadsideAssistanceScreen.swift`:
  ```swift
  struct RoadsideAssistanceScreen: View {
      @StateObject private var viewModel = RoadsideAssistanceViewModel()
      @State private var showCallDialog = false

      var body: some View {
          VStack {
              // Карта с текущим местоположением
              MapView(currentLocation: $viewModel.currentLocation)

              // Кнопка вызова помощи
              Button(action: { showCallDialog = true }) {
                  Text("roadside_call_help".localized)
                      .font(.headline)
                      .foregroundColor(.white)
                      .frame(maxWidth: .infinity)
                      .padding()
                      .background(Color.red)
                      .cornerRadius(10)
              }
              .padding()

              // Список активных запросов
              if !viewModel.activeRequests.isEmpty {
                  List(viewModel.activeRequests) { request in
                      RoadsideRequestRow(request: request)
                  }
              }

              // История обращений
              List(viewModel.requestHistory) { request in
                  RoadsideHistoryRow(request: request)
              }
          }
          .sheet(isPresented: $showCallDialog) {
              RoadsideCallDialog(viewModel: viewModel)
          }
      }
  }
  ```
- Реализовать геолокацию для определения места
- Добавить обработку состояний (ожидание, в пути, прибытие)
- Создать диалог для вызова помощи с информацией о ТС

**Тестирование:** Экран работает, геолокация определяется, вызовы API работают
**Риски:** Проблемы с геолокацией, ошибки API, неправильное отображение статусов

#### **27. `roadside_localization` - Добавить локализацию для текстов помощи на дороге**
**Цель:** Перевести все тексты roadside assistance

**Действия:**
- В `LocalizedVersions/Russian.json` добавить:
  ```json
  "roadside_call_help": "Вызвать помощь на дороге",
  "roadside_status_waiting": "Ожидание помощи",
  "roadside_status_en_route": "Помощь в пути",
  "roadside_status_arrived": "Помощь прибыла",
  "roadside_cancel_request": "Отменить запрос",
  "roadside_call_dialog_title": "Вызов помощи на дороге",
  "roadside_vehicle_info": "Информация о транспортном средстве",
  "roadside_location_sharing": "Поделиться местоположением",
  "roadside_emergency_contact": "Экстренный контакт"
  ```
- Добавить английские переводы
- Использовать ключи в `RoadsideAssistanceScreen`
- Протестировать на разных языках

**Тестирование:** Все тексты отображаются корректно на обоих языках
**Риски:** Отсутствие ключей, ошибки в локализации

---

### **🧪 ЭТАП 5: ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ ПРОДАКШЕНА (Задачи 28-60)**

#### **28. `final_mock_verification` - Проверить что все mock данные заменены на реальные API**
**Цель:** Убедиться что приложение использует только реальные данные**

**Чек-лист:**
- [ ] `AppConfig.useMockAPI = false` работает в продакшене
- [ ] Все 25 endpoint'ов добавлены в `AppConfig.Endpoint`
- [ ] Все жесткие строки "/api/..." заменены на `AppConfig.Endpoint.*`
- [ ] `NotificationsViewModel` получает данные с сервера
- [ ] `AIAssistantViewModel` отправляет запросы на сервер
- [ ] `AnalyticsService` использует `RemoteAnalyticsService`
- [ ] Нет `DispatchQueue.main.asyncAfter` симуляций
- [ ] Все ViewModel'ы возвращают реальные данные

**Тестирование:** Приложение работает только с реальными API
**Риски:** Пропущенные mock данные

#### **29. `final_api_integration_test` - Полное интеграционное тестирование с сервером**
**Цель:** Проверить что все API работают корректно**

**Тест-кейсы:**
- [ ] **Аутентификация:** Регистрация семьи → Получение токенов → Валидация JWT
- [ ] **AI Assistant:** Отправка сообщений → Получение ответов → Обработка ошибок
- [ ] **Notifications:** Получение уведомлений → Отметка прочитанными → Удаление
- [ ] **Analytics:** Загрузка статистики → Фильтры → Экспорт данных
- [ ] **Family Management:** Добавление членов → Управление ролями → Чат
- [ ] **Security:** Сканирование → Блокировка угроз → Отчеты
- [ ] **Settings:** Сохранение настроек → Синхронизация → Восстановление

**Тестирование:** Все API работают, данные корректны
**Риски:** Сетевые ошибки, неправильные ответы сервера

#### **30. `final_performance_test` - Тестирование производительности и отклика**
**Цель:** Убедиться что приложение быстрое и отзывчивое**

**Метрики:**
- [ ] **Время запуска:** < 3 секунд
- [ ] **API отклик:** < 500ms для основных запросов
- [ ] **Память:** < 100MB при нормальном использовании
- [ ] **Батарея:** Оптимизированное потребление
- [ ] **Сеть:** Эффективное кэширование и сжатие

**Тестирование:** Все метрики в норме
**Риски:** Низкая производительность, высокий расход ресурсов

#### **31. `final_security_audit` - Аудит безопасности и валидация токенов**
**Цель:** Проверить enterprise уровень безопасности**

**Проверки:**
- [ ] **JWT токены:** Правильная валидация и хранение
- [ ] **Keychain:** Шифрование чувствительных данных
- [ ] **SSL Pinning:** Защита от MITM атак
- [ ] **Input validation:** Все входные данные проверены
- [ ] **Logs:** Нет логирования паролей/токенов
- [ ] **Permissions:** Корректные запросы доступа

**Тестирование:** Безопасность на enterprise уровне
**Риски:** Уязвимости, неправильное хранение данных

#### **32. `final_localization_test` - Тестирование всех переводов и локализации**
**Цель:** Все тексты переведены и работают**

**Проверки:**
- [ ] **Русский язык:** Все тексты на русском
- [ ] **Английский язык:** Fallback работает
- [ ] **Динамические тексты:** Правильные формы числительных
- [ ] **RTL языки:** Поддержка если понадобится
- [ ] **Обновления:** Новые ключи добавлены

**Тестирование:** Все локализации работают корректно
**Риски:** Отсутствующие переводы, неправильная локализация

#### **33. `final_device_compatibility` - Тестирование на разных устройствах и iOS версиях**
**Цель:** Совместимость со всеми устройствами**

**Устройства для тестирования:**
- [ ] **iPhone:** SE, 8, X, 11, 12, 13, 14, 15
- [ ] **iPad:** Mini, Air, Pro (9.7", 11", 12.9")
- [ ] **iOS версии:** 15.0+ (минимум iOS 15)
- [ ] **Ориентации:** Портрет + Ландшафт
- [ ] **Разрешения:** HD, Full HD, 4K

**Тестирование:** Работает на всех устройствах
**Риски:** Проблемы с конкретными моделями устройств

#### **34-60. Оставшиеся задачи финального тестирования**
**Включают:**
- Тестирование offline режима
- Финальный QA чек-лист
- Проверка App Store требований
- Тестирование push-уведомлений
- Проверка платежей
- Итоговое подтверждение готовности

---

## **🎯 КЛЮЧЕВЫЕ ФАЙЛЫ ДЛЯ РАБОТЫ**

### **Критически важные:**
1. `Core/Config/AppConfig.swift` - Конфигурация приложения
2. `Core/Network/APIService.swift` - Все API вызовы
3. `ALADDIN/Info.plist` - Системная конфигурация
4. `Core/Localization/LocalizationManager.swift` - Управление переводами

### **Файлы с mock данными:**
1. `ViewModels/NotificationsViewModel.swift` - Уведомления
2. `ViewModels/AIAssistantViewModel.swift` - AI чат
3. `Screens/22_DeviceDetailScreen.swift` - Детали устройства
4. `Screens/27_ProtectionStatsScreen.swift` - Статистика защиты

### **Серверные файлы:**
1. `api_gateway_server_current.py` - API сервер

---

## **🚀 ПОРЯДОК ВЫПОЛНЕНИЯ**

1. **Начать с Этапа 0** - исправить mock данные (критично!)
2. **Аварийный этап** - AI Assistant
3. **Этап 1** - Notifications
4. **Этапы 2-4** - остальные функции
5. **Этап 5** - финальное тестирование (обязательно!)

---

## **⚠️ ВАЖНЫЕ ПРАВИЛА**

- **Бэкапы перед каждым изменением!**
- **Тестирование после каждого коммита**
- **Использовать AppConfig.Endpoint вместо жестких строк**
- **Все тексты через localizationManager**
- **Проверять безопасность всех изменений**

---

**Этот файл содержит полную инструкцию для выполнения всех 60 задач ALADDIN iOS проекта!** 🎯</content>
</xai:function_call/>\
<xai:function_call name="run_terminal_cmd">
<parameter name="command">ls -lh ALADDIN_IMPLEMENTATION_TASKS.md