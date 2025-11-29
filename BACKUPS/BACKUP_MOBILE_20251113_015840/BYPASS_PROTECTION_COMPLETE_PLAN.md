# 🚨 Полный план рефакторинга "Защита от обхода"

## ✅ Все согласованные решения

### 1. VPN Экран (упрощение)
- ✅ Удалить всю старую карточку "🚨 Защита от обхода" (статистика + 4 детекции)
- ✅ Добавить упрощенную секцию "🌐 Обнаружение сторонних VPN"
- ✅ Оставить только детекцию VPN с простым toggle
- ✅ Удалить компонент `BypassDetectionItem`

### 2. Родительский контроль (7-я карточка)
- ✅ Добавить 7-ю карточку "🚨 Защита от обхода" (желтый/янтарный цвет)
- ✅ Карточка имеет toggle (можно включить/выключить)
- ✅ Перенести детекции: Скрытый режим, Tor, Proxy

### 3. Замена терминов
- ✅ "Инкогнито" → "Скрытый режим" (везде в коде, модалах, уведомлениях)

### 4. Модал защиты от обхода
- ✅ Создать `FamilyBypassProtectionModal`
- ✅ 3 детекции с toggle:
  - 🕶️ Детекция Скрытого режима → "Приватный режим браузера"
  - 🧅 Детекция Tor → "Анонимный браузер"
  - 🔀 Детекция Proxy → "Скрытие IP (адрес)"
- ✅ Статистика попыток обхода

### 5. Система уведомлений
- ✅ Уведомления ТОЛЬКО в `NotificationsScreen`
- ✅ Push-уведомления можно отключить через настройки
- ✅ Добавить фильтр "Обход" в NotificationsScreen
- ✅ Добавить toggle "Попытки обхода" в NotificationSettingsScreen

### 6. Интеграция с отчетами
- ✅ Добавить секцию "🚨 ПОПЫТКИ ОБХОДА" в FamilyReportsModal
- ✅ Показывать статистику попыток обхода
- ✅ Использовать "Скрытый режим" вместо "Инкогнито"

---

## 📋 Полный чек-лист задач

### 🔧 Этап 1: Рефакторинг VPN экрана

#### Файл: `Screens/03_VPNScreen.swift`

- [ ] **Удалить использование карточки** (строка ~81)
  ```swift
  // УДАЛИТЬ:
  // Bypass Protection Section
  bypassProtectionCard
  ```

- [ ] **Удалить функцию `bypassProtectionCard`** (строки 719-784)
  - Удалить весь блок кода с комментарием `// MARK: - Bypass Protection Card`
  - Удалить заголовок "🚨 Защита от обхода"
  - Удалить статистику (3 колонки)
  - Удалить 4 детекции (VPN + Инкогнито + Tor + Proxy)

- [ ] **Удалить компонент `BypassDetectionItem`** (строки 787-854)
  - Удалить весь `struct BypassDetectionItem: View { ... }`

- [ ] **Добавить новую секцию `thirdPartyVPNDetectionCard`**
  ```swift
  // MARK: - Third-Party VPN Detection Card
  private var thirdPartyVPNDetectionCard: some View {
      VStack(spacing: Spacing.m) {
          // Header
          HStack {
              Text("🌐 Обнаружение сторонних VPN")
                  .font(.h3)
                  .foregroundColor(.textPrimary)
              
              Spacer()
          }
          
          // Description
          VStack(alignment: .leading, spacing: Spacing.s) {
              Text("Обнаружение других VPN для защиты ALADDIN VPN")
                  .font(.body)
                  .foregroundColor(.textPrimary)
              
              Text("NordVPN, ExpressVPN, Surfshark и др.")
                  .font(.caption)
                  .foregroundColor(.textSecondary)
          }
          .frame(maxWidth: .infinity, alignment: .leading)
          
          // Toggle
          HStack {
              Text(isThirdPartyVPNDetectionEnabled ? "Включено" : "Выключено")
                  .font(.body)
                  .foregroundColor(isThirdPartyVPNDetectionEnabled ? .successGreen : .textSecondary)
              
              Spacer()
              
              Toggle("", isOn: $isThirdPartyVPNDetectionEnabled)
                  .toggleStyle(SwitchToggleStyle(tint: .successGreen))
          }
          .padding(Spacing.m)
          .background(Color.backgroundMedium.opacity(0.3))
          .cornerRadius(CornerRadius.medium)
      }
      .padding(Spacing.cardPadding)
      .background(backgroundShape)
      .cardShadow()
      .padding(.horizontal, Spacing.screenPadding)
  }
  ```

