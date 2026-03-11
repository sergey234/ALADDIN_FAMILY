# 📋 BUILD 104: ДЕТАЛЬНЫЙ TODO ЛИСТ ИСПРАВЛЕНИЙ

**Дата создания:** 2026-03-11  
**Build:** 104  
**Статус:** 🔴 **КРИТИЧЕСКАЯ ПРОБЛЕМА - ДВА РАЗНЫХ КРАША**

---

## 🎯 ОБЗОР ПРОБЛЕМ

### Проблема 1: Краш при переходе на страницу (Thread 0 - main thread)
- **Когда:** При первом переходе на страницу "Защита АЛАДДИН"
- **Причина:** `Task {}` в `NetworkProtectionViewModel.init()` вызывает пересоздание View
- **Решение:** Убрать `Task {}` из `init()`, загружать статусы в `.onAppear`

### Проблема 2: Краш при переключении тумблеров (Thread 2 - background thread)
- **Когда:** При переключении тумблеров на странице
- **Причина:** Dictionary создается в background thread в `toggleComponent()`
- **Решение:** Обернуть вызовы аналитики в `await MainActor.run {}`

---

## 📋 ДЕТАЛЬНЫЙ TODO ЛИСТ

### ✅ ЭТАП 1: ИСПРАВЛЕНИЕ КРАША ПРИ ПЕРЕХОДЕ НА СТРАНИЦУ (7 задач)

#### Задача 1.1: Убрать `Task {}` из `NetworkProtectionViewModel.init()`
- **Файл:** `ViewModels/NetworkProtectionViewModel.swift`
- **Строки:** 61-63
- **Текущий код:**
  ```swift
  init(...) {
      // ...
      // Загружаем статусы компонентов при инициализации
      Task {  // ❌ УБРАТЬ!
          await loadComponentStatuses()
      }
  }
  ```
- **Исправленный код:**
  ```swift
  init(...) {
      self.statusService = statusService
      self.configurationService = configurationService
      self.retryManager = retryManager
      // ✅ УБРАЛИ Task {} из init()
  }
  ```
- **Приоритет:** 🔴 Критический
- **Статус:** ⏳ Ожидает выполнения

---

#### Задача 1.2: Убрать `Task { @MainActor in }` из `updateStatusForComponent()`
- **Файл:** `ViewModels/NetworkProtectionViewModel.swift`
- **Строка:** 242
- **Текущий код:**
  ```swift
  private func updateStatusForComponent(componentId: String, isEnabled: Bool) {
      Task { @MainActor in  // ❌ УБРАТЬ!
          switch componentId {
          case "crash_detection_agent":
              crashDetectionEnabled = isEnabled
          // ...
          }
      }
  }
  ```
- **Исправленный код:**
  ```swift
  private func updateStatusForComponent(componentId: String, isEnabled: Bool) {
      // ✅ УБРАЛИ Task { @MainActor in } - метод уже на @MainActor
      switch componentId {
      case "crash_detection_agent":
          crashDetectionEnabled = isEnabled
      case "roadside_assistance_agent":
          roadsideAssistanceEnabled = isEnabled
      case "emergency_response_bot":
          emergencyResponseEnabled = isEnabled
      case "emergency_event_manager":
          emergencyEventEnabled = isEnabled
      case "phishing_protection_agent":
          phishingProtectionEnabled = isEnabled
      case "malware_detection_agent":
          malwareDetectionEnabled = isEnabled
      case "mobile_security_agent":
          mobileSecurityEnabled = isEnabled
      case "network_security_agent":
          networkSecurityEnabled = isEnabled
      case "incident_response_agent":
          incidentResponseEnabled = isEnabled
      case "password_security_agent":
          passwordSecurityEnabled = isEnabled
      default:
          break
      }
  }
  ```
- **Приоритет:** 🔴 Критический
- **Статус:** ⏳ Ожидает выполнения

---

#### Задача 1.3: Убрать `await MainActor.run {}` из `loadDemoModeStatuses()`
- **Файл:** `ViewModels/NetworkProtectionViewModel.swift`
- **Строка:** 94
- **Текущий код:**
  ```swift
  private func loadDemoModeStatuses(...) async {
      for item in prioritizedItems {
          let isEnabled = UserDefaults.standard.bool(forKey: userDefaultsKey)
          
          await MainActor.run {  // ❌ УБРАТЬ!
              self.updateStatusForComponent(componentId: item.id, isEnabled: isEnabled)
          }
      }
  }
  ```
