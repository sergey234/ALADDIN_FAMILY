# 🎯 ПОЛНАЯ ДОКУМЕНТАЦИЯ СИСТЕМЫ ЛОГИРОВАНИЯ ALADDIN

## 📋 ОБЗОР СИСТЕМЫ

Система логирования MasterLogger предоставляет комплексное решение для отслеживания всех действий пользователей и системных событий в приложении ALADDIN.

**Версия:** 1.0
**Дата создания:** 24 февраля 2026
**Статус:** Production Ready

---

## 🏗️ АРХИТЕКТУРА СИСТЕМЫ

### Основные компоненты:

#### 1. **MasterLogger** (`Core/Utilities/MasterLogger.swift`)
- **Единый фасад** для всех типов логирования
- **6 уровней логирования:** TRACE, DEBUG, INFO, WARN, ERROR, FATAL
- **7 категорий:** SYSTEM, UI, NETWORK, BUSINESS, SECURITY, PERFORMANCE, ERROR
- **Три способа вывода:**
  - Xcode Console (DEBUG mode)
  - Visual Logger (на экране приложения)
  - SettingsDiagnosticsLogger (для продакшена)

#### 2. **SettingsDiagnosticsLogger** (`Core/Diagnostics/SettingsDiagnosticsLogger.swift`)
- **Детальное логирование** с экспортом в файл
- **Thread-safe** операции
- **Маскировка чувствительных данных**

#### 3. **VisualLogger** (`Core/Utilities/VisualLogger.swift`)
- **Отображение логов на экране** (только DEBUG)
- **Цветовое кодирование** по уровням
- **Автоматическая очистка** (50 записей макс)

#### 4. **NetworkLogger** (`Core/Network/NetworkLogger.swift`)
- **Специализированное логирование** HTTP запросов
- **Автоматическая маскировка** токенов и паролей

---

## 🎯 ИСПОЛЬЗОВАНИЕ СИСТЕМЫ

### Базовое использование:

```swift
import SwiftUI

// 1. ДОБАВИТЬ В КАЖДЫЙ ФАЙЛ:
private let logger = MasterLogger.shared

struct MyView: View {
    var body: some View {
        Button("Нажми меня") {
            // 2. ЛОГИРОВАТЬ ДЕЙСТВИЯ:
            logger.buttonTap("Нажми меня", screen: "MyView")
        }
    }
}
```

### Категории логирования:

```swift
// UI действия пользователя
logger.buttonTap("ButtonName", screen: "ScreenName")
logger.toggleChanged("SettingName", newValue: true, screen: "ScreenName")
logger.navigation(from: "ScreenA", to: "ScreenB")

// Бизнес-логика
logger.business("User logged in successfully")
logger.business("Payment processed: $29.99")

// Системные события
logger.screenLoad("MainScreen")
logger.business("Initializing service")

// Ошибки
logger.error("Network request failed", error: error)
logger.fatal("Critical system error")

// Сетевые запросы (автоматически логируются в NetworkManager)
logger.network("API call started")
```

---

## 🔒 БЕЗОПАСНОСТЬ И PRODUCTION

### ✅ Автоматическая защита:

#### 1. **Маскировка чувствительных данных:**
```swift
// HTTP заголовки автоматически очищаются:
Authorization: Bearer abc123 → Authorization: <redacted>
```

#### 2. **Production режим:**
```swift
// В DEBUG: все логи
logger.business("Debug info") // ✅ ВЫВОДИТСЯ

// В RELEASE: только критичные логи
logger.error("Error occurred") // ✅ ВЫВОДИТСЯ
logger.business("Normal operation") // ❌ НЕ ВЫВОДИТСЯ
```

#### 3. **Исключения из логирования:**
- ✅ Пароли и токены
- ✅ Личные данные пользователей
- ✅ Финансовая информация
- ✅ Медицинские данные

---

## 📊 ПРИМЕРЫ ЛОГОВ

### Xcode Console (DEBUG):
```
🔍 [INFO] [UI] [SettingsScreen:125] Button tapped: Biometric Toggle on Settings
🔄 [INFO] [BUSINESS] [MainViewModel:45] Loading dashboard data
➡️ [INFO] [NETWORK] [NetworkManager:234] POST https://api.aladdin.family/login headers=[...]
🚨 [FATAL] [BUSINESS] [ElderlyInterfaceViewModel:28] EMERGENCY: Elderly triggered SOS
```

### Visual Logger (на экране):
```
┌─────────────────────────────────────┐
│     📋 ЛОГИ                         │
├─────────────────────────────────────┤
│ 🔍 [INFO] Screen loaded: MainScreen  │
│ 🔘 [UI] Button tapped: Settings      │
│ 🧭 [UI] Navigation: Main → Settings  │
│ ✅ [BUSINESS] User profile loaded    │
└─────────────────────────────────────┘
```

---

## 🎯 ПОЛНЫЙ СПИСОК ИНТЕГРИРОВАННЫХ КОМПОНЕНТОВ

### ✅ Основные экраны (6/6):
- [x] **SettingsScreen** - тумблеры, кнопки, модалы
- [x] **FamilyScreen** - управление семьей, участники
- [x] **NetworkProtectionScreen** - настройки защиты
- [x] **AnalyticsScreen** - аналитика и графики
- [x] **ProfileScreen** - профиль пользователя
- [x] **MainScreen** - главный экран

### ✅ ViewModels бизнес-логики (10/15):
- [x] **MainViewModel** - основная логика приложения
- [x] **FamilyViewModel** - управление семьей
- [x] **ParentalControlViewModel** - родительский контроль
- [x] **ChildInterfaceViewModel** - детский интерфейс
- [x] **ElderlyInterfaceViewModel** - интерфейс пожилых
- [x] **NotificationsViewModel** - push уведомления
- [x] **ProfileViewModel** - профиль пользователя
- [x] **AnalyticsViewModel** - аналитика данных
- [x] **PaymentQRViewModel** - платежи и QR коды
- [x] **TariffsViewModel** - тарифы и покупки

