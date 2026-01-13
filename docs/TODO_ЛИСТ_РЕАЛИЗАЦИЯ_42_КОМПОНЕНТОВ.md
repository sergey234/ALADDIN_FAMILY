# ✅ TODO ЛИСТ: РЕАЛИЗАЦИЯ 42 КОМПОНЕНТОВ

**Дата создания:** 13 января 2026  
**Статус:** 🟡 В РАБОТЕ  
**Прогресс:** 0/42 компонентов (0%)

---

## 📋 ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ

- ✅ Отмечайте выполненные пункты как `- [x]`
- ⬜ Невыполненные пункты оставляйте как `- [ ]`
- После выполнения пункта зачеркивайте его: `~~- [x]~~`
- Обновляйте прогресс в заголовке

---

## 🎯 ЭТАП 0: ПОДГОТОВКА И ИНФРАСТРУКТУРА

### 0.1 Создание базовой структуры файлов

- [ ] **Создать директории для новых файлов**
  - [ ] `ViewModels/` - проверить существование
  - [ ] `Core/Components/` - создать если нет
  - [ ] `Core/Managers/` - создать если нет
  - [ ] `Core/Models/` - проверить существование
  - [ ] `Shared/Components/` - проверить существование
  - [ ] `Shared/Utils/` - создать если нет
  - [ ] `Tests/ViewModels/` - создать если нет
  - [ ] `Tests/Services/` - создать если нет
  - [ ] `LocalizedStrings/ru.lproj/` - создать если нет
  - [ ] `LocalizedStrings/en.lproj/` - создать если нет

**Как делать:**
```bash
mkdir -p Core/Components Core/Managers Shared/Utils Tests/ViewModels Tests/Services
mkdir -p LocalizedStrings/ru.lproj LocalizedStrings/en.lproj
```

---

### 0.2 Создание базовых моделей данных

- [ ] **Создать `Core/Models/ComponentStatus.swift`**
  - [ ] Структура `ComponentStatus` с полями:
    - `componentId: String`
    - `isEnabled: Bool`
    - `lastUpdate: Date?`
    - `configuration: ComponentConfiguration?`
  - [ ] Реализовать `Codable` протокол
  - [ ] Добавить инициализаторы

**Пример кода:**
```swift
struct ComponentStatus: Codable, Identifiable {
    let id: String
    let componentId: String
    let isEnabled: Bool
    let lastUpdate: Date?
    let configuration: ComponentConfiguration?
    
    init(componentId: String, isEnabled: Bool, lastUpdate: Date? = nil, configuration: ComponentConfiguration? = nil) {
        self.id = UUID().uuidString
        self.componentId = componentId
        self.isEnabled = isEnabled
        self.lastUpdate = lastUpdate
        self.configuration = configuration
    }
}
```

- [ ] **Создать `Core/Models/ComponentConfiguration.swift`**
  - [ ] Структура для хранения настроек компонентов
  - [ ] Поддержка разных типов конфигураций

- [ ] **Создать `Core/Models/ComponentError.swift`**
  - [ ] Enum для типов ошибок
  - [ ] Локализованные сообщения об ошибках

---

### 0.3 Создание сервисов

- [ ] **Создать `Core/Services/ComponentStatusService.swift`**
  - [ ] Singleton паттерн
  - [ ] Метод `getStatus(for:priority:)` с ленивой загрузкой
  - [ ] Метод `loadCriticalComponentsStatus()` для batch загрузки
  - [ ] Кэширование с TTL (5 минут)
  - [ ] Background refresh
  - [ ] Использовать Combine для реактивности

**Как делать:**
1. Создать класс `ComponentStatusService`
2. Реализовать кэширование в памяти
3. Интегрировать с `APIService`
4. Добавить поддержку приоритетов (critical, normal, low)

- [ ] **Создать `Core/Services/ComponentConfigurationService.swift`**
  - [ ] Методы для сохранения/загрузки конфигураций
  - [ ] Валидация конфигураций

- [ ] **Создать `Core/Services/ComponentCacheService.swift`**
  - [ ] Сохранение в UserDefaults
  - [ ] TTL для кэша
  - [ ] Методы очистки кэша

---

### 0.4 Создание утилит

- [ ] **Создать `Shared/Utils/RetryManager.swift`**
  - [ ] Метод `retry(maxAttempts:delay:operation:)`
  - [ ] Экспоненциальная задержка
  - [ ] Поддержка Combine

- [ ] **Создать `Shared/Utils/ToastManager.swift`**
  - [ ] ObservableObject для управления toast
  - [ ] Методы `showSuccess`, `showError`, `showInfo`
  - [ ] SwiftUI компонент `ToastView`

---

### 0.5 Расширение APIService