- [ ] **Добавить состояние для новой секции**
  ```swift
  @State private var isThirdPartyVPNDetectionEnabled: Bool = true
  ```

- [ ] **Добавить использование новой секции** (после `antivirusCard`)
  ```swift
  // Third-Party VPN Detection Section
  thirdPartyVPNDetectionCard
  ```

---

### 🎨 Этап 2: Добавление 7-й карточки в родительский контроль

#### Файл: `Screens/02_FamilyScreen.swift`

- [ ] **Добавить состояния для новой карточки**
  ```swift
  @State private var isBypassProtectionEnabled: Bool = true
  @State private var showBypassProtectionModal: Bool = false
  @State private var bypassAttemptsToday: Int = 0
  @State private var bypassAttemptsWeek: Int = 47
  @State private var bypassAttemptsBlocked: Int = 47
  @State private var bypassDetectionActive: Int = 3  // 3 из 3 активно
  ```

- [ ] **Добавить 7-ю карточку в сетку** (после существующих 6 карточек)
  ```swift
  // 7. Защита от обхода (НОВАЯ)
  FamilyParentalControlCard(
      icon: "🚨",
      title: "Защита от\nобхода",
      statusBadge: bypassAttemptsToday > 0 ? "🚨 \(bypassAttemptsToday)" : "✅ 0",
      statusText: "🚫 \(bypassAttemptsBlocked) заблокировано",
      metric: "\(bypassDetectionActive)/3 активно",
      cardColor: Color(hex: "F59E0B").opacity(0.2),  // Янтарный (новый цвет!)
      borderColor: Color(hex: "F59E0B").opacity(0.4),
      badgeColor: bypassAttemptsToday > 0 ? .dangerRed : .successGreen,
      isEnabled: $isBypassProtectionEnabled,
      action: { showBypassProtectionModal = true }
  )
  ```

- [ ] **Добавить `.sheet` для модала**
  ```swift
  .sheet(isPresented: $showBypassProtectionModal) {
      FamilyBypassProtectionModal(
          isPresented: $showBypassProtectionModal,
          isEnabled: $isBypassProtectionEnabled
      )
  }
  ```

- [ ] **Обновить функцию `loadParentalControlStats()`**
  - Добавить загрузку статистики обхода из API

#### Файл: `Screens/07_ParentalControlScreen.swift`

- [ ] **Добавить те же состояния** что и в FamilyScreen
- [ ] **Добавить 7-ю карточку** в сетку `parentalControlCards`
- [ ] **Добавить `.sheet` для модала**
- [ ] **Обновить `loadParentalControlStats()`** для загрузки статистики обхода

---

### 📝 Этап 3: Создание модала защиты от обхода

#### Новый файл: `Screens/Modals/FamilyBypassProtectionModal.swift`

- [ ] **Создать новый файл**
- [ ] **Реализовать структуру модала**
  ```swift
  struct FamilyBypassProtectionModal: View {
      @Binding var isPresented: Bool
      @Binding var isEnabled: Bool
      
      @AppStorage("bypass_incognito_enabled") private var isIncognitoDetectionEnabled: Bool = true
      @AppStorage("bypass_tor_enabled") private var isTorDetectionEnabled: Bool = true
      @AppStorage("bypass_proxy_enabled") private var isProxyDetectionEnabled: Bool = true
      
      @State private var attemptsToday: Int = 0
      @State private var attemptsWeek: Int = 47
      @State private var attemptsBlocked: Int = 47
      @State private var incognitoAttempts: Int = 15
      @State private var torAttempts: Int = 8
      @State private var proxyAttempts: Int = 6
      
      var body: some View {
          FamilyModalBaseView(
              title: "🚨 Защита от обхода",
              isPresented: $isPresented
          ) {
              VStack(spacing: Spacing.m) {
                  // 3 детекции с пояснениями
                  // ...
                  // Статистика
                  // ...
              }
          }
      }
  }
  ```

