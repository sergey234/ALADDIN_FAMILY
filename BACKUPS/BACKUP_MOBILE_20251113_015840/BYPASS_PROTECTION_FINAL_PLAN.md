# 🚨 Финальный план рефакторинга "Защита от обхода"

## ✅ Утвержденные решения

### 1. Система уведомлений
- ✅ **Только один тип:** уведомления показываются ТОЛЬКО в экране `NotificationsScreen`
- ✅ **Push-уведомления:** можно отключить через настройки (`NotificationSettingsScreen`)
- ❌ **БЕЗ:** push-уведомлений в Notification Center (если отключены)
- ❌ **БЕЗ:** badge на иконке приложения (если отключены)

### 2. 7-я карточка "Защита от обхода"
- ✅ **Toggle:** можно включить/выключить (как у всех остальных 6 карточек)
- ✅ **Цвет:** желтый/янтарный (отличается от остальных)

### 3. Замена терминов
- ✅ **"Инкогнито" → "Скрытый режим"** (более простое и понятное)
- ✅ Заменить во всех файлах: код, модалы, уведомления, описания

---

## 📋 Детальный план

### 1. Рефакторинг VPN экрана (упрощение)

**Что удаляем:**
```
❌ Вся карточка "🚨 Защита от обхода"
   ├── Статистика (3 колонки)
   └── 4 детекции (VPN + Инкогнито + Tor + Proxy)
```

**Что добавляем:**
```
✅ Простая секция "🌐 Обнаружение сторонних VPN"
   ├── Описание: "Обнаружение других VPN для защиты ALADDIN VPN"
   ├── Список: "NordVPN, ExpressVPN, Surfshark и др."
   └── Toggle: [Включено / Выключено]
```

**Код:**
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

---

### 2. 7-я карточка "Защита от обхода" (родительский контроль)

**Параметры карточки:**
```swift
// 7. Защита от обхода (НОВАЯ)
FamilyParentalControlCard(
    icon: "🚨",
    title: "Защита от\nобхода",
    statusBadge: bypassAttemptsToday > 0 ? "🚨 \(bypassAttemptsToday)" : "✅ 0",
    statusText: "🚫 \(bypassAttemptsBlocked) заблокировано",
    metric: "\(bypassDetectionActive)/3 активно",  // Скрытый режим, Tor, Proxy
    cardColor: Color(hex: "F59E0B").opacity(0.2),  // Янтарный (новый цвет!)
    borderColor: Color(hex: "F59E0B").opacity(0.4),
    badgeColor: bypassAttemptsToday > 0 ? .dangerRed : .successGreen,
    isEnabled: $isBypassProtectionEnabled,  // ⬅️ TOGGLE можно включить/выключить!
    action: { showBypassProtectionModal = true }
)
```

**Состояния:**
```swift
@State private var isBypassProtectionEnabled: Bool = true  // ⬅️ Можно включить/выключить
@State private var showBypassProtectionModal: Bool = false
@State private var bypassAttemptsToday: Int = 0
@State private var bypassAttemptsWeek: Int = 47
@State private var bypassAttemptsBlocked: Int = 47
@State private var bypassDetectionActive: Int = 3  // 3 из 3 активно
```

---

### 3. Модал "Защита от обхода" (с заменой терминов)

**ВАЖНО: Заменяем "Инкогнито" на "Скрытый режим"**