- [ ] **Расширить `Core/Network/APIService.swift`**
  - [ ] Добавить методы для всех 42 компонентов:
    - `enableCrashDetection(completion:)`
    - `disableCrashDetection(completion:)`
    - `getCrashDetectionStatus(completion:)`
    - Аналогично для всех остальных компонентов
  - [ ] Использовать Combine версии методов (для ViewModels)
  - [ ] Обработка ошибок

**Как делать:**
1. Для каждого компонента добавить 3 метода: enable, disable, getStatus
2. Использовать существующий паттерн из APIService
3. Endpoints должны следовать паттерну: `/api/agents/{component-id}/enable`

---

### 0.6 Локализация

- [ ] **Создать `LocalizedStrings/ru.lproj/Localizable.strings`**
  - [ ] Добавить все ключи для 42 компонентов:
    - `crash_detection_title` = "Обнаружение аварий"
    - `crash_detection_description` = "Автоматическое обнаружение аварий"
    - Аналогично для всех компонентов
  - [ ] Ключи для кнопок: `button_settings`, `button_generator`, `button_contact`
  - [ ] Ключи для сообщений: `component_enabled`, `component_disabled`, `error_loading_status`
  - [ ] Ключи для разделов: `security_features_section`, `emergency_assistance_section`

- [ ] **Создать `LocalizedStrings/en.lproj/Localizable.strings`**
  - [ ] Английские переводы всех ключей из русского файла
  - [ ] Проверить корректность переводов

- [ ] **Расширить `Core/Localization/LocalizationManager.swift`**
  - [ ] Добавить метод `localized(_:args:)` для параметризованных строк
  - [ ] Поддержка pluralization

---

### 0.7 Создание UI компонентов

- [ ] **Создать `Shared/Components/SettingsAccordion.swift`**
  - [ ] Компонент аккордеона с анимацией
  - [ ] Поддержка иконок и заголовков
  - [ ] Плавная анимация раскрытия/сворачивания

- [ ] **Создать `Shared/Components/SecurityFeatureRow.swift`**
  - [ ] Компонент строки с тумблером
  - [ ] Поддержка описания
  - [ ] Кнопка "Настройки" (опционально)
  - [ ] Accessibility labels

- [ ] **Создать `Shared/Components/ComponentToggleCard.swift`**
  - [ ] Карточка с тумблером для компонента
  - [ ] Иконка, название, описание
  - [ ] Состояния (enabled/disabled/loading)

- [ ] **Создать `Shared/Components/ComponentSettingsModal.swift`**
  - [ ] Модальное окно для настроек компонента
  - [ ] Формы для разных типов настроек
  - [ ] Валидация ввода

---

## 🎯 ЭТАП 1: NetworkProtectionScreen (10 компонентов)

### 1.1 Создание ViewModel

- [ ] **Создать `ViewModels/NetworkProtectionViewModel.swift`**
  - [ ] @Published свойства для всех 10 компонентов:
    - `crashDetectionEnabled: Bool`
    - `roadsideAssistanceEnabled: Bool`
    - `incidentResponseEnabled: Bool`
    - `passwordSecurityEnabled: Bool`
    - `phishingProtectionEnabled: Bool`
    - `malwareDetectionEnabled: Bool`
    - `mobileSecurityEnabled: Bool`
    - `networkSecurityEnabled: Bool`
    - `emergencyResponseEnabled: Bool`
    - `emergencyEventEnabled: Bool`
  - [ ] @Published свойства для UI:
    - `isLoading: Bool`
    - `errorMessage: String?`
    - `showPasswordGenerator: Bool`
    - `showIncidentResponseSettings: Bool`
  - [ ] Метод `loadCriticalComponents()` - загрузка только критичных
  - [ ] Методы `toggle*()` для каждого компонента
  - [ ] Интеграция с `RetryManager` для retry логики
  - [ ] Интеграция с `ToastManager` для уведомлений
  - [ ] Использование `ComponentStatusService` для загрузки статусов

**Как делать:**
1. Создать класс `VPNScreenViewModel: ObservableObject`
2. Добавить все @Published свойства
3. В `init()` вызвать `loadCriticalComponents()`
4. Для каждого компонента создать метод `toggle*()` с retry логикой
5. Использовать Combine для реактивности

---

### 1.2 Расширение VPNScreen

- [ ] **Найти файл `Screens/03_NetworkProtectionScreen.swift` (уже существует)**
  - [ ] Добавить `@StateObject private var viewModel = VPNScreenViewModel()`
  - [ ] Заменить все `@State` переменные на использование `viewModel`
  - [ ] Добавить аккордеоны для группировки компонентов

- [ ] **Добавить раздел "Экстренная помощь"**
  - [ ] Аккордеон с заголовком "Экстренная помощь" (иконка: 🚨)
  - [ ] `SecurityFeatureRow` для `crash_detection_agent`
  - [ ] `SecurityFeatureRow` для `roadside_assistance_agent`
  - [ ] `SecurityFeatureRow` для `emergency_response_bot`
  - [ ] `SecurityFeatureRow` для `emergency_event_manager`

