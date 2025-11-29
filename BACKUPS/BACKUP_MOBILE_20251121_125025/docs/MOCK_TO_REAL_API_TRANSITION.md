# 🔄 ПЕРЕХОД С MOCK API НА РЕАЛЬНЫЙ СЕРВЕР

**Дата:** 15 ноября 2025  
**Статус:** ✅ **АЛГОРИТМ ГОТОВ**

---

## ✅ ВАЖНО: МОКИ УДАЛЯТЬ НЕ НУЖНО!

**Mock API остается в проекте** и может использоваться для:
- Тестирования без сервера
- Разработки новых функций
- Отладки
- Демонстрации функциональности

**Переключение происходит автоматически** через настройку `AppConfig.useMockAPI`.

---

## 🎯 АЛГОРИТМ ПЕРЕХОДА НА РЕАЛЬНЫЙ СЕРВЕР

### Шаг 1: Проверить URL реального сервера

**Файл:** `Core/Config/AppConfig.swift`

```swift
static let apiBaseURL: String = currentEnvironment.baseURL
```

**Проверить:**
- ✅ URL реального сервера указан правильно
- ✅ Сервер доступен и работает
- ✅ SSL сертификаты валидны

---

### Шаг 2: Отключить Mock API

**Вариант A: В коде (для Release)**

**Файл:** `Core/Config/AppConfig.swift`

```swift
static var useMockAPI: Bool {
    get {
        #if DEBUG
        // В DEBUG можно включать/выключать через UserDefaults
        if UserDefaults.standard.object(forKey: "useMockAPI") == nil {
            return false // ✅ ИЗМЕНИТЬ НА false для использования реального API
        }
        return UserDefaults.standard.bool(forKey: "useMockAPI")
        #else
        return false // В Release всегда используем реальный API
        #endif
    }
    set {
        #if DEBUG
        UserDefaults.standard.set(newValue, forKey: "useMockAPI")
        #endif
    }
}
```

**Вариант B: Через UserDefaults (в DEBUG режиме)**

```swift
// В коде или через настройки приложения
AppConfig.useMockAPI = false
```

---

### Шаг 3: Проверить переключение

**Файл:** `Core/Network/APIService.swift`

```swift
static var shared: APIService {
    #if DEBUG
    if AppConfig.useMockAPI {
        return MockAPIService.mockShared // Mock API
    }
    #endif
    // Real API Service (по умолчанию)
    let networkManager = NetworkManager()
    return APIService(networkManager: networkManager) // ✅ Реальный API
}
```

**Логика:**
- Если `AppConfig.useMockAPI == true` → используется `MockAPIService`
- Если `AppConfig.useMockAPI == false` → используется реальный `APIService`

---

### Шаг 4: Проверить настройки сети

**Файл:** `Core/Network/NetworkManager.swift`

**Проверить:**
- ✅ `baseURL` указывает на реальный сервер
- ✅ SSL Pinning настроен (если используется)
- ✅ Таймауты установлены правильно
- ✅ Сертификаты загружены

---

### Шаг 5: Протестировать подключение

**Тестовый сценарий:**

1. **Запустить приложение**
2. **Проверить первый запрос:**
   - Открыть экран Profile
   - Проверить, что данные загружаются с реального сервера
   - Проверить логи в консоли

3. **Проверить критические функции:**
   - ✅ Вход в систему
   - ✅ Загрузка профиля
   - ✅ Загрузка семьи
   - ✅ Загрузка тарифов
   - ✅ VPN статус

---

## 🔧 НАСТРОЙКА ДЛЯ РАЗНЫХ ОКРУЖЕНИЙ

### Development (разработка)

**Файл:** `Core/Config/AppConfig.swift`

