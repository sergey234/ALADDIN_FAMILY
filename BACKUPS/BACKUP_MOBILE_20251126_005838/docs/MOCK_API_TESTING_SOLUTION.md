# 🔧 РЕШЕНИЕ: Тестирование БЕЗ реального сервера

**Дата:** 14 ноября 2025  
**Проблема:** Нет реального сервера для тестирования  
**Решение:** Mock API Service

---

## 🎯 ПРОБЛЕМА

**Нужно протестировать:**
- ✅ Удаление аккаунта
- ✅ Умные уведомления
- ✅ Все основные функции
- ✅ Интеграцию с API

**Но:** Нет реального сервера

---

## ✅ РЕШЕНИЕ: Mock API Service

### Что это такое?

**Mock API Service** - это замена реального API, которая возвращает тестовые данные без реального сервера.

**Преимущества:**
- ✅ Можно тестировать без сервера
- ✅ Быстро и легко
- ✅ Можно протестировать все сценарии
- ✅ Не зависит от доступности сервера
- ✅ Можно протестировать ошибки

---

## 📋 ПЛАН РЕАЛИЗАЦИИ

### Шаг 1: Создать MockAPIService

**Файл:** `Core/Network/MockAPIService.swift`

**Что сделать:**
1. Создать класс `MockAPIService`
2. Реализовать все методы из `APIService`
3. Возвращать mock данные
4. Симулировать задержки сети
5. Симулировать ошибки (опционально)

**Время:** 1-2 часа

---

### Шаг 2: Добавить переключение между Mock и Real API

**Файл:** `Core/Config/AppConfig.swift`

**Что добавить:**
```swift
static var useMockAPI: Bool {
    #if DEBUG
    return UserDefaults.standard.bool(forKey: "useMockAPI")
    #else
    return false // В Release всегда используем реальный API
    #endif
}
```

**Время:** 15 минут

---

### Шаг 3: Обновить APIService для использования Mock

**Файл:** `Core/Network/APIService.swift`

**Что добавить:**
```swift
static var shared: APIService {
    if AppConfig.useMockAPI {
        return MockAPIService.shared
    } else {
        return RealAPIService.shared
    }
}
```

**Время:** 30 минут

---

### Шаг 4: Реализовать Mock методы

**Что нужно реализовать:**

#### 4.1. Удаление аккаунта

```swift
func deleteAccount(confirmationCode: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
    // Симулируем задержку сети
    DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
        if confirmationCode.uppercased() == "УДАЛИТЬ" || confirmationCode.uppercased() == "DELETE" {
            // Успешное удаление
            let response = APIResponse<Bool>(
                success: true,
                data: true,
                message: "Account deleted successfully"
            )
            completion(.success(response))
        } else {
            // Ошибка подтверждения
            let error = NetworkError.badRequest("Invalid confirmation code")
            completion(.failure(error))
        }
    }
}
```

#### 4.2. Умные уведомления

```swift
func checkSubscriptionNotifications(completion: @escaping (Result<SubscriptionNotificationsResponse, Error>) -> Void) {
    DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
        let response = SubscriptionNotificationsResponse(
            checked: 5,
            sent: 5,
            failed: 0
        )
        completion(.success(response))
    }
}
```

#### 4.3. Другие методы

- Регистрация
- Вход
- Профиль
- Тарифы
- VPN
- Семья
- И т.д.

**Время:** 2-3 часа

---

## 🎯 ЧТО МОЖНО ПРОТЕСТИРОВАТЬ С MOCK API

### ✅ Основные функции:

1. **Регистрация**
   - Создание семьи
   - Присоединение к семье
   - Восстановление аккаунта

2. **Вход в систему**
   - Авторизация
   - Сохранение токена
   - Восстановление сессии

3. **Удаление аккаунта**
   - Подтверждение
   - Вызов API
   - Очистка данных
   - Навигация

4. **Покупка подписки**
   - Выбор тарифа
   - QR-оплата (UI)
   - IAP (симуляция)

5. **Умные уведомления**
   - Планирование
   - Отображение
   - Действия

6. **VPN**
   - Подключение
   - Отключение
   - Статус

7. **Семейные функции**
   - Добавление членов
   - Управление
   - Чат

8. **Локализация**
   - RU/EN переключение
   - Отображение текстов

---

## 📝 ПРИМЕР РЕАЛИЗАЦИИ

### MockAPIService.swift