- [ ] **Добавить раздел "Защита от угроз"**
  - [ ] Аккордеон с заголовком "Защита от угроз" (иконка: 🛡️)
  - [ ] `SecurityFeatureRow` для `phishing_protection_agent` + кнопка "Настройки"
  - [ ] `SecurityFeatureRow` для `malware_detection_agent` + кнопка "Настройки"
  - [ ] `SecurityFeatureRow` для `mobile_security_agent` + кнопка "Настройки"
  - [ ] `SecurityFeatureRow` для `network_security_agent` + кнопка "Настройки"

- [ ] **Добавить раздел "Реагирование на инциденты"**
  - [ ] Аккордеон с заголовком "Реагирование" (иконка: 🚨)
  - [ ] `SecurityFeatureRow` для `incident_response_agent` + кнопка "Настройки"
  - [ ] Модальное окно `IncidentResponseSettingsModal` при нажатии на "Настройки"

- [ ] **Добавить раздел "Безопасность паролей"**
  - [ ] Аккордеон с заголовком "Пароли" (иконка: 🔐)
  - [ ] `SecurityFeatureRow` для `password_security_agent` + кнопка "Генератор"
  - [ ] Модальное окно `PasswordGeneratorModal` при нажатии на "Генератор"

- [ ] **Добавить обработку ошибок**
  - [ ] Показывать `ToastView` при ошибках
  - [ ] Откатывать изменения при ошибке API

- [ ] **Добавить загрузку статусов**
  - [ ] В `onAppear` вызывать `viewModel.loadCriticalComponents()`
  - [ ] Показывать индикатор загрузки

---

### 1.3 Создание модальных окон для настроек

- [ ] **Создать `Shared/Components/Modals/IncidentResponseSettingsModal.swift`**
  - [ ] Форма с полями:
    - Пороги эскалации (критичность: низкая/средняя/высокая/критическая)
    - Сроки SLA (время реакции в минутах)
    - Контактные роли (кто оповещается)
    - Автодействия (блокировать/уведомить/эскалировать)
  - [ ] Валидация ввода
  - [ ] Кнопки "Сохранить" и "Отмена"
  - [ ] Интеграция с API для сохранения настроек

- [ ] **Создать `Shared/Components/Modals/PasswordGeneratorModal.swift`**
  - [ ] Поля для настройки генератора:
    - Длина пароля (8-64 символов, слайдер)
    - Типы символов (чекбоксы: заглавные, строчные, цифры, спецсимволы)
  - [ ] Кнопка "Сгенерировать"
  - [ ] Поле для отображения сгенерированного пароля
  - [ ] Кнопка "Скопировать"
  - [ ] Интеграция с API для генерации пароля

---

### 1.4 Тестирование VPNScreen

- [ ] **Создать `Tests/ViewModels/NetworkProtectionViewModelTests.swift`**
  - [ ] Тест `testToggleCrashDetection_Success()`
  - [ ] Тест `testToggleCrashDetection_Failure()`
  - [ ] Тест `testLoadCriticalComponents_Success()`
  - [ ] Тест `testLoadCriticalComponents_Failure()`
  - [ ] Использовать MockAPIService

- [ ] **Создать `Tests/UITests/NetworkProtectionScreenUITests.swift`**
  - [ ] Тест `testToggleCrashDetection()`
  - [ ] Тест `testAccessibility()`
  - [ ] Тест `testAccordionExpansion()`

---

## 🎯 ЭТАП 2: ParentalControlScreen (5 компонентов)

### 2.1 Расширение ViewModel

- [ ] **Расширить `ViewModels/ParentalControlViewModel.swift` (или создать новый)**
  - [ ] Добавить @Published свойства:
    - `selfHarmDetectionEnabled: Bool`
    - `groomingDetectionEnabled: Bool`
    - `onlinePredatorsEnabled: Bool`
    - `psychologicalSupportEnabled: Bool`
  - [ ] Добавить @Published свойства для UI:
    - `showPsychologicalSupportModal: Bool`
  - [ ] Методы `toggle*()` для каждого компонента
  - [ ] Метод `requestPsychologicalSupport()` для связи с психологом

---

### 2.2 Расширение ParentalControlScreen

- [ ] **Найти файл `Screens/07_ParentalControlScreen.swift`**
  - [ ] Добавить `@StateObject private var viewModel = ParentalControlViewModel()`
  - [ ] Добавить новый раздел "Защита детей" после существующих карточек

- [ ] **Добавить раздел "Защита детей"**
  - [ ] Заголовок раздела: "Защита детей" (иконка: 🛡️)
  - [ ] `ChildProtectionCard` для `self_harm_detection_agent`
  - [ ] `ChildProtectionCard` для `grooming_detection_agent`
  - [ ] `ChildProtectionCard` для `online_predators_agent`
  - [ ] `ChildProtectionCard` для `psychological_support_agent` + кнопка "Связаться с психологом"

