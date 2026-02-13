# 🔐 ПЛАН РЕАЛИЗАЦИИ: Авторизация + Тарифы

**Дата:** 2026-02-09  
**Цель:** Реализовать комбинированную авторизацию и проверить интеграцию с тарифами

---

## 📋 TODO ЛИСТ (ВСЕ ПУНКТЫ)

### **iOS КОД (9 задач):**

1. ✅ **APIModels.swift** - добавить `access_token` и `refresh_token` в `CreateFamilyResponse` (строки 107-113)
2. ✅ **APIModels.swift** - добавить структуры `RecoveryCodeLoginRequest` и `RecoveryCodeLoginResponse`
3. ✅ **APIService.swift** - добавить метод `loginByRecoveryCode()` (после строки 97)
4. ✅ **FamilyRegistrationViewModel.swift** - удалить моковые данные (строки 264-330)
5. ✅ **FamilyRegistrationViewModel.swift** - раскомментировать API код (строки 332-368)
6. ✅ **FamilyRegistrationViewModel.swift** - добавить сохранение токенов (Попытка 1) в `case .success`
7. ✅ **FamilyRegistrationViewModel.swift** - добавить метод fallback `loginByRecoveryCode()` (Попытка 2)
8. ✅ **FamilyRegistrationViewModel.swift** - добавить метод `saveTokens()` с проверкой и повторной попыткой
9. ✅ **FamilyRegistrationViewModel.swift** - добавить безопасное логирование (без recovery code в логах)

### **BACKEND API (2 задачи):**

10. ✅ **Backend** - изменить `/api/family/create` - добавить генерацию токенов и поля в response
11. ✅ **Backend** - создать новый endpoint `/api/auth/login-by-recovery-code` с проверкой recovery_code

### **ТЕСТИРОВАНИЕ (6 задач):**

12. ✅ **iOS тестирование** - протестировать Попытку 1 (токены в response)
13. ✅ **iOS тестирование** - протестировать Попытку 2 (fallback)
14. ✅ **iOS тестирование** - протестировать сохранение токенов в Keychain
15. ✅ **Интеграционное тестирование** - протестировать полный flow регистрации на реальном устройстве
16. ✅ **Интеграционное тестирование** - протестировать работу API запросов после авторизации
17. ✅ **Backend тестирование** - протестировать оба endpoint (с токенами и без, валидный/невалидный код)

### **ДЕПЛОЙ (3 задачи):**

18. ✅ **Backend деплой** - задеплоить изменения в `/api/family/create`
19. ✅ **Backend деплой** - задеплоить новый endpoint `/api/auth/login-by-recovery-code`
20. ✅ **iOS деплой** - собрать релизную версию и протестировать на TestFlight

**ИТОГО: 20 задач**

---

## 🔍 КАК РАБОТАЕТ МЕХАНИЗМ АВТОРИЗАЦИИ

### **Попытка 1: API возвращает токены при создании семьи**

#### **Как работает:**
```
1. Пользователь создает семью
   ↓
2. POST /api/family/create
   {
       "role": "parent",
       "age_group": "Adult (18-64)",
       "personal_letter": "V"
   }
   ↓
3. Backend создает семью в БД
   ↓
4. Backend генерирует токены (access_token, refresh_token)
   ↓
5. Response возвращает:
   {
       "family_id": "FAM_123",
       "recovery_code": "FAM-ABCD-EFGH-IJKL",
       "access_token": "eyJhbGciOiJIUzI1NiIs...",  // ✅ Токены
       "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
   }
   ↓
6. iOS сохраняет токены в Keychain
   ↓
7. ✅ Готово! Пользователь авторизован
```

#### **Почему токенов может не быть:**
1. **Backend не поддерживает токены в response** (старая версия API)
2. **Ошибка генерации токенов** на backend
3. **Backend возвращает токены в другом формате**
4. **Backend требует отдельный запрос** для получения токенов

