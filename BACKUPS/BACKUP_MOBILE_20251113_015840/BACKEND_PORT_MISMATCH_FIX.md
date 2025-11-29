# 🚨 НАЙДЕНА ПРОБЛЕМА: НЕСОВПАДЕНИЕ ПОРТОВ!

## ✅ НАЙДЕНО

**Backend сервер ЗАПУЩЕН, но на другом порту!**

### Текущая ситуация:

- **iOS приложение ожидает:** `http://localhost:8000/api` ❌
- **Backend сервер работает на:** `http://localhost:8080` ✅

**Процесс Python слушает порт 8080:**
```
Python     5463 sergejhlystov    5u  IPv6  ...  TCP *:8080 (LISTEN)
```

### IP адрес вашего Mac:
```
192.168.0.101
```

---

## 🔧 РЕШЕНИЕ

### Вариант 1: Изменить порт в iOS (РЕКОМЕНДУЕТСЯ)

**Файл:** `Core/Config/AppConfig.swift`
**Строка 22:**

```swift
#if DEBUG
// ✅ ИСПРАВЛЕНИЕ: Используем правильный порт и IP адрес Mac
let localhostURL = "http://192.168.0.101:8080/api"  // Исправлено: порт 8080 и IP Mac
return localhostURL
#else
return "https://api.aladdin.family/api"
#endif
```

**Почему IP адрес Mac?**
- Для iOS симулятора `localhost` не работает (localhost = сам симулятор)
- Нужно использовать IP адрес Mac (`192.168.0.101`)

---

### Вариант 2: Изменить порт backend на 8000

**Если у вас есть доступ к backend коду:**

Изменить порт запуска с 8080 на 8000:

```python
# Для FastAPI/Uvicorn:
uvicorn main:app --host 0.0.0.0 --port 8000

# Для Flask:
app.run(host='0.0.0.0', port=8000)
```

**Важно:** Backend должен слушать на `0.0.0.0` (не `127.0.0.1`), чтобы принимать запросы из сети!

---

## 🧪 ПРОВЕРКА

После исправления можете протестировать:

```bash
# Прямо с Mac:
curl -X POST "http://localhost:8080/api/payments/qr/create" \
  -H "Content-Type: application/json" \
  -d '{"amount": 590.0, "currency": "RUB", "description": "СЕМЕЙНЫЙ", "tariffId": "family"}'

# С IP адреса Mac (для симулятора):
curl -X POST "http://192.168.0.101:8080/api/payments/qr/create" \
  -H "Content-Type: application/json" \
  -d '{"amount": 590.0, "currency": "RUB", "description": "СЕМЕЙНЫЙ", "tariffId": "family"}'
```

---

## ✅ ЧТО СДЕЛАТЬ ПРЯМО СЕЙЧАС

1. **Откройте:** `Core/Config/AppConfig.swift`
2. **Найдите строку 22:** `let localhostURL = "http://localhost:8000/api"`
3. **Замените на:** `let localhostURL = "http://192.168.0.101:8080/api"`
4. **Перезапустите приложение в симуляторе**

После этого iOS приложение сможет подключиться к backend и получить QR код!

---

## 📊 РЕЗЮМЕ

**Проблема:**
- Backend запущен на порту **8080**
- iOS пытается подключиться к порту **8000**
- iOS использует `localhost` который не работает в симуляторе

**Решение:**
- Изменить URL в `AppConfig.swift` на `http://192.168.0.101:8080/api`
- Использовать IP адрес Mac для симулятора

**После исправления:**
- iOS сможет подключиться к backend
- QR код должен появиться автоматически
- Проблема должна быть решена!

