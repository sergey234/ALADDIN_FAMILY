# 🧪 ПЛАН РУЧНОГО ТЕСТИРОВАНИЯ ENDPOINT'ОВ

**Дата:** 2026-02-11  
**Метод:** Ручное тестирование по одному endpoint'у  
**Цель:** Убедиться, что каждый endpoint работает на сервере и в мобильном приложении

---

## 🎯 ПРИНЦИП ТЕСТИРОВАНИЯ

### **Порядок:**
1. ✅ Тестируем endpoint на **сервере** (через curl/Postman)
2. ✅ Если работает на сервере → тестируем в **мобильном приложении**
3. ✅ Если не работает → исправляем и повторяем

---

## 📋 СПИСОК ENDPOINT'ОВ ДЛЯ ТЕСТИРОВАНИЯ

### **1. Базовые endpoint'ы (проверка работы сервера)**

#### **1.1 GET /api/health**
- **Цель:** Проверить, что сервер работает
- **Метод:** GET
- **Авторизация:** Не требуется
- **Ожидаемый ответ:** `{"status": "ok"}`

**Тест на сервере:**
```bash
curl -X GET "http://149.154.65.180:8002/api/health"
```

**Тест в iOS:**
- Проверить в `APIService.swift` метод `getHealth()`

---

### **2. Авторизация**

#### **2.1 POST /api/auth/login**
- **Цель:** Авторизация через email/password (для тестирования)
- **Метод:** POST
- **Авторизация:** Не требуется
- **Тело запроса:**
  ```json
  {
    "email": "test@test.com",
    "password": "test"
  }
  ```
- **Ожидаемый ответ:**
  ```json
  {
    "access_token": "...",
    "refresh_token": "...",
    "expires_in": 3600,
    "token_type": "Bearer"
  }
  ```

**Тест на сервере:**
```bash
curl -X POST "http://149.154.65.180:8002/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "test"}'
```

**Тест в iOS:**
- Проверить в `APIService.swift` метод `login(email:password:)`

---

#### **2.2 POST /api/auth/login-by-recovery-code** ⚠️
- **Цель:** Авторизация через recovery code (БЕЗ персональных данных)
- **Метод:** POST
- **Авторизация:** Не требуется
- **Тело запроса:**
  ```json
  {
    "family_id": "FAM_59316C46-3F9",
    "recovery_code": "FAM-835E-78F4-E5B7"
  }
  ```
- **Ожидаемый ответ:**
  ```json
  {
    "access_token": "...",
    "refresh_token": "...",
    "expires_in": 3600
  }
  ```

**Статус:** ❌ НЕ реализован на сервере

**Тест на сервере:**
```bash
curl -X POST "http://149.154.65.180:8002/api/auth/login-by-recovery-code" \
  -H "Content-Type: application/json" \
  -d '{"family_id": "FAM_TEST", "recovery_code": "TEST"}'
```

**Ожидаемый результат:** 404 Not Found (endpoint не существует)

---

### **3. Семья**

#### **3.1 POST /api/family/create** ⚠️
- **Цель:** Создание семьи БЕЗ персональных данных
- **Метод:** POST
- **Авторизация:** Не требуется
- **Тело запроса:**
  ```json
  {
    "role": "parent",
    "age_group": "Adult (18-64)",
    "personal_letter": "V",
    "device_type": "iOS"
  }
  ```
- **Ожидаемый ответ:**
  ```json
  {
    "success": true,
    "family_id": "FAM_59316C46-3F9",
    "recovery_code": "FAM-835E-78F4-E5B7",
    "members": [...],
    "your_member_id": "..."
  }
  ```

**Статус:** ⚠️ Функция существует, но endpoint не подключен

**Тест на сервере:**
```bash
curl -X POST "http://149.154.65.180:8002/api/family/create" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "parent",
    "age_group": "Adult (18-64)",
    "personal_letter": "V",
    "device_type": "iOS"
  }'
```

**Ожидаемый результат:** 404 Not Found (endpoint не подключен)

---

#### **3.2 GET /api/family/stats**
- **Цель:** Получить статистику семьи
- **Метод:** GET
- **Авторизация:** Требуется (Bearer Token)
- **Ожидаемый ответ:**
  ```json
  {
    "totalMembers": 3,
    "totalDevices": 5,
    "totalThreats": 10,
    "protectionLevel": 85,
    "familyStatus": "protected",
    "familyStatusMessage": "Все в порядке"
  }
  ```

**Тест на сервере:**
```bash
# 1. Получить токен
TOKEN=$(curl -s -X POST "http://149.154.65.180:8002/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "test"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")

# 2. Использовать токен
curl -X GET "http://149.154.65.180:8002/api/family/stats" \
  -H "Authorization: Bearer $TOKEN"
```

**Тест в iOS:**
- Проверить в `APIService.swift` метод `getFamilyStats()`

---

## 🎯 ПЛАН ДЕЙСТВИЙ

### **ШАГ 1: Проверить базовые endpoint'ы**
1. ✅ GET /api/health
2. ✅ POST /api/auth/login

### **ШАГ 2: Проверить endpoint'ы семьи**
1. ⚠️ POST /api/family/create (проверить, работает ли)
2. ✅ GET /api/family/stats (если есть токен)

### **ШАГ 3: Проверить в мобильном приложении**
1. Открыть Xcode
2. Запустить приложение
3. Проверить каждый endpoint через UI

---

## 📝 ШАБЛОН ДЛЯ ТЕСТИРОВАНИЯ

### **Для каждого endpoint'а:**

**1. Тест на сервере:**
- [ ] Запрос выполнен
- [ ] Получен ответ
- [ ] Статус код правильный (200, 201, и т.д.)
- [ ] Формат ответа правильный (JSON)

**2. Тест в iOS:**
- [ ] Метод существует в `APIService.swift`
- [ ] Запрос выполняется
- [ ] Ответ обрабатывается
- [ ] UI обновляется

**3. Результат:**
- ✅ Работает
- ❌ Не работает (описать проблему)
- ⚠️ Частично работает (описать что не работает)

---

**Последнее обновление:** 2026-02-11  
**Статус:** 🧪 **ГОТОВ К ТЕСТИРОВАНИЮ**
