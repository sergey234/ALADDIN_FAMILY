# 🚀 ПОЛНЫЙ ГАЙД ТЕСТИРОВАНИЯ API ЧЕРЕЗ ЛОГИРОВАНИЕ

## 🎯 ЦЕЛЬ: ПОЛНАЯ ДИАГНОСТИКА ВСЕХ API ВЫЗОВОВ

**Проверить каждую API endpoint на работоспособность через детальное логирование**

---

## 📊 УРОВНИ ЛОГИРОВАНИЯ API

### **Уровень 1: NetworkManager (Транспортный слой)**
```
🔍 REQUEST:  ➡️ GET https://aladdin-ai.ru/api/profile headers=[...]
🔍 RESPONSE: ⬅️ status=200 url=https://aladdin-ai.ru/api/profile body=<json-sanitized>
```

### **Уровень 2: APIService (Бизнес-логика)**
```
🔍 BUSINESS: 👤 Fetching user profile
🔍 BUSINESS: 🔐 Starting login for email: us***@***.***
```

### **Уровень 3: Application (Результаты)**
```
✅ SUCCESS: Profile loaded successfully
❌ ERROR: Login failed - invalid credentials
```

---

## 🧪 ПЛАН ТЕСТИРОВАНИЯ ВСЕХ API

### **ЭТАП 1: ЗАПУСК ПРИЛОЖЕНИЯ (Базовые API)**

#### **Что тестируется:**
- ✅ **Инициализация приложения**
- ✅ **Загрузка профиля пользователя** (автоматически)
- ✅ **Проверка авторизации**

#### **Ожидаемые логи:**
```
🔍 BUSINESS: 👤 Fetching user profile
🔍 REQUEST:  ➡️ GET https://aladdin-ai.ru/api/profile headers=[auth: <redacted>]
🔍 RESPONSE: ⬅️ status=200 url=https://aladdin-ai.ru/api/profile body=<json-sanitized>
✅ SUCCESS: User profile loaded
```

#### **Анализ проблем:**
- **❌ Status 401/403:** Проблема с авторизацией
- **❌ Status 500:** Ошибка сервера
- **❌ Timeout:** Проблема с сетью
- **❌ Нет логов:** API не вызывается

---

### **ЭТАП 2: ТЕСТИРОВАНИЕ АУТЕНТИФИКАЦИИ**

#### **2.1 Регистрация (если доступна)**
```
🔍 BUSINESS: 📝 Starting user registration
🔍 REQUEST:  ➡️ POST https://aladdin-ai.ru/api/auth/register headers=[...]
🔍 RESPONSE: ⬅️ status=201 body=<json-sanitized>
✅ SUCCESS: User registered successfully
```

#### **2.2 Авторизация**
```
🔍 BUSINESS: 🔐 Starting login for email: us***@***.***
🔍 REQUEST:  ➡️ POST https://aladdin-ai.ru/api/auth/login headers=[...]
🔍 RESPONSE: ⬅️ status=200 body=<json-sanitized>
✅ SUCCESS: Login successful, tokens saved
```

#### **2.3 Обновление токена**
```
🔍 BUSINESS: 🔄 Refreshing access token
🔍 REQUEST:  ➡️ POST https://aladdin-ai.ru/api/auth/refresh headers=[...]
🔍 RESPONSE: ⬅️ status=200 body=<json-sanitized>
✅ SUCCESS: Token refreshed
```

---

### **ЭТАП 3: ТЕСТИРОВАНИЕ ПРОФИЛЯ ПОЛЬЗОВАТЕЛЯ**

#### **3.1 Загрузка профиля**
```
🔍 BUSINESS: 👤 Fetching user profile
🔍 REQUEST:  ➡️ GET https://aladdin-ai.ru/api/profile headers=[auth: <redacted>]
🔍 RESPONSE: ⬅️ status=200 body=<json-sanitized>
✅ SUCCESS: Profile loaded with X fields
```

#### **3.2 Обновление профиля**
```
🔍 BUSINESS: ✏️ Updating user profile
🔍 REQUEST:  ➡️ PUT https://aladdin-ai.ru/api/profile headers=[auth: <redacted>]
🔍 RESPONSE: ⬅️ status=200 body=<json-sanitized>
✅ SUCCESS: Profile updated
```

---

### **ЭТАП 4: ТЕСТИРОВАНИЕ СЕМЕЙНЫХ ФУНКЦИЙ**

