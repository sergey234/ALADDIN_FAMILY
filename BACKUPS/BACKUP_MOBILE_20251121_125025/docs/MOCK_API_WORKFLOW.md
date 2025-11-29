# 🔧 КАК БУДЕТ РАБОТАТЬ MOCK API

**Дата:** 15 ноября 2025  
**Задача:** Создание Mock API для тестирования без реального сервера

---

## 🎯 КАК ЭТО БУДЕТ РАБОТАТЬ

### 📋 Общая схема:

```
┌─────────────────────────────────────────────────────────┐
│                    iOS Приложение                        │
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │  ViewModels  │ ──────> │  APIService  │             │
│  │              │         │              │             │
│  └──────────────┘         └──────┬───────┘             │
│                                   │                      │
│                                   ▼                      │
│                          ┌─────────────────┐            │
│                          │  AppConfig      │            │
│                          │  useMockAPI?    │            │
│                          └────────┬────────┘            │
│                                   │                      │
│                    ┌──────────────┴──────────────┐      │
│                    │                             │      │
│                    ▼                             ▼      │
│          ┌─────────────────┐         ┌─────────────────┐│
│          │ MockAPIService  │         │ RealAPIService  ││
│          │  (тестовые      │         │  (реальный      ││
│          │   данные)       │         │   сервер)       ││
│          └─────────────────┘         └─────────────────┘│
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 ПЕРЕКЛЮЧЕНИЕ MOCK/REAL

### В AppConfig.swift:

```swift
static var useMockAPI: Bool {
    #if DEBUG
    // В DEBUG режиме можно переключать через UserDefaults
    return UserDefaults.standard.bool(forKey: "useMockAPI")
    #else
    // В Release всегда используем реальный API
    return false
    #endif
}
```

### В APIService.swift:

```swift
static var shared: APIService {
    if AppConfig.useMockAPI {
        return MockAPIService.shared
    } else {
        return RealAPIService.shared
    }
}
```

### В SettingsScreen (опционально):

```swift
#if DEBUG
Toggle("Use Mock API", isOn: Binding(
    get: { AppConfig.useMockAPI },
    set: { UserDefaults.standard.set($0, forKey: "useMockAPI") }
))
#endif
```

---

## 📋 КРИТИЧЕСКИЕ МЕТОДЫ ДЛЯ MOCK

### Список методов (15 методов):

1. **Auth:**
   - `login()` - вход в систему
   - `logout()` - выход из системы

2. **Registration:**
   - `createFamily()` - создание семьи
   - `joinFamily()` - присоединение к семье

3. **User:**
   - `getUserProfile()` - загрузка профиля
   - `deleteAccount()` - удаление аккаунта

4. **Family:**
   - `getFamilyMembers()` - загрузка членов семьи
   - `getFamilyStats()` - статистика семьи

5. **Subscription:**
   - `getTariffs()` - загрузка тарифов
   - `createQRPayment()` - создание QR-оплаты
   - `checkQRPaymentStatus()` - проверка статуса оплаты

6. **VPN:**
   - `getVPNStatus()` - статус VPN
   - `connectVPN()` - подключение VPN
   - `disconnectVPN()` - отключение VPN

7. **Analytics:**
   - `getAnalytics()` - аналитика
   - `getTopThreats()` - топ угроз

8. **Notifications:**
   - `getNotifications()` - уведомления

---

## 🎯 ПРИМЕРЫ MOCK ДАННЫХ

### 1. Mock UserProfile:

```swift
UserProfile(
    id: "user_mock_123",
    name: "Test User",
    email: "test@aladdin.family",
    phone: "+7 (999) 123-45-67",
    registrationDate: "2025-01-01",
    subscriptionType: "family",
    subscriptionEndDate: "2025-12-31",
    threatsBlocked: 47,
    familyMembers: 4,
    devices: 8
)
```

### 2. Mock FamilyMembers:

```swift
[
    FamilyMemberResponse(
        id: "member_1",
        name: "Родитель",
        role: "parent",
        avatar: "👨",
        status: "protected",
        threatsBlocked: 15,
        lastActive: "2 минуты назад",
        devices: 2
    ),
    FamilyMemberResponse(
        id: "member_2",
        name: "Ребенок",
        role: "child",
        avatar: "👶",
        status: "protected",
        threatsBlocked: 8,
        lastActive: "5 минут назад",
        devices: 1
    )
]
```

### 3. Mock Tariffs:

```swift
[
    TariffResponse(
        id: "free",
        name: "Free",
        price: 0,
        period: "month",
        features: [...]
    ),
    TariffResponse(
        id: "personal",
        name: "Personal",
        price: 299,
        period: "month",
        features: [...]
    ),
    TariffResponse(
        id: "family",
        name: "Family",
        price: 499,
        period: "month",
        features: [...]
    )
]
```

---

## ⏱️ СИМУЛЯЦИЯ ЗАДЕРЖКИ СЕТИ

### Реализация:

```swift
private func simulateNetworkDelay(completion: @escaping () -> Void) {
    // Симулируем задержку сети (0.5-1.5 секунды)
    let delay = Double.random(in: 0.5...1.5)
    DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
        completion()
    }
}
```

### Использование:

```swift
func getUserProfile(completion: @escaping (Result<UserProfile, Error>) -> Void) {
    simulateNetworkDelay {
        let mockProfile = UserProfile(...)
        completion(.success(mockProfile))
    }
}
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

## 🔄 ПРОЦЕСС РАБОТЫ

### Шаг 1: Включить Mock API

```swift
// В SettingsScreen или через UserDefaults
UserDefaults.standard.set(true, forKey: "useMockAPI")
```

### Шаг 2: Перезапустить приложение

```swift
// APIService.shared автоматически переключится на MockAPIService
```

### Шаг 3: Тестировать

```swift
// Все API вызовы будут использовать Mock данные
// Например:
apiService.getUserProfile { result in
    // Получим mock профиль
}
```

### Шаг 4: Выключить Mock API

```swift
UserDefaults.standard.set(false, forKey: "useMockAPI")
// Перезапустить приложение
// APIService.shared переключится на RealAPIService
```

---

## 📝 ПРИМЕР ИСПОЛЬЗОВАНИЯ

### В ViewModel:

```swift
class ProfileViewModel: ObservableObject {
    func loadProfile() {
        // Не нужно менять код!
        // APIService.shared автоматически использует Mock или Real
        APIService.shared.getUserProfile { [weak self] result in
            switch result {
            case .success(let profile):
                self?.profile = profile
            case .failure(let error):
                self?.errorMessage = error.localizedDescription
            }
        }
    }
}
```

### Переключение:

```swift
// Включить Mock API
UserDefaults.standard.set(true, forKey: "useMockAPI")

// Выключить Mock API
UserDefaults.standard.set(false, forKey: "useMockAPI")

// Перезапустить приложение
```

---

## ✅ ИТОГ

### ✅ **КАК БУДЕТ РАБОТАТЬ:**

1. **Создаем MockAPIService.swift** с 15 критическими методами
2. **Добавляем переключение** в AppConfig и APIService
3. **Тестируем** с Mock данными
4. **Переключаемся** на реальный API когда сервер готов

### ✅ **ПРЕИМУЩЕСТВА:**

- ✅ Не нужно менять код ViewModels
- ✅ Легко переключаться между Mock и Real
- ✅ Можно тестировать без сервера
- ✅ Готово к App Store

---

**Дата создания:** 15 ноября 2025  
**Статус:** ✅ **ПЛАН ГОТОВ**  
**Следующий шаг:** Создать MockAPIService.swift