```swift
struct FamilyBypassProtectionModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool  // ⬅️ Главный toggle карточки
    
    // Состояния для 3 переключателей
    @AppStorage("bypass_incognito_enabled") private var isIncognitoDetectionEnabled: Bool = true
    @AppStorage("bypass_tor_enabled") private var isTorDetectionEnabled: Bool = true
    @AppStorage("bypass_proxy_enabled") private var isProxyDetectionEnabled: Bool = true
    
    var body: some View {
        FamilyModalBaseView(
            title: "🚨 Защита от обхода",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Детекция Скрытого режима (было "Инкогнито")
                FamilyContentBlockItem(
                    icon: "🕶️",
                    title: "Детекция Скрытого режима",  // ⬅️ НОВОЕ название!
                    description: "Приватный режим браузера",  // ⬅️ Короткое пояснение (2-3 слова)
                    isEnabled: $isIncognitoDetectionEnabled
                )
                
                // 2. Детекция Tor
                FamilyContentBlockItem(
                    icon: "🧅",
                    title: "Детекция Tor",
                    description: "Анонимный браузер",  // ⬅️ Короткое пояснение (2-3 слова)
                    isEnabled: $isTorDetectionEnabled
                )
                
                // 3. Детекция Proxy
                FamilyContentBlockItem(
                    icon: "🔀",
                    title: "Детекция Proxy",
                    description: "Скрытие IP (адрес)",  // ⬅️ Пояснение на одной строке
                    isEnabled: $isProxyDetectionEnabled
                )
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Статистика
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("📊 Статистика за неделю:")
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    HStack(spacing: Spacing.m) {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Попыток сегодня")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Text("\(attemptsToday)")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                        
                        Spacer()
                        
                        VStack(alignment: .trailing, spacing: 4) {
                            Text("Всего за неделю")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Text("\(attemptsWeek)")
                                .font(.bodyBold)
                                .foregroundColor(.warningOrange)
                        }
                    }
                    
                    HStack {
                        Text("Заблокировано")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text("\(attemptsBlocked)")
                            .font(.bodyBold)
                            .foregroundColor(.successGreen)
                    }
                    
                    // Детализация по типам (с заменой названий)
                    VStack(spacing: Spacing.xs) {
                        HStack {
                            Text("🕶️ Скрытый режим")  // ⬅️ НОВОЕ название!
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(incognitoAttempts)")
                                .font(.caption)
                                .foregroundColor(.textPrimary)
                        }
                        
                        HStack {
                            Text("🧅 Tor")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(torAttempts)")
                                .font(.caption)
                                .foregroundColor(.textPrimary)
                        }
                        
                        HStack {
                            Text("🔀 Скрытие IP (адрес)")  // ⬅️ Обновленное пояснение
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(proxyAttempts)")
                                .font(.caption)
                                .foregroundColor(.textPrimary)
                        }
                    }
                    .padding(.top, Spacing.s)
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
            }
        }
    }
}
```

---

### 4. Система уведомлений (только в экране уведомлений)

**ВАЖНО:** Уведомления показываются ТОЛЬКО в `NotificationsScreen`, push-уведомления можно отключить.

#### 4.1. Расширение типов уведомлений

```swift
// В NotificationsViewModel.swift или NotificationManager.swift

enum NotificationType: String {
    case threat = "Угроза"
    case success = "Успех"
    case info = "Информация"
    case warning = "Предупреждение"
    case bypassAttempt = "Обход"  // ⬅️ НОВЫЙ тип
    
    var icon: String {
        switch self {
        case .threat: return "🚨"
        case .success: return "✅"
        case .info: return "ℹ️"
        case .warning: return "⚠️"
        case .bypassAttempt: return "🚨"  // Или "🔒"
        }
    }
    
    var color: Color {
        switch self {
        case .threat: return .dangerRed
        case .success: return .successGreen
        case .info: return .infoBlue
        case .warning: return .warningOrange
        case .bypassAttempt: return .warningOrange
        }
    }
}
```

#### 4.2. Добавление фильтра "Обход" в NotificationsScreen

```swift
// В NotificationsScreen.swift

enum NotificationFilter: String, CaseIterable {
    case all = "Все"
    case threat = "Угрозы"
    case bypass = "Обход"  // ⬅️ НОВЫЙ фильтр
    case success = "Успех"
    case info = "Информация"
    case warning = "Предупреждение"
    
    var subtitle: String {
        switch self {
        case .all: return "Все уведомления"
        case .threat: return "Угрозы и опасности"
        case .bypass: return "Попытки обхода блокировок"  // ⬅️ НОВЫЙ
        case .success: return "Успешные действия"
        case .info: return "Информационные"
        case .warning: return "Предупреждения"
        }
    }
    
    var color: Color {
        switch self {
        case .all: return .secondaryGold
        case .threat: return .dangerRed
        case .bypass: return .warningOrange  // ⬅️ НОВЫЙ
        case .success: return .successGreen
        case .info: return .infoBlue
        case .warning: return .warningOrange
        }
    }
}
```

#### 4.3. Создание уведомления при попытке обхода (БЕЗ push, если отключено)

```swift
// В ParentalControlManager.swift или BypassProtectionService.swift

func detectBypassAttempt(
    type: BypassType,
    childId: String,
    completion: ((Bool) -> Void)? = nil
) {
    // Обнаружили попытку обхода
    let attempt = BypassAttempt(
        id: UUID(),
        type: type,
        timestamp: Date(),
        blocked: true,
        deviceName: getDeviceName(for: childId)
    )
    
    // Сохраняем в историю
    saveBypassAttempt(attempt)
    
    // Создаем уведомление ТОЛЬКО для экрана уведомлений
    let notification = Notification(
        id: UUID(),
        type: .bypassAttempt,
        title: "🚨 Попытка обхода заблокирована",
        message: "\(type.displayName) был заблокирован для \(childId)",  // ⬅️ Используем displayName вместо rawValue
        time: formatTime(Date()),
        isRead: false
    )
    
    // Добавляем в список уведомлений (ViewModel)
    NotificationsViewModel.shared.addNotification(notification)
    
    // Push-уведомление ТОЛЬКО если включено в настройках
    let settings = NotificationManager.shared.notificationSettings
    if settings.bypassEnabled {  // ⬅️ Новая настройка!
        NotificationManager.shared.sendLocalNotification(
            title: "🚨 Попытка обхода",
            body: "\(type.displayName) заблокирован",
            category: .security,
            userInfo: [
                "type": "bypass",
                "bypass_type": type.rawValue,
                "child_id": childId
            ]
        )
    }
    
    completion?(true)
}
```

