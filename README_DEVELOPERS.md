# 👨‍💻 README ДЛЯ РАЗРАБОТЧИКОВ - ALADDIN iOS

**Версия:** 1.0.0  
**Дата:** 2025-11-25  
**Платформа:** iOS 15.2+  
**Язык:** Swift 5.0+  
**UI Framework:** SwiftUI

---

## 📋 ОГЛАВЛЕНИЕ

1. [Быстрый старт](#быстрый-старт)
2. [Требования](#требования)
3. [Установка](#установка)
4. [Структура проекта](#структура-проекта)
5. [Архитектура](#архитектура)
6. [Запуск проекта](#запуск-проекта)
7. [Тестирование](#тестирование)
8. [Конфигурация](#конфигурация)
9. [Работа с API](#работа-с-api)
10. [Добавление новых экранов](#добавление-новых-экранов)
11. [Локализация](#локализация)
12. [Отладка](#отладка)
13. [Сборка для продакшена](#сборка-для-продакшена)

---

## 🚀 БЫСТРЫЙ СТАРТ

### 1. Клонирование репозитория
```bash
cd /path/to/project
git clone <repository_url>
cd ALADDIN_iOS
```

### 2. Открытие проекта
```bash
open ALADDIN.xcodeproj
```

### 3. Выбор схемы
- Выберите схему `ALADDIN` в Xcode
- Выберите симулятор (например, iPhone 13 Pro Max)

### 4. Запуск
- Нажмите `Cmd + R` или кнопку "Run"

---

## 📦 ТРЕБОВАНИЯ

### Системные требования
- **macOS:** 12.0 (Monterey) или выше
- **Xcode:** 14.0 или выше
- **Swift:** 5.7 или выше
- **iOS Deployment Target:** 15.2

### Зависимости
Проект использует только нативные фреймворки Apple:
- SwiftUI
- Combine
- NetworkExtension
- LocalAuthentication
- CryptoKit

**Внешние зависимости отсутствуют** - проект полностью нативный.

---

## 🔧 УСТАНОВКА

### 1. Установка Xcode
```bash
# Установите Xcode из App Store или с сайта Apple Developer
```

### 2. Настройка проекта
```bash
# Откройте проект
open ALADDIN.xcodeproj

# Проверьте настройки:
# - Team: Выберите вашу команду разработчиков
# - Bundle Identifier: family.aladdin.ios
# - Deployment Target: iOS 15.2
```

### 3. Настройка API
Откройте `Core/Config/AppConfig.swift` и проверьте:
```swift
static let apiBaseURL: String = "https://aladdin-ai.ru/api"
```

### 4. Первый запуск
1. Выберите симулятор iPhone 13 Pro Max
2. Нажмите `Cmd + R`
3. Дождитесь компиляции и запуска

---

## 📁 СТРУКТУРА ПРОЕКТА

```
ALADDIN_iOS/
├── ALADDIN.xcodeproj/          # Xcode проект
├── ALADDIN/                    # Основное приложение
│   ├── ALADDINApp.swift        # Точка входа
│   ├── ALADDINPacketTunnel/   # Network Extension для VPN
│   └── Info.plist             # Конфигурация приложения
│
├── Screens/                    # Экраны приложения (40+)
│   ├── 01_MainScreen.swift
│   ├── 02_FamilyScreen.swift
│   ├── 03_VPNScreen.swift
│   └── ...
│
├── Core/                       # Основные модули
│   ├── Config/                # Конфигурация
│   │   └── AppConfig.swift
│   ├── Models/                # Модели данных
│   │   └── APIModels.swift
│   ├── Network/               # Сетевая логика
│   │   ├── NetworkManager.swift
│   │   └── APIService.swift
│   ├── VPN/                   # VPN функциональность
│   │   └── VPNManager.swift
│   ├── Security/              # Безопасность
│   │   └── SecurityManager.swift
│   ├── Localization/          # Локализация
│   │   └── LocalizationManager.swift
│   └── ...
│
├── ViewModels/                 # View Models (MVVM)
│   ├── MainViewModel.swift
│   ├── FamilyViewModel.swift
│   └── ...
│
├── Shared/                     # Общие компоненты
│   ├── Components/            # UI компоненты
│   │   ├── Buttons/
│   │   ├── Cards/
│   │   ├── Modals/
│   │   └── ...
│   └── Styles/                # Стили
│
├── Tests/                     # Тесты
│   ├── VPNIntegrationTest.swift
│   └── ...
│
├── Resources/                  # Ресурсы
│   ├── Localizable.strings    # Локализация
│   └── ...
│
├── Assets.xcassets/           # Графические ресурсы
│   ├── AppIcon.appiconset/
│   └── ...
│
└── docs/                      # Документация
    ├── API_DOCUMENTATION.md
    └── ...
```

---

## 🏗️ АРХИТЕКТУРА

### MVVM (Model-View-ViewModel)

Проект использует архитектуру MVVM:

```
View (SwiftUI) → ViewModel → Model/API
```

**Пример:**
```swift
// View
struct MainScreen: View {
    @StateObject private var viewModel = MainViewModel()
    
    var body: some View {
        Text(viewModel.status)
    }
}

// ViewModel
class MainViewModel: ObservableObject {
    @Published var status: String = ""
    
    func loadData() {
        APIService.shared.getVPNStatus { result in
            // Обработка результата
        }
    }
}
```

### Основные компоненты

1. **Screens** - SwiftUI экраны (View)
2. **ViewModels** - Бизнес-логика (ViewModel)
3. **Core** - Основные модули (Model/Services)
4. **Shared** - Переиспользуемые компоненты

---

## ▶️ ЗАПУСК ПРОЕКТА

### Запуск в симуляторе

1. Откройте Xcode
2. Выберите схему `ALADDIN`
3. Выберите симулятор (например, iPhone 13 Pro Max)
4. Нажмите `Cmd + R`

### Запуск на устройстве

1. Подключите iPhone/iPad
2. Выберите устройство в Xcode
3. Настройте Code Signing (выберите Team)
4. Нажмите `Cmd + R`

### Запуск Network Extension

Network Extension (VPN) работает только на реальном устройстве:
1. Подключите устройство
2. Запустите приложение
3. Перейдите в VPN экран
4. Включите VPN

---

## 🧪 ТЕСТИРОВАНИЕ

### Запуск тестов

```bash
# В Xcode: Cmd + U
# Или через терминал:
xcodebuild test -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13 Pro Max'
```

### Структура тестов

```
Tests/
├── VPNIntegrationTest.swift      # Тесты VPN
├── APIServiceTests.swift         # Тесты API
└── ...
```

### Написание тестов

```swift
import XCTest
@testable import ALADDIN

class VPNManagerTests: XCTestCase {
    func testVPNConnection() {
        let manager = VPNManager.shared
        // Тест логика
    }
}
```

---

## ⚙️ КОНФИГУРАЦИЯ

### AppConfig.swift

Основной файл конфигурации: `Core/Config/AppConfig.swift`

```swift
// API URL
static let apiBaseURL: String = "https://aladdin-ai.ru/api"

// Использовать Mock API (только для DEBUG)
static let useMockAPI: Bool = false

// Режим отладки
static let isDebugMode: Bool = true
```

### Endpoints

Все endpoints определены в `AppConfig.Endpoint`:

```swift
enum Endpoint {
    static let vpnStatus = "/vpn/status"
    static let vpnConnect = "/vpn/connect"
    // ...
}
```

---

## 🌐 РАБОТА С API

### Использование APIService

```swift
// Получить статус VPN
APIService.shared.getVPNStatus { result in
    switch result {
    case .success(let status):
        print("VPN подключен: \(status.isConnected)")
    case .failure(let error):
        print("Ошибка: \(error)")
    }
}
```

### Async/Await (новые методы)

```swift
// IoT API использует async/await
Task {
    do {
        let status = try await APIService.shared.getIoTStatus(homeId: "home_123")
        print("IoT статус: \(status)")
    } catch {
        print("Ошибка: \(error)")
    }
}
```

### Обработка ошибок

```swift
APIService.shared.getVPNStatus { result in
    switch result {
    case .success(let data):
        // Успех
        break
    case .failure(let error):
        if let networkError = error as? NetworkError {
            switch networkError {
            case .unauthorized:
                // Требуется авторизация
                break
            case .notFound:
                // Ресурс не найден
                break
            default:
                break
            }
        }
    }
}
```

---

## 📱 ДОБАВЛЕНИЕ НОВЫХ ЭКРАНОВ

### Шаг 1: Создание экрана

Создайте файл в `Screens/`:

```swift
import SwiftUI

struct NewScreen: View {
    var body: some View {
        Text("Новый экран")
    }
}
```

### Шаг 2: Добавление навигации

В `Core/Navigation/NavigationManager.swift`:

```swift
enum Screen {
    case newScreen
    // ...
}
```

### Шаг 3: Регистрация в ContentView

В `ContentView.swift` или главном экране:

```swift
NavigationLink(destination: NewScreen()) {
    Text("Открыть новый экран")
}
```

### Шаг 4: Добавление в Xcode проект

1. Правый клик на `Screens/` в Xcode
2. "Add Files to ALADDIN..."
3. Выберите созданный файл
4. Убедитесь, что файл добавлен в target `ALADDIN`

---

## 🌍 ЛОКАЛИЗАЦИЯ

### Добавление перевода

1. Откройте `Resources/Localizable.strings`
2. Добавьте ключ:

```swift
"new_key" = "Новый текст";
```

### Использование в коде

```swift
let localizationManager = LocalizationManager.shared
let text = localizationManager.localized("new_key")
```

### Поддерживаемые языки

- Русский (ru) - основной
- Английский (en) - в разработке

---

## 🐛 ОТЛАДКА

### Логирование

```swift
// В DEBUG режиме
#if DEBUG
print("Debug: \(message)")
#endif
```

### Breakpoints

1. Установите breakpoint (клик на номере строки)
2. Запустите приложение
3. При достижении breakpoint выполнение остановится

### Console в Xcode

- Откройте Console: `View → Debug Area → Activate Console`
- Или `Cmd + Shift + Y`

### Network Debugging

В `NetworkManager.swift` включите логирование:

```swift
#if DEBUG
print("Request: \(url)")
print("Response: \(response)")
#endif
```

---

## 📦 СБОРКА ДЛЯ ПРОДАКШЕНА

### 1. Настройка Code Signing

1. Откройте проект в Xcode
2. Выберите target `ALADDIN`
3. Перейдите в "Signing & Capabilities"
4. Выберите Team
5. Включите "Automatically manage signing"

### 2. Создание Archive

1. В Xcode: `Product → Archive`
2. Дождитесь завершения
3. Откроется Organizer

### 3. Загрузка в App Store Connect

1. В Organizer выберите Archive
2. Нажмите "Distribute App"
3. Выберите "App Store Connect"
4. Следуйте инструкциям

### 4. Проверка перед загрузкой

- [ ] Все тесты пройдены
- [ ] Нет предупреждений компилятора
- [ ] Code Signing настроен
- [ ] Версия и build number обновлены

---

## 📚 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

### Документация

- **API Документация:** `docs/API_DOCUMENTATION.md`
- **TODO Анализ:** `docs/COMPLETE_TODO_ANALYSIS.md`
- **План реализации:** `docs/ML_SYSTEM_IMPLEMENTATION_PLAN.md`

### Полезные ссылки

- **Apple Developer:** https://developer.apple.com
- **SwiftUI Документация:** https://developer.apple.com/documentation/swiftui
- **Network Extension:** https://developer.apple.com/documentation/networkextension

### Поддержка

- **Telegram:** [@aladdin_support_bot](https://t.me/aladdin_support_bot)
- **Телефон:** +7 (927) 005-15-77
- **FAQ:** https://aladdin-ai.ru/help-faq.html

---

## 🔧 ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ

### Q: Как добавить новый API endpoint?

A: Добавьте метод в `APIService.swift`:

```swift
func getNewData(completion: @escaping (Result<NewDataResponse, Error>) -> Void) {
    networkManager.get(endpoint: "/new/endpoint", completion: completion)
}
```

### Q: Как изменить базовый URL API?

A: Измените в `Core/Config/AppConfig.swift`:

```swift
static let apiBaseURL: String = "https://your-api.com/api"
```

### Q: VPN не работает в симуляторе?

A: Network Extension работает только на реальном устройстве. Используйте iPhone/iPad для тестирования VPN.

### Q: Как добавить новый экран?

A: См. раздел [Добавление новых экранов](#добавление-новых-экранов)

### Q: Как изменить язык приложения?

A: Измените в настройках iOS или через `LocalizationManager`:

```swift
LocalizationManager.shared.setLanguage("en")
```

---

## 📝 ЛИЦЕНЗИЯ

Проект ALADDIN iOS - проприетарное программное обеспечение.

---

**Версия:** 1.0.0  
**Последнее обновление:** 2025-11-25  
**Автор:** ALADDIN Development Team