#### **Что нужно изменить:**
- **Backend:** Добавить генерацию токенов в endpoint `/api/family/create`
- **Backend:** Вернуть токены в response
- **iOS:** Проверить наличие токенов в response
- **iOS:** Сохранить токены в Keychain

---

### **Попытка 2: Авторизация по recovery code (fallback)**

#### **Как работает:**
```
1. Попытка 1 не сработала (токенов нет в response)
   ↓
2. iOS получает family_id и recovery_code из response
   ↓
3. POST /api/auth/login-by-recovery-code
   {
       "family_id": "FAM_123",
       "recovery_code": "FAM-ABCD-EFGH-IJKL"
   }
   ↓
4. Backend проверяет recovery_code
   ↓
5. Backend генерирует токены
   ↓
6. Response возвращает:
   {
       "access_token": "eyJhbGciOiJIUzI1NiIs...",
       "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
   }
   ↓
7. iOS сохраняет токены в Keychain
   ↓
8. ✅ Готово! Пользователь авторизован
```

#### **Почему это нужно:**
- ✅ Работает, если backend не поддерживает токены в response
- ✅ Работает, если есть ошибка в Попытке 1
- ✅ Обеспечивает надежность

#### **Что нужно изменить:**
- **Backend:** Создать новый endpoint `/api/auth/login-by-recovery-code`
- **Backend:** Реализовать проверку recovery_code
- **Backend:** Генерировать токены
- **iOS:** Добавить метод `loginByRecoveryCode()` в APIService
- **iOS:** Вызвать метод, если токенов нет в response

---

## ⚠️ КАК ИЗБАВИТЬСЯ ОТ РИСКОВ

### **Риск 1: API не поддерживает токены → используется fallback**

#### **Проблема:**
Backend не может сразу изменить `/api/family/create` для возврата токенов

#### **Решение:**
- ✅ **Fallback уже предусмотрен** - Попытка 2 сработает автоматически
- ✅ **Поэтапная реализация** - можно начать с Попытки 2, потом добавить Попытку 1
- ✅ **Обратная совместимость** - код работает в обоих случаях

#### **Код для митигации:**
```swift
// Проверка токенов в response
if let accessToken = response.access_token,
   let refreshToken = response.refresh_token {
    // ✅ Попытка 1: Токены есть - сохраняем
    saveTokens(accessToken: accessToken, refreshToken: refreshToken)
} else {
    // ✅ Попытка 2: Токенов нет - используем fallback
    loginByRecoveryCode(familyID: response.family_id, recoveryCode: response.recovery_code)
}
```

---

### **Риск 2: Ошибка в fallback → демо режим**

#### **Проблема:**
Оба способа не сработали, пользователь остается без токенов

#### **Решение:**
- ✅ **Обработка ошибок** - ловим все ошибки
- ✅ **Демо режим** - приложение работает локально
- ✅ **Логирование** - записываем ошибки для отладки
- ✅ **Повторная попытка** - можно попробовать снова при следующем запуске

#### **Код для митигации:**
```swift
private func loginByRecoveryCode(familyID: String, recoveryCode: String) {
    apiService.loginByRecoveryCode(familyID: familyID, recoveryCode: recoveryCode) { [weak self] result in
        switch result {
        case .success(let loginResponse):
            // ✅ Успех - сохраняем токены
            saveTokens(accessToken: loginResponse.access_token, refreshToken: loginResponse.refresh_token)
        case .failure(let error):
            // ✅ Обработка ошибки
            print("⚠️ Ошибка авторизации: \(error.localizedDescription)")
            // Продолжаем работу в демо режиме
            // Пользователь может использовать приложение локально
        }
    }
}
```

---

### **Риск 3: Проблемы с Keychain → повторная попытка**

#### **Проблема:**
Токены не сохраняются в Keychain (ошибка доступа, переполнение и т.д.)

#### **Решение:**
- ✅ **Проверка сохранения** - проверяем, что токены сохранены
- ✅ **Повторная попытка** - если не сохранилось, пробуем еще раз
- ✅ **Логирование** - записываем ошибки Keychain
- ✅ **Обработка ошибок** - показываем пользователю, если критично

