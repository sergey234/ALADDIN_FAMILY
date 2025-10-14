# 📱 ALADDIN Family Security - iOS App

**Версия:** 1.0.0  
**iOS:** 14.0+  
**Язык:** Swift 5.9+  
**UI Framework:** SwiftUI  
**Архитектура:** MVVM

---

## 🎯 **ОПИСАНИЕ**

Мобильное приложение для комплексной защиты семьи в интернете с функциями VPN, родительского контроля, аналитики угроз и AI помощника.

---

## 📁 **СТРУКТУРА ПРОЕКТА**

```
ALADDIN_iOS/
├── App/                          # Точка входа приложения
│   ├── ALADDINApp.swift         # @main App
│   ├── AppDelegate.swift        # App lifecycle
│   └── SceneDelegate.swift      # Scene management
│
├── Core/                         # Основная функциональность
│   ├── Networking/              # API клиент
│   │   ├── APIClient.swift
│   │   ├── Endpoints.swift
│   │   └── NetworkError.swift
│   ├── Storage/                 # Локальное хранилище
│   │   ├── DatabaseManager.swift
│   │   └── KeychainManager.swift
│   ├── VPN/                     # VPN функциональность
│   │   ├── VPNManager.swift
│   │   └── WireGuardTunnel.swift
│   └── Utilities/               # Вспомогательные утилиты
│       ├── Logger.swift
│       └── Constants.swift
│
├── Features/                     # Экраны и фичи (14 штук)
│   ├── Auth/                    # Авторизация
│   │   ├── Views/
│   │   │   ├── LoginView.swift
│   │   │   └── RegisterView.swift
│   │   ├── ViewModels/
│   │   │   └── AuthViewModel.swift
│   │   └── Models/
│   │       └── User.swift
│   │
│   ├── Main/                    # 1. Главный экран
│   │   ├── Views/
│   │   │   └── MainScreen.swift
│   │   ├── ViewModels/
│   │   │   └── MainViewModel.swift
│   │   └── Models/
│   │       └── MainStatus.swift
│   │
│   ├── Family/                  # 2. Семейный экран
│   │   ├── Views/
│   │   │   ├── FamilyScreen.swift
│   │   │   └── FamilyMemberCard.swift
│   │   ├── ViewModels/
│   │   │   └── FamilyViewModel.swift
│   │   └── Models/
│   │       ├── FamilyMember.swift
│   │       └── FamilyStatus.swift
│   │
│   ├── Protection/              # 3. VPN защита
│   │   ├── Views/
│   │   │   ├── ProtectionScreen.swift
│   │   │   └── ServerListView.swift
│   │   ├── ViewModels/
│   │   │   └── ProtectionViewModel.swift
│   │   └── Models/
│   │       ├── VPNStatus.swift
│   │       └── VPNServer.swift
│   │
│   ├── Analytics/               # 4. Аналитика
│   │   ├── Views/
│   │   │   ├── AnalyticsScreen.swift
│   │   │   └── ChartView.swift
│   │   ├── ViewModels/
│   │   │   └── AnalyticsViewModel.swift
│   │   └── Models/
│   │       └── ThreatStats.swift
│   │
│   ├── Settings/                # 5. Настройки
│   │   ├── Views/
│   │   │   ├── SettingsScreen.swift
│   │   │   └── SettingsSectionView.swift
│   │   ├── ViewModels/
│   │   │   └── SettingsViewModel.swift
│   │   └── Models/
│   │       └── Settings.swift
│   │
│   ├── ParentalControl/         # 6. Родительский контроль
│   │   ├── Views/
│   │   │   ├── ParentalControlScreen.swift
│   │   │   └── ControlToggleView.swift
│   │   ├── ViewModels/
│   │   │   └── ParentalControlViewModel.swift
│   │   └── Models/
│   │       └── ParentalSettings.swift
│   │
│   ├── AIAssistant/             # 7. AI помощник
│   │   ├── Views/
│   │   │   ├── AIAssistantScreen.swift
│   │   │   └── ChatMessageView.swift
│   │   ├── ViewModels/
│   │   │   └── AIAssistantViewModel.swift
│   │   └── Models/
│   │       └── ChatMessage.swift
│   │
│   ├── Profile/                 # 8. Профиль
│   │   ├── Views/
│   │   │   └── ProfileScreen.swift
│   │   ├── ViewModels/
│   │   │   └── ProfileViewModel.swift
│   │   └── Models/
│   │       └── UserProfile.swift
│   │
│   ├── Devices/                 # 9. Устройства
│   │   ├── Views/
│   │   │   ├── DevicesScreen.swift
│   │   │   └── DeviceCard.swift
│   │   ├── ViewModels/
│   │   │   └── DevicesViewModel.swift
│   │   └── Models/
│   │       └── Device.swift
│   │
│   ├── Child/                   # 10. Детский интерфейс
│   │   ├── Views/
│   │   │   └── ChildInterfaceScreen.swift
│   │   ├── ViewModels/
│   │   │   └── ChildViewModel.swift
│   │   └── Models/
│   │       └── Achievement.swift
│   │
│   ├── Elderly/                 # 11. Интерфейс для пожилых
│   │   ├── Views/
│   │   │   └── ElderlyInterfaceScreen.swift
│   │   ├── ViewModels/
│   │   │   └── ElderlyViewModel.swift
│   │   └── Models/
│   │       └── EmergencyContact.swift
│   │
│   ├── Tariffs/                 # 12. Тарифы
│   │   ├── Views/
│   │   │   ├── TariffsScreen.swift
│   │   │   └── TariffCard.swift
│   │   ├── ViewModels/
│   │   │   └── TariffsViewModel.swift
│   │   └── Models/
│   │       └── Tariff.swift
│   │
│   ├── Info/                    # 13. Информация
│   │   ├── Views/
│   │   │   └── InfoScreen.swift
│   │   ├── ViewModels/
│   │   │   └── InfoViewModel.swift
│   │   └── Models/
│   │       └── AppInfo.swift
│   │
│   └── Notifications/           # 14. Уведомления
│       ├── Views/
│       │   ├── NotificationsScreen.swift
│       │   └── NotificationRow.swift
│       ├── ViewModels/
│       │   └── NotificationsViewModel.swift
│       └── Models/
│           └── Notification.swift
│
├── Shared/                       # Переиспользуемые компоненты
│   ├── Components/              # UI компоненты
│   │   ├── Buttons/
│   │   │   ├── PrimaryButton.swift
│   │   │   └── SecondaryButton.swift
│   │   ├── Cards/
│   │   │   ├── StatusCard.swift
│   │   │   └── FamilyCard.swift
│   │   └── Modals/
│   │       └── AlertModal.swift
│   ├── Extensions/              # Swift расширения
│   │   ├── Color+Extensions.swift
│   │   ├── View+Extensions.swift
│   │   └── String+Extensions.swift
│   └── Styles/                  # Стили и темы
│       ├── Colors.swift
│       ├── Fonts.swift
│       └── Shadows.swift
│
├── Resources/                    # Ресурсы
│   ├── Assets.xcassets/         # Изображения, иконки
│   ├── Localizable.strings      # Переводы RU + EN
│   └── Info.plist               # Конфигурация приложения
│
└── Tests/                        # Тесты
    ├── UnitTests/               # Unit тесты
    └── UITests/                 # UI тесты
```

