# 🚀 **ALADDIN PRODUCTION READINESS TESTING GUIDE**

## **Для другой ML системы с серверным доступом**

**Дата создания:** 4 марта 2026 года  
**Версия:** 1.0.0  
**Цель:** Полное тестирование продакшн готовности ALADDIN iOS приложения  

---

## 📋 **СОДЕРЖАНИЕ**

1. [🎯 ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ](#-предварительные-требования)
2. [🧪 ЭТАП 1: СЕРВЕРНАЯ ДОСТУПНОСТЬ](#-этап-1-серверная-доступность)
3. [🔐 ЭТАП 2: JWT АУТЕНТИФИКАЦИЯ](#-этап-2-jwt-аутентификация)
4. [🤖 ЭТАП 3: AI ASSISTANT ИНТЕГРАЦИЯ](#-этап-3-ai-assistant-интеграция)
5. [📊 ЭТАП 4: METRICS СИСТЕМА](#-этап-4-metrics-система)
6. [💰 ЭТАП 5: TRIAL-TO-PAID UPGRADE](#-этап-5-trial-to-paid-upgrade)
7. [📱 ЭТАП 6: RUNTIME ТЕСТИРОВАНИЕ](#-этап-6-runtime-тестирование)
8. [🧪 ЭТАП 7: ИНТЕГРАЦИОННОЕ ТЕСТИРОВАНИЕ](#-этап-7-интеграционное-тестирование)
9. [📋 КРИТЕРИИ ПРОДАКШН ГОТОВНОСТИ](#-критерии-продакшн-готовности)
10. [🚨 ОБРАБОТКА ОШИБОК](#-обработка-ошибок)
11. [📊 ОТЧЕТНОСТЬ](#-отчетность)

---

## 🎯 **ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ**

### **Обязательные условия:**
- ✅ **Сервер ALADDIN запущен** и доступен по HTTPS
- ✅ **API Gateway** работает на порту 8002 (или настроенном)
- ✅ **SFM HTTP API** работает на порту 8003 (или настроенном)
- ✅ **SSL сертификат** действующий для aladdin-ai.ru
- ✅ **База данных** PostgreSQL подключена и работает
- ✅ **TestFlight** или **Development** provisioning profile

### **Инструменты для тестирования:**
```bash
# Необходимые инструменты
curl                    # HTTP запросы
jq                      # JSON обработка
openssl               # SSL проверка
python3               # Скрипты тестирования
xcodebuild           # Компиляция iOS
xcode-select        # Xcode tools
```

### **Тестовые данные:**
```json
{
  "testDeviceId": "test-device-prod-ready-001",
  "testUserEmail": "test@aladdin.ai",
  "testMessage": "Проверка работы AI системы",
  "testContext": "general"
}
```

---

## 🧪 **ЭТАП 1: СЕРВЕРНАЯ ДОСТУПНОСТЬ**

### **🎯 ЦЕЛЬ:**
Убедиться что серверная инфраструктура работает и доступна для мобильного приложения.

### **📋 ЧТО ТЕСТИРУЕМ:**
- Доступность основного домена
- HTTPS шифрование
- API Gateway доступность
- SFM HTTP API доступность
- Health check endpoints

### **🔧 КАК ТЕСТИРУЕМ:**

#### **1.1 Базовая доступность сервера:**
```bash
# Тест основного домена
curl -I https://aladdin-ai.ru/

# Ожидаемый результат:
# HTTP/2 200
# server: nginx
# content-type: text/html
# x-powered-by: Express
```

#### **1.2 SSL сертификат:**
```bash
# Проверка SSL
openssl s_client -connect aladdin-ai.ru:443 -servername aladdin-ai.ru < /dev/null

# Ожидаемый результат:
# Verify return code: 0 (ok)
# SSL certificate verify ok
```

#### **1.3 API Gateway health:**
```bash
# Тест API Gateway
curl -s https://aladdin-ai.ru:8002/health | jq .

# Ожидаемый результат:
{
  "status": "healthy",
  "timestamp": "2026-03-04T...",
  "version": "1.0.0"
}
```

#### **1.4 SFM API health:**
```bash
# Тест SFM API
curl -s https://aladdin-ai.ru:8003/health | jq .

# Ожидаемый результат:
{
  "status": "ok",
  "functions_count": 1074,
  "uptime": "123456s"
}
```

#### **1.5 DNS разрешение:**
```bash
# Проверка DNS
nslookup aladdin-ai.ru

# Ожидаемый результат:
# Name: aladdin-ai.ru
# Address: XXX.XXX.XXX.XXX
```

### **✅ КРИТЕРИИ УСПЕХА:**
- [ ] HTTPS доступен (HTTP/2 200)
- [ ] SSL сертификат валиден
- [ ] API Gateway отвечает на health check
- [ ] SFM API отвечает на health check
- [ ] DNS разрешается корректно

### **🚨 ВОЗМОЖНЫЕ ПРОБЛЕМЫ:**
- **Порт 8002/8003 закрыт:** Проверить firewall настройки
- **SSL ошибка:** Обновить сертификат
- **DNS проблема:** Проверить DNS записи

---

## 🔐 **ЭТАП 2: JWT АУТЕНТИФИКАЦИЯ**

### **🎯 ЦЕЛЬ:**
Проверить что JWT система работает корректно и выдает реальные токены.

### **📋 ЧТО ТЕСТИРУЕМ:**
- Trial device registration
- JWT token generation
- Token payload structure
- Subscription data в JWT
- Token expiration logic

### **🔧 КАК ТЕСТИРУЕМ:**

#### **2.1 Trial device registration:**
```bash
# Регистрация тестового устройства
curl -X POST https://aladdin-ai.ru/auth/register-device \
  -H "Content-Type: application/json" \
  -d '{
    "deviceId": "test-device-prod-ready-001",
    "deviceType": "ios"
  }' | jq .

# Ожидаемый результат:
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "deviceId": "test-device-prod-ready-001",
  "subscription": {
    "level": "trial",
    "start_date": "2026-03-04T...",
    "end_date": "2026-03-11T...",
    "trial_info": {
      "duration_days": 14
    },
    "limits": {
      "max_devices": 3,
      "max_ai_messages": 50
    }
  }
}
```

#### **2.2 JWT token validation:**
```bash
# Декодирование JWT (для проверки структуры)
# Используйте https://jwt.io или python скрипт

# Ожидаемая структура payload:
{
  "sub": "test-device-prod-ready-001",
  "device_id": "test-device-prod-ready-001",
  "subscription": {
    "level": "trial",
    "start_date": "2026-03-04T...",
    "end_date": "2026-03-11T...",
    "is_active": true,
    "trial_info": {
      "start_date": "2026-03-04T...",
      "end_date": "2026-03-11T...",
      "duration_days": 14
    },
    "limits": {...},
    "components": [...]
  },
  "exp": 1677801600,
  "iat": 1609459200,
  "iss": "aladdin-backend"
}
```

#### **2.3 Token expiration test:**
```bash
# Проверить exp время (14 дней от создания)
# Проверить что токен не просрочен
```

### **✅ КРИТЕРИИ УСПЕХА:**
- [ ] Trial registration возвращает HTTP 200
- [ ] JWT token присутствует в ответе
- [ ] Payload содержит правильную структуру
- [ ] Subscription level = "trial"
- [ ] Trial duration = 14 дней
- [ ] Limits соответствуют trial плану
- [ ] Token не просрочен

### **🚨 ВОЗМОЖНЫЕ ПРОБЛЕМЫ:**
- **404 ошибка:** Endpoint /auth/register-device не существует
- **500 ошибка:** Серверная ошибка в JWT генерации
- **Неверный payload:** Проблема в subscription логике

---

## 🤖 **ЭТАП 3: AI ASSISTANT ИНТЕГРАЦИЯ**

### **🎯 ЦЕЛЬ:**
Убедиться что AI Assistant работает с реальными ответами от сервера.

### **📋 ЧТО ТЕСТИРУЕМ:**
- AI API доступность
- Ответы от сервера (не mock)
- Контекстная обработка
- Response format validation
- Performance (время ответа)

### **🔧 КАК ТЕСТИРУЕМ:**

#### **3.1 Basic AI request:**
```bash
# Тест базового запроса
curl -X POST https://aladdin-ai.ru/api/ai/assistant/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Привет, как работает защита?",
    "context": "general"
  }' | jq .

# Ожидаемый результат:
{
  "response": "Я реальный AI ALADDIN...",
  "confidence": 0.95,
  "suggestions": ["Проверить статус защиты", "Посмотреть статистику"],
  "follow_up_questions": ["Что вас беспокоит?"],
  "timestamp": "2026-03-04T..."
}
```

#### **3.2 Context testing:**
```bash
# Тест разных контекстов
curl -X POST https://aladdin-ai.ru/api/ai/assistant/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Как настроить защиту?", "context": "protection_status"}'

curl -X POST https://aladdin-ai.ru/api/ai/assistant/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Угрозы в системе", "context": "threat_analysis"}'
```

#### **3.3 Performance test:**
```bash
# Тест производительности
time curl -X POST https://aladdin-ai.ru/api/ai/assistant/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "context": "general"}' -s -o /dev/null

# Ожидаемое время: < 2 секунд
```

#### **3.4 Response diversity check:**
```bash
# Отправить 5 одинаковых запросов
for i in {1..5}; do
  curl -X POST https://aladdin-ai.ru/api/ai/assistant/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "test", "context": "general"}' \
    -s | jq -r '.response' | head -1
done

# Ожидаем: Разные ответы (не одинаковые)
```

### **✅ КРИТЕРИИ УСПЕХА:**
- [ ] AI API возвращает HTTP 200
- [ ] Response содержит реальный текст (не "mock")
- [ ] Confidence > 0.8
- [ ] Suggestions присутствуют
- [ ] Timestamp корректный
- [ ] Время ответа < 2 секунд
- [ ] Ответы разнообразные (не идентичные)

### **🚨 ВОЗМОЖНЫЕ ПРОБЛЕМЫ:**
- **Одинаковые ответы:** Кэширование на сервере
- **Долгое время ответа:** Проблемы с AI моделью
- **404 ошибка:** AI endpoint не настроен

---

## 📊 **ЭТАП 4: METRICS СИСТЕМА**

### **🎯 ЦЕЛЬ:**
Проверить что система сбора метрик работает корректно.

### **📋 ЧТО ТЕСТИРУЕМ:**
- Metrics upload endpoint
- Data validation
- Storage confirmation
- Error handling

### **🔧 КАК ТЕСТИРУЕМ:**

#### **4.1 Metrics upload test:**
```bash
# Тест отправки метрик
curl -X POST https://aladdin-ai.ru/metrics/upload \
  -H "Content-Type: application/json" \
  -d '{
    "deviceId": "test-device-prod-ready-001",
    "appVersion": "1.0.0",
    "platform": "ios",
    "metrics": [
      {
        "timestamp": "2026-03-04T10:00:00Z",
        "type": "api_request",
        "endpoint": "/api/ai/assistant/chat",
        "responseTime": 1.5,
        "statusCode": 200,
        "success": true
      },
      {
        "timestamp": "2026-03-04T10:00:01Z",
        "type": "user_action",
        "action": "ai_message_sent",
        "value": 1
      }
    ]
  }' | jq .

# Ожидаемый результат:
{
  "success": true,
  "message": "Metrics uploaded successfully: 2 metrics from device test-device-prod-ready-001",
  "uploaded_at": "2026-03-04T...",
  "status": "processed",
  "metrics_count": 2,
  "device_id": "test-device-prod-ready-001"
}
```

#### **4.2 Invalid data test:**
```bash
# Тест с невалидными данными
curl -X POST https://aladdin-ai.ru/metrics/upload \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}'

# Ожидаемая ошибка:
{
  "success": false,
  "error": "Invalid metrics data: deviceId and metrics required"
}
```

### **✅ КРИТЕРИИ УСПЕХА:**
- [ ] Metrics upload возвращает HTTP 200
- [ ] Success = true
- [ ] Сообщение содержит количество метрик
- [ ] Invalid data возвращает ошибку

### **🚨 ВОЗМОЖНЫЕ ПРОБЛЕМЫ:**
- **404 ошибка:** Endpoint не реализован
- **500 ошибка:** Проблема с сохранением в БД

---

## 💰 **ЭТАП 5: TRIAL-TO-PAID UPGRADE**

### **🎯 ЦЕЛЬ:**
Проверить полный цикл upgrade от trial к платной подписке.

### **📋 ЧТО ТЕСТИРУЕМ:**
- Trial activation
- Subscription status
- Payment processing
- JWT token update
- Feature unlocking

### **🔧 КАК ТЕСТИРУЕМ:**

#### **5.1 Trial activation (уже протестировано в этапе 2)**

#### **5.2 Subscription status check:**
```bash
# Проверить статус подписки (нужен JWT из trial)
curl -X GET https://aladdin-ai.ru/api/subscription/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" | jq .

# Ожидаемый результат:
{
  "subscription": {
    "level": "trial",
    "is_active": true,
    "days_remaining": 12
  }
}
```

#### **5.3 Payment simulation:**
```bash
# Имитация оплаты (нужен реальный payment endpoint)
curl -X POST https://aladdin-ai.ru/api/payment/process \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "personal",
    "payment_method": "card",
    "amount": 299
  }' | jq .

# Ожидаемый результат:
{
  "success": true,
  "subscription": {
    "level": "personal",
    "start_date": "2026-03-04T...",
    "end_date": "2027-03-04T..."
  },
  "new_token": "new.jwt.token.with.personal.access"
}
```

### **✅ КРИТЕРИИ УСПЕХА:**
- [ ] Trial активирован успешно
- [ ] Subscription status возвращает trial
- [ ] Payment processing работает
- [ ] Новый JWT содержит personal уровень

---

## 📱 **ЭТАП 6: RUNTIME ТЕСТИРОВАНИЕ**

### **🎯 ЦЕЛЬ:**
Протестировать приложение в реальных условиях.

### **📋 ЧТО ТЕСТИРУЕМ:**
- Application launch
- Trial activation flow
- AI Assistant interaction
- Settings functionality
- Error handling

### **🔧 КАК ТЕСТИРУЕМ:**

#### **6.1 Application build:**
```bash
# Сборка приложения
cd /path/to/ios/project
xcodebuild -scheme ALADDIN -sdk iphoneos -configuration Release build

# Ожидаемая сборка без ошибок
```

#### **6.2 Simulator testing:**
```bash
# Запуск на симуляторе
xcodebuild -scheme ALADDIN -sdk iphonesimulator -configuration Debug test

# Проверка логов на отсутствие ошибок
```

#### **6.3 Real device testing:**
```
1. Установить приложение на устройство через Xcode
2. Запустить приложение
3. Проверить:
   - Trial activation
   - AI Assistant работает
   - Настройки сохраняются
   - Нет crash'ей
```

### **✅ КРИТЕРИИ УСПЕХА:**
- [ ] Приложение компилируется без ошибок
- [ ] Запускается на симуляторе
- [ ] Работает на реальном устройстве
- [ ] Нет runtime ошибок
- [ ] Все функции доступны

---

## 🧪 **ЭТАП 7: ИНТЕГРАЦИОННОЕ ТЕСТИРОВАНИЕ**

### **🎯 ЦЕЛЬ:**
Комплексное тестирование всех компонентов вместе.

### **📋 ЧТО ТЕСТИРУЕМ:**
- Полный user journey
- API rate limiting
- Error recovery
- Data persistence

### **🔧 КАК ТЕСТИРУЕМ:**

#### **7.1 Complete user flow:**
```
1. Установить приложение
2. Запустить (trial activation происходит автоматически)
3. Отправить сообщение AI Assistant
4. Проверить статус защиты
5. Попытаться upgrade на Personal
6. Проверить новые возможности
7. Отправить метрики
```

#### **7.2 Load testing:**
```bash
# Тест rate limiting
for i in {1..100}; do
  curl -X POST https://aladdin-ai.ru/api/ai/assistant/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "test '$i'", "context": "general"}' \
    -s -o /dev/null &
done

# Проверить что rate limiting работает
```

#### **7.3 Error scenarios:**
```
1. Отключить интернет - проверить offline поведение
2. Сервер недоступен - проверить error handling
3. Invalid JWT - проверить token refresh
4. Corrupted data - проверить recovery
```

### **✅ КРИТЕРИИ УСПЕХА:**
- [ ] Полный user journey работает
- [ ] Rate limiting предотвращает abuse
- [ ] Error handling graceful
- [ ] Offline режим работает
- [ ] Data recovery работает

---

## 📋 **КРИТЕРИИ ПРОДАКШН ГОТОВНОСТИ**

### **🟢 ОБЯЗАТЕЛЬНЫЕ (БЛОКИРУЮТ РЕЛИЗ):**
- [ ] Сервер доступен 99.9% времени
- [ ] Все API endpoints отвечают корректно
- [ ] JWT система выдает валидные токены
- [ ] AI Assistant работает с реальными ответами
- [ ] Trial-to-paid upgrade функционирует
- [ ] Приложение не крашится в нормальном использовании
- [ ] SSL сертификат валиден
- [ ] Rate limiting настроен

### **🟡 РЕКОМЕНДУЕМЫЕ:**
- [ ] Metrics система собирает данные
- [ ] Performance соответствует ожиданиям
- [ ] Error logging настроен
- [ ] Backup системы работают

### **🔴 КРИТИЧЕСКИЕ ПРОБЛЕМЫ:**
- [ ] 404 ошибки на основных endpoints
- [ ] JWT токены не генерируются
- [ ] AI возвращает mock ответы
- [ ] Приложение крашится при запуске
- [ ] SSL сертификат истек

---

## 🚨 **ОБРАБОТКА ОШИБОК**

### **КОММОН ПРОБЛЕМЫ И РЕШЕНИЯ:**

#### **1. Сервер недоступен:**
```bash
# Диагностика
ping aladdin-ai.ru
traceroute aladdin-ai.ru
curl -I https://aladdin-ai.ru/

# Решения:
# - Проверить firewall
# - Проверить DNS
# - Проверить server logs
```

#### **2. API возвращает 404:**
```bash
# Проверить endpoint
curl -I https://aladdin-ai.ru/api/ai/assistant/chat

# Решения:
# - Проверить routing в API Gateway
# - Проверить SFM API endpoints
# - Проверить server logs
```

#### **3. JWT токены invalid:**
```bash
# Декодировать токен
echo "token" | jq -R 'split(".") | .[1] | @base64d | fromjson'

# Решения:
# - Проверить JWT_SECRET на сервере
# - Проверить expiration time
# - Проверить payload structure
```

#### **4. AI возвращает одинаковые ответы:**
```
# Решения:
# - Отключить кэширование на сервере
# - Проверить AI model diversity
# - Добавить randomization в responses
```

---

## 📊 **ОТЧЕТНОСТЬ**

### **ФОРМАТ ОТЧЕТА:**

```markdown
# ALADDIN Production Readiness Report

## Executive Summary
- Overall Status: ✅ READY / ⚠️ ISSUES / ❌ BLOCKED
- Test Date: YYYY-MM-DD
- Tester: [Name]

## Test Results Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Server Availability | ✅ | All endpoints accessible |
| JWT Authentication | ✅ | Tokens generated correctly |
| AI Integration | ⚠️ | Identical responses detected |
| Metrics System | ❌ | 404 on upload endpoint |

## Detailed Results

### 1. Server Testing
- Domain: aladdin-ai.ru ✅
- SSL Certificate: Valid ✅
- API Gateway: Port 8002 ✅
- SFM API: Port 8003 ✅

### 2. JWT Testing
- Trial Registration: ✅
- Token Structure: ✅
- Payload Validation: ✅
- Expiration: ✅

### 3. AI Testing
- Endpoint Response: ✅
- Response Diversity: ❌ (All responses identical)
- Performance: ✅ (< 2s)

## Issues Found

### Critical Issues
1. **Metrics Upload 404**
   - Endpoint: `/metrics/upload`
   - Impact: No analytics collection
   - Solution: Implement endpoint in API Gateway

2. **AI Response Caching**
   - Problem: Identical responses to different queries
   - Impact: Poor user experience
   - Solution: Disable caching or add randomization

### Minor Issues
1. Rate limiting not tested
2. Error recovery not validated

## Recommendations

### Immediate Actions
1. Fix metrics upload endpoint
2. Investigate AI response caching
3. Implement comprehensive error logging

### Pre-Launch Checklist
- [ ] All critical issues resolved
- [ ] Full integration testing completed
- [ ] Performance benchmarks met
- [ ] Security audit passed
- [ ] User acceptance testing completed

## Conclusion
**READY FOR PRODUCTION: YES/NO**

**Go/No-Go Decision:** [Reasoning]

**Signed:** [Tester Name]
**Date:** [YYYY-MM-DD]
```

---

## 🎯 **ИТОГОВЫЕ РЕКОМЕНДАЦИИ**

### **ДЛЯ УСПЕШНОГО ПРОДАКШН РЕЛИЗА:**

1. **🔴 ОБЯЗАТЕЛЬНО:** Исправить все критические проблемы
2. **🟡 РЕКОМЕНДУЕТСЯ:** Провести полное интеграционное тестирование
3. **🟢 ОПЦИОНАЛЬНО:** Оптимизировать performance и UX

### **ВРЕМЕННЫЕ РАМКИ:**
- **Критические проблемы:** 2-4 часа
- **Полное тестирование:** 4-8 часов
- **Интеграционное тестирование:** 4-8 часов

### **КОМАНДА ТЕСТИРОВАНИЯ:**
- **Backend Developer:** Исправление серверных проблем
- **Mobile Developer:** Runtime тестирование
- **QA Engineer:** Интеграционное тестирование
- **DevOps:** Infrastructure validation

---

**🚀 ЭТОТ ГАЙД ОБЕСПЕЧИТ 100% ПРОДАКШН ГОТОВНОСТИ ALADDIN СИСТЕМЫ!**

**Используйте его для любой ML системы с серверной интеграцией!** 🎯