```swift
enum Environment {
    case development
    case staging
    case production
    
    var baseURL: String {
        switch self {
        case .development:
            return "https://api-dev.aladdin.family/api" // ✅ Ваш dev сервер
        case .staging:
            return "https://api-staging.aladdin.family/api" // ✅ Ваш staging сервер
        case .production:
            return "https://api.aladdin.family/api" // ✅ Ваш production сервер
        }
    }
}

static let currentEnvironment: Environment = {
    #if DEBUG
    return .development // ✅ В DEBUG используем development
    #else
    return .production // ✅ В Release используем production
    #endif
}()
```

---

## 📋 ЧЕКЛИСТ ПЕРЕХОДА

### Перед переходом:

- [ ] Реальный сервер запущен и доступен
- [ ] URL сервера указан правильно в `AppConfig`
- [ ] SSL сертификаты настроены (если используется SSL Pinning)
- [ ] API endpoints соответствуют реальному серверу
- [ ] Тестовый аккаунт создан на реальном сервере

### Переход:

- [ ] Установить `AppConfig.useMockAPI = false` (или изменить по умолчанию)
- [ ] Проверить, что `AppConfig.apiBaseURL` указывает на реальный сервер
- [ ] Запустить приложение и проверить первый запрос

### После перехода:

- [ ] Протестировать все критические функции
- [ ] Проверить обработку ошибок сети
- [ ] Проверить таймауты
- [ ] Проверить SSL соединение
- [ ] Проверить логи в консоли

---

## 🎯 РЕКОМЕНДУЕМЫЙ ПОДХОД

### Для разработки:

```swift
// В DEBUG режиме можно переключаться
#if DEBUG
AppConfig.useMockAPI = true  // Использовать Mock API
// или
AppConfig.useMockAPI = false // Использовать реальный API
#endif
```

### Для Release:

```swift
// В Release всегда используется реальный API
// useMockAPI всегда возвращает false
```

---

## 🔄 ОБРАТНЫЙ ПЕРЕХОД (если нужно вернуться к Mock)

**Просто установить:**

```swift
AppConfig.useMockAPI = true
```

**Или в коде изменить по умолчанию:**

```swift
static var useMockAPI: Bool {
    get {
        #if DEBUG
        if UserDefaults.standard.object(forKey: "useMockAPI") == nil {
            return true // ✅ Вернуть Mock API по умолчанию
        }
        return UserDefaults.standard.bool(forKey: "useMockAPI")
        #else
        return false
        #endif
    }
}
```

---

## ✅ ПРЕИМУЩЕСТВА ТАКОГО ПОДХОДА

1. ✅ **Не нужно удалять код** - Mock API остается для тестирования
2. ✅ **Легкое переключение** - одна настройка
3. ✅ **Безопасность** - в Release всегда реальный API
4. ✅ **Гибкость** - можно переключаться в DEBUG режиме
5. ✅ **Тестирование** - можно тестировать с Mock и Real API

---

## 📝 ПРИМЕР ИСПОЛЬЗОВАНИЯ

### В коде приложения:

```swift
// Все ViewModels используют APIService.shared
// Переключение происходит автоматически

let apiService = APIService.shared // ✅ Автоматически выбирает Mock или Real

// Использование одинаковое для обоих случаев
apiService.getUserProfile { result in
    switch result {
    case .success(let profile):
        // Обработка успешного ответа
    case .failure(let error):
        // Обработка ошибки
    }
}
```

---

## 🎯 ИТОГ

**Алгоритм перехода:**

1. ✅ **Проверить URL** реального сервера в `AppConfig`
2. ✅ **Установить** `AppConfig.useMockAPI = false`
3. ✅ **Проверить** подключение к реальному серверу
4. ✅ **Протестировать** все функции
5. ✅ **Готово!** Система работает с реальным сервером

**Моки удалять НЕ нужно** - они остаются для тестирования и разработки.

---

**Дата создания:** 15 ноября 2025  
**Статус:** ✅ **АЛГОРИТМ ГОТОВ К ИСПОЛЬЗОВАНИЮ**