- **Исправленный код:**
  ```swift
  private func loadDemoModeStatuses(...) async {
      // ✅ УБРАЛИ await MainActor.run {} - метод уже на @MainActor
      for item in prioritizedItems {
          let isEnabled = UserDefaults.standard.bool(forKey: userDefaultsKey)
          self.updateStatusForComponent(componentId: item.id, isEnabled: isEnabled)
      }
  }
  ```
- **Приоритет:** 🔴 Критический
- **Статус:** ⏳ Ожидает выполнения

---

#### Задача 1.4: Убрать `await MainActor.run {}` из `loadProductionModeStatuses()`
- **Файл:** `ViewModels/NetworkProtectionViewModel.swift`
- **Строка:** 107
- **Текущий код:**
  ```swift
  private func loadProductionModeStatuses(...) async {
      for item in prioritizedItems {
          do {
              let status = try await APIService.shared.getComponentStatus(componentId: item.id)
              await MainActor.run {  // ❌ УБРАТЬ!
                  self.updateStatusForComponent(componentId: item.id, status: status)
              }
          } catch {
              // ...
          }
      }
  }
  ```
- **Исправленный код:**
  ```swift
  private func loadProductionModeStatuses(...) async {
      // ✅ УБРАЛИ await MainActor.run {} - метод уже на @MainActor
      for item in prioritizedItems {
          do {
              let status = try await APIService.shared.getComponentStatus(componentId: item.id)
              self.updateStatusForComponent(componentId: item.id, status: status)
          } catch {
              print("⚠️ Ошибка загрузки статуса для \(item.id): \(error.localizedDescription)")
          }
      }
  }
  ```
- **Приоритет:** 🔴 Критический
- **Статус:** ⏳ Ожидает выполнения

---

#### Задача 1.5: Добавить флаг `hasLoadedStatuses` в `NetworkProtectionViewModel`
- **Файл:** `ViewModels/NetworkProtectionViewModel.swift`
- **Место:** После строки 47 (после `@Published var errorMessage: String?`)
- **Добавить:**
  ```swift
  // ✅ BUILD 104: Защита от повторной загрузки статусов
  private var hasLoadedStatuses = false
  ```
- **Изменить `loadComponentStatuses()`:**
  ```swift
  func loadComponentStatuses() async {
      // ✅ BUILD 104: Защита от повторной загрузки
      guard !hasLoadedStatuses else {
          print("⚠️ NetworkProtectionViewModel: Статусы уже загружены, пропускаем")
          return
      }
      
      hasLoadedStatuses = true
      isLoading = true
      defer { isLoading = false }
      
      // ... остальной код
  }
  ```
- **Приоритет:** 🔴 Критический
- **Статус:** ⏳ Ожидает выполнения

---

#### Задача 1.6: Переместить загрузку статусов в `.onAppear` в `NetworkProtectionScreen`
- **Файл:** `Screens/03_NetworkProtectionScreen.swift`
- **Строки:** 365-371
- **Добавить флаг:**
  ```swift
  @State private var hasLoadedStatuses = false
  ```
- **Изменить `.onAppear`:**
  ```swift
  .onAppear {
      // ✅ BUILD 104: Загружаем статусы только один раз
      if !hasLoadedStatuses {
          hasLoadedStatuses = true
          Task {
              await viewModel.loadComponentStatuses()
          }
      }
      
      // Отследить просмотр экрана с компонентами (с защитой)
      if !hasTrackedScreenView {
          hasTrackedScreenView = true
          ComponentAnalytics.shared.trackComponentScreenView(
              screenName: "NetworkProtectionScreen",
              componentCount: 10
          )
      }
  }
  ```
- **Приоритет:** 🔴 Критический
- **Статус:** ⏳ Ожидает выполнения

---

#### Задача 1.7: Добавить защиту от повторного вызова в `.onAppear` для `trackComponentScreenView()`
- **Файл:** `Screens/03_NetworkProtectionScreen.swift`
- **Строки:** 365-371
- **Добавить флаг:**
  ```swift
  @State private var hasTrackedScreenView = false
  ```
- **Изменить `.onAppear`:** (см. Задачу 1.6)
- **Приоритет:** 🔴 Критический
- **Статус:** ⏳ Ожидает выполнения

---

### ✅ ЭТАП 2: ИСПРАВЛЕНИЕ КРАША ПРИ ПЕРЕКЛЮЧЕНИИ ТУМБЛЕРОВ (4 задачи)