- [ ] **Улучшить `parental_control_bot` (уже есть в экране)**
  - [ ] Добавить расширенные настройки:
    - Профили детей (выбор ребенка, возрастная группа)
    - Расписания (время использования, дни недели)
    - Белые/черные списки (разрешенные/запрещенные сайты/приложения)
    - Уровни фильтрации (строгий/умеренный/мягкий)
    - Антиобход (обнаружение попыток обхода блокировок)
  - [ ] Создать модальное окно для расширенных настроек

- [ ] **Создать компонент `ChildProtectionCard`**
  - [ ] Карточка с иконкой, названием, описанием
  - [ ] Тумблер для включения/выключения
  - [ ] Опциональная кнопка действия

---

### 2.3 Создание модальных окон

- [ ] **Создать `Shared/Components/Modals/PsychologicalSupportModal.swift`**
  - [ ] Форма для связи с психологом
  - [ ] Поля: имя, возраст, проблема, контакт
  - [ ] Кнопка "Отправить запрос"
  - [ ] Интеграция с API

- [ ] **Создать `Shared/Components/Modals/ParentalControlAdvancedSettingsModal.swift`**
  - [ ] Форма с расширенными настройками родительского контроля
  - [ ] Все поля из требований (профили, расписания, списки, фильтрация)
  - [ ] Валидация и сохранение

---

### 2.4 Тестирование ParentalControlScreen

- [ ] **Расширить `Tests/ViewModels/ParentalControlViewModelTests.swift`**
  - [ ] Тесты для всех новых методов toggle
  - [ ] Тест для `requestPsychologicalSupport()`

- [ ] **Создать `Tests/UITests/ParentalControlScreenUITests.swift`**
  - [ ] Тесты для новых компонентов защиты детей

---

## 🎯 ЭТАП 3: AdvancedProtectionSettingsScreen (13 компонентов)

### 3.1 Создание ViewModel

- [ ] **Создать `ViewModels/ProtectionSettingsViewModel.swift`**
  - [ ] @Published свойства для всех 13 компонентов:
    - Мессенджеры (6): telegram, whatsapp, instagram, max_messenger, gaming, browser
    - Приватность (3): location_bubble, personal_data_cleanup, anti_tracker
    - Мониторинг (4): dark_web_monitoring, russian_identity_theft, ai_categories, driving_reports
  - [ ] @Published свойства для модальных окон настроек
  - [ ] Методы `toggle*()` для каждого компонента
  - [ ] Методы `loadComponentStatus()` для ленивой загрузки

---

### 3.2 Расширение AdvancedProtectionSettingsScreen

- [ ] **Найти или создать файл `Screens/AdvancedProtectionSettingsScreen.swift`**
  - [ ] Добавить `@StateObject private var viewModel = ProtectionSettingsViewModel()`

- [ ] **Добавить раздел "Защита в мессенджерах"**
  - [ ] Аккордеон с заголовком "Защита в мессенджерах"
  - [ ] `SecurityFeatureRow` для каждого мессенджера + кнопка "Настроить"
  - [ ] Модальные окна для настройки каждого мессенджера

- [ ] **Добавить раздел "Приватность"**
  - [ ] Аккордеон с заголовком "Приватность"
  - [ ] `SecurityFeatureRow` для каждого компонента приватности + кнопка "Настроить"
  - [ ] Модальные окна для настроек

- [ ] **Добавить раздел "Мониторинг"**
  - [ ] Аккордеон с заголовком "Мониторинг"
  - [ ] `SecurityFeatureRow` для каждого компонента мониторинга + кнопка "Настроить"
  - [ ] Модальные окна для настроек

---

### 3.3 Создание модальных окон для мессенджеров

- [ ] **Создать `Shared/Components/Modals/TelegramSecuritySettingsModal.swift`**
  - [ ] Форма с полями:
    - Подключение аккаунта (токен API, авторизация)
    - Выбор чатов/групп (какие чаты мониторить)
    - Уровни фильтрации (строгий/умеренный/мягкий)
    - Язык/чувствительность
  - [ ] Валидация и сохранение

- [ ] **Создать аналогичные модальные окна для:**
  - [ ] `WhatsAppSecuritySettingsModal.swift`
  - [ ] `InstagramSecuritySettingsModal.swift`
  - [ ] `MaxMessengerSecuritySettingsModal.swift`
  - [ ] `GamingSecuritySettingsModal.swift`
  - [ ] `BrowserSecuritySettingsModal.swift`

---

### 3.4 Создание модальных окон для приватности и мониторинга

- [ ] **Создать модальные окна для приватности:**
  - [ ] `LocationBubbleSettingsModal.swift` (радиус пузыря, кому показывать, точность)
  - [ ] `PersonalDataCleanupSettingsModal.swift` (площадки, периодичность, авто-удаление)
  - [ ] `AntiTrackerSettingsModal.swift` (списки блокировок, агрессивность)

