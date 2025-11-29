# 🚨 План рефакторинга "Защита от обхода"

## 📋 Содержание
1. [Анализ структуры карточек](#анализ-структуры-карточек)
2. [План изменений VPN экрана](#план-изменений-vpn-экрана)
3. [План добавления 7-й карточки](#план-добавления-7-й-карточки)
4. [Интеграция с отчетами](#интеграция-с-отчетами)
5. [Система уведомлений](#система-уведомлений)

---

## 🎨 Анализ структуры карточек

### Существующие 6 карточек:

| # | Иконка | Название | Цвет карточки | Цвет border | Badge цвет | Высота |
|---|--------|----------|---------------|-------------|------------|--------|
| 1 | 🔒 | Блокировка контента | `.red.opacity(0.2)` | `.red.opacity(0.4)` | `.successGreen` | 190 |
| 2 | ⏱️ | Управление временем | `.blue.opacity(0.2)` | `.blue.opacity(0.4)` | `.warningOrange` | 190 |
| 3 | 👀 | Мониторинг | `.purple.opacity(0.2)` | `.purple.opacity(0.4)` | `.successGreen` | 190 |
| 4 | 📍 | Геолокация | `.green.opacity(0.2)` | `.green.opacity(0.4)` | `.successGreen` | 190 |
| 5 | 📊 | Отчёты | `.orange.opacity(0.2)` | `.orange.opacity(0.4)` | `.dangerRed` | 190 |
| 6 | ⚙️ | Дополнительно | `.gray.opacity(0.2)` | `.gray.opacity(0.4)` | `.warningOrange` | 190 |

### Структура карточки `FamilyParentalControlCard`:

```swift
FamilyParentalControlCard(
    icon: String,              // Эмодзи иконка
    title: String,             // Название (может быть многострочным с \n)
    statusBadge: String,       // Badge в верхнем правом углу
    statusText: String,        // Статус (например, "✅ 3 активно")
    metric: String,            // Метрика (например, "1245 заблокировано")
    cardColor: Color,          // Цвет фона карточки
    borderColor: Color,        // Цвет границы (НЕ используется, только для справки)
    badgeColor: Color,         // Цвет badge
    isEnabled: Binding<Bool>,  // Toggle состояние
    action: () -> Void         // Действие при клике
)
```

### Компоненты карточки (по порядку сверху вниз):

1. **Badge** (верхний правый угол) - высота 20px
   - `statusBadge` текст
   - Фон: `badgeColor.opacity(0.2)`
   - Граница: `badgeColor.opacity(0.5)`

2. **Spacer()** - заполняет пространство

3. **Иконка** - размер 28, высота 32px
   - `Text(icon)`

4. **Название** - `font(.caption)`, высота 32px, multilineTextAlignment(.center), lineLimit(2)
   - `Text(title)`

5. **Статус** - `font(.captionSmall)`, высота 14px, lineLimit(1)
   - `Text(statusText)`

6. **Метрика** - `font(.captionSmall)`, высота 14px, lineLimit(1)
   - `Text(metric)`

7. **Spacer(minLength: 4)**

8. **Toggle** - высота 24px
   - `HStack` с "ON"/"OFF" текстом и кастомным toggle
   - Toggle градиент: `[Color(hex: "#8B5CF6"), Color(hex: "#A78BFA")]` когда ON
   - Toggle фон: `[Color.backgroundMedium, Color.backgroundMedium.opacity(0.5)]` когда OFF

**Общая высота карточки:** 190px  
**Padding:** `.horizontal(8)`, `.vertical(10)`  
**Border:** только когда `isEnabled == true`, золотая граница `Color.secondaryGold.opacity(0.5)`, ширина 2px

---

## 🔄 План изменений VPN экрана

### Что удаляем:
- ❌ Удалить карточку `bypassProtectionCard` полностью
- ❌ Удалить компонент `BypassDetectionItem`
- ❌ Удалить детекции: Инкогнито, Tor, Proxy

### Что оставляем:
- ✅ Детекцию VPN (но в упрощенном виде)
- ✅ Переименовать секцию в "Обнаружение сторонних VPN"

### Новая структура VPN экрана:

```
VPNScreen:
├── VPN Status Card
├── Connection Info Card
├── Battery Saving Tip Card
├── Server Selection Card
├── Security Features Card
├── Statistics Card
├── Quick Actions Card
├── Antivirus Card
└── 🌐 Обнаружение сторонних VPN (НОВАЯ упрощенная секция)
    ├── Заголовок: "🌐 Обнаружение сторонних VPN"
    ├── Описание: "Обнаружение других VPN для защиты ALADDIN VPN"
    └── Детекция VPN:
        ├── Статус: Включено/Выключено
        └── Toggle для включения/выключения
```

### Реализация новой секции:

```swift
// MARK: - Third-Party VPN Detection Card

private var thirdPartyVPNDetectionCard: some View {
    VStack(spacing: Spacing.m) {
        HStack {
            Text("🌐 Обнаружение сторонних VPN")
                .font(.h3)
                .foregroundColor(.textPrimary)
            
            Spacer()
        }
        
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text("Обнаружение других VPN")
                    .font(.body)
                    .foregroundColor(.textPrimary)
                
                Text("NordVPN, ExpressVPN, Surfshark и др.")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
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

## ➕ План добавления 7-й карточки

### 7. 🚨 Защита от обхода (НОВАЯ)

#### Параметры карточки:

```swift
FamilyParentalControlCard(
    icon: "🚨",
    title: "Защита от\nобхода",
    statusBadge: "\(bypassAttemptsToday) попыток",
    statusText: "🚫 \(bypassAttemptsBlocked) заблокировано",
    metric: "\(bypassDetectionActive)/3 активно",  // Инкогнито, Tor, Proxy
    cardColor: .yellow.opacity(0.2),  // ⚠️ Желтый/янтарный цвет (новый!)
    borderColor: .yellow.opacity(0.4),  // Для справки
    badgeColor: bypassAttemptsToday > 0 ? .dangerRed : .successGreen,  // Красный если есть попытки
    isEnabled: $isBypassProtectionEnabled,
    action: { showBypassProtectionModal = true }
)
```

#### Цветовая схема:
- **Фон карточки:** `.yellow.opacity(0.2)` - мягкий желтый фон
- **Граница:** `.secondaryGold.opacity(0.5)` когда включено (как у всех карточек)
- **Badge цвет:** 
  - `.dangerRed` если есть попытки обхода сегодня
  - `.successGreen` если попыток нет

#### State переменные для новой карточки:

```swift
// Состояния для новой карточки
@State private var isBypassProtectionEnabled: Bool = true
@State private var bypassAttemptsToday: Int = 0
@State private var bypassAttemptsWeek: Int = 47
@State private var bypassAttemptsBlocked: Int = 47  // Все заблокированы
@State private var bypassDetectionActive: Int = 3  // 3 из 3 активно (Инкогнито, Tor, Proxy)
@State private var showBypassProtectionModal: Bool = false
```

#### Интеграция в сетку:

**Вариант 1: Сетка 2x4 (рекомендуется)**
- Изменить сетку с `count: 2` на динамическую сетку
- 7 карточек в 2 колонки: первые 6 в сетке 2x3, 7-я в отдельной строке (полная ширина)

**Вариант 2: Сетка 2x3 + отдельная карточка**
- Оставить сетку 2x3 для первых 6 карточек
- Добавить 7-ю карточку после сетки (полная ширина)

**Вариант 3: Сетка 2x4 + перенос**
- Все 7 карточек в сетке 2x4, 7-я автоматически переносится

**Рекомендую Вариант 1 или 2** для лучшей визуальной иерархии.

---

## 📊 Интеграция с отчетами

### Карточка "Отчёты" - добавить секцию "Попытки обхода"

В модале `FamilyReportsModal` добавить новую секцию:

```swift
// В FamilyReportsModal.swift

// Новая секция после существующих секций
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
    
    // Детализация по типам обхода
    VStack(spacing: Spacing.s) {
        bypassAttemptRow(icon: "🕶️", title: "Инкогнито", count: 15, blocked: 15)
        bypassAttemptRow(icon: "🧅", title: "Tor", count: 8, blocked: 8)
        bypassAttemptRow(icon: "🔀", title: "Proxy", count: 6, blocked: 6)
    }
    
    // Кнопка "Посмотреть историю"
    Button(action: {
        // Открыть детальную историю попыток обхода
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

### История попыток обхода:

Создать новый модал `BypassAttemptsHistoryModal`:

```swift
struct BypassAttemptsHistoryModal: View {
    @Binding var isPresented: Bool
    @State private var bypassHistory: [BypassAttempt] = []
    
    struct BypassAttempt: Identifiable {
        let id: UUID
        let type: BypassType  // .incognito, .tor, .proxy
        let timestamp: Date
        let blocked: Bool
        let deviceName: String
    }
    
    enum BypassType: String {
        case incognito = "Инкогнито"
        case tor = "Tor"
        case proxy = "Proxy"
        
        var icon: String {
            switch self {
            case .incognito: return "🕶️"
            case .tor: return "🧅"
            case .proxy: return "🔀"
            }
        }
    }
}
```

---

## 🔔 Система уведомлений о попытках обхода

### Что будет с уведомлениями?

**НЕ на главном экране!** Вместо этого:

1. **В экране уведомлений** (`NotificationsScreen`)
   - Новый тип уведомлений: `.bypassAttempt`
   - Показывается в фильтре "Угрозы" или отдельный фильтр "Обход"

2. **Push-уведомления** (через NotificationManager)
   - Мгновенное уведомление при попытке обхода
   - Формат: "🚨 Попытка обхода: [тип] заблокирована"

3. **Badge на карточке**
   - На карточке "Защита от обхода" показывается количество попыток
   - Обновляется в реальном времени

### Реализация уведомлений:

#### 1. Расширить `NotificationType`:

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
        case .bypassAttempt: return .warningOrange  // Оранжевый для обхода
        }
    }
}
```

#### 2. Создать уведомление при обнаружении попытки:

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
    
    // Создаем уведомление
    let notification = Notification(
        id: UUID(),
        type: .bypassAttempt,
        title: "🚨 Попытка обхода заблокирована",
        message: "\(type.rawValue) был заблокирован для \(childId)",
        time: formatTime(Date()),
        isRead: false
    )
    
    // Отправляем через NotificationManager
    NotificationManager.shared.sendNotification(notification)
    
    // Push-уведомление
    NotificationManager.shared.sendPushNotification(
        title: "🚨 Попытка обхода",
        body: "\(type.rawValue) заблокирован",
        userInfo: ["type": "bypass", "bypassType": type.rawValue]
    )
    
    completion?(true)
}
```

#### 3. Добавить фильтр в `NotificationsScreen`:

```swift
// В NotificationsScreen.swift

enum NotificationFilter: String, CaseIterable {
    case all = "Все"
    case threat = "Угрозы"
    case bypass = "Обход"  // ⬅️ НОВЫЙ фильтр
    case success = "Успех"
    case info = "Информация"
    case warning = "Предупреждение"
}
```

---

## 📝 Создание модала FamilyBypassProtectionModal

### Структура модала:

```swift
struct FamilyBypassProtectionModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    
    // Manager для обработки защиты от обхода
    @StateObject private var manager = ParentalControlManager.shared
    
    // Выбранный ребёнок
    @AppStorage("parental_selected_child") private var selectedChild: String = "Маша"
    
    // Состояния для 3 переключателей с сохранением в UserDefaults
    @AppStorage("bypass_incognito_enabled") private var isIncognitoDetectionEnabled: Bool = true
    @AppStorage("bypass_tor_enabled") private var isTorDetectionEnabled: Bool = true
    @AppStorage("bypass_proxy_enabled") private var isProxyDetectionEnabled: Bool = true
    
    // Статистика
    @State private var attemptsToday: Int = 0
    @State private var attemptsWeek: Int = 47
    @State private var attemptsBlocked: Int = 47
    
    // Детализация по типам
    @State private var incognitoAttempts: Int = 15
    @State private var torAttempts: Int = 8
    @State private var proxyAttempts: Int = 6
    
    var body: some View {
        FamilyModalBaseView(
            title: "🚨 Защита от обхода",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Детекция Инкогнито
                FamilyContentBlockItem(
                    icon: "🕶️",
                    title: "Детекция Инкогнито",
                    description: "6 браузеров: Safari, Chrome, Firefox, Edge, Opera, Brave",
                    isEnabled: $isIncognitoDetectionEnabled
                )
                
                // 2. Детекция Tor
                FamilyContentBlockItem(
                    icon: "🧅",
                    title: "Детекция Tor",
                    description: "Блокировка Tor браузера и .onion сайтов",
                    isEnabled: $isTorDetectionEnabled
                )
                
                // 3. Детекция Proxy
                FamilyContentBlockItem(
                    icon: "🔀",
                    title: "Детекция Proxy",
                    description: "HTTP, HTTPS, SOCKS прокси-серверы",
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
                    
                    // Детализация по типам
                    VStack(spacing: Spacing.xs) {
                        HStack {
                            Text("🕶️ Инкогнито")
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
                            Text("🔀 Proxy")
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
        .onAppear {
            loadBypassStatistics()
        }
        .onChange(of: isIncognitoDetectionEnabled) { newValue in
            applyBypassProtection()
        }
        .onChange(of: isTorDetectionEnabled) { newValue in
            applyBypassProtection()
        }
        .onChange(of: isProxyDetectionEnabled) { newValue in
            applyBypassProtection()
        }
    }
    
    private func loadBypassStatistics() {
        // Загружаем статистику из API или UserDefaults
        manager.getBypassStats(childId: selectedChild) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let stats):
                    attemptsToday = stats.today
                    attemptsWeek = stats.week
                    attemptsBlocked = stats.blocked
                    incognitoAttempts = stats.incognito
                    torAttempts = stats.tor
                    proxyAttempts = stats.proxy
                case .failure(let error):
                    print("❌ Ошибка загрузки статистики обхода: \(error.localizedDescription)")
                }
            }
        }
    }
    
    private func applyBypassProtection() {
        manager.applyBypassProtection(
            childId: selectedChild,
            incognito: isIncognitoDetectionEnabled,
            tor: isTorDetectionEnabled,
            proxy: isProxyDetectionEnabled
        )
    }
}
```

---

## 📋 Чек-лист изменений

### ⚠️ ВАЖНО: Замена терминов
**Везде заменить "Инкогнито" на "Скрытый режим":**
- ✅ Более простое и понятное название
- ✅ Понятно для всех пользователей
- ✅ Заменяем во всех файлах: код, модалы, уведомления

### Файл: `Screens/03_VPNScreen.swift`

- [ ] Удалить `bypassProtectionCard` (строки 721-784)
- [ ] Удалить `BypassDetectionItem` struct (строки 789-854)
- [ ] Удалить состояние `@State private var bypassDetectionEnabled: Bool`
- [ ] Добавить новую секцию `thirdPartyVPNDetectionCard`
- [ ] Добавить состояние `@State private var isThirdPartyVPNDetectionEnabled: Bool = true`
- [ ] Переименовать заголовок в "🌐 Обнаружение сторонних VPN"
- [ ] Упростить UI: только описание и toggle

### Файл: `Screens/02_FamilyScreen.swift`

- [ ] Добавить состояние для новой карточки:
  ```swift
  @State private var isBypassProtectionEnabled: Bool = true
  @State private var showBypassProtectionModal: Bool = false
  @State private var bypassAttemptsToday: Int = 0
  @State private var bypassAttemptsWeek: Int = 47
  @State private var bypassAttemptsBlocked: Int = 47
  @State private var bypassDetectionActive: Int = 3
  ```
- [ ] Изменить сетку с `count: 2` на `count: 2` (оставить как есть)
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
- [ ] Использовать `FamilyModalBaseView` как базовый компонент
- [ ] Реализовать загрузку статистики из API

### Файл: `Screens/02_FamilyScreen.swift` (FamilyReportsModal)

- [ ] Добавить секцию "🚨 ПОПЫТКИ ОБХОДА" в модал отчетов
- [ ] Показывать статистику попыток обхода
- [ ] Добавить кнопку "Посмотреть историю"
- [ ] Создать `BypassAttemptsHistoryModal` для детальной истории

### Файл: `Core/Managers/ParentalControlManager.swift`

- [ ] Добавить функцию `getBypassStats(childId:completion:)`
- [ ] Добавить функцию `applyBypassProtection(childId:incognito:tor:proxy:completion:)`
- [ ] Добавить функцию `detectBypassAttempt(type:childId:completion:)`
- [ ] Добавить функцию `saveBypassAttempt(_:BypassAttempt)`

### Файл: `ViewModels/NotificationsViewModel.swift` или `Core/Notifications/NotificationManager.swift`

- [ ] Добавить `NotificationType.bypassAttempt`
- [ ] Добавить логику создания уведомлений при обнаружении попыток обхода
- [ ] Добавить push-уведомления для попыток обхода

### Файл: `Screens/12_NotificationsScreen.swift`

- [ ] Добавить фильтр `.bypass` в `NotificationFilter`
- [ ] Обновить фильтрацию уведомлений для нового типа

---

## 🎯 Итоговая структура

### VPN экран:
```
VPNScreen:
├── ... (существующие секции)
└── 🌐 Обнаружение сторонних VPN
    └── Toggle для включения/выключения детекции VPN
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
```

### Модал защиты от обхода:
```
FamilyBypassProtectionModal:
├── 🕶️ Детекция Инкогнито (toggle)
├── 🧅 Детекция Tor (toggle)
├── 🔀 Детекция Proxy (toggle)
└── 📊 Статистика попыток обхода
```

### Уведомления:
```
NotificationsScreen:
├── Фильтр "Обход" ⬅️ НОВЫЙ
└── Уведомления типа .bypassAttempt

Push-уведомления:
└── Мгновенное уведомление при попытке обхода
```

---

## ✅ Что будет с предыдущей карточкой на VPN странице?

### После распределения:

1. **Удаляется:** Вся карточка `bypassProtectionCard` (4 детекции)
2. **Заменяется:** Упрощенной секцией "🌐 Обнаружение сторонних VPN"
   - Только детекция VPN
   - Простой toggle
   - Без статистики (статистика переносится в родительский контроль)

### Визуальное сравнение:

**БЫЛО:**
```
🚨 Защита от обхода
├── 0 попыток сегодня | 47 всего | 100% заблокировано
├── 🌐 Детекция VPN (accordion)
├── 🕶️ Детекция Инкогнито (accordion)
├── 🧅 Детекция Tor (accordion)
└── 🔀 Детекция Proxy (accordion)
```

**СТАНЕТ:**
```
🌐 Обнаружение сторонних VPN
├── Описание: "Обнаружение других VPN для защиты ALADDIN VPN"
└── Toggle: Включено/Выключено
```

---

## 📱 Про "объединить статистику на главном экране"

**Уточнение:** На главном экране (`MainScreen`) нет статистики попыток обхода.

**Вместо этого:**
1. **Уведомления** — показываются в экране `NotificationsScreen`
2. **Badge на карточке** — количество попыток видно на карточке "Защита от обхода"
3. **Push-уведомления** — мгновенные уведомления при обнаружении попыток

**Если нужна статистика на главном:**
- Можно добавить маленький badge на карточке "ALADDIN FAMILY" в `MainScreen`
- Например: "🚨 2 попытки обхода заблокированы"

---

## 🚀 Порядок выполнения

1. ✅ Создать модал `FamilyBypassProtectionModal`
2. ✅ Добавить состояния в `FamilyScreen` и `ParentalControlScreen`
3. ✅ Добавить 7-ю карточку в родительский контроль (желтый цвет)
4. ✅ Рефакторинг VPN экрана (упростить секцию)
5. ✅ Интеграция с отчетами (добавить секцию в модал отчетов)
6. ✅ Система уведомлений (расширить типы уведомлений)
7. ✅ Обновить `ParentalControlManager` (добавить функции)

---

## 🎨 Цветовая схема для 7-й карточки

**Рекомендуемый цвет:**
```swift
cardColor: .yellow.opacity(0.2)  // Мягкий желтый фон
// или
cardColor: Color(hex: "F59E0B").opacity(0.2)  // Янтарный (warningOrange)
```

**Badge цвет динамический:**
```swift
badgeColor: bypassAttemptsToday > 0 ? .dangerRed : .successGreen
```

**Текст badge:**
```swift
statusBadge: bypassAttemptsToday > 0 ? "🚨 \(bypassAttemptsToday)" : "✅ 0"
```

---

## 📝 Пример кода для 7-й карточки

```swift
// 7. Защита от обхода (НОВАЯ)
FamilyParentalControlCard(
    icon: "🚨",
    title: "Защита от\nобхода",
    statusBadge: bypassAttemptsToday > 0 ? "🚨 \(bypassAttemptsToday)" : "✅ 0",
    statusText: "🚫 \(bypassAttemptsBlocked) заблокировано",
    metric: "\(bypassDetectionActive)/3 активно",
    cardColor: Color(hex: "F59E0B").opacity(0.2),  // Янтарный (warningOrange)
    borderColor: Color(hex: "F59E0B").opacity(0.4),
    badgeColor: bypassAttemptsToday > 0 ? .dangerRed : .successGreen,
    isEnabled: $isBypassProtectionEnabled,
    action: { showBypassProtectionModal = true }
)
```

---

## ✅ Готово к реализации!

Все детали описаны. Можно начинать реализацию по порядку выполнения.