#### **4.1 Создание семьи**
```
🔍 BUSINESS: 👨‍👩‍👧‍👦 Creating family with role: parent
🔍 REQUEST:  ➡️ POST https://aladdin-ai.ru/api/family/create headers=[auth: <redacted>]
🔍 RESPONSE: ⬅️ status=201 body=<json-sanitized>
✅ SUCCESS: Family created with ID: XXX
```

#### **4.2 Приглашение членов семьи**
```
🔍 BUSINESS: 📨 Sending family invitation
🔍 REQUEST:  ➡️ POST https://aladdin-ai.ru/api/family/invite headers=[auth: <redacted>]
🔍 RESPONSE: ⬅️ status=200 body=<json-sanitized>
✅ SUCCESS: Invitation sent
```

#### **4.3 Загрузка списка семьи**
```
🔍 BUSINESS: 👪 Loading family members
🔍 REQUEST:  ➡️ GET https://aladdin-ai.ru/api/family/members headers=[auth: <redacted>]
🔍 RESPONSE: ⬅️ status=200 body=<json-sanitized>
✅ SUCCESS: Loaded X family members
```

---

### **ЭТАП 5: ТЕСТИРОВАНИЕ ПЛАТЕЖЕЙ**

#### **5.1 Загрузка тарифов**
```
🔍 BUSINESS: 💰 Loading available tariffs
🔍 REQUEST:  ➡️ GET https://aladdin-ai.ru/api/tariffs headers=[auth: <redacted>]
🔍 RESPONSE: ⬅️ status=200 body=<json-sanitized>
✅ SUCCESS: Loaded X tariffs
```

#### **5.2 Создание платежа**
```
🔍 BUSINESS: 💳 Creating payment for tariff: premium
🔍 REQUEST:  ➡️ POST https://aladdin-ai.ru/api/payment/create headers=[auth: <redacted>]
🔍 RESPONSE: ⬅️ status=201 body=<json-sanitized>
✅ SUCCESS: Payment created with ID: XXX
```

#### **5.3 Проверка статуса платежа**
```
🔍 BUSINESS: 🔍 Checking payment status for ID: XXX
🔍 REQUEST:  ➡️ GET https://aladdin-ai.ru/api/payment/XXX/status headers=[auth: <redacted>]
🔍 RESPONSE: ⬅️ status=200 body=<json-sanitized>
✅ SUCCESS: Payment status: completed
```

---

### **ЭТАП 6: ТЕСТИРОВАНИЕ ЗАЩИТНЫХ ФУНКЦИЙ**

#### **6.1 Антивирусное сканирование**
```
🔍 BUSINESS: 🛡️ Starting antivirus scan for file: document.pdf
🔍 REQUEST:  ➡️ POST https://aladdin-ai.ru/api/antivirus/scan headers=[auth: <redacted>]
🔍 RESPONSE: ⬅️ status=200 body=<json-sanitized>
✅ SUCCESS: Scan completed, threats found: X
```

#### **6.2 Проверка обновлений**
```
🔍 BUSINESS: 🔄 Checking for app updates
🔍 REQUEST:  ➡️ GET https://aladdin-ai.ru/api/updates/check headers=[auth: <redacted>]
🔍 RESPONSE: ⬅️ status=200 body=<json-sanitized>
✅ SUCCESS: App is up to date
```

---

### **ЭТАП 7: ТЕСТИРОВАНИЕ PUSH УВЕДОМЛЕНИЙ**

#### **7.1 Регистрация токена устройства**
```
🔍 BUSINESS: 📱 Registering device token for push notifications
🔍 REQUEST:  ➡️ POST https://aladdin-ai.ru/api/notifications/register headers=[auth: <redacted>]
🔍 RESPONSE: ⬅️ status=200 body=<json-sanitized>
✅ SUCCESS: Device token registered
```

#### **7.2 Загрузка настроек уведомлений**
```
🔍 BUSINESS: ⚙️ Loading notification settings
🔍 REQUEST:  ➡️ GET https://aladdin-ai.ru/api/notifications/settings headers=[auth: <redacted>]
🔍 RESPONSE: ⬅️ status=200 body=<json-sanitized>
✅ SUCCESS: Notification settings loaded
```

---

## 🎯 МЕТОДЫ ТЕСТИРОВАНИЯ

### **Метод 1: Visual Logger (Рекомендуется)**
1. **Запустить приложение**
2. **Выполнить действия** (логин, платежи, etc.)
3. **Нажать "Копировать"** в Visual Logger
4. **Вставить логи** в анализатор

