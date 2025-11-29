# 🎯 ПЛАН ПОДКЛЮЧЕНИЯ API ДЛЯ РОДИТЕЛЬСКОГО КОНТРОЛЯ

## 📋 ЧТО МОЖНО ДЕЛАТЬ СЕЙЧАС (до подключения к серверу)

### ✅ **ЭТАП 1: ПОДГОТОВКА СТРУКТУРЫ (можно делать сейчас)**

#### 1.1. Добавить модели данных для API
```swift
// ✅ Можно делать сейчас - просто структуры данных
struct ParentalControlRulesRequest: Codable {
    let childId: String
    let ageGroup: String
    let rules: [String: Any]
}

struct ApplyBlockingRequest: Codable {
    let childId: String
    let type: String  // "website", "app", "search"
    let enabled: Bool
}

struct AccessRequestResponse: Codable {
    let requestId: String
    let app: String
    let time: String
    let reason: String
}
```

**Где:** `Core/Models/APIModels.swift`  
**Когда:** Сейчас (не требует сервера)

---

#### 1.2. Добавить методы в APIService
```swift
// ✅ Можно делать сейчас - заглушки методов
extension APIService {
    // MARK: - Parental Control API
    
    func applyParentalControlRules(
        childId: String,
        rules: [String: Any],
        completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void
    ) {
        // Сейчас: mock-ответ
        // Потом: реальный запрос к серверу
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            completion(.success(APIResponse(success: true, data: true, message: "Rules applied")))
        }
    }
    
    func handleAccessRequest(
        requestId: String,
        action: String, // "accept" или "reject"
        completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void
    ) {
        // Mock-ответ сейчас
        completion(.success(APIResponse(success: true, data: true, message: "Request \(action)ed")))
    }
    
    func getAccessRequests(
        completion: @escaping (Result<[AccessRequestResponse], Error>) -> Void
    ) {
        // Mock-данные сейчас
        let mockRequests = [
            AccessRequestResponse(requestId: "1", app: "Instagram", time: "10 мин назад", reason: "Хочу посмотреть сообщения"),
            AccessRequestResponse(requestId: "2", app: "YouTube", time: "5 мин назад", reason: "Нужно посмотреть урок")
        ]
        completion(.success(mockRequests))
    }
}
```

**Где:** `Core/Network/APIService.swift`  
**Когда:** Сейчас (с mock-ответами, потом заменим на реальные)

---

#### 1.3. Создать обработчики действий
```swift
// ✅ Можно делать сейчас - логика обработки
class ParentalControlManager {
    private let apiService: APIService
    
    func applyBlocking(childId: String, type: String, enabled: Bool) {
        // 1. Сохраняем в UserDefaults (уже работает)
        // 2. Вызываем API (mock сейчас, реальный потом)
        apiService.applyBlocking(childId: childId, type: type, enabled: enabled) { result in
            switch result {
            case .success:
                print("✅ Блокировка применена")
            case .failure(let error):
                print("❌ Ошибка: \(error)")
            }
        }
    }
}
```

**Где:** Новый файл `Core/Managers/ParentalControlManager.swift`  
**Когда:** Сейчас

---

### ✅ **ЭТАП 2: ПОДКЛЮЧЕНИЕ К UI (можно делать сейчас)**

#### 2.1. Подключить обработчики к кнопкам
```swift
// ✅ В FamilyContentBlockModal
Button(action: {
    // 1. Сохраняем в UserDefaults (уже работает)
    // 2. Вызываем API через Manager (mock сейчас)
    parentalControlManager.applyBlocking(
        childId: selectedChild,
        type: "website",
        enabled: isWebsiteBlockingEnabled
    )
}) {
    // UI кнопки
}
```

**Где:** `Screens/02_FamilyScreen.swift`  
**Когда:** Сейчас (с mock API)

---

#### 2.2. Обработка запросов доступа
```swift
// ✅ В AccessRequestsModal
Button("Принять") {
    // 1. Обновляем UI
    // 2. Вызываем API (mock сейчас)
    apiService.handleAccessRequest(
        requestId: request.id,
        action: "accept"
    ) { result in
        // Обновляем список запросов
    }
}
```

**Где:** `Screens/02_FamilyScreen.swift` (AccessRequestsModal)  
**Когда:** Сейчас (с mock API)

---

## ⚠️ ЧТО ТРЕБУЕТ РЕАЛЬНОГО СЕРВЕРА

### 🔴 **ЭТАП 3: ПОДКЛЮЧЕНИЕ К РЕАЛЬНОМУ API**

#### 3.1. Заменить mock на реальные запросы
```swift
// ⚠️ ТРЕБУЕТ СЕРВЕРА
func applyParentalControlRules(...) {
    // Заменяем mock на реальный запрос:
    networkManager.post(
        endpoint: "/parental-control/apply-rules",
        body: request,
        completion: completion
    )
}
```

**Когда:** После подключения к серверу

---

#### 3.2. Получение реальных данных
```swift
// ⚠️ ТРЕБУЕТ СЕРВЕРА
func getBrowserHistory(...) {
    // Заменяем mock-данные на реальные:
    networkManager.get(
        endpoint: "/parental-control/browser-history",
        completion: completion
    )
}
```

**Когда:** После подключения к серверу

---

## 📊 ПЛАН ПО ЭТАПАМ

