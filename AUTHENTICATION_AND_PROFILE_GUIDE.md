# 🔐 ПОЛНАЯ ИНСТРУКЦИЯ: АВТОРИЗАЦИЯ И ПРОФИЛЬ

**Дата:** 2026-02-13  
**Цель:** Объяснить, как правильно авторизоваться и загрузить профиль

---

## 📋 СОДЕРЖАНИЕ:

1. [Как авторизоваться в приложении?](#1-как-авторизоваться-в-приложении)
2. [Что нужно сделать для профиля?](#2-что-нужно-сделать-для-профиля)
3. [Проверка логики работы](#3-проверка-логики-работы)
4. [Решение проблем](#4-решение-проблем)

---

## 1. КАК АВТОРИЗОВАТЬСЯ В ПРИЛОЖЕНИИ?

### **Способ 1: Регистрация новой семьи (ОСНОВНОЙ)** ✅

**Как это работает:**

1. **Запустите приложение** → Показывается онбординг (7 страниц)
2. **После онбординга** → Автоматически начинается регистрация:
   - Модальное окно #1: Выбор роли (Parent, Child, Teenager, Elderly)
   - Модальное окно #2: Выбор возрастной группы
   - Модальное окно #3: Выбор буквы имени
   - Модальное окно #4: Семья создана! (показывается Recovery Code)

3. **Автоматическая авторизация:**
   - После создания семьи автоматически происходит авторизация по Recovery Code
   - Токены сохраняются в Keychain
   - Приложение переходит в обычный режим (не демо)

**Где это происходит:**
- `ViewModels/FamilyRegistrationViewModel.swift` - логика регистрации
- `Screens/MainScreenWithRegistration.swift` - UI регистрации

**Что происходит внутри:**
```swift
// 1. Создание семьи
apiService.createFamily(request: request) { result in
    // 2. Получение family_id и recovery_code
    // 3. Автоматическая авторизация
    loginByRecoveryCode(familyID: family_id, recoveryCode: recovery_code)
    // 4. Сохранение токенов в Keychain
    saveTokens(accessToken: ..., refreshToken: ...)
}
```

---

### **Способ 2: Авторизация по Recovery Code (для существующих пользователей)** ✅

**Если у вас уже есть Recovery Code:**

1. **В Debug Console Xcode** выполните:
```swift
// Получить Recovery Code из Keychain
let recoveryCode = RecoveryCodeStorageManager.shared.getRecoveryCode()
let familyID = RecoveryCodeStorageManager.shared.getFamilyID()

// Авторизоваться
APIService.shared.loginByRecoveryCode(
    familyID: familyID,
    recoveryCode: recoveryCode
) { result in
    switch result {
    case .success(let response):
        print("✅ Авторизация успешна!")
        // Токены автоматически сохраняются
    case .failure(let error):
        print("❌ Ошибка: \(error)")
    }
}
```

---

### **Способ 3: Email/Password (ТОЛЬКО ДЛЯ ТЕСТИРОВАНИЯ)** ⚠️

**⚠️ ВНИМАНИЕ:** Этот способ требует персональные данные (email) и используется только для тестирования!

**В Debug Console Xcode:**
```swift
performRealLogin(email: "test@example.com", password: "password123") { success in
    if success {
        print("✅ Авторизация успешна!")
    } else {
        print("❌ Ошибка авторизации")
    }
}
```

**Или через переменные окружения:**
1. Xcode → Scheme → Edit Scheme → Run → Arguments → Environment Variables
2. Добавьте:
   - `AUTO_LOGIN_EMAIL` = `test@example.com`
   - `AUTO_LOGIN_PASSWORD` = `password123`
3. Запустите приложение → Автоматический логин произойдет через 2 секунды

---

## 2. ЧТО НУЖНО СДЕЛАТЬ ДЛЯ ПРОФИЛЯ?

### **Проблема:**
```
⚠️ HTTP Error: 404 - https://aladdin-ai.ru/api/user/profile
```

**Причина:**
- Endpoint `/api/user/profile` **НЕ реализован на сервере**
- Или требует авторизацию, но токен не передается

### **Решение:**

#### **Вариант 1: Реализовать endpoint на сервере** ✅

**На сервере нужно создать:**
```python
@router.get("/user/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user)  # Требует авторизацию
):
    """
    Получить профиль текущего пользователя
    """
    return UserProfileResponse(
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        ...
    )
```

**Проверка на сервере:**
```bash
# Проверить, существует ли endpoint
curl -X GET "https://aladdin-ai.ru/api/user/profile" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Если 404 - endpoint не реализован
# Если 401 - нужна авторизация
# Если 200 - работает!
```

---

#### **Вариант 2: Использовать альтернативный endpoint** ✅

**Если есть endpoint `/api/user/profile/sync`:**
```swift
// Вместо getUserProfile используйте syncUserProfile
apiService.syncUserProfile(
    userId: "your_user_id",
    deviceId: "device_id"
) { result in
    switch result {
    case .success(let profile):
        print("✅ Профиль загружен: \(profile.name)")
    case .failure(let error):
        print("❌ Ошибка: \(error)")
    }
}
```

---

#### **Вариант 3: Временно использовать кеш** ⚠️

**Если профиль уже был загружен ранее:**
```swift
// UserProfileManager использует кеш из UserDefaults
let profileManager = UserProfileManager.shared
let name = profileManager.displayName  // Из кеша
let email = profileManager.email       // Из кеша
```

**Но это временное решение!** В продакшн профиль должен загружаться с сервера.

---

## 3. ПРОВЕРКА ЛОГИКИ РАБОТЫ

### **Текущая логика авторизации:**

```
1. Запуск приложения
   ↓
2. Онбординг (7 страниц)
   ↓
3. Регистрация семьи (если первый запуск)
   ├─ Выбор роли
   ├─ Выбор возраста
   ├─ Выбор буквы
   └─ Создание семьи → Получение family_id и recovery_code
   ↓
4. Автоматическая авторизация
   ├─ Попытка 1: Токены из response.createFamily
   └─ Попытка 2: Авторизация по recovery_code
   ↓
5. Сохранение токенов в Keychain
   ↓
6. Загрузка профиля (если endpoint существует)
   └─ getUserProfile() → /api/user/profile
```

### **Проблемы в текущей логике:**

1. ❌ **Профиль не загружается** - endpoint `/api/user/profile` возвращает 404
2. ⚠️ **Демо режим активируется** - если авторизация не удалась
3. ⚠️ **Нет проверки токена** - приложение не проверяет, валиден ли токен

---

## 4. РЕШЕНИЕ ПРОБЛЕМ

### **Проблема 1: Профиль не загружается (404)**

**Что нужно сделать:**

1. **Проверить на сервере:**
```bash
ssh root@149.154.65.180
cd /opt/aladdin-backend
grep -r "user/profile" security/api/routers/
```

2. **Если endpoint не существует:**
   - Создать endpoint `/api/user/profile` на сервере
   - Или использовать альтернативный endpoint

3. **Если endpoint существует, но требует авторизацию:**
   - Проверить, что токен передается в заголовках
   - Проверить, что токен валиден

---

### **Проблема 2: Демо режим активируется**

**Что нужно сделать:**

1. **Проверить авторизацию:**
```swift
// В Debug Console
let keychain = KeychainManager.shared
let token = keychain.loadString(forKey: .authToken)
print("Токен: \(token ?? "НЕТ")")
```

2. **Если токена нет:**
   - Пройти регистрацию заново
   - Или авторизоваться по Recovery Code

3. **Если токен есть, но демо режим:**
   - Проверить логику в `MainViewModel.swift`
   - Убедиться, что токен используется в запросах

---

### **Проблема 3: Нет проверки токена**

**Что нужно сделать:**

1. **Добавить проверку токена при запуске:**
```swift
// В ALADDINApp.swift
private func checkAuthToken() {
    let keychain = KeychainManager.shared
    if let token = keychain.loadString(forKey: .authToken) {
        // Проверить валидность токена
        if isValidToken(token) {
            // Токен валиден - обычный режим
        } else {
            // Токен невалиден - нужно переавторизоваться
        }
    } else {
        // Токена нет - демо режим или регистрация
    }
}
```

---

## 📋 ЧЕКЛИСТ ДЛЯ ПРОВЕРКИ:

- [ ] Регистрация семьи работает
- [ ] Авторизация по recovery code работает
- [ ] Токены сохраняются в Keychain
- [ ] Endpoint `/api/user/profile` существует на сервере
- [ ] Профиль загружается после авторизации
- [ ] Демо режим отключается после авторизации
- [ ] Все API запросы используют токен

---

## 🎯 РЕКОМЕНДАЦИИ:

1. **Для тестирования:**
   - Используйте регистрацию новой семьи (Способ 1)
   - Проверьте, что токены сохраняются
   - Проверьте, что профиль загружается

2. **Для продакшн:**
   - Убедитесь, что endpoint `/api/user/profile` реализован
   - Убедитесь, что авторизация обязательна
   - Убедитесь, что демо режим не активируется автоматически

3. **Для отладки:**
   - Используйте Debug Console для проверки токенов
   - Проверяйте логи на наличие ошибок 404/401
   - Используйте переменные окружения для автоматического логина

---

**Последнее обновление:** 2026-02-13