#### **Код для митигации:**
```swift
func saveTokens(accessToken: String, refreshToken: String?) -> Bool {
    // Попытка 1
    let saved1 = KeychainManager.shared.save(accessToken, forKey: .authToken)
    var saved2 = true
    if let refreshToken = refreshToken {
        saved2 = KeychainManager.shared.save(refreshToken, forKey: .refreshToken)
    }
    
    if saved1 && saved2 {
        print("✅ Токены сохранены успешно")
        return true
    } else {
        print("⚠️ Ошибка сохранения токенов, повторная попытка...")
        // Попытка 2
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            let retry1 = KeychainManager.shared.save(accessToken, forKey: .authToken)
            let retry2 = refreshToken != nil ? KeychainManager.shared.save(refreshToken!, forKey: .refreshToken) : true
            if retry1 && retry2 {
                print("✅ Токены сохранены после повторной попытки")
            } else {
                print("❌ Критическая ошибка: токены не сохранены")
            }
        }
        return false
    }
}
```

---

### **Риск 4: Задержка релиза → можно реализовать поэтапно**

#### **Проблема:**
Backend команда не успевает изменить API, нужно отложить релиз

#### **Решение:**
- ✅ **Поэтапная реализация** - можно начать с Попытки 2 (не требует изменения backend)
- ✅ **Независимость** - Попытка 2 работает отдельно
- ✅ **Гибкость** - можно добавить Попытку 1 позже

#### **План поэтапной реализации:**

**Этап 1 (2-3 часа): Реализовать только Попытку 2**
- ✅ Не требует изменения backend (можно добавить endpoint позже)
- ✅ Работает сразу после создания семьи
- ✅ Пользователь авторизован

**Этап 2 (1-2 часа): Добавить Попытку 1**
- ✅ Когда backend готов, добавить проверку токенов в response
- ✅ Автоматически начнет работать
- ✅ Улучшает UX (быстрее)

---

## 🔗 ВЗАИМОДЕЙСТВИЕ С ТАРИФАМИ

### **Текущая логика активации тарифов:**

#### **1. Бесплатный тариф активируется автоматически:**

```swift
// ALADDINApp.swift (строки ~200-250)
func initializeNavigation() {
    // ...
    
    // ✅ Автоматическая активация бесплатного тарифа
    if !UserDefaults.standard.bool(forKey: "hasFreeTariffActivated") {
        StoreManager.shared.activateFreeTariff()
        UserDefaults.standard.set(true, forKey: "hasFreeTariffActivated")
    }
}
```

#### **2. Тарифы НЕ зависят от авторизации:**

- ✅ **Бесплатный тариф** активируется локально (без API)
- ✅ **Платные тарифы** активируются через StoreKit (без API)
- ⚠️ **Синхронизация тарифов** с сервером требует авторизации

#### **3. Что требует авторизации:**

- ✅ **Синхронизация статуса тарифа** с сервером
- ✅ **Активация тарифа через код** (если есть)
- ✅ **История платежей** (billing history)
- ✅ **Обновление подписки** (upgrade subscription)

#### **4. Что НЕ требует авторизации:**

- ✅ **Активация бесплатного тарифа** (локально)
- ✅ **Покупка через StoreKit** (локально)
- ✅ **Отображение тарифов** (локально)

---

### **Влияние авторизации на тарифы:**

#### **ДО авторизации:**
```
✅ Бесплатный тариф активирован локально
✅ Платные тарифы можно купить через StoreKit
❌ Синхронизация с сервером не работает
❌ История платежей не загружается
❌ Обновление подписки не работает
```

#### **ПОСЛЕ авторизации:**
```
✅ Бесплатный тариф активирован локально
✅ Платные тарифы можно купить через StoreKit
✅ Синхронизация с сервером работает
✅ История платежей загружается
✅ Обновление подписки работает
```

---

### **Вывод:**