- [ ] **Создать модальные окна для мониторинга:**
  - [ ] `DarkWebMonitoringSettingsModal.swift` (поля мониторинга, регионы, частота)
  - [ ] `IdentityTheftProtectionSettingsModal.swift` (источники РФ, типы документов)
  - [ ] `AICategoriesSettingsModal.swift` (белые/черные списки, уровни фильтрации)
  - [ ] `DrivingReportsSettingsModal.swift` (режим приватности, частота, получатели)

---

### 3.5 Тестирование AdvancedProtectionSettingsScreen

- [ ] **Создать `Tests/ViewModels/ProtectionSettingsViewModelTests.swift`**
  - [ ] Тесты для всех компонентов

- [ ] **Создать `Tests/UITests/ProtectionSettingsScreenUITests.swift`**
  - [ ] UI тесты для всех разделов

---

## 🎯 ЭТАП 4: SettingsScreen (5 менеджеров через NavigationLink)

### 4.1 Создание View для менеджеров

- [ ] **Создать `Screens/Views/EmergencyContactsView.swift`**
  - [ ] Список контактов (добавить/удалить/редактировать)
  - [ ] Порядок дозвона (последовательность при экстренной ситуации)
  - [ ] Каналы связи (звонок/SMS/мессенджер)
  - [ ] Приоритет контакта (основной/резервный)
  - [ ] Интеграция с API

- [ ] **Создать `Screens/Views/EmergencyNotificationsView.swift`**
  - [ ] Шаблоны сообщений (текст для разных типов событий)
  - [ ] Каналы доставки (push/SMS/email/звонок)
  - [ ] Частота повторов
  - [ ] Временные окна (когда отправлять)
  - [ ] Интеграция с API

- [ ] **Создать `Screens/Views/VoiceControlView.swift`**
  - [ ] Активационное слово (выбор из списка)
  - [ ] Языки/акценты (русский/английский, региональные акценты)
  - [ ] Чувствительность (низкая/средняя/высокая)
  - [ ] Режим работы (онлайн/оффлайн)
  - [ ] Интеграция с API

- [ ] **Создать `Screens/Views/ComplianceView.swift`**
  - [ ] Раздел "Защита детей" (russian_child_protection_manager):
    - Юридический профиль (дети/взрослые)
    - Регионы (выбор регионов РФ)
    - Политика хранения (сроки хранения данных)
    - Политика удаления (автоматическое/ручное)
  - [ ] Раздел "Защита данных" (russian_data_protection_manager):
    - Юридический профиль (физические/юридические лица)
    - Регионы (выбор регионов РФ)
    - Политика хранения (сроки, шифрование)
    - Политика удаления (автоматическое/ручное)
  - [ ] Интеграция с API

---

### 4.2 Расширение SettingsScreen

- [ ] **Найти файл `Screens/05_SettingsScreen.swift`**
  - [ ] В раздел `securitySection` добавить NavigationLink для каждого менеджера:
    - [ ] NavigationLink на `EmergencyContactsView`
    - [ ] NavigationLink на `EmergencyNotificationsView`
    - [ ] NavigationLink на `VoiceControlView`
    - [ ] NavigationLink на `ComplianceView` (с параметром раздела)

- [ ] **Добавить иконки и описания для каждого NavigationLink**
  - [ ] Использовать `settingRow` компонент
  - [ ] Локализованные тексты

---

### 4.3 Тестирование SettingsScreen

- [ ] **Создать тесты для новых View:**
  - [ ] `Tests/ViewModels/EmergencyContactsViewModelTests.swift`
  - [ ] `Tests/ViewModels/EmergencyNotificationsViewModelTests.swift`
  - [ ] `Tests/ViewModels/VoiceControlViewModelTests.swift`
  - [ ] `Tests/ViewModels/ComplianceViewModelTests.swift`

- [ ] **Создать UI тесты:**
  - [ ] `Tests/UITests/SettingsScreenUITests.swift`

---

## 🎯 ЭТАП 5: Улучшение существующих менеджеров (9 компонентов)

### 5.1 Улучшение family_notification_manager

- [ ] **Найти `FamilyScreen.swift`**
  - [ ] Найти существующий `family_notification_manager`
  - [ ] Добавить расширенные настройки:
    - Каналы (push/email/SMS)
    - Частота (мгновенно/ежедневно/еженедельно)
    - Шаблоны (текст уведомлений)
    - Приоритеты тем (безопасность/активность/награды)
  - [ ] Создать модальное окно для настроек
  - [ ] Интеграция с API

---

### 5.2 Улучшение smart_notification_manager

- [ ] **Найти `NotificationSettingsScreen.swift`**
  - [ ] Найти существующий `smart_notification_manager`
  - [ ] Добавить расширенные настройки:
    - Каналы (push/email/SMS)
    - Умная частота (на основе активности)
    - Шаблоны (текст уведомлений)
    - Приоритеты тем
  - [ ] Создать модальное окно для настроек
  - [ ] Интеграция с API

