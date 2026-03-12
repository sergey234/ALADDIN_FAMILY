# 🔍 ЛОГИКА РЕГИСТРАЦИИ И СОХРАНЕНИЯ your_member_id

**Дата:** 2026-03-12  
**BUILD:** 115

---

## 📋 КРАТКОЕ РЕЗЮМЕ

**`your_member_id` сохраняется ТОЛЬКО при:**
1. ✅ **Создании семьи** (`createFamily()`)
2. ✅ **Присоединении к семье** (`joinFamily()`)

**`your_member_id` НЕ сохраняется при:**
- ❌ Регистрации устройства (`registerDeviceAnonymously()`)
- ❌ Активации триал периода
- ❌ Первом запуске приложения

---

## 🔄 ПОЛНЫЙ FLOW РЕГИСТРАЦИИ

### 1️⃣ РЕГИСТРАЦИЯ УСТРОЙСТВА (Первый запуск)

**Когда вызывается:**
- При первом запуске приложения, если нет токена
- В `SubscriptionManager.initializeOnAppStart()` → `performDeviceRegistration()` → `registerDeviceAnonymously()`

**Что происходит:**
```swift
// Core/Managers/SubscriptionManager.swift:652
func registerDeviceAnonymously() async throws -> JWTToken {
    // 1. Получаем deviceId
    let deviceId = UIDevice.current.identifierForVendor?.uuidString ?? UUID().uuidString
    
    // 2. Вызываем API: POST /api/auth/register-device
    let response = try await APIService.shared.registerDeviceAnonymously(...)
    
    // 3. Сохраняем токен в Keychain
    await storeToken(jwtToken)
    
    // ❌ НЕ сохраняет your_member_id!
}
```

**API Response:**
```json
{
  "token": "eyJ...",
  "deviceId": "8993C837-3B23-41A5-B4D3-E4C346606AE7",
  "expiresAt": "2026-03-13T12:00:00Z",
  "registeredAt": "2026-03-12T12:00:00Z",
  "subscription": {
    "level": "free",
    "isActive": true
  }
}
```

**Результат:**
- ✅ Токен сохранен в Keychain
- ✅ Устройство зарегистрировано
- ❌ `your_member_id` НЕ сохранен (его нет в ответе API)

---

### 2️⃣ СОЗДАНИЕ СЕМЬИ

**Когда вызывается:**
- Пользователь проходит онбординг и выбирает "Создать семью"
- В `FamilyRegistrationViewModel.createFamily()`

**Что происходит:**
```swift
// ViewModels/FamilyRegistrationViewModel.swift:286
apiService.createFamily(request: request) { result in
    case .success(let response):
        // ✅ СОХРАНЯЕТ your_member_id
        UserDefaults.standard.set(response.your_member_id, forKey: "your_member_id")
        logger.business("Member ID saved: \(response.your_member_id)")
}
```

**API Response:**
```json
{
  "family_id": "FAM_A1B2C3D4E5F6",
  "your_member_id": "mem_abc123",  // ✅ ЕСТЬ В ОТВЕТЕ
  "recovery_code": "...",
  "access_token": "...",
  "refresh_token": "..."
}
```

**Результат:**
- ✅ Семья создана
- ✅ `your_member_id` сохранен в UserDefaults
- ✅ ID будет отображаться на главном экране

---

### 3️⃣ ПРИСОЕДИНЕНИЕ К СЕМЬЕ

**Когда вызывается:**
- Пользователь вводит код приглашения и присоединяется к существующей семье
- В `FamilyRegistrationViewModel.joinFamily()`

**Что происходит:**
```swift
// ViewModels/FamilyRegistrationViewModel.swift:515
apiService.joinFamily(request: request) { result in
    case .success(let response):
        guard let data = response.data else { return }
        
        // ✅ СОХРАНЯЕТ your_member_id
        UserDefaults.standard.set(data.your_member_id, forKey: "your_member_id")
        print("✅ your_member_id сохранен: \(data.your_member_id)")
}
```

**API Response:**
```json
{
  "data": {
    "family_id": "FAM_A1B2C3D4E5F6",
    "your_member_id": "mem_xyz789",  // ✅ ЕСТЬ В ОТВЕТЕ
    "members": [...]
  }
}
```