**Тарифы НЕ зависят от авторизации для базовой функциональности:**
- ✅ Пользователь может использовать приложение без авторизации
- ✅ Бесплатный тариф работает локально
- ✅ Покупка тарифов работает через StoreKit

**Авторизация нужна для:**
- ✅ Синхронизации с сервером
- ✅ Загрузки истории платежей
- ✅ Обновления подписки
- ✅ Активации тарифа через код (если есть)

**Рекомендация:**
- ✅ Авторизация улучшает функциональность, но не блокирует использование
- ✅ Можно реализовать авторизацию независимо от тарифов
- ✅ Тарифы работают в любом случае

---

## 📋 ДЕТАЛЬНЫЙ ПЛАН РЕАЛИЗАЦИИ

### **ЭТАП 1: Подготовка (30 минут)**

#### **1.1. Создать бэкап текущего кода**
- [ ] Создать git branch: `feature/combined-authentication`
- [ ] Закоммитить текущее состояние
- [ ] Создать бэкап файлов, которые будут изменены

#### **1.2. Проверить структуру API**
- [ ] Проверить текущий endpoint `/api/family/create`
- [ ] Проверить, есть ли endpoint для авторизации
- [ ] Согласовать с backend командой изменения

#### **1.3. Подготовить тестовые данные**
- [ ] Подготовить тестовый recovery code
- [ ] Подготовить тестовый family_id
- [ ] Подготовить моковые токены для тестирования

---

### **ЭТАП 2: Изменение iOS кода (2-3 часа)**

#### **2.1. Изменить APIModels.swift (15 минут)**

**Файл:** `Core/Models/APIModels.swift`  
**Строки:** 107-113

**Задачи:**
- [ ] Добавить поля `access_token` и `refresh_token` в `CreateFamilyResponse`
- [ ] Добавить структуру `RecoveryCodeLoginRequest`
- [ ] Добавить структуру `RecoveryCodeLoginResponse`

**Код:**
```swift
struct CreateFamilyResponse: Codable {
    let success: Bool
    let family_id: String
    let recovery_code: String
    let members: [FamilyMemberResponse]
    let your_member_id: String
    let access_token: String?  // ✅ ДОБАВИТЬ
    let refresh_token: String? // ✅ ДОБАВИТЬ
}

struct RecoveryCodeLoginRequest: Codable {
    let family_id: String
    let recovery_code: String
}

struct RecoveryCodeLoginResponse: Codable {
    let access_token: String
    let refresh_token: String?
    let expires_in: TimeInterval?
}
```

---

#### **2.2. Добавить метод в APIService.swift (30 минут)**

**Файл:** `Core/Network/APIService.swift`  
**Строки:** После строки 97 (после `joinFamily`)

**Задачи:**
- [ ] Добавить метод `loginByRecoveryCode()`
- [ ] Реализовать POST запрос к `/auth/login-by-recovery-code`
- [ ] Добавить обработку ошибок

**Код:**
```swift
func loginByRecoveryCode(familyID: String, recoveryCode: String, completion: @escaping (Result<RecoveryCodeLoginResponse, Error>) -> Void) {
    let request = RecoveryCodeLoginRequest(family_id: familyID, recovery_code: recoveryCode)
    networkManager.post(endpoint: "/auth/login-by-recovery-code", body: request, completion: completion)
}
```

---

#### **2.3. Изменить FamilyRegistrationViewModel.swift (1.5-2 часа)**

**Файл:** `ViewModels/FamilyRegistrationViewModel.swift`  
**Строки:** 256-369

**Задачи:**

**2.3.1. Удалить моковые данные (строки 264-330)**
- [ ] Удалить блок с моковыми данными
- [ ] Удалить генерацию `mockFamilyID` и `mockRecoveryCode`
- [ ] Удалить сохранение моковых данных в UserDefaults

**2.3.2. Раскомментировать API код (строки 332-368)**
- [ ] Удалить комментарии `/* ЗАКОММЕНТИРОВАННЫЙ API КОД */`
- [ ] Оставить только код API запроса