---

### 5.3 Улучшение child_interface_manager

- [ ] **Найти `ChildInterfaceScreen.swift`**
  - [ ] Найти существующий `child_interface_manager`
  - [ ] Добавить формы/настройки:
    - Профили детей
    - Интерфейсы (настройки UI для детей)
  - [ ] Интеграция с API

---

### 5.4 Улучшение elderly_interface_manager

- [ ] **Найти `ElderlyInterfaceScreen.swift`**
  - [ ] Найти существующий `elderly_interface_manager`
  - [ ] Добавить формы/настройки:
    - Профили пожилых
    - Интерфейсы (настройки UI для пожилых)
  - [ ] Интеграция с API

---

### 5.5 Улучшение subscription_manager

- [ ] **Найти `TariffsScreen.swift`**
  - [ ] Найти существующий `subscription_manager`
  - [ ] Улучшить формы/настройки:
    - Тарифы (отображение, выбор)
    - Коды (активация промокодов)
    - Статусы (активный/истек/отменен)
  - [ ] НЕ добавлять тумблер (это не тумблер, а формы)
  - [ ] Интеграция с API

---

### 5.6 Улучшение referral_manager

- [ ] **Найти `ReferralScreen.swift`**
  - [ ] Найти существующий `referral_manager`
  - [ ] Улучшить формы/настройки:
    - Коды (реферальные коды)
    - Статистика (количество приглашенных, награды)
  - [ ] НЕ добавлять тумблер
  - [ ] Интеграция с API

---

### 5.7 Улучшение qr_payment_manager

- [ ] **Найти `PaymentQRScreen.swift`**
  - [ ] Найти существующий `qr_payment_manager`
  - [ ] Улучшить формы/настройки:
    - QR коды (генерация, отображение)
    - Статусы (оплачено/ожидание/ошибка)
  - [ ] НЕ добавлять тумблер
  - [ ] Интеграция с API

---

### 5.8 Улучшение analytics_manager

- [ ] **Найти `AnalyticsScreen.swift`**
  - [ ] Найти существующий `analytics_manager`
  - [ ] Добавить расширенные настройки:
    - Выбор периодов (день/неделя/месяц/год)
    - Метрики (какие метрики показывать)
    - Расписание отчетов (частота автоматических отчетов)
  - [ ] Создать модальное окно для настроек
  - [ ] Интеграция с API

---

### 5.9 Улучшение report_manager

- [ ] **Найти экраны, где используется `report_manager`**
  - [ ] Добавить расширенные настройки:
    - Выбор периодов (день/неделя/месяц/год)
    - Метрики (какие метрики показывать)
    - Расписание отчетов (частота автоматических отчетов)
  - [ ] Создать модальное окно для настроек
  - [ ] Интеграция с API

---

## 🎯 ЭТАП 6: ДОСТУПНОСТЬ И ЛОКАЛИЗАЦИЯ

### 6.1 Добавление Accessibility

- [ ] **Для всех компонентов добавить:**
  - [ ] `.accessibilityLabel()` для всех тумблеров
  - [ ] `.accessibilityHint()` для описания действий
  - [ ] `.accessibilityValue()` для текущего состояния
  - [ ] Поддержка VoiceOver

- [ ] **Добавить Dynamic Type:**
  - [ ] Использовать `.dynamicTypeSize(...DynamicTypeSize.xxxLarge)` для всех текстов
  - [ ] Проверить на всех размерах шрифта

- [ ] **Добавить поддержку увеличенного контраста:**
  - [ ] Проверить цвета на контрастность
  - [ ] Использовать системные цвета где возможно

---

### 6.2 Проверка локализации

- [ ] **Проверить все экраны на хардкод:**
  - [ ] Запустить скрипт проверки хардкода
  - [ ] Заменить все хардкодные строки на `LocalizationManager.shared.localized()`
  - [ ] Проверить все ключи локализации

- [ ] **Проверить переводы:**
  - [ ] Все ключи имеют русский перевод
  - [ ] Все ключи имеют английский перевод
  - [ ] Переводы корректны и понятны

---

## 🎯 ЭТАП 7: ТЕСТИРОВАНИЕ

### 7.1 Unit тесты

- [ ] **Тесты для всех ViewModels:**
  - [ ] `VPNScreenViewModelTests.swift` - все методы
  - [ ] `ParentalControlViewModelTests.swift` - все методы
  - [ ] `ProtectionSettingsViewModelTests.swift` - все методы
  - [ ] Тесты для всех менеджеров

- [ ] **Тесты для сервисов:**
  - [ ] `ComponentStatusServiceTests.swift`
  - [ ] `ComponentConfigurationServiceTests.swift`
  - [ ] `ComponentCacheServiceTests.swift`

