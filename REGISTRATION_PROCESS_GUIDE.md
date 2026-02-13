# 📋 ГАЙД: Процесс регистрации и проверка токенов

**Дата:** 2026-02-12

---

## 🔄 ПРОЦЕСС РЕГИСТРАЦИИ (ШАГ ЗА ШАГОМ)

### **Шаг 1: Открытие регистрации**
1. На главном экране нажмите на желтую карточку "FAMILY"
2. Нажмите кнопку "Добавить участника" или "Создать семью"
3. Откроется экран регистрации

---

### **Шаг 2: Выбор роли**
- Выберите роль: **Родитель** или **Ребенок**
- Роль сохраняется в `UserDefaults`

**В логах вы увидите:**
```
✅ [FamilyRegistrationViewModel] Роль сохранена: parent
```

---

### **Шаг 3: Выбор возраста**
- Выберите возрастную группу:
  - Toddler (0-3)
  - Child (4-12)
  - Teen (13-17)
  - Adult (18-64)
  - Senior (65+)

**В логах вы увидите:**
```
🚨 Нажата кнопка возраста - вызываю onAgeGroupSelected(.Adult (18-64))
🏠 [FamilyRegistrationViewModel.createFamily] Возрастная группа (клиент): Adult (18-64)
🏠 [FamilyRegistrationViewModel.createFamily] Возрастная группа (сервер): 24-55
```

---

### **Шаг 4: Выбор буквы**
- Выберите букву для идентификации (A-Z)
- Буква используется как имя участника

**В логах вы увидите:**
```
🏠 [FamilyRegistrationViewModel.createFamily] Буква: P
```

---

### **Шаг 5: Создание семьи (API запрос)**
После выбора буквы автоматически отправляется запрос на сервер:

**В логах вы увидите:**
```
🔵 NetworkManager.post: Начало
   - URL: https://aladdin-ai.ru/api/family/create
   - Body: {"age_group":"24-55","personal_letter":"P","role":"parent","device_type":"smartphone"}
```

**Ответ сервера:**
```
✅ HTTP Status: 200
✅ NetworkManager.performRequest: Декодирование успешно
✅ APIResponseValidator: Валидация CreateFamilyResponse пройдена
✅ your_member_id сохранен: MEM_ED5AC89A
```

---

### **Шаг 6: Авторизация по Recovery Code**
После создания семьи автоматически происходит авторизация:

**В логах вы увидите:**
```
🔄 Попытка 2: авторизация по recovery code (попытка 1)
🔵 NetworkManager.post: Начало
   - URL: https://aladdin-ai.ru/api/auth/login-by-recovery-code
   - Body: {"family_id":"FAM_03F8BB425B7C","recovery_code":"FAM-03F8-BB42-5B7C"}
```

**Ответ сервера:**
```
✅ HTTP Status: 200
✅ NetworkManager.performRequest: Декодирование успешно
✅ Попытка 2 успешна: получены токены
🔐 Сохранение токенов в Keychain...
✅ Токены успешно сохранены и проверены
```

---

### **Шаг 7: Показ Recovery Code**
После успешной авторизации показывается модальное окно с Recovery Code:

**В логах вы увидите:**
```
✅ RecoveryCodeStorageManager: Код сохранен: FAM-03F8-BB42-5B7C
✅ Recovery Code автоматически сохранен в Keychain
✅ [AddMemberOptionsScreen] Регистрация завершена, закрываем модал
```

---

### **Шаг 8: Завершение**
- Модальное окно закрывается
- Пользователь перенаправляется на экран семьи
- Токены сохранены в Keychain

---

## 🔍 КАК ПРОВЕРИТЬ ТОКЕНЫ

### **Способ 1: Через логи (самый простой)**

После регистрации в логах должны появиться:

**✅ Успешное сохранение:**
```
✅ Токены успешно сохранены и проверены
✅ Попытка 2 завершена: токены сохранены
```

**✅ Проверка токена:**
```
✅ JWT Token действителен ещё 84976 секунд (истекает: 2026-02-13 10:32:56 +0000)
✅ JWT: Access token действителен, обновление не требуется
```

**❌ Если токен отсутствует:**
```
❌ KeychainManager: Failed to load data for key auth_token. Status: -25300
❌ JWT: Access token не найден в Keychain
```

---

### **Способ 2: Через Debug Console в Xcode**

1. Запустите приложение в Xcode
2. Откройте Debug Console (View → Debug Area → Activate Console)
3. Введите команду:

```swift
// Проверка токенов
let keychain = KeychainManager.shared
if let accessToken = keychain.loadString(forKey: .authToken) {
    print("✅ Access token найден (длина: \(accessToken.count))")
    print("   Токен: \(accessToken.prefix(50))...")
} else {
    print("❌ Access token НЕ найден!")
}

if let refreshToken = keychain.loadString(forKey: .refreshToken) {
    print("✅ Refresh token найден (длина: \(refreshToken.count))")
} else {
    print("❌ Refresh token НЕ найден!")
}
```

---

### **Способ 3: Через проверку ID пользователя**

Если ID пользователя отображается на главном экране, значит регистрация прошла успешно:

**В логах:**
```
✅ MainScreen.onAppear: ID найден: MEM_ED5AC89A
✅ MainScreen: ID найден и будет отображен: MEM_ED5AC89A
```

**На экране:**
- В желтом прямоугольнике "FAMILY" должен отображаться ID пользователя
- Можно скопировать ID, нажав на кнопку копирования

---

## ✅ ЧТО ДОЛЖНО БЫТЬ ПОСЛЕ РЕГИСТРАЦИИ

### **1. ID пользователя**
- ✅ Сохранен в `UserDefaults` с ключом `"your_member_id"`
- ✅ Отображается на главном экране
- ✅ Можно скопировать

### **2. Токены**
- ✅ `access_token` сохранен в Keychain
- ✅ `refresh_token` сохранен в Keychain
- ✅ Токены можно прочитать без ошибок

### **3. Recovery Code**
- ✅ Сохранен в Keychain
- ✅ Показан в модальном окне
- ✅ Можно использовать для восстановления доступа

### **4. Family ID**
- ✅ Сохранен в `UserDefaults` с ключом `"family_id"`
- ✅ Используется для API запросов

---

## 🧪 ТЕСТИРОВАНИЕ РЕГИСТРАЦИИ

### **Пошаговая инструкция:**

1. **Запустите приложение**
   - Должен открыться онбординг (если первый запуск)
   - Или главный экран (если уже проходили онбординг)

2. **Откройте регистрацию**
   - Нажмите на желтую карточку "FAMILY"
   - Нажмите "Добавить участника" или "Создать семью"

3. **Выберите данные:**
   - Роль: Родитель
   - Возраст: Adult (18-64)
   - Буква: любую (например, P)

4. **Дождитесь завершения:**
   - Должно появиться модальное окно с Recovery Code
   - Нажмите "Готово" или закройте модал

5. **Проверьте результат:**
   - ID должен отображаться на главном экране
   - В логах должны быть сообщения об успешном сохранении токенов

---

## 🔍 ПРОВЕРКА В ЛОГАХ

После регистрации ищите в логах:

**✅ Успешная регистрация:**
```
✅ your_member_id сохранен: MEM_XXXXX
✅ Попытка 2 успешна: получены токены
✅ Токены успешно сохранены и проверены
✅ Recovery Code автоматически сохранен в Keychain
```

**✅ Токены работают:**
```
✅ JWT Token действителен ещё X секунд
✅ JWT: Access token действителен, обновление не требуется
```

**❌ Если что-то не так:**
```
❌ KeychainManager: Failed to decode object for key auth_token
⚠️ KeychainManager: Повреждённый auth_token удалён из Keychain
```

Если видите ошибку декодирования - значит где-то еще используется `load(String.self, ...)` вместо `loadString(...)`.

---

## 📝 КОМАНДЫ ДЛЯ ПРОВЕРКИ

### **В Debug Console Xcode:**

```swift
// 1. Проверить ID пользователя
let memberId = UserDefaults.standard.string(forKey: "your_member_id")
print("ID пользователя: \(memberId ?? "не найден")")

// 2. Проверить Family ID
let familyId = UserDefaults.standard.string(forKey: "family_id")
print("Family ID: \(familyId ?? "не найден")")

// 3. Проверить токены
let keychain = KeychainManager.shared
let accessToken = keychain.loadString(forKey: .authToken)
let refreshToken = keychain.loadString(forKey: .refreshToken)

print("Access token: \(accessToken != nil ? "✅ найден (\(accessToken!.count) символов)" : "❌ не найден")")
print("Refresh token: \(refreshToken != nil ? "✅ найден (\(refreshToken!.count) символов)" : "❌ не найден")")

// 4. Проверить Recovery Code
let recoveryCode = RecoveryCodeStorageManager.shared.getRecoveryCode()
print("Recovery Code: \(recoveryCode ?? "не найден")")
```

---

**Автор:** AI Assistant  
**Дата:** 2026-02-12
