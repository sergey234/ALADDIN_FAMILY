# 🔍 КРИТИЧЕСКИЙ АНАЛИЗ: Регистрация vs Авторизация

**Дата:** 2026-02-09  
**Проблема:** Пользователь зарегистрировался, но все еще получает ошибки 403/404

---

## ❌ ПРОБЛЕМА

### **Что происходит:**

1. ✅ Пользователь **зарегистрировался** (создал семью)
2. ✅ Данные сохранены локально (UserDefaults, Keychain)
3. ❌ **НО:** Токены авторизации **НЕ сохранены**
4. ❌ API запросы возвращают **403/404** (нет авторизации)

---

## 🔍 ПРИЧИНА

### **Текущая логика регистрации:**

#### **1. Регистрация семьи (FamilyRegistrationViewModel.swift):**

```swift
// Строки 256-268: МОКОВЫЕ ДАННЫЕ
// API request (закомментировано, используем mock данные)
let _ = CreateFamilyRequest(...)

// МОКОВЫЕ ДАННЫЕ для тестирования (без реального API)
let mockFamilyID = "FAM_\(UUID().uuidString.prefix(12))"
let mockRecoveryCode = "FAM-..."

// Сохранение только локально:
UserDefaults.standard.set(mockFamilyID, forKey: "family_id")
RecoveryCodeStorageManager.shared.saveRecoveryCode(...)
```

**Проблема:**
- ❌ API запросы **закомментированы** (строки 332-368)
- ❌ Используются **моковые данные** (не реальный API)
- ❌ **Токены авторизации НЕ сохраняются**

#### **2. Закомментированный API код:**

```swift
/* ЗАКОММЕНТИРОВАННЫЙ API КОД
apiService.createFamily(request: request) { [weak self] result in
    switch result {
    case .success(let response):
        self?.familyID = response.family_id
        self?.recoveryCode = response.recovery_code
        // ❌ НЕТ сохранения токенов!
    }
}
*/
```

**Проблема:**
- ❌ API код закомментирован
- ❌ Даже если раскомментировать, токены не сохраняются

---

## 🎯 РЕШЕНИЕ

### **Вариант 1: API возвращает токены при создании семьи**

Если API endpoint `/family/create` возвращает токены авторизации:

```swift
struct CreateFamilyResponse: Codable {
    let family_id: String
    let recovery_code: String
    let access_token: String?  // ✅ Добавить
    let refresh_token: String? // ✅ Добавить
}
```

**Что нужно сделать:**
1. Раскомментировать API код
2. Сохранить токены после успешной регистрации
3. Использовать токены для последующих запросов

---

### **Вариант 2: Отдельный процесс авторизации после регистрации**

Если API НЕ возвращает токены при создании семьи:

**Нужно:**
1. После регистрации вызвать `performRealLogin()`
2. Или создать отдельный endpoint для авторизации после регистрации

---

## 📋 ЧТО НУЖНО ПРОВЕРИТЬ

### **1. Проверить API endpoint `/family/create`:**

**Вопросы:**
- ✅ Возвращает ли он токены авторизации?
- ✅ Или нужен отдельный процесс авторизации?

**Проверка:**
```bash
# Проверить документацию API
POST /api/family/create
Response: {
    "family_id": "...",
    "recovery_code": "...",
    "access_token": "..."?,  // Есть ли?
    "refresh_token": "..."?  // Есть ли?
}
```

---

### **2. Проверить текущую логику:**

**Файл:** `ViewModels/FamilyRegistrationViewModel.swift`

**Строки 256-268:** Моковые данные
**Строки 332-368:** Закомментированный API код

**Вопросы:**
- ✅ Почему API закомментирован?
- ✅ Когда планируется включить реальный API?
- ✅ Нужно ли сохранять токены после регистрации?

---

## 🔧 ПЛАН ИСПРАВЛЕНИЯ

### **Шаг 1: Проверить API endpoint**