- [ ] **Покрытие тестами должно быть >80%**

---

### 7.2 UI тесты

- [ ] **UI тесты для всех экранов:**
  - [ ] `VPNScreenUITests.swift`
  - [ ] `ParentalControlScreenUITests.swift`
  - [ ] `ProtectionSettingsScreenUITests.swift`
  - [ ] `SettingsScreenUITests.swift`

- [ ] **Тесты доступности:**
  - [ ] Проверка VoiceOver
  - [ ] Проверка Dynamic Type
  - [ ] Проверка контрастности

---

### 7.3 Integration тесты

- [ ] **Тесты интеграции с API:**
  - [ ] Тесты для всех endpoints
  - [ ] Тесты для retry логики
  - [ ] Тесты для кэширования

### 7.4 API Integration тесты (42 компонента)

- [ ] **Создать `Tests/Integration/ComponentAPITests.swift`**
  - [ ] Тест для каждого из 42 компонентов:
    - [ ] `testGetComponentStatus()` - получить статус
    - [ ] `testEnableComponent()` - включить компонент
    - [ ] `testDisableComponent()` - выключить компонент
    - [ ] `testGetComponentConfiguration()` - получить настройки
    - [ ] `testUpdateComponentConfiguration()` - обновить настройки
  - [ ] Тесты для batch операций:
    - [ ] `testLoadCriticalComponentsStatus()` - загрузка критичных компонентов
    - [ ] `testBatchUpdateComponents()` - массовое обновление
  - [ ] Тесты для ошибок:
    - [ ] `testComponentNotFound()` - компонент не найден
    - [ ] `testNetworkError()` - ошибка сети
    - [ ] `testInvalidConfiguration()` - невалидная конфигурация

- [ ] **Создать `Tests/Integration/ComponentAPIIntegrationTests.swift`**
  - [ ] Тесты реального API (требуют подключения к серверу):
    - [ ] Проверить все 42 endpoints на сервере
    - [ ] Проверить работу каждого компонента
    - [ ] Проверить сохранение настроек
    - [ ] Проверить синхронизацию статусов

**Как делать:**
1. Создать тестовый класс `ComponentAPITests`
2. Для каждого компонента создать набор тестов
3. Использовать MockAPIService для unit тестов
4. Использовать реальный APIService для integration тестов
5. Проверить все сценарии (успех, ошибки, retry)

---

## 🎯 ЭТАП 8: АНАЛИТИКА

### 8.1 Интеграция аналитики

- [ ] **Создать `Core/Analytics/ComponentAnalytics.swift`**
  - [ ] Метод `trackComponentToggle(componentId:enabled:)`
  - [ ] Метод `trackComponentSettingsOpened(componentId:)`
  - [ ] Метод `trackComponentError(componentId:error:)`

- [ ] **Добавить трекинг во все ViewModels:**
  - [ ] В методы `toggle*()` добавить вызовы аналитики
  - [ ] При открытии модальных окон настроек
  - [ ] При ошибках

---

## 🎯 ЭТАП 9: ФИНАЛЬНАЯ ПРОВЕРКА

### 9.1 Проверка всех компонентов

- [ ] **Проверить все 42 компонента:**
  - [ ] Все компоненты интегрированы
  - [ ] Все тумблеры работают
  - [ ] Все модальные окна открываются
  - [ ] Все настройки сохраняются
  - [ ] Все API endpoints подключены

### 9.5 Тестирование API интеграции (42 компонента)

- [ ] **Проверить API endpoints на сервере:**
  - [ ] `GET /components/status/{componentId}` - работает для всех 42 компонентов
  - [ ] `POST /components/enable/{componentId}` - работает для всех 42 компонентов
  - [ ] `POST /components/disable/{componentId}` - работает для всех 42 компонентов
  - [ ] `GET /components/configuration/{componentId}` - работает для всех 42 компонентов
  - [ ] `POST /components/configuration/{componentId}` - работает для всех 42 компонентов