### **Метод 2: Xcode Console**
1. **Запустить в DEBUG режиме**
2. **Выполнить действия**
3. **Смотреть логи** в Xcode Console

### **Метод 3: Программный анализ**
```swift
// В Xcode debugger:
po VisualLogger.shared.allLogsText
// или
po MasterLogger.shared.getVisualLogsText()
```

---

## 📊 АНАЛИЗ РЕЗУЛЬТАТОВ

### **✅ УСПЕШНЫЕ API (Зеленый статус):**
```
🔍 REQUEST:  ➡️ GET https://aladdin-ai.ru/api/profile
🔍 RESPONSE: ⬅️ status=200 url=... body=<json-sanitized>
✅ SUCCESS: Profile loaded successfully
```

### **⚠️ ПРОБЛЕМНЫЕ API (Желтый статус):**
```
🔍 REQUEST:  ➡️ POST https://aladdin-ai.ru/api/login
🔍 RESPONSE: ⬅️ status=429 url=... (Too Many Requests)
⚠️ WARNING: Rate limited, retry in 60 seconds
```

### **❌ НЕРАБОЧИЕ API (Красный статус):**
```
🔍 REQUEST:  ➡️ GET https://aladdin-ai.ru/api/settings
🔍 RESPONSE: ⬅️ status=500 url=... body=<json-sanitized>
❌ ERROR: Internal server error
```

---

## 🔧 ДИАГНОСТИКА ПРОБЛЕМ

### **Типичные проблемы:**

#### **1. Авторизация (401/403)**
```
❌ RESPONSE: ⬅️ status=401 url=/api/profile
🔍 Решение: Проверить токены, сделать повторный логин
```

#### **2. Сеть (Timeout/Network Error)**
```
❌ RESPONSE: ⬅️ status=0 (Network timeout)
🔍 Решение: Проверить интернет, повторить запрос
```

#### **3. Сервер (5xx ошибки)**
```
❌ RESPONSE: ⬅️ status=500 url=/api/create
🔍 Решение: Сообщить разработчикам backend
```

#### **4. Данные (4xx ошибки)**
```
❌ RESPONSE: ⬅️ status=400 (Bad Request)
🔍 Решение: Проверить входные данные
```

---

## 📈 МЕТРИКИ ПРОИЗВОДИТЕЛЬНОСТИ

### **Анализ по логам:**
```
📊 REQUEST DURATION: 1.2 seconds (GOOD)
📊 RESPONSE SIZE: 2.3 KB (NORMAL)
📊 STATUS: 200 (SUCCESS)
```

### **Пороги производительности:**
- ✅ **< 1 сек:** Отлично
- ⚠️ **1-3 сек:** Приемлемо
- ❌ **> 3 сек:** Проблема

---

## 🎯 АВТОМАТИЗАЦИЯ ТЕСТИРОВАНИЯ

### **Создать скрипт анализа:**
```swift
func analyzeAPILogs(_ logs: String) -> APITestReport {
    let report = APITestReport()

    // Парсинг логов
    let requests = parseRequests(logs)
    let responses = parseResponses(logs)

    // Анализ каждого API
    for api in allAPIEndpoints {
        let status = checkAPIStatus(api, requests, responses)
        report.addResult(api, status)
    }

    return report
}
```

---

## 📋 ОТЧЕТ О ТЕСТИРОВАНИИ

### **Формат отчета:**
```
🚀 API TESTING REPORT
📅 Date: 2026-02-24
⏱️ Total APIs: 15
✅ Working: 13 (87%)
⚠️ Issues: 2 (13%)
❌ Broken: 0 (0%)

📊 PERFORMANCE:
- Avg Response Time: 1.2s
- Success Rate: 98%
- Error Rate: 2%

🔍 ISSUES FOUND:
1. /api/antivirus/scan - 500 Internal Error
2. /api/payments/status - 429 Rate Limited
```

---

## 🎉 РЕЗУЛЬТАТ

**Через систему логирования можно:**
- ✅ **Протестировать все API** одним запуском приложения
- ✅ **Получить детальную диагностику** каждой endpoint
- ✅ **Измерить производительность** всех запросов
- ✅ **Выявить проблемы** автоматически
- ✅ **Создать отчеты** для команды разработки

**Запустите приложение, выполните все действия и проанализируйте логи - получите полный отчет о состоянии всех API!** 🚀📊