**2.3.3. Добавить сохранение токенов (Попытка 1)**
- [ ] В `case .success(let response):` добавить проверку токенов
- [ ] Если токены есть → сохранить в Keychain
- [ ] Добавить логирование

**2.3.4. Добавить метод fallback (Попытка 2)**
- [ ] Добавить метод `loginByRecoveryCode()` в ViewModel
- [ ] Вызвать метод, если токенов нет в response
- [ ] Добавить обработку ошибок

**Код:**
```swift
case .success(let response):
    self?.familyID = response.family_id
    self?.recoveryCode = response.recovery_code
    
    // ✅ ПОПЫТКА 1: Токены в response
    if let accessToken = response.access_token,
       let refreshToken = response.refresh_token {
        KeychainManager.shared.save(accessToken, forKey: .authToken)
        KeychainManager.shared.save(refreshToken, forKey: .refreshToken)
        print("✅ Токены сохранены из response")
    } else {
        // ✅ ПОПЫТКА 2: Авторизация по recovery code
        self?.loginByRecoveryCode(
            familyID: response.family_id,
            recoveryCode: response.recovery_code
        )
    }
    
    // ... остальной код ...

private func loginByRecoveryCode(familyID: String, recoveryCode: String) {
    apiService.loginByRecoveryCode(familyID: familyID, recoveryCode: recoveryCode) { [weak self] result in
        switch result {
        case .success(let loginResponse):
            KeychainManager.shared.save(loginResponse.access_token, forKey: .authToken)
            if let refreshToken = loginResponse.refresh_token {
                KeychainManager.shared.save(refreshToken, forKey: .refreshToken)
            }
            print("✅ Токены сохранены через recovery code")
        case .failure(let error):
            print("⚠️ Ошибка авторизации: \(error.localizedDescription)")
        }
    }
}
```

---

#### **2.4. Добавить проверку сохранения токенов (30 минут)**

**Файл:** `ViewModels/FamilyRegistrationViewModel.swift`

**Задачи:**
- [ ] Добавить метод `saveTokens()` с проверкой
- [ ] Добавить повторную попытку сохранения
- [ ] Добавить логирование ошибок

**Код:**
```swift
private func saveTokens(accessToken: String, refreshToken: String?) -> Bool {
    let saved1 = KeychainManager.shared.save(accessToken, forKey: .authToken)
    var saved2 = true
    if let refreshToken = refreshToken {
        saved2 = KeychainManager.shared.save(refreshToken, forKey: .refreshToken)
    }
    
    if saved1 && saved2 {
        print("✅ Токены сохранены успешно")
        return true
    } else {
        print("⚠️ Ошибка сохранения токенов")
        return false
    }
}
```

---

#### **2.5. Тестирование iOS кода (30 минут)**

**Задачи:**
- [ ] Тестировать с моковыми данными (токены в response)
- [ ] Тестировать fallback (токенов нет в response)
- [ ] Проверить сохранение токенов в Keychain
- [ ] Проверить обработку ошибок

---

### **ЭТАП 3: Изменение Backend API (2-3 часа)**

#### **3.1. Изменить `/api/family/create` (1-1.5 часа)**

**Файл:** Backend API (Python)

**Задачи:**
- [ ] Добавить генерацию токенов после создания семьи
- [ ] Добавить поля `access_token` и `refresh_token` в response
- [ ] Добавить обработку ошибок генерации токенов
- [ ] Добавить логирование

**Код:**
```python
@router.post("/family/create")
async def create_family(request: CreateFamilyRequest):
    # Создать семью
    family = create_family_in_db(...)
    
    # ✅ Генерация токенов
    try:
        access_token = generate_access_token(family_id=family.id)
        refresh_token = generate_refresh_token(family_id=family.id)
    except Exception as e:
        # Если не удалось, возвращаем без токенов (fallback сработает)
        access_token = None
        refresh_token = None
        logger.warning(f"Не удалось сгенерировать токены: {e}")
    
    return {
        "success": True,
        "family_id": family.id,
        "recovery_code": family.recovery_code,
        "members": [...],
        "your_member_id": "...",
        "access_token": access_token,  # ✅ ДОБАВИТЬ
        "refresh_token": refresh_token # ✅ ДОБАВИТЬ
    }
```

---

#### **3.2. Добавить `/api/auth/login-by-recovery-code` (1-1.5 часа)**

**Файл:** Backend API (Python) - новый endpoint

**Задачи:**
- [ ] Создать новый endpoint `/api/auth/login-by-recovery-code`
- [ ] Реализовать проверку recovery_code
- [ ] Реализовать проверку family_id
- [ ] Генерировать токены
- [ ] Добавить обработку ошибок
- [ ] Добавить логирование

**Код:**
```python
@router.post("/auth/login-by-recovery-code")
async def login_by_recovery_code(request: RecoveryCodeLoginRequest):
    # Проверить recovery_code
    family = get_family_by_recovery_code(request.recovery_code)
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    
    # Проверить family_id
    if family.id != request.family_id:
        raise HTTPException(status_code=403, detail="Invalid recovery code")
    
    # Генерировать токены
    access_token = generate_access_token(family_id=family.id)
    refresh_token = generate_refresh_token(family_id=family.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 3600
    }
```

---

#### **3.3. Тестирование Backend API (30 минут)**

**Задачи:**
- [ ] Тестировать `/api/family/create` с токенами
- [ ] Тестировать `/api/family/create` без токенов (ошибка генерации)
- [ ] Тестировать `/api/auth/login-by-recovery-code` с валидным кодом
- [ ] Тестировать `/api/auth/login-by-recovery-code` с невалидным кодом
- [ ] Проверить обработку ошибок

---

### **ЭТАП 4: Интеграционное тестирование (1 час)**

#### **4.1. Тестирование полного flow (30 минут)**

**Задачи:**
- [ ] Тестировать регистрацию семьи с токенами в response (Попытка 1)
- [ ] Тестировать регистрацию семьи без токенов (Попытка 2)
- [ ] Проверить сохранение токенов в Keychain
- [ ] Проверить работу API запросов после авторизации
- [ ] Проверить обработку ошибок

#### **4.2. Тестирование на реальном устройстве (30 минут)**

**Задачи:**
- [ ] Тестировать на реальном устройстве (TestFlight)
- [ ] Проверить работу Keychain на реальном устройстве
- [ ] Проверить работу API запросов
- [ ] Проверить обработку ошибок сети

---

### **ЭТАП 5: Деплой (30 минут)**

#### **5.1. Деплой Backend (15 минут)**

**Задачи:**
- [ ] Деплой изменений в `/api/family/create`
- [ ] Деплой нового endpoint `/api/auth/login-by-recovery-code`
- [ ] Проверить работу endpoints
- [ ] Мониторинг логов

#### **5.2. Деплой iOS (15 минут)**

**Задачи:**
- [ ] Собрать релизную версию
- [ ] Протестировать на TestFlight
- [ ] Мониторинг логов
- [ ] Проверить работу авторизации

---

## ✅ TODO ЛИСТ

### **iOS КОД:**

#### **Файл 1: `Core/Models/APIModels.swift`**
- [ ] Добавить `access_token: String?` в `CreateFamilyResponse` (строка 107-113)
- [ ] Добавить `refresh_token: String?` в `CreateFamilyResponse` (строка 107-113)
- [ ] Добавить структуру `RecoveryCodeLoginRequest` (после `CreateFamilyResponse`)
- [ ] Добавить структуру `RecoveryCodeLoginResponse` (после `RecoveryCodeLoginRequest`)

#### **Файл 2: `Core/Network/APIService.swift`**
- [ ] Добавить метод `loginByRecoveryCode(familyID:recoveryCode:completion:)` (после строки 97)
- [ ] Реализовать POST запрос к `/auth/login-by-recovery-code`
- [ ] Добавить обработку ошибок