- [ ] **Добавить 3 детекции с toggle и пояснениями**
  ```swift
  // 1. Детекция Скрытого режима
  FamilyContentBlockItem(
      icon: "🕶️",
      title: "Детекция Скрытого режима",  // ⬅️ НОВОЕ название!
      description: "Приватный режим браузера",  // ⬅️ Пояснение (2-3 слова)
      isEnabled: $isIncognitoDetectionEnabled
  )
  
  // 2. Детекция Tor
  FamilyContentBlockItem(
      icon: "🧅",
      title: "Детекция Tor",
      description: "Анонимный браузер",  // ⬅️ Пояснение (2-3 слова)
      isEnabled: $isTorDetectionEnabled
  )
  
  // 3. Детекция Proxy
  FamilyContentBlockItem(
      icon: "🔀",
      title: "Детекция Proxy",
      description: "Скрытие IP (адрес)",  // ⬅️ Пояснение на одной строке
      isEnabled: $isProxyDetectionEnabled
  )
  ```

- [ ] **Добавить секцию статистики** (попытки сегодня, всего за неделю, заблокировано, детализация по типам)
- [ ] **Реализовать `loadBypassStatistics()`** для загрузки из API
- [ ] **Реализовать `applyBypassProtection()`** для применения настроек

---

### 🔄 Этап 4: Замена терминов (глобальная)

#### Файлы для замены:

- [ ] `Screens/03_VPNScreen.swift`
  - Заменить "Инкогнито" → "Скрытый режим" (если осталось)

- [ ] `Screens/02_FamilyScreen.swift`
  - Заменить "Инкогнито" → "Скрытый режим"
  - Заменить "Детекция Инкогнито" → "Детекция Скрытого режима"

- [ ] `Screens/07_ParentalControlScreen.swift`
  - Заменить "Инкогнито" → "Скрытый режим"

- [ ] `Screens/Modals/FamilyBypassProtectionModal.swift` (новый)
  - Использовать "Скрытый режим" во всех местах

- [ ] `Core/Managers/ParentalControlManager.swift`
  - Добавить `BypassType.displayName` для отображения в UI
  ```swift
  enum BypassType: String {
      case incognito = "incognito"  // Внутренний код
      case tor = "tor"
      case proxy = "proxy"
      
      var displayName: String {  // ⬅️ НОВОЕ свойство для UI
          switch self {
          case .incognito: return "Скрытый режим"  // ⬅️ Простое название
          case .tor: return "Tor"
          case .proxy: return "Proxy"
          }
      }
      
      var icon: String {
          switch self {
          case .incognito: return "🕶️"
          case .tor: return "🧅"
          case .proxy: return "🔀"
          }
      }
  }
  ```

- [ ] `ViewModels/NotificationsViewModel.swift`
  - Использовать `displayName` вместо `rawValue` в уведомлениях

---

### 🔔 Этап 5: Система уведомлений

#### Файл: `ViewModels/NotificationsViewModel.swift`

- [ ] **Добавить `NotificationType.bypassAttempt`**
  ```swift
  enum NotificationType: String {
      case threat = "Угроза"
      case success = "Успех"
      case info = "Информация"
      case warning = "Предупреждение"
      case bypassAttempt = "Обход"  // ⬅️ НОВЫЙ тип
      
      var icon: String {
          switch self {
          case .bypassAttempt: return "🚨"
          // ...
          }
      }
      
      var color: Color {
          switch self {
          case .bypassAttempt: return .warningOrange
          // ...
          }
      }
  }
  ```