**ВАЖНО:** `type.displayName` используется для показа "Скрытый режим" вместо "Инкогнито":

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

---

### 5. Настройки уведомлений (возможность отключения push)

**Добавить новую настройку в `NotificationSettings`:**
```swift
// В NotificationManager.swift или NotificationSettings.swift

struct NotificationSettings: Codable, Equatable {
    var securityEnabled: Bool = true
    var familyEnabled: Bool = true
    var vpnEnabled: Bool = true
    var aiEnabled: Bool = true
    var bypassEnabled: Bool = true  // ⬅️ НОВАЯ настройка!
    var soundEnabled: Bool = true
    var badgeEnabled: Bool = true
    var quietModeEnabled: Bool = false
    var quietHoursEnabled: Bool = false
    var quietHoursStart: String = "22:00"
    var quietHoursEnd: String = "08:00"
    var importantOnlyMode: Bool = false
    var doNotDisturbMode: Bool = false
    var doNotDisturbUntil: Date? = nil
    var highPriorityOnly: Bool = false
    var maxNotificationsPerHour: Int? = nil
}
```

**Добавить toggle в `NotificationSettingsScreen`:**
```swift
// В NotificationSettingsScreen.swift

NotificationToggle(
    title: "Попытки обхода",  // ⬅️ НОВЫЙ toggle
    subtitle: "Уведомления о заблокированных попытках обхода",
    icon: "🚨",
    isOn: $settings.bypassEnabled  // ⬅️ Можно отключить!
)
```

**Проверка перед отправкой push:**
```swift
// В detectBypassAttempt (см. выше)

if settings.bypassEnabled {  // ⬅️ Только если включено
    NotificationManager.shared.sendLocalNotification(...)
}
```

---

## 📝 Чек-лист изменений

### Файл: `Screens/03_VPNScreen.swift`

- [ ] Удалить `bypassProtectionCard` (строки 721-784)
- [ ] Удалить `BypassDetectionItem` struct (строки 789-854)
- [ ] Удалить состояние `@State private var bypassDetectionEnabled: Bool`
- [ ] Добавить новую секцию `thirdPartyVPNDetectionCard` (см. код выше)
- [ ] Добавить состояние `@State private var isThirdPartyVPNDetectionEnabled: Bool = true`

### Файл: `Screens/02_FamilyScreen.swift`

- [ ] Добавить состояния для новой карточки (см. выше)
- [ ] Добавить 7-ю карточку после существующих 6 карточек
- [ ] Добавить `.sheet(isPresented: $showBypassProtectionModal)`
- [ ] Обновить функцию `loadParentalControlStats()` для загрузки статистики обхода

### Файл: `Screens/07_ParentalControlScreen.swift`

- [ ] Добавить те же состояния что и в FamilyScreen
- [ ] Добавить 7-ю карточку в сетку `parentalControlCards`
- [ ] Добавить `.sheet(isPresented: $showBypassProtectionModal)`
- [ ] Обновить `loadParentalControlStats()` для загрузки статистики обхода

### Новый файл: `Screens/Modals/FamilyBypassProtectionModal.swift`

- [ ] Создать новый файл
- [ ] Реализовать `FamilyBypassProtectionModal` (см. структуру выше)
- [ ] Использовать "Скрытый режим" вместо "Инкогнито" ⬅️ ВАЖНО!
- [ ] Использовать `FamilyModalBaseView` как базовый компонент
- [ ] Реализовать загрузку статистики из API

### Файл: `Core/Managers/ParentalControlManager.swift`

- [ ] Добавить функцию `getBypassStats(childId:completion:)`
- [ ] Добавить функцию `applyBypassProtection(childId:incognito:tor:proxy:completion:)`
- [ ] Добавить функцию `detectBypassAttempt(type:childId:completion:)`
- [ ] Добавить функцию `saveBypassAttempt(_:BypassAttempt)`
- [ ] Использовать `BypassType.displayName` вместо `rawValue` ⬅️ ВАЖНО!

### Файл: `ViewModels/NotificationsViewModel.swift`