#### **Файл 3: `ViewModels/FamilyRegistrationViewModel.swift`**
- [ ] Удалить моковые данные (строки 264-330)
- [ ] Раскомментировать API код (строки 332-368)
- [ ] В `case .success(let response):` добавить проверку токенов (Попытка 1)
- [ ] Если токены есть → сохранить в Keychain
- [ ] Если токенов нет → вызвать `loginByRecoveryCode()` (Попытка 2)
- [ ] Добавить метод `loginByRecoveryCode(familyID:recoveryCode:)` (после `createFamily`)
- [ ] Добавить метод `saveTokens(accessToken:refreshToken:)` с проверкой
- [ ] Добавить обработку ошибок в обоих способах
- [ ] Добавить логирование (безопасное, без recovery code)
- [ ] Добавить повторную попытку сохранения токенов

#### **Файл 4: `Core/Config/AppConfig.swift` (опционально)**
- [ ] Добавить `static let loginByRecoveryCode = "/auth/login-by-recovery-code"` в enum Endpoint

---

### **BACKEND API:**

#### **Endpoint 1: `/api/family/create`**
- [ ] Добавить генерацию `access_token` после создания семьи
- [ ] Добавить генерацию `refresh_token` после создания семьи
- [ ] Добавить поля `access_token` и `refresh_token` в response
- [ ] Добавить обработку ошибок генерации токенов
- [ ] Добавить логирование
- [ ] Добавить тесты

#### **Endpoint 2: `/api/auth/login-by-recovery-code` (новый)**
- [ ] Создать новый endpoint `/api/auth/login-by-recovery-code`
- [ ] Реализовать проверку `recovery_code`
- [ ] Реализовать проверку `family_id`
- [ ] Генерировать `access_token`
- [ ] Генерировать `refresh_token`
- [ ] Добавить обработку ошибок (404, 403)
- [ ] Добавить логирование
- [ ] Добавить тесты

---

### **ТЕСТИРОВАНИЕ:**

#### **iOS:**
- [ ] Тестировать Попытку 1 (токены в response)
- [ ] Тестировать Попытку 2 (fallback)
- [ ] Тестировать сохранение токенов в Keychain
- [ ] Тестировать обработку ошибок
- [ ] Тестировать на реальном устройстве

#### **Backend:**
- [ ] Тестировать `/api/family/create` с токенами
- [ ] Тестировать `/api/family/create` без токенов
- [ ] Тестировать `/api/auth/login-by-recovery-code` с валидным кодом
- [ ] Тестировать `/api/auth/login-by-recovery-code` с невалидным кодом

#### **Интеграционное:**
- [ ] Тестировать полный flow регистрации
- [ ] Тестировать работу API запросов после авторизации
- [ ] Тестировать на реальном устройстве (TestFlight)

---

### **ДЕПЛОЙ:**

#### **Backend:**
- [ ] Деплой изменений в `/api/family/create`
- [ ] Деплой нового endpoint `/api/auth/login-by-recovery-code`
- [ ] Проверить работу endpoints
- [ ] Мониторинг логов

#### **iOS:**
- [ ] Собрать релизную версию
- [ ] Протестировать на TestFlight
- [ ] Мониторинг логов
- [ ] Проверить работу авторизации

---

## 📊 ИТОГОВАЯ СТАТИСТИКА

### **Время реализации:**
- **iOS:** 2-3 часа
- **Backend:** 2-3 часа
- **Тестирование:** 1 час
- **Деплой:** 30 минут
- **Итого:** 5.5-7.5 часов

### **Файлов для изменения:**
- **iOS:** 3 файла
- **Backend:** 2 endpoint
- **Итого:** 5 файлов/endpoint

### **Строк кода:**
- **iOS:** ~200 строк (изменение + добавление)
- **Backend:** ~100 строк (изменение + добавление)
- **Итого:** ~300 строк

---

**Готово!** Детальный план реализации с TODO листом по всем пунктам.