**Результат:**
- ✅ Пользователь присоединился к семье
- ✅ `your_member_id` сохранен в UserDefaults
- ✅ ID будет отображаться на главном экране

---

## 🎁 ТРИАЛ ПЕРИОД

**Когда активируется:**
- При регистрации устройства с триал периодом (`register-device-trial`)
- Или через `SubscriptionManager.activateTrialIfNeeded()`

**Что происходит:**
```swift
// Core/Managers/SubscriptionManager.swift:493
func activateTrialIfNeeded() async {
    // Проверяет, использован ли триал
    let hasUsedTrial = UserDefaults.standard.bool(forKey: "trial_used")
    
    // Активирует триал через registerDeviceAnonymously()
    // ❌ НЕ создает семью и НЕ сохраняет your_member_id
}
```

**Важно:**
- Триал период НЕ создает семью автоматически
- Триал период НЕ сохраняет `your_member_id`
- Для сохранения `your_member_id` нужно создать семью или присоединиться к существующей

---

## 🔍 ДИАГНОСТИКА

### Проверка наличия `your_member_id`:

```swift
let memberId = UserDefaults.standard.string(forKey: "your_member_id")
if memberId == nil {
    print("⚠️ your_member_id не найден!")
    print("   - Пользователь не создал семью")
    print("   - Пользователь не присоединился к семье")
} else {
    print("✅ your_member_id найден: \(memberId!)")
}
```

### Логи для отслеживания:

**При регистрации устройства:**
```
🔍 Проверка your_member_id после регистрации устройства:
   - your_member_id в UserDefaults: НЕ НАЙДЕН
   - ⚠️ ВНИМАНИЕ: your_member_id не сохранен!
   - ℹ️ your_member_id сохраняется ТОЛЬКО при создании/присоединении к семье
```

**При создании семьи:**
```
✅ FamilyRegistrationViewModel: your_member_id сохранен при создании семьи: mem_abc123
✅ FamilyRegistrationViewModel: Проверка успешна - ID сохранен корректно
```

**При присоединении к семье:**
```
✅ FamilyRegistrationViewModel: your_member_id сохранен при присоединении к семье: mem_xyz789
✅ FamilyRegistrationViewModel: Проверка успешна - ID сохранен корректно
```

---

## ❓ ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ

### Q: Почему ID не отображается на главном экране?

**A:** Потому что `your_member_id` не сохранен в UserDefaults. Это происходит, если:
- Пользователь только зарегистрировал устройство, но не создал семью
- Пользователь не присоединился к существующей семье

**Решение:** Создать семью или присоединиться к существующей.

---

### Q: Можно ли получить `your_member_id` при регистрации устройства?

**A:** Нет, API `/api/auth/register-device` не возвращает `your_member_id`. Это сделано намеренно:
- Регистрация устройства - это анонимная операция
- `your_member_id` присваивается только при создании/присоединении к семье
- Это соответствует архитектуре: семья = группа пользователей, каждый получает уникальный ID

---

### Q: Как связаны триал период и регистрация семьи?

**A:** Они НЕ связаны напрямую:
- Триал период активируется при регистрации устройства
- Семья создается отдельно через онбординг
- Можно иметь триал период БЕЗ семьи (но тогда не будет `your_member_id`)
- Можно иметь семью БЕЗ триал периода

---

## ✅ РЕКОМЕНДАЦИИ

1. **Для отображения ID:**
   - Убедитесь, что пользователь прошел онбординг
   - Убедитесь, что пользователь создал семью или присоединился к существующей
   - Проверьте логи на наличие сообщений о сохранении `your_member_id`

2. **Для диагностики:**
   - Проверьте логи при запуске приложения
   - Проверьте логи при создании/присоединении к семье
   - Используйте `UserDefaults.standard.string(forKey: "your_member_id")` для проверки

3. **Для пользователей:**
   - Если ID не отображается, предложите создать семью или присоединиться к существующей
   - Объясните, что ID присваивается только при работе с семьей

---

## 📝 ИЗМЕНЕНИЯ BUILD 115

1. ✅ Добавлена диагностика `your_member_id` при регистрации устройства
2. ✅ Добавлена проверка сохранения `your_member_id` при создании/присоединении к семье
3. ✅ Улучшено логирование для отслеживания сохранения ID
4. ✅ Создан документ с полным описанием логики