- [ ] **Добавить метод `addNotification(_:Notification)`**
  - Для добавления уведомлений в список

#### Файл: `Screens/12_NotificationsScreen.swift`

- [ ] **Добавить фильтр `.bypass` в `NotificationFilter`**
  ```swift
  enum NotificationFilter: String, CaseIterable {
      case all = "Все"
      case threat = "Угрозы"
      case bypass = "Обход"  // ⬅️ НОВЫЙ фильтр
      case success = "Успех"
      case info = "Информация"
      case warning = "Предупреждение"
      
      var subtitle: String {
          switch self {
          case .bypass: return "Попытки обхода блокировок"  // ⬅️ НОВЫЙ
          // ...
          }
      }
      
      var color: Color {
          switch self {
          case .bypass: return .warningOrange  // ⬅️ НОВЫЙ
          // ...
          }
      }
  }
  ```

- [ ] **Обновить фильтрацию** для нового типа `.bypassAttempt`

#### Файл: `Core/Notifications/NotificationManager.swift`

- [ ] **Добавить `bypassEnabled: Bool` в `NotificationSettings`**
  ```swift
  struct NotificationSettings: Codable, Equatable {
      var securityEnabled: Bool = true
      var familyEnabled: Bool = true
      var vpnEnabled: Bool = true
      var aiEnabled: Bool = true
      var bypassEnabled: Bool = true  // ⬅️ НОВАЯ настройка!
      // ...
  }
  ```

- [ ] **Добавить проверку `settings.bypassEnabled`** перед отправкой push-уведомления
  ```swift
  // В detectBypassAttempt или где отправляются push
  if settings.bypassEnabled {  // ⬅️ Только если включено
      NotificationManager.shared.sendLocalNotification(...)
  }
  ```

#### Файл: `Screens/NotificationSettingsScreen.swift`

- [ ] **Добавить toggle "Попытки обхода"** в секцию типов уведомлений
  ```swift
  NotificationToggle(
      title: "Попытки обхода",  // ⬅️ НОВЫЙ toggle
      subtitle: "Уведомления о заблокированных попытках обхода",
      icon: "🚨",
      isOn: $settings.bypassEnabled  // ⬅️ Можно отключить!
  )
  ```

---

### 📊 Этап 6: Интеграция с отчетами

#### Файл: `Screens/02_FamilyScreen.swift` (FamilyReportsModal)

- [ ] **Добавить секцию "🚨 ПОПЫТКИ ОБХОДА"** в модал отчетов
  ```swift
  VStack(alignment: .leading, spacing: Spacing.m) {
      Text("🚨 ПОПЫТКИ ОБХОДА")
          .font(.h3)
          .foregroundColor(.warningOrange)
      
      // Статистика
      HStack(spacing: Spacing.m) {
          VStack(alignment: .leading, spacing: 4) {
              Text("Попыток сегодня")
                  .font(.caption)
                  .foregroundColor(.textSecondary)
              Text("\(bypassAttemptsToday)")
                  .font(.bodyBold)
                  .foregroundColor(.textPrimary)
          }
          
          Spacer()
          
          VStack(alignment: .trailing, spacing: 4) {
              Text("Всего за неделю")
                  .font(.caption)
                  .foregroundColor(.textSecondary)
              Text("\(bypassAttemptsWeek)")
                  .font(.bodyBold)
                  .foregroundColor(.warningOrange)
          }
      }
      
      // Детализация по типам (с заменой названий)
      VStack(spacing: Spacing.s) {
          bypassAttemptRow(icon: "🕶️", title: "Скрытый режим", count: 15, blocked: 15)  // ⬅️ НОВОЕ название!
          bypassAttemptRow(icon: "🧅", title: "Tor", count: 8, blocked: 8)
          bypassAttemptRow(icon: "🔀", title: "Скрытие IP (адрес)", count: 6, blocked: 6)  // ⬅️ Обновленное
      }
      
      // Кнопка "Посмотреть историю"
      Button(action: {
          // Открыть BypassAttemptsHistoryModal
      }) {
          Text("📊 Посмотреть историю")
              .font(.body)
              .foregroundColor(.primaryBlue)
              .frame(maxWidth: .infinity)
              .padding(Spacing.m)
              .background(Color.primaryBlue.opacity(0.1))
              .cornerRadius(CornerRadius.medium)
      }
  }
  ```