- [ ] Добавить `NotificationType.bypassAttempt`
- [ ] Добавить метод `addNotification(_:Notification)` для добавления уведомлений в список
- [ ] Обновить фильтрацию для нового типа `.bypassAttempt`

### Файл: `Core/Notifications/NotificationManager.swift`

- [ ] Добавить `bypassEnabled: Bool` в `NotificationSettings`
- [ ] Добавить проверку `settings.bypassEnabled` перед отправкой push-уведомления
- [ ] Обновить метод `sendLocalNotification` для учета новых настроек

### Файл: `Screens/NotificationSettingsScreen.swift`

- [ ] Добавить новый toggle "Попытки обхода" в секцию типов уведомлений
- [ ] Подключить к `settings.bypassEnabled`

### Файл: `Screens/12_NotificationsScreen.swift`

- [ ] Добавить фильтр `.bypass` в `NotificationFilter`
- [ ] Обновить фильтрацию уведомлений для нового типа

### Файл: `Screens/02_FamilyScreen.swift` (FamilyReportsModal)

- [ ] Добавить секцию "🚨 ПОПЫТКИ ОБХОДА" в модал отчетов
- [ ] Показывать статистику попыток обхода
- [ ] Использовать "Скрытый режим" вместо "Инкогнито" ⬅️ ВАЖНО!
- [ ] Добавить кнопку "Посмотреть историю"
- [ ] Создать `BypassAttemptsHistoryModal` для детальной истории

### ⚠️ ГЛОБАЛЬНАЯ ЗАМЕНА ТЕРМИНОВ

**Заменить во всех файлах:**
- [ ] "Инкогнито" → "Скрытый режим"
- [ ] "Детекция Инкогнито" → "Детекция Скрытого режима"
- [ ] Использовать `BypassType.displayName` вместо `rawValue` в UI

**Файлы для замены:**
- [ ] `Screens/03_VPNScreen.swift`
- [ ] `Screens/02_FamilyScreen.swift`
- [ ] `Screens/07_ParentalControlScreen.swift`
- [ ] `Screens/Modals/FamilyBypassProtectionModal.swift` (новый)
- [ ] `Core/Managers/ParentalControlManager.swift`
- [ ] `ViewModels/NotificationsViewModel.swift`
- [ ] Все модалы и компоненты, использующие термин "Инкогнито"

---

## ✅ Итоговая структура

### VPN экран:
```
VPNScreen:
├── ... (существующие секции)
└── 🌐 Обнаружение сторонних VPN (упрощенная секция)
    ├── Описание
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
    ├── Badge: количество попыток
    ├── Статус: "X заблокировано"
    ├── Метрика: "3/3 активно"
    └── Toggle: [ON / OFF] ⬅️ Можно включить/выключить!
```

### Модал защиты от обхода:
```
FamilyBypassProtectionModal:
├── 🕶️ Детекция Скрытого режима (toggle) ⬅️ НОВОЕ название!
│   └── "Приватный режим браузера" ⬅️ Пояснение (2-3 слова)
├── 🧅 Детекция Tor (toggle)
│   └── "Анонимный браузер" ⬅️ Пояснение (2-3 слова)
├── 🔀 Детекция Proxy (toggle)
│   └── "Скрытие IP (адрес)" ⬅️ Пояснение на одной строке
└── 📊 Статистика попыток обхода
```

### Уведомления:
```
NotificationsScreen:
├── Фильтр "Обход" ⬅️ НОВЫЙ фильтр
└── Уведомления типа .bypassAttempt
    └── "🚨 Попытка обхода заблокирована"
        "Скрытый режим был заблокирован" ⬅️ НОВОЕ название!

NotificationSettingsScreen:
└── Toggle "Попытки обхода" ⬅️ Можно отключить push-уведомления!
```

---

## 🎯 Порядок выполнения

1. ✅ **Глобальная замена терминов** - заменить "Инкогнито" → "Скрытый режим"
2. ✅ **Рефакторинг VPN экрана** - упростить секцию
3. ✅ **Создание 7-й карточки** - добавить в родительский контроль
4. ✅ **Создание модала** - `FamilyBypassProtectionModal`
5. ✅ **Система уведомлений** - добавить тип и фильтр
6. ✅ **Настройки уведомлений** - добавить toggle для отключения push
7. ✅ **Интеграция с отчетами** - добавить секцию в модал отчетов

---

## ✅ Готово к реализации!

Все требования учтены:
- ✅ Уведомления только в экране уведомлений
- ✅ Push-уведомления можно отключить
- ✅ 7-я карточка с toggle (можно включить/выключить)
- ✅ "Инкогнито" заменено на "Скрытый режим"