### ✅ **ЭТАП 1: ПОДГОТОВКА (можно делать СЕЙЧАС)**
**Цель:** Готовность структуры к подключению API

1. ✅ Добавить модели данных (`APIModels.swift`)
2. ✅ Добавить методы в `APIService` (с mock-ответами)
3. ✅ Создать `ParentalControlManager` для логики
4. ✅ Подключить обработчики к UI кнопкам
5. ✅ Тестирование с mock-данными

**Результат:** Всё работает с mock-данными, готово к подключению реального API

**Время:** 1-2 дня работы

---

### ⚠️ **ЭТАП 2: ПОДКЛЮЧЕНИЕ К СЕРВЕРУ (после готовности API)**
**Цель:** Замена mock на реальные запросы

1. ⚠️ Получить URL сервера и токены авторизации
2. ⚠️ Заменить mock-ответы на реальные HTTP-запросы
3. ⚠️ Обработка ошибок сети
4. ⚠️ Тестирование с реальным сервером

**Результат:** Полная интеграция с бэкендом

**Время:** 2-3 дня работы (зависит от готовности API)

---

## 🎯 ЧТО ДЕЛАТЬ СЕЙЧАС?

### ✅ **РЕКОМЕНДУЮ: НАЧАТЬ С ЭТАПА 1**

**Почему:**
1. ✅ Не требует сервера
2. ✅ Можно тестировать сразу
3. ✅ Когда API будет готов - просто заменим mock на реальные запросы
4. ✅ Вся логика уже будет на месте

**Что делать:**
1. Создать модели данных для родительского контроля
2. Добавить методы в `APIService` (с mock)
3. Создать `ParentalControlManager`
4. Подключить к UI

---

## 📝 КОНКРЕТНЫЙ ПЛАН ДЕЙСТВИЙ

### **ШАГ 1: Модели данных** (30 минут)
```swift
// Файл: Core/Models/APIModels.swift
// Добавить в конец файла:

// MARK: - Parental Control Models

struct ApplyBlockingRequest: Codable {
    let childId: String
    let type: BlockingType
    let enabled: Bool
}

enum BlockingType: String, Codable {
    case website
    case app
    case search
    case safesearch
}
```

### **ШАГ 2: API методы** (1 час)
```swift
// Файл: Core/Network/APIService.swift
// Добавить extension:

extension APIService {
    // MARK: - Parental Control API
    
    func applyBlocking(
        childId: String,
        type: BlockingType,
        enabled: Bool,
        completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void
    ) {
        // Mock сейчас, реальный запрос потом
        let request = ApplyBlockingRequest(childId: childId, type: type, enabled: enabled)
        
        // TODO: Заменить на реальный запрос
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
            completion(.success(APIResponse(success: true, data: true, message: "Blocking applied")))
        }
    }
}
```

### **ШАГ 3: Manager** (1 час)
```swift
// Новый файл: Core/Managers/ParentalControlManager.swift

class ParentalControlManager: ObservableObject {
    private let apiService: APIService
    
    init(apiService: APIService = APIService.shared) {
        self.apiService = apiService
    }
    
    func applyContentBlocking(
        childId: String,
        websiteBlocking: Bool,
        appBlocking: Bool,
        searchBlocking: Bool,
        safesearch: Bool
    ) {
        // Применяем все типы блокировки
        apiService.applyBlocking(childId: childId, type: .website, enabled: websiteBlocking) { _ in }
        apiService.applyBlocking(childId: childId, type: .app, enabled: appBlocking) { _ in }
        apiService.applyBlocking(childId: childId, type: .search, enabled: searchBlocking) { _ in }
        apiService.applyBlocking(childId: childId, type: .safesearch, enabled: safesearch) { _ in }
    }
}
```

### **ШАГ 4: Подключение к UI** (2 часа)
```swift
// Файл: Screens/02_FamilyScreen.swift
// В FamilyContentBlockModal добавить:

@StateObject private var parentalControlManager = ParentalControlManager()

// В onChange toggle:
.onChange(of: isWebsiteBlockingEnabled) { newValue in
    // 1. Сохраняется автоматически через @AppStorage
    // 2. Вызываем API
    parentalControlManager.applyContentBlocking(
        childId: selectedChild,
        websiteBlocking: newValue,
        // ...
    )
}
```

---

## ✅ ИТОГИ

### **Можно делать СЕЙЧАС:**
- ✅ Структуры данных (модели)
- ✅ API методы с mock-ответами
- ✅ Manager для логики
- ✅ Подключение к UI
- ✅ Тестирование с mock-данными

### **Требует сервера:**
- ⚠️ Замена mock на реальные HTTP-запросы
- ⚠️ Получение реальных данных (история, отчёты)
- ⚠️ Обработка ошибок сети

### **Преимущества подхода:**
1. ✅ Можно начинать СЕЙЧАС
2. ✅ Всё будет готово к подключению API
3. ✅ Когда API готов - просто заменяем mock
4. ✅ Можно тестировать сразу

---

## 🚀 РЕКОМЕНДАЦИЯ

**Начать с ЭТАПА 1 прямо сейчас:**
- Подготовим всю структуру
- Всё будет работать с mock-данными
- Когда API будет готов - заменим 1 строку кода

**Это правильный подход для разработки!**