#### Задача 2.1: Обернуть `componentAnalytics.trackComponentToggle()` в `await MainActor.run {}`
- **Файл:** `ViewModels/NetworkProtectionViewModel.swift`
- **Строки:** 320-325
- **Текущий код:**
  ```swift
  // Успешное обновление
  // ✅ BUILD 102: Автоматически на main thread благодаря @MainActor
  componentAnalytics.trackComponentToggle(
      componentId: componentId,
      enabled: newValue
  )
  ```
- **Исправленный код:**
  ```swift
  // Успешное обновление
  // ✅ BUILD 104: Явно оборачиваем в await MainActor.run {} для гарантии main thread
  await MainActor.run {
      componentAnalytics.trackComponentToggle(
          componentId: componentId,
          enabled: newValue
      )
  }
  ```
- **Приоритет:** 🔴 Критический
- **Статус:** ⏳ Ожидает выполнения

---

#### Задача 2.2: Обернуть `componentAnalytics.trackComponentError()` в `await MainActor.run {}`
- **Файл:** `ViewModels/NetworkProtectionViewModel.swift`
- **Строка:** 340
- **Текущий код:**
  ```swift
  // Отследить ошибку
  // ✅ BUILD 102: Автоматически на main thread благодаря @MainActor
  componentAnalytics.trackComponentError(componentId: componentId, error: error)
  ```
- **Исправленный код:**
  ```swift
  // Отследить ошибку
  // ✅ BUILD 104: Явно оборачиваем в await MainActor.run {} для гарантии main thread
  await MainActor.run {
      componentAnalytics.trackComponentError(componentId: componentId, error: error)
  }
  ```
- **Приоритет:** 🔴 Критический
- **Статус:** ⏳ Ожидает выполнения

---

#### Задача 2.3: Обернуть `toastManager.showSuccess/showError` в `await MainActor.run {}`
- **Файл:** `ViewModels/NetworkProtectionViewModel.swift`
- **Строки:** 327-331, 341
- **Текущий код:**
  ```swift
  if AppConfig.authToken == nil {
      toastManager.showSuccess("Компонент обновлен (демо режим)")
  } else {
      toastManager.showSuccess("Компонент обновлен")
  }
  
  // В catch блоке:
  toastManager.showError("Ошибка: \(error.localizedDescription)")
  ```
- **Исправленный код:**
  ```swift
  await MainActor.run {
      if AppConfig.authToken == nil {
          toastManager.showSuccess("Компонент обновлен (демо режим)")
      } else {
          toastManager.showSuccess("Компонент обновлен")
      }
  }
  
  // В catch блоке:
  await MainActor.run {
      toastManager.showError("Ошибка: \(error.localizedDescription)")
  }
  ```
- **Приоритет:** 🔴 Критический
- **Статус:** ⏳ Ожидает выполнения

---

#### Задача 2.4: Убрать `await MainActor.run {}` из `toggleComponent()` для UserDefaults
- **Файл:** `ViewModels/NetworkProtectionViewModel.swift`
- **Строка:** 314
- **Текущий код:**
  ```swift
  // Демо режим: сохраняем локально в UserDefaults
  // ✅ BUILD 102: UserDefaults.standard.set() на main thread
  await MainActor.run {
      let userDefaultsKey = "demo_component_\(componentId)_enabled"
      UserDefaults.standard.set(newValue, forKey: userDefaultsKey)
  }
  ```
- **Исправленный код:**
  ```swift
  // Демо режим: сохраняем локально в UserDefaults
  // ✅ BUILD 104: УБРАЛИ await MainActor.run {} - метод уже на @MainActor
  let userDefaultsKey = "demo_component_\(componentId)_enabled"
  UserDefaults.standard.set(newValue, forKey: userDefaultsKey)
  ```
- **Приоритет:** 🔴 Критический
- **Статус:** ⏳ Ожидает выполнения

---

### ✅ ЭТАП 3: ТЕСТИРОВАНИЕ (4 задачи)

#### Задача 3.1: Скомпилировать проект
- **Действие:** Запустить компиляцию проекта
- **Проверка:** Убедиться, что нет ошибок компиляции
- **Приоритет:** 🟡 Высокий
- **Статус:** ⏳ Ожидает выполнения

---

#### Задача 3.2: Протестировать переход на страницу
- **Действие:** Перейти на страницу "Защита АЛАДДИН"
- **Проверка:** Убедиться, что нет краша при первом переходе
- **Проверка:** Убедиться, что нет краша при повторном переходе
- **Приоритет:** 🟡 Высокий
- **Статус:** ⏳ Ожидает выполнения

---