```swift
import Foundation

class MockAPIService: APIService {
    static let shared = MockAPIService()
    
    private init() {}
    
    // MARK: - Auth
    
    func login(email: String, password: String, completion: @escaping (Result<LoginResponse, Error>) -> Void) {
        simulateNetworkDelay {
            let response = LoginResponse(
                token: "mock_token_12345",
                user: UserProfile(
                    id: "user_123",
                    name: "Test User",
                    email: email,
                    subscriptionStatus: "active"
                )
            )
            completion(.success(response))
        }
    }
    
    // MARK: - Account Deletion
    
    func deleteAccount(confirmationCode: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void) {
        simulateNetworkDelay {
            if confirmationCode.uppercased() == "УДАЛИТЬ" || confirmationCode.uppercased() == "DELETE" {
                let response = APIResponse<Bool>(
                    success: true,
                    data: true,
                    message: "Account deleted successfully"
                )
                completion(.success(response))
            } else {
                let error = NetworkError.badRequest("Invalid confirmation code")
                completion(.failure(error))
            }
        }
    }
    
    // MARK: - Helper
    
    private func simulateNetworkDelay(completion: @escaping () -> Void) {
        DispatchQueue.main.asyncAfter(deadline: .now() + Double.random(in: 0.5...1.5)) {
            completion()
        }
    }
}
```

---

## 🔄 ПЕРЕКЛЮЧЕНИЕ МЕЖДУ MOCK И REAL API

### В AppConfig.swift

```swift
static var useMockAPI: Bool {
    #if DEBUG
    // Можно переключать через UserDefaults или через настройки
    return UserDefaults.standard.bool(forKey: "useMockAPI")
    #else
    return false // В Release всегда реальный API
    #endif
}
```

### В SettingsScreen (опционально)

```swift
Toggle("Use Mock API", isOn: Binding(
    get: { AppConfig.useMockAPI },
    set: { UserDefaults.standard.set($0, forKey: "useMockAPI") }
))
```

---

## ✅ ПРЕИМУЩЕСТВА

### ✅ Для разработки:

- ✅ Можно тестировать без сервера
- ✅ Быстро и легко
- ✅ Можно протестировать все сценарии
- ✅ Можно протестировать ошибки

### ✅ Для App Store:

- ✅ Можно протестировать все функции
- ✅ Можно показать Apple, что все работает
- ✅ Не зависит от доступности сервера
- ✅ Можно протестировать edge cases

---

## ⚠️ ОГРАНИЧЕНИЯ

### ⚠️ Что НЕЛЬЗЯ протестировать с Mock API:

- ❌ Реальные данные с сервера
- ❌ Реальная интеграция с backend
- ❌ Реальные платежи
- ❌ Реальные уведомления с сервера

### ✅ Что МОЖНО протестировать:

- ✅ UI/UX
- ✅ Логику приложения
- ✅ Обработку ошибок
- ✅ Навигацию
- ✅ Локализацию
- ✅ Все основные сценарии

---

## 🎯 РЕКОМЕНДАЦИЯ

### ✅ Использовать Mock API для:

1. **Тестирования UI/UX**
2. **Тестирования логики приложения**
3. **Тестирования всех сценариев**
4. **Подготовки к App Store**

### ⚠️ После получения реального сервера:

1. **Переключиться на реальный API**
2. **Протестировать с реальными данными**
3. **Проверить интеграцию**
4. **Финальное тестирование**

---

## 📋 ЧЕКЛИСТ РЕАЛИЗАЦИИ

- [ ] Создать `MockAPIService.swift`
- [ ] Реализовать все методы из `APIService`
- [ ] Добавить переключение в `AppConfig`
- [ ] Обновить `APIService.shared`
- [ ] Протестировать все сценарии
- [ ] Добавить опциональный переключатель в Settings

---

## ⏱️ ОЦЕНКА ВРЕМЕНИ

| Задача | Время |
|--------|-------|
| Создание MockAPIService | 1-2 часа |
| Реализация всех методов | 2-3 часа |
| Переключение Mock/Real | 30 минут |
| Тестирование | 1-2 часа |

**Общее время:** ~5-8 часов

---

## ✅ ИТОГ

### ✅ **РЕШЕНИЕ ГОТОВО**

**Mock API Service** - это идеальное решение для тестирования без реального сервера.

**Преимущества:**
- ✅ Можно тестировать все функции
- ✅ Быстро и легко
- ✅ Не зависит от сервера
- ✅ Готово к App Store

**Рекомендация:** Реализовать Mock API Service для тестирования, а после получения реального сервера - протестировать с реальным API.

---

**Дата создания:** 14 ноября 2025  
**Статус:** ✅ **РЕШЕНИЕ ГОТОВО**  
**Следующий шаг:** Реализовать MockAPIService




