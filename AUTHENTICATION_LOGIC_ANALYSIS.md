# 🔐 АНАЛИЗ ЛОГИКИ АВТОРИЗАЦИИ В ALADDIN

**Дата:** 2026-02-11  
**Цель:** Понять, как работает авторизация БЕЗ персональных данных

---

## 🎯 ТРЕБОВАНИЯ

### **Ключевое требование:**
- ✅ **НЕ собирать персональные данные** (email, password, телефон)
- ✅ Авторизация для работы API
- ✅ Безопасность

---

## 📊 НАЙДЕННЫЕ МЕТОДЫ АВТОРИЗАЦИИ

### **1. Авторизация через Recovery Code** ✅ **ОСНОВНОЙ МЕТОД**

**Endpoint:** `POST /api/auth/login-by-recovery-code`

**Формат запроса:**
```json
{
  "family_id": "FAM_59316C46-3F9",
  "recovery_code": "FAM-835E-78F4-E5B7"
}
```

**Формат ответа:**
```json
{
  "access_token": "jwt_token_here",
  "refresh_token": "refresh_token_here",
  "expires_in": 3600
}
```

**Как работает:**
1. При создании семьи генерируется `family_id` и `recovery_code`
2. Recovery code используется для авторизации (БЕЗ email/password)
3. Система возвращает токены доступа
4. Токены используются для всех API запросов

**Преимущества:**
- ✅ Не требует персональных данных
- ✅ Автоматическая авторизация после создания семьи
- ✅ Безопасно (recovery code в Keychain)

**Реализация в iOS:**
```swift
// Core/Network/APIService.swift
func loginByRecoveryCode(familyID: String, recoveryCode: String, completion: @escaping (Result<RecoveryCodeLoginResponse, Error>) -> Void) {
    let request = RecoveryCodeLoginRequest(family_id: familyID, recovery_code: recoveryCode)
    networkManager.post(endpoint: AppConfig.Endpoint.loginByRecoveryCode, body: request, completion: completion)
}
```

**Endpoint в AppConfig:**
```swift
static let loginByRecoveryCode = "/auth/login-by-recovery-code"
```

---

### **2. Авторизация через Email/Password** ⚠️ **ДЛЯ ТЕСТИРОВАНИЯ/АДМИНОВ**

**Endpoint:** `POST /api/auth/login`

**Формат запроса:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Примечание:**
- ⚠️ Этот метод требует персональные данные (email)
- ⚠️ Используется для тестирования или администраторов
- ⚠️ НЕ используется в основном приложении

**Реализация на сервере:**
```python
@router.post("/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Авторизация пользователя
    
    Принимает email и password, возвращает access_token и refresh_token
    """
    user = get_user_by_email(db, login_data.email)
    # ...
```

---

## ✅ ПРАВИЛЬНАЯ ЛОГИКА АВТОРИЗАЦИИ

### **Для тестирования endpoint'ов нужно использовать:**

**Метод 1: Recovery Code (правильный для приложения)** ✅
```bash
# Получить токен через recovery code
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login-by-recovery-code" \
  -H "Content-Type: application/json" \
  -d '{"family_id": "FAM_59316C46-3F9", "recovery_code": "FAM-835E-78F4-E5B7"}' \
  | jq -r '.access_token // .token // ""')
```

**Метод 2: Email/Password (только для тестирования)** ⚠️
```bash
# Получить токен через email (только для тестирования)
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "test"}' \
  | jq -r '.access_token // .data.access_token // .token // ""')
```

---

## 🔍 ПРОВЕРКА НА СЕРВЕРЕ

### **Что нужно проверить:**

1. **Существует ли endpoint `/api/auth/login-by-recovery-code`?**
   - Проверить на сервере
   - Проверить формат ответа

2. **Какой формат ответа?**
   - Где находится `access_token`?
   - В корне ответа или в `data.access_token`?

3. **Работает ли endpoint?**
   - Протестировать с реальными данными
   - Проверить формат ошибок

---

## 🎯 РЕКОМЕНДАЦИИ ДЛЯ СКРИПТА ТЕСТИРОВАНИЯ

### **Вариант 1: Использовать Recovery Code (правильный)** ✅

**Преимущества:**
- ✅ Соответствует логике приложения
- ✅ Не требует персональных данных
- ✅ Правильный способ авторизации

**Недостатки:**
- ⚠️ Нужны реальные `family_id` и `recovery_code`
- ⚠️ Нужно создать тестовую семью

**Реализация:**
```bash
# 1. Создать тестовую семью
FAMILY_RESPONSE=$(curl -s -X POST "$BASE_URL/api/family/create" \
  -H "Content-Type: application/json" \
  -d '{"role": "parent", "age_group": "Adult (18-64)", "personal_letter": "V"}')

FAMILY_ID=$(echo "$FAMILY_RESPONSE" | jq -r '.family_id')
RECOVERY_CODE=$(echo "$FAMILY_RESPONSE" | jq -r '.recovery_code')

# 2. Получить токен через recovery code
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login-by-recovery-code" \
  -H "Content-Type: application/json" \
  -d "{\"family_id\": \"$FAMILY_ID\", \"recovery_code\": \"$RECOVERY_CODE\"}" \
  | jq -r '.access_token // .token // ""')
```

---

### **Вариант 2: Использовать Email/Password (для тестирования)** ⚠️

**Преимущества:**
- ✅ Проще для тестирования
- ✅ Не нужно создавать семью

**Недостатки:**
- ❌ Требует персональные данные (email)
- ❌ Не соответствует логике приложения
- ❌ Может не работать, если нет тестового пользователя

**Реализация:**
```bash
# Получить токен через email (только для тестирования)
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "test"}' \
  | jq -r '.access_token // .data.access_token // .token // ""')
```

---

## ✅ ВЫВОДЫ

### **Правильная логика авторизации:**

1. ✅ **Основной метод:** Recovery Code (БЕЗ персональных данных)
   - Endpoint: `/api/auth/login-by-recovery-code`
   - Формат: `{"family_id": "...", "recovery_code": "..."}`
   - Используется в приложении

2. ⚠️ **Для тестирования:** Email/Password (требует персональные данные)
   - Endpoint: `/api/auth/login`
   - Формат: `{"email": "...", "password": "..."}`
   - Только для тестирования/админов

### **Рекомендация для скрипта:**

**Использовать Recovery Code:**
1. Создать тестовую семью
2. Получить `family_id` и `recovery_code`
3. Использовать для авторизации
4. Получить токен
5. Использовать токен для всех запросов

**Это соответствует логике приложения и не требует персональных данных!**

---

**Последнее обновление:** 2026-02-11  
**Статус:** ✅ **АНАЛИЗ ЗАВЕРШЕН**

**Вывод:** Использовать Recovery Code для авторизации в скрипте тестирования!