### ✅ Core сервисы инфраструктуры (9/9):
- [x] **UserProfileManager** - менеджер профиля
- [x] **StoreManager** - App Store покупки
- [x] **NotificationManager** - push уведомления
- [x] **AnalyticsManager** - аналитика событий
- [x] **AntivirusManager** - антивирусное сканирование
- [x] **NetworkProtectionManager** - сетевая защита
- [x] **PerformanceMonitor** - мониторинг производительности
- [x] **LocalizationManager** - локализация
- [x] **APIService** - сетевые запросы

### ✅ Дополнительные ViewModels (4+):
- [x] **AIAssistantViewModel** - AI чат
- [x] **OnboardingViewModel** - онбординг
- [x] **SupportViewModel** - поддержка
- [x] **FamilyRegistrationViewModel** - регистрация семьи

---

## 🚀 РАСШИРЕНИЕ СИСТЕМЫ

### Добавление логирования в новый файл:

```swift
// 1. Импорт (если нужно)
import SwiftUI

// 2. ДОБАВИТЬ LOGGER (ОБЯЗАТЕЛЬНО)
private let logger = MasterLogger.shared

class MyNewViewModel: ObservableObject {

    // 3. ЛОГИРОВАТЬ ИНИЦИАЛИЗАЦИЮ
    init() {
        logger.business("Initializing MyNewViewModel")
    }

    // 4. ЛОГИРОВАТЬ ВАЖНЫЕ ДЕЙСТВИЯ
    func importantAction() {
        logger.business("User performed important action")
        // ... код действия
    }

    // 5. ЛОГИРОВАТЬ ОШИБКИ
    func riskyOperation() {
        do {
            try performRiskyTask()
            logger.business("Risky operation completed successfully")
        } catch {
            logger.error("Risky operation failed", error: error)
        }
    }
}
```

### Добавление нового типа логов:

```swift
extension MasterLogger {
    func customLog(_ message: String, function: String = #function, file: String = #file, line: Int = #line) {
        log(.info, category: .business, message: message, function: function, file: file, line: line)
    }
}

// Использование:
logger.customLog("Custom business event")
```

---

## 🔧 КОНФИГУРАЦИЯ

### Включение/выключение Visual Logger:

```swift
// В коде приложения:
MasterLogger.shared.setVisualLogging(enabled: true)  // Включить
MasterLogger.shared.setVisualLogging(enabled: false) // Выключить
```

### Уровни логирования:

```swift
// В DEBUG: TRACE, DEBUG, INFO, WARN, ERROR, FATAL
// В RELEASE: INFO, WARN, ERROR, FATAL

// Изменить уровень (если нужно):
MasterLogger.shared.maxLogLevel = .warn // Только WARN и выше
```

---

## 📈 МОНИТОРИНГ И АНАЛИТИКА

### Типы отслеживаемых событий:

#### 🔍 **Пользовательские действия:**
- Навигация между экранами
- Нажатия кнопок и тумблеров
- Заполнение форм
- Взаимодействие с контентом

#### 💰 **Бизнес-метрики:**
- Покупки и платежи
- Регистрации пользователей
- Завершения онбординга
- Использование премиум-функций

#### 🔒 **Безопасность:**
- Попытки входа/выхода
- Изменение настроек безопасности
- Детекция угроз
- Экстренные ситуации

#### 📊 **Производительность:**
- Время загрузки экранов
- Длительность сетевых запросов
- Использование памяти
- FPS и анимации

---

## 🎯 РЕКОМЕНДАЦИИ ПО ИСПОЛЬЗОВАНИЮ

### ✅ Логировать:
- Все действия пользователей
- Важные бизнес-события
- Ошибки и исключения
- Сетевые запросы
- Изменения состояния

### ⚠️ НЕ логировать:
- Чувствительные данные (пароли, токены, персональные данные)
- Временные значения переменных
- Отладочную информацию низкого уровня
- Повторяющиеся события (в циклах)

### 🎨 Соглашения по сообщениям:
- **UI действия:** "Button tapped: [Name] on [Screen]"
- **Бизнес-логика:** "User [action] [object]"
- **Ошибки:** "Failed to [action]: [reason]"
- **Сеть:** "API [method] [endpoint]"

---

## 🏆 ПРЕИМУЩЕСТВА СИСТЕМЫ

### 🔍 **Отладка:**
- Быстрое нахождение багов
- Отслеживание последовательности действий
- Диагностика проблем пользователей

### 📊 **Аналитика:**
- Понимание поведения пользователей
- Оптимизация UX/UI
- Метрики использования функций

### 🔒 **Безопасность:**
- Мониторинг подозрительной активности
- Аудит важных операций
- Детекция инцидентов

### 🚀 **Разработка:**
- Улучшенная поддержка кода
- Быстрое тестирование
- Документирование поведения

---

## 📞 ПОДДЕРЖКА И ОБНОВЛЕНИЯ

### Контакты:
- **Ответственный:** iOS Development Team
- **Документация:** `LOGGING_SYSTEM_DOCUMENTATION.md`
- **Статус:** `LOGGING_IMPLEMENTATION_STATUS.md`

### Обновления:
- Регулярно проверять новые версии MasterLogger
- Добавлять логирование в новые компоненты
- Обновлять документацию при изменениях

---

*Документация создана: 24 февраля 2026*
*Версия системы: 1.0*
*Статус: Production Ready* ✨