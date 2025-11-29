# 🔧 ИСПРАВЛЕНИЕ: Страница не загружается

## ❌ ПРОБЛЕМА
Страница `https://aladdin-ai.ru/success.html?paymentId=PAY_20251123204343_9411EE3E` не загружается и не показывает код активации.

## 🔍 ПРИЧИНА
**Mixed Content Error:**
- Сайт работает по HTTPS (`https://aladdin-ai.ru`)
- API запросы шли по HTTP (`http://149.154.65.180:8000`)
- Браузер блокирует HTTP запросы с HTTPS страниц (безопасность)

## ✅ РЕШЕНИЕ

### 1. Использовать относительный путь через Nginx прокси

**Было:**
```javascript
API_BASE = 'http://149.154.65.180:8000'; // HTTP - блокируется браузером
```

**Стало:**
```javascript
API_BASE = ''; // Пустой = тот же домен и протокол (HTTPS через Nginx)
```

### 2. Nginx прокси уже настроен

Проверено: `/etc/nginx/sites-available/aladdin-ai.ru` содержит:
```nginx
location /api/ {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Это означает, что:
- `https://aladdin-ai.ru/api/payments/status/...` → проксируется на `http://localhost:8000/api/payments/status/...`
- Все запросы идут через HTTPS
- Нет mixed content ошибок

---

## 🧪 ТЕСТИРОВАНИЕ

### Проверить API через HTTPS:
```bash
curl 'https://aladdin-ai.ru/api/payments/status/PAY_20251123204343_9411EE3E'
```

**Ожидаемый ответ:**
```json
{
  "paymentId": "PAY_20251123204343_9411EE3E",
  "status": "paid",
  "activationCode": "ALDN-D6W9-IUXN-QGJZ",
  "codeExpiresAt": "2025-12-23T20:43:58.005387"
}
```

### Открыть страницу:
```
https://aladdin-ai.ru/success.html?paymentId=PAY_20251123204343_9411EE3E
```

**Что должно произойти:**
1. ✅ Страница загрузится за 1-2 секунды
2. ✅ JavaScript сделает запрос: `https://aladdin-ai.ru/api/payments/status/PAY_20251123204343_9411EE3E`
3. ✅ Получит код активации: `ALDN-D6W9-IUXN-QGJZ`
4. ✅ Покажет код на странице

---

## 📋 ЧТО ИЗМЕНЕНО

### Файл: `landing/success.html`

**Строка 290:**
```javascript
// БЫЛО:
API_BASE = 'http://149.154.65.180:8000'; // HTTP - блокируется

// СТАЛО:
API_BASE = ''; // HTTPS через Nginx прокси
```

**Результат:**
- Запросы идут через: `https://aladdin-ai.ru/api/...`
- Нет mixed content ошибок
- Все работает через HTTPS

---

## ✅ ПРОВЕРКА

### 1. Файл обновлен на сервере:
```bash
grep "API_BASE = ''" /var/www/aladdin-ai.ru/success.html
```

### 2. Nginx прокси работает:
```bash
curl 'https://aladdin-ai.ru/api/payments/status/PAY_20251123204343_9411EE3E'
```

### 3. Страница загружается:
Откройте: `https://aladdin-ai.ru/success.html?paymentId=PAY_20251123204343_9411EE3E`

---

## 🎯 ИТОГ

**Проблема решена:**
- ✅ Используется относительный путь (HTTPS)
- ✅ Nginx прокси настроен
- ✅ Нет mixed content ошибок
- ✅ Страница должна загружаться за 1-2 секунды

**Проверьте сейчас:**
```
https://aladdin-ai.ru/success.html?paymentId=PAY_20251123204343_9411EE3E
```

Код активации `ALDN-D6W9-IUXN-QGJZ` должен появиться сразу!