1. Проверить документацию API
2. Узнать, возвращает ли `/family/create` токены
3. Если нет — нужен отдельный процесс авторизации

---

### **Шаг 2: Раскомментировать API код**

**Файл:** `ViewModels/FamilyRegistrationViewModel.swift`

**Строки 332-368:** Раскомментировать API код

```swift
// БЫЛО:
/* ЗАКОММЕНТИРОВАННЫЙ API КОД
apiService.createFamily(...)
*/

// СТАЛО:
apiService.createFamily(request: request) { [weak self] result in
    DispatchQueue.main.async {
        self?.isLoading = false
        
        switch result {
        case .success(let response):
            self?.familyID = response.family_id
            self?.recoveryCode = response.recovery_code
            
            // ✅ ДОБАВИТЬ: Сохранение токенов
            if let accessToken = response.access_token,
               let refreshToken = response.refresh_token {
                KeychainManager.shared.save(accessToken, forKey: .authToken)
                KeychainManager.shared.save(refreshToken, forKey: .refreshToken)
                print("✅ Токены сохранены после регистрации")
            }
            
            // ... остальной код
        }
    }
}
```

---

### **Шаг 3: Добавить сохранение токенов**

**Если API возвращает токены:**

```swift
// В CreateFamilyResponse добавить:
struct CreateFamilyResponse: Codable {
    let family_id: String
    let recovery_code: String
    let access_token: String?  // ✅ Добавить
    let refresh_token: String? // ✅ Добавить
}

// В FamilyRegistrationViewModel.createFamily():
case .success(let response):
    // Сохранить токены
    if let accessToken = response.access_token,
       let refreshToken = response.refresh_token {
        KeychainManager.shared.save(accessToken, forKey: .authToken)
        KeychainManager.shared.save(refreshToken, forKey: .refreshToken)
    }
```

**Если API НЕ возвращает токены:**

```swift
// После успешной регистрации вызвать авторизацию:
case .success(let response):
    self?.familyID = response.family_id
    self?.recoveryCode = response.recovery_code
    
    // ✅ Автоматическая авторизация после регистрации
    // (нужно знать email/password пользователя)
    // Или использовать recovery_code для авторизации
```

---

## 📊 ТЕКУЩАЯ ЛОГИКА

### **Что происходит сейчас:**

1. **Регистрация семьи:**
   - ✅ Создается familyID (моковый)
   - ✅ Генерируется recovery code (моковый)
   - ✅ Сохраняется в UserDefaults и Keychain
   - ❌ **Токены НЕ сохраняются**

2. **API запросы:**
   - ❌ Возвращают 403/404 (нет токенов)
   - ❌ Пользователь не авторизован

3. **Авторизация:**
   - ⚠️ Нужно вызывать `performRealLogin()` вручную
   - ⚠️ Но пользователь уже зарегистрирован!

---

## 🎯 ВЫВОД

### **Проблема:**

**Регистрация семьи ≠ Авторизация**

- ✅ Регистрация создает семью локально
- ❌ Но **НЕ авторизует** пользователя
- ❌ Токены **НЕ сохраняются**

### **Решение:**

1. **Если API возвращает токены:**
   - Раскомментировать API код
   - Сохранить токены после регистрации

2. **Если API НЕ возвращает токены:**
   - После регистрации вызвать авторизацию
   - Или использовать recovery_code для авторизации

---

## 📌 ИТОГ

### **Почему ошибки 403/404:**

- ✅ Пользователь **зарегистрировался** (создал семью)
- ❌ Но **НЕ авторизован** (нет токенов)
- ❌ API запросы требуют токены → 403/404

### **Что нужно сделать:**

1. ✅ Проверить, возвращает ли API токены при создании семьи
2. ✅ Раскомментировать API код
3. ✅ Сохранить токены после регистрации
4. ✅ Или добавить автоматическую авторизацию после регистрации

---

**Готово!** Теперь понятно, почему после регистрации все еще ошибки 403/404.