---

## 🎯 **ОСНОВНЫЕ ПРИНЦИПЫ АРХИТЕКТУРЫ**

### **MVVM (Model-View-ViewModel)**

```
┌─────────────┐
│    View     │ ← Отображение (SwiftUI)
│  (Screen)   │   Только UI, никакой логики
└─────┬───────┘
      │ binding (@Published)
      ↓
┌─────────────┐
│  ViewModel  │ ← Логика и состояние
│   (Logic)   │   ObservableObject, бизнес-логика
└─────┬───────┘
      │ data flow
      ↓
┌─────────────┐
│    Model    │ ← Данные
│   (Data)    │   Struct, простые данные
└─────────────┘
```

**Преимущества:**
- ✅ Чистый код (каждый файл делает одно)
- ✅ Легко тестировать (ViewModel отдельно)
- ✅ Переиспользование (View может быть в разных местах)
- ✅ SwiftUI идеально подходит

---

## 📋 **14 ЭКРАНОВ (FEATURES)**

| № | Feature | HTML Источник | Приоритет |
|---|---------|---------------|-----------|
| 1 | Main | 01_main_screen.html | 🔴 HIGH |
| 2 | Family | 03_family_screen.html | 🔴 HIGH |
| 3 | Protection | 02_protection_screen.html | 🔴 HIGH |
| 4 | Analytics | 04_analytics_screen.html | 🔴 HIGH |
| 5 | Settings | 05_settings_screen.html | 🟠 MEDIUM |
| 6 | ParentalControl | 14_parental_control_screen.html | 🔴 HIGH |
| 7 | AIAssistant | 08_ai_assistant.html | 🟠 MEDIUM |
| 8 | Profile | 11_profile_screen.html | 🟠 MEDIUM |
| 9 | Devices | 12_devices_screen.html | 🟠 MEDIUM |
| 10 | Child | 06_child_interface.html | 🟡 LOW |
| 11 | Elderly | 07_elderly_interface.html | 🟡 LOW |
| 12 | Tariffs | 09_tariffs_screen.html | 🟠 MEDIUM |
| 13 | Info | 10_info_screen.html | 🟡 LOW |
| 14 | Notifications | 08_notifications_screen.html | 🟠 MEDIUM |

**Каждая папка содержит:**
- `Views/` - SwiftUI views (UI код)
- `ViewModels/` - ObservableObject (логика)
- `Models/` - Struct (данные)

---

## 🔧 **ТРЕБОВАНИЯ**

### **Минимальные версии:**
- iOS 14.0+
- Xcode 15.0+
- Swift 5.9+

### **Зависимости (будут добавлены через SPM):**
```
dependencies: [
    .package(url: "Alamofire", from: "5.0.0"),
    .package(url: "Realm", from: "10.0.0"),
    .package(url: "KeychainAccess", from: "4.0.0"),
    .package(url: "Kingfisher", from: "7.0.0"),
]
```