- [ ] **Проверить работу каждого компонента:**
  - [ ] NetworkProtectionScreen (10 компонентов):
    - [ ] crash_detection_agent
    - [ ] roadside_assistance_agent
    - [ ] incident_response_agent
    - [ ] password_security_agent
    - [ ] phishing_protection_agent
    - [ ] malware_detection_agent
    - [ ] mobile_security_agent
    - [ ] network_security_agent
    - [ ] emergency_response_bot
    - [ ] emergency_event_manager
  - [ ] ParentalControlScreen (5 компонентов):
    - [ ] self_harm_detection_agent
    - [ ] grooming_detection_agent
    - [ ] online_predators_agent
    - [ ] psychological_support_agent
    - [ ] parental_control_bot
  - [ ] AdvancedProtectionSettingsScreen (13 компонентов):
    - [ ] telegram_security_bot
    - [ ] whatsapp_security_bot
    - [ ] instagram_security_bot
    - [ ] max_messenger_security_bot
    - [ ] gaming_security_bot
    - [ ] browser_security_bot
    - [ ] location_bubble_agent
    - [ ] personal_data_cleanup_agent
    - [ ] anti_tracker_agent
    - [ ] dark_web_monitoring_agent
    - [ ] russian_identity_theft_protection_agent
    - [ ] ai_categories_agent
    - [ ] driving_reports_agent
  - [ ] SettingsScreen (5 менеджеров):
    - [ ] emergency_contact_manager
    - [ ] emergency_notification_manager
    - [ ] voice_control_manager
    - [ ] russian_child_protection_manager
    - [ ] russian_data_protection_manager
  - [ ] Улучшение существующих (9 менеджеров):
    - [ ] family_notification_manager
    - [ ] smart_notification_manager
    - [ ] child_interface_manager
    - [ ] elderly_interface_manager
    - [ ] subscription_manager
    - [ ] referral_manager
    - [ ] qr_payment_manager
    - [ ] analytics_manager
    - [ ] report_manager

- [ ] **Проверить интеграцию мобильного приложения с сервером:**
  - [ ] Все команды отправляются на сервер
  - [ ] Все статусы получаются с сервера
  - [ ] Все настройки сохраняются на сервере
  - [ ] Retry механизм работает корректно
  - [ ] Кэширование работает корректно
  - [ ] Toast уведомления показываются при ошибках

- [ ] **Проверить функциональность компонентов:**
  - [ ] Каждый компонент действительно включается/выключается на сервере
  - [ ] Каждый компонент выполняет свои функции защиты
  - [ ] Настройки применяются корректно
  - [ ] Уведомления приходят при событиях

**Как делать:**
1. Подключиться к реальному серверу (development/staging)
2. Для каждого компонента выполнить полный цикл:
   - Получить статус
   - Включить компонент
   - Проверить, что он работает
   - Обновить настройки
   - Выключить компонент
   - Проверить, что он выключен
3. Задокументировать результаты тестирования
4. Исправить найденные проблемы

---

### 9.2 Проверка производительности

- [ ] **Проверить производительность:**
  - [ ] Время загрузки экранов < 1 секунды
  - [ ] Плавная анимация (60 FPS)
  - [ ] Нет утечек памяти
  - [ ] Кэширование работает корректно

---

### 9.3 Проверка UI/UX

- [ ] **Проверить UI/UX:**
  - [ ] Аккордеоны работают плавно
  - [ ] Все тексты локализованы
  - [ ] Доступность работает
  - [ ] Toast уведомления показываются корректно

---

### 9.4 Финальная документация

- [ ] **Обновить документацию:**
  - [ ] Обновить README с новыми компонентами
  - [ ] Обновить архитектурную документацию
  - [ ] Создать changelog

---

## 📊 ПРОГРЕСС

**Общий прогресс:** 0/42 компонентов (0%)

### По этапам:

- [ ] **Этап 0:** Подготовка и инфраструктура (0/7 подэтапов)
- [ ] **Этап 1:** NetworkProtectionScreen (0/10 компонентов)
- [ ] **Этап 2:** ParentalControlScreen (0/5 компонентов)
- [ ] **Этап 3:** AdvancedProtectionSettingsScreen (0/13 компонентов)
- [ ] **Этап 4:** SettingsScreen (0/5 компонентов)
- [ ] **Этап 5:** Улучшение существующих (0/9 компонентов)
- [ ] **Этап 6:** Доступность и локализация (0/2 подэтапа)
- [ ] **Этап 7:** Тестирование (0/4 подэтапа)
- [ ] **Этап 8:** Аналитика (0/1 подэтап)
- [ ] **Этап 9:** Финальная проверка (0/5 подэтапов)

---

## 📝 ЗАМЕТКИ

**Важные напоминания:**
- ✅ Всегда использовать `LocalizationManager.shared.localized()` вместо хардкода
- ✅ Всегда обрабатывать ошибки с retry логикой
- ✅ Всегда показывать toast уведомления при ошибках
- ✅ Всегда добавлять accessibility labels
- ✅ Всегда тестировать перед коммитом

**Полезные ссылки:**
- Документ с архитектурой: `docs/ДЕТАЛЬНАЯ_АРХИТЕКТУРА_И_УЛУЧШЕНИЯ_42_КОМПОНЕНТОВ.md`
- Документ с планом: `docs/ФИНАЛЬНАЯ_ИНСТРУКЦИЯ_ДЛЯ_ML_СИСТЕМЫ_РЕАЛИЗАЦИЯ_42_КОМПОНЕНТОВ.md`
- Экспертный анализ: `docs/ЭКСПЕРТНЫЙ_АНАЛИЗ_42_КОМПОНЕНТОВ_ПЛАН_ДЕЙСТВИЙ.md`

---

**Дата последнего обновления:** 13 января 2026  
**Статус:** 🟡 В РАБОТЕ