- [ ] **Создать `BypassAttemptsHistoryModal`** (опционально, для детальной истории)

---

### 🔧 Этап 7: Обновление ParentalControlManager

#### Файл: `Core/Managers/ParentalControlManager.swift`

- [ ] **Добавить функцию `getBypassStats(childId:completion:)`**
  ```swift
  func getBypassStats(
      childId: String? = nil,
      completion: @escaping (Result<BypassStatsResponse, Error>) -> Void
  ) {
      // Загрузка статистики обхода из API
  }
  ```

- [ ] **Добавить функцию `applyBypassProtection(...)`**
  ```swift
  func applyBypassProtection(
      childId: String,
      incognito: Bool,
      tor: Bool,
      proxy: Bool,
      completion: ((Bool, String?) -> Void)? = nil
  ) {
      // Применение настроек защиты от обхода
  }
  ```

- [ ] **Добавить функцию `detectBypassAttempt(...)`**
  ```swift
  func detectBypassAttempt(
      type: BypassType,
      childId: String,
      completion: ((Bool) -> Void)? = nil
  ) {
      // Обнаружение попытки обхода
      // Создание уведомления
      // Отправка push (если включено)
  }
  ```

- [ ] **Добавить функцию `saveBypassAttempt(_:BypassAttempt)`**
  - Сохранение попытки обхода в историю

- [ ] **Добавить enum `BypassType`** с `displayName`
  - Использовать для отображения в UI

---

## 🎯 Порядок выполнения

### Приоритет 1 (Базовые изменения):
1. ✅ Рефакторинг VPN экрана (упростить секцию)
2. ✅ Добавление 7-й карточки в родительский контроль
3. ✅ Создание модала FamilyBypassProtectionModal

### Приоритет 2 (Интеграция):
4. ✅ Замена терминов (глобальная)
5. ✅ Система уведомлений (тип, фильтр, настройки)
6. ✅ Интеграция с отчетами

### Приоритет 3 (API и данные):
7. ✅ Обновление ParentalControlManager
8. ✅ Загрузка статистики из API

---

## 📊 Итоговая структура

### VPN экран:
```
VPNScreen:
└── 🌐 Обнаружение сторонних VPN (упрощенная секция)
    └── Toggle: [Включено / Выключено]
```

### Родительский контроль (7 карточек):
```
Родительский контроль:
├── 1. 🔒 Блокировка контента (красный)
├── 2. ⏱️ Управление временем (синий)
├── 3. 👀 Мониторинг (фиолетовый)
├── 4. 📍 Геолокация (зеленый)
├── 5. 📊 Отчёты (оранжевый)
├── 6. ⚙️ Дополнительно (серый)
└── 7. 🚨 Защита от обхода (желтый) ⬅️ НОВАЯ
    └── Toggle: [ON / OFF]
```

### Модал защиты от обхода:
```
FamilyBypassProtectionModal:
├── 🕶️ Детекция Скрытого режима → "Приватный режим браузера"
├── 🧅 Детекция Tor → "Анонимный браузер"
├── 🔀 Детекция Proxy → "Скрытие IP (адрес)"
└── 📊 Статистика попыток обхода
```

### Уведомления:
```
NotificationsScreen:
├── Фильтр "Обход" ⬅️ НОВЫЙ
└── Уведомления типа .bypassAttempt

NotificationSettingsScreen:
└── Toggle "Попытки обхода" ⬅️ Можно отключить push!
```

---

## ✅ Готово к реализации!

Все задачи структурированы и готовы к выполнению по порядку.