#### Задача 3.3: Протестировать переключение тумблеров
- **Действие:** Переключить каждый тумблер на странице
- **Проверка:** Убедиться, что нет краша при переключении
- **Проверка:** Убедиться, что тумблеры работают корректно
- **Проверка:** Проверить работу в demo режиме
- **Проверка:** Проверить работу в production режиме
- **Приоритет:** 🟡 Высокий
- **Статус:** ⏳ Ожидает выполнения

---

#### Задача 3.4: Протестировать на реальном устройстве
- **Действие:** Запустить приложение на реальном устройстве
- **Проверка:** Протестировать все сценарии использования
- **Проверка:** Убедиться, что нет крашей
- **Приоритет:** 🟡 Высокий
- **Статус:** ⏳ Ожидает выполнения

---

## 📊 СВОДНАЯ ТАБЛИЦА ПРОГРЕССА

| № | Задача | Файл | Строки | Приоритет | Статус |
|---|--------|------|--------|-----------|--------|
| 1.1 | Убрать Task {} из init() | NetworkProtectionViewModel.swift | 61-63 | 🔴 Критический | ⏳ Ожидает |
| 1.2 | Убрать Task { @MainActor in } из updateStatusForComponent() | NetworkProtectionViewModel.swift | 242 | 🔴 Критический | ⏳ Ожидает |
| 1.3 | Убрать await MainActor.run {} из loadDemoModeStatuses() | NetworkProtectionViewModel.swift | 94 | 🔴 Критический | ⏳ Ожидает |
| 1.4 | Убрать await MainActor.run {} из loadProductionModeStatuses() | NetworkProtectionViewModel.swift | 107 | 🔴 Критический | ⏳ Ожидает |
| 1.5 | Добавить флаг hasLoadedStatuses | NetworkProtectionViewModel.swift | после 47 | 🔴 Критический | ⏳ Ожидает |
| 1.6 | Переместить загрузку в .onAppear | NetworkProtectionScreen.swift | 365-371 | 🔴 Критический | ⏳ Ожидает |
| 1.7 | Добавить защиту в .onAppear для trackComponentScreenView() | NetworkProtectionScreen.swift | 365-371 | 🔴 Критический | ⏳ Ожидает |
| 2.1 | Обернуть trackComponentToggle() в await MainActor.run {} | NetworkProtectionViewModel.swift | 322 | 🔴 Критический | ⏳ Ожидает |
| 2.2 | Обернуть trackComponentError() в await MainActor.run {} | NetworkProtectionViewModel.swift | 340 | 🔴 Критический | ⏳ Ожидает |
| 2.3 | Обернуть toastManager в await MainActor.run {} | NetworkProtectionViewModel.swift | 328-331, 341 | 🔴 Критический | ⏳ Ожидает |
| 2.4 | Убрать await MainActor.run {} для UserDefaults | NetworkProtectionViewModel.swift | 314 | 🔴 Критический | ⏳ Ожидает |
| 3.1 | Скомпилировать проект | - | - | 🟡 Высокий | ⏳ Ожидает |
| 3.2 | Протестировать переход на страницу | - | - | 🟡 Высокий | ⏳ Ожидает |
| 3.3 | Протестировать переключение тумблеров | - | - | 🟡 Высокий | ⏳ Ожидает |
| 3.4 | Протестировать на реальном устройстве | - | - | 🟡 Высокий | ⏳ Ожидает |

---

## 🎯 ИТОГОВАЯ СТАТИСТИКА

- **Всего задач:** 15
- **Критических задач:** 11
- **Высокоприоритетных задач:** 4
- **Файлов для изменения:** 2
  - `ViewModels/NetworkProtectionViewModel.swift` (10 задач)
  - `Screens/03_NetworkProtectionScreen.swift` (2 задачи)

---

## ✅ ПРОВЕРКА ПОЛНОТЫ ПЛАНА

### Проверено:
- ✅ Все причины краша при переходе на страницу учтены
- ✅ Все причины краша при переключении тумблеров учтены
- ✅ Все файлы, которые нужно изменить, указаны
- ✅ Все строки кода, которые нужно изменить, указаны
- ✅ Все исправления имеют приоритет
- ✅ Все исправления имеют статус отслеживания

### Что будет исправлено:
- ✅ Краш при переходе на страницу (main thread)
- ✅ Краш при переключении тумблеров (background thread)
- ✅ Рекурсия в `init()`
- ✅ Рекурсия в `updateStatusForComponent()`
- ✅ Рекурсия в `toggleComponent()`
- ✅ Dictionary создается на main thread

---

**ГОТОВ К ВЫПОЛНЕНИЮ!** 🚀