---

## 🚀 **КАК НАЧАТЬ РАЗРАБОТКУ**

### **Шаг 1: Открыть проект**
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
open ALADDIN.xcodeproj  # (будет создан позже)
```

### **Шаг 2: Выбрать Feature для работы**
Например, начинаем с MainScreen:
```
Features/Main/
├── Views/MainScreen.swift        ← Создаём UI
├── ViewModels/MainViewModel.swift ← Создаём логику
└── Models/MainStatus.swift       ← Создаём модель данных
```

### **Шаг 3: Использовать HTML как ТЗ**
```
1. Открыть: mobile/wireframes/01_main_screen.html
2. Посмотреть дизайн
3. Скопировать в SwiftUI:
   - Цвета из CSS
   - Размеры из CSS
   - Структуру из HTML
   - Логику из JavaScript
```

### **Шаг 4: Подключить к API**
```swift
// В ViewModel
func loadData() async {
    let status = try await APIClient.shared.get("/family/status")
    self.status = status
}
```

### **Шаг 5: Запустить и протестировать**
```
Cmd + R → Запуск в симуляторе
Проверить что работает как в HTML
```

---

## 📐 **ДИЗАЙН-СИСТЕМА**

### **Цвета:**
```swift
// Shared/Styles/Colors.swift
extension Color {
    static let primaryBlue = Color(hex: "#2E5BFF")
    static let secondaryGold = Color(hex: "#FCD34D")
    static let successGreen = Color(hex: "#10B981")
    static let dangerRed = Color(hex: "#EF4444")
    static let warningOrange = Color(hex: "#F59E0B")
    
    static let backgroundDark = Color(hex: "#0F172A")
    static let surfaceDark = Color(hex: "#1E293B")
    static let textPrimary = Color.white
    static let textSecondary = Color(hex: "#94A3B8")
}
```

### **Шрифты:**
```swift
// Shared/Styles/Fonts.swift
extension Font {
    static let h1 = Font.system(size: 32, weight: .bold)
    static let h2 = Font.system(size: 24, weight: .bold)
    static let h3 = Font.system(size: 20, weight: .semibold)
    static let body = Font.system(size: 16, weight: .regular)
    static let caption = Font.system(size: 14, weight: .regular)
    static let small = Font.system(size: 12, weight: .regular)
}
```

### **Отступы:**
```swift
// Shared/Styles/Spacing.swift
enum Spacing {
    static let xxs: CGFloat = 4
    static let xs: CGFloat = 8
    static let s: CGFloat = 12
    static let m: CGFloat = 16
    static let l: CGFloat = 24
    static let xl: CGFloat = 32
    static let xxl: CGFloat = 48
}
```

---

## 🔗 **API ИНТЕГРАЦИЯ**

### **Base URL:**
```swift
let baseURL = "https://api.aladdin.family/v1/"
```

### **Аутентификация:**
```swift
// Bearer token в заголовках
headers["Authorization"] = "Bearer \(token)"
```

### **Основные endpoints:**
```
GET  /family/status       → Статус семьи
GET  /family/members      → Список членов
POST /vpn/connect         → Подключить VPN
GET  /analytics/dashboard → Дашборд аналитики
POST /ai/chat             → Чат с AI
```

---

## ✅ **ЧЕКЛИСТ РАЗРАБОТКИ**

### **Для каждого экрана:**

- [ ] Создать View (SwiftUI)
- [ ] Создать ViewModel (ObservableObject)
- [ ] Создать Models (Struct)
- [ ] Подключить к API
- [ ] Добавить навигацию
- [ ] Сделать responsive
- [ ] Добавить Accessibility labels
- [ ] Написать Unit tests
- [ ] Code review
- [ ] Merge в main

---

## 🧪 **ТЕСТИРОВАНИЕ**

### **Unit Tests:**
```bash
Cmd + U  # Запустить все тесты
```

### **UI Tests:**
```bash
Cmd + U  # В схеме UITests
```

### **Покрытие:**
Минимум 70% code coverage

---

## 📚 **ДОКУМЕНТАЦИЯ**

- **API:** См. Swagger документацию на https://api.aladdin.family/docs
- **Дизайн:** См. HTML wireframes в `mobile/wireframes/`
- **ТЗ:** См. `TECHNICAL_SPECIFICATION.md`

---

## 👥 **КОМАНДА**

**iOS Разработчики:**
- iOS Developer #1 (Lead)
- iOS Developer #2

**Code Review:** обязательно перед merge

---

## 📞 **КОНТАКТЫ**

**Product Owner:** sergej.hlystov@aladdin.family  
**Technical Lead:** TBD  
**Вопросы:** Telegram @aladdin_dev

---

## 🎯 **ТЕКУЩИЙ СТАТУС**

**Прогресс:** 0% (структура готова)  
**Следующий шаг:** Создание базовых файлов и начало разработки

---

**Создано:** 11 октября 2025  
**Автор:** ALADDIN Security Team  
**Статус:** ✅ Готово к разработке



