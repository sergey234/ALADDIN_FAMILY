# 🔐 ПОЛНЫЙ АНАЛИЗ АВТОРИЗАЦИИ В ALADDIN

**Дата:** 2026-02-11  
**Цель:** Понять реальную логику авторизации БЕЗ персональных данных

---

## 🎯 КЛЮЧЕВОЕ ТРЕБОВАНИЕ

### **НЕ собирать персональные данные:**
- ❌ Email
- ❌ Password
- ❌ Телефон
- ❌ Имя

---

## 📊 РЕАЛЬНАЯ ЛОГИКА АВТОРИЗАЦИИ

### **Как работает авторизация в приложении:**

#### **ШАГ 1: Создание семьи (БЕЗ персональных данных)** ✅

**Endpoint:** `POST /api/family/create`

**Запрос:**
```json
{
  "role": "parent",
  "age_group": "Adult (18-64)",
  "personal_letter": "V",
  "device_type": "iOS"
}
```

**Ответ:**
```json
{
  "success": true,
  "family_id": "FAM_59316C46-3F9",
  "recovery_code": "FAM-835E-78F4-E5B7",
  "members": [...],
  "your_member_id": "...",
  "access_token": "...",  // ✅ Опционально (если API поддерживает)
  "refresh_token": "..."   // ✅ Опционально (если API поддерживает)
}
```

**Вывод:** ✅ Создание семьи НЕ требует персональных данных!

---

#### **ШАГ 2: Авторизация (два варианта)** ✅

**Вариант 1: Автоматическая авторизация (если API возвращает токены)** ✅

**Логика:**
- Если `CreateFamilyResponse` содержит `access_token` и `refresh_token`
- Сохранить токены в Keychain
- Готово! Авторизация завершена

**Код в iOS:**
```swift
// ViewModels/FamilyRegistrationViewModel.swift
case .success(let response):
    // ✅ ПОПЫТКА 1: Проверяем, есть ли токены в response
    if let accessToken = response.access_token,
       let refreshToken = response.refresh_token {
        // Сохранить токены
        KeychainManager.shared.save(accessToken, forKey: .authToken)
        KeychainManager.shared.save(refreshToken, forKey: .refreshToken)
        print("✅ Токены сохранены из response")
    }
```

---

**Вариант 2: Авторизация по Recovery Code (fallback)** ✅

**Логика:**
- Если токенов нет в response от `/family/create`
- Использовать `family_id` и `recovery_code` для авторизации
- Endpoint: `POST /api/auth/login-by-recovery-code`

**Запрос:**
```json
{
  "family_id": "FAM_59316C46-3F9",
  "recovery_code": "FAM-835E-78F4-E5B7"
}
```

**Ответ:**
```json
{
  "access_token": "jwt_token_here",
  "refresh_token": "refresh_token_here",
  "expires_in": 3600
}
```

**Код в iOS:**
```swift
// ✅ ПОПЫТКА 2: Авторизация по recovery code (fallback)
self?.loginByRecoveryCode(
    familyID: response.family_id,
    recoveryCode: response.recovery_code
)
```

---

## ✅ ВЫВОДЫ

### **1. Авторизация БЕЗ персональных данных:** ✅

**Как это работает:**
1. Пользователь создает семью (БЕЗ email/password)
2. Получает `family_id` и `recovery_code`
3. Автоматически авторизуется (через токены в response или через recovery code)
4. Токены сохраняются в Keychain
5. Все последующие запросы используют токены

**Вывод:** ✅ **НЕ собираются персональные данные!**

---

### **2. Email/Password авторизация:** ⚠️

**Используется только для:**
- ⚠️ Тестирования
- ⚠️ Администраторов
- ⚠️ Разработки

**НЕ используется в основном приложении!**

---

## 🎯 ДЛЯ СКРИПТА ТЕСТИРОВАНИЯ

### **Рекомендуемый подход:**

**Использовать Recovery Code авторизацию:**

1. **Создать тестовую семью:**
   ```bash
   FAMILY_RESPONSE=$(curl -s -X POST "$BASE_URL/api/family/create" \
     -H "Content-Type: application/json" \
     -d '{
       "role": "parent",
       "age_group": "Adult (18-64)",
       "personal_letter": "V",
       "device_type": "iOS"
     }')
   
   FAMILY_ID=$(echo "$FAMILY_RESPONSE" | jq -r '.family_id')
   RECOVERY_CODE=$(echo "$FAMILY_RESPONSE" | jq -r '.recovery_code')
   ```

2. **Попытка 1: Проверить токены в response:**
   ```bash
   ACCESS_TOKEN=$(echo "$FAMILY_RESPONSE" | jq -r '.access_token // ""')
   REFRESH_TOKEN=$(echo "$FAMILY_RESPONSE" | jq -r '.refresh_token // ""')
   ```

3. **Попытка 2: Авторизация по Recovery Code (если токенов нет):**
   ```bash
   if [ -z "$ACCESS_TOKEN" ]; then
     TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login-by-recovery-code" \
       -H "Content-Type: application/json" \
       -d "{\"family_id\": \"$FAMILY_ID\", \"recovery_code\": \"$RECOVERY_CODE\"}")
     
     ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token // .token // ""')
   fi
   ```

4. **Использовать токен для всех запросов:**
   ```bash
   curl -X GET "$BASE_URL/api/gamification/balance/test_user" \
     -H "Authorization: Bearer $ACCESS_TOKEN"
   ```

---

## ✅ ПРЕИМУЩЕСТВА ЭТОГО ПОДХОДА

1. ✅ **Не требует персональных данных** (email/password)
2. ✅ **Соответствует логике приложения**
3. ✅ **Автоматическая авторизация**
4. ✅ **Безопасно** (recovery code в Keychain)
5. ✅ **Работает для тестирования**

---

## 📋 ПЛАН ДЛЯ СКРИПТА

### **ШАГ 1: Создать тестовую семью** ✅
- Получить `family_id` и `recovery_code`
- Проверить, есть ли токены в response

### **ШАГ 2: Получить токен** ✅
- Попытка 1: Из response от `/family/create`
- Попытка 2: Через `/api/auth/login-by-recovery-code`

### **ШАГ 3: Использовать токен** ✅
- Добавить токен ко всем запросам
- Тестировать все endpoint'ы

---

**Последнее обновление:** 2026-02-11  
**Статус:** ✅ **АНАЛИЗ ЗАВЕРШЕН**

**Вывод:** Использовать Recovery Code авторизацию для скрипта тестирования!
