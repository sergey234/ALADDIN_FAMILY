# 🔧 ИСПРАВЛЕНИЕ: ДВОЙНОЙ /api/ В URL

## 🐛 ПРОБЛЕМА

### Обнаружено:

В `NetworkManager.swift` используется конкатенация:
```swift
let url = URL(string: baseURL + endpoint)
```

Где:
- `baseURL` = `"http://192.168.0.101:8080/api"` (уже содержит `/api`)
- `endpoint` = `"/api/payments/qr/create"` (также содержит `/api/`)

**Результат:** Двойной `/api/` в итоговом URL:
```
❌ http://192.168.0.101:8080/api/api/payments/qr/create
```

---

## ✅ ИСПРАВЛЕНИЕ

### Что было изменено:

**Файл:** `Core/Network/APIService.swift`

**Было:**
```swift
func createQRPayment(...) {
    networkManager.post(endpoint: "/api/payments/qr/create", ...)
}

func checkQRPaymentStatus(...) {
    networkManager.get(endpoint: "/api/payments/qr/status/\(paymentId)", ...)
}
```

**Стало:**
```swift
func createQRPayment(...) {
    // ✅ baseURL уже содержит /api, убираем из endpoint
    networkManager.post(endpoint: "/payments/qr/create", ...)
}

func checkQRPaymentStatus(...) {
    // ✅ baseURL уже содержит /api, убираем из endpoint
    networkManager.get(endpoint: "/payments/qr/status/\(paymentId)", ...)
}
```

**Результат:**
- ✅ Правильный URL: `http://192.168.0.101:8080/api/payments/qr/create`
- ✅ Нет двойного `/api/`

---

## 📊 ИТОГОВЫЕ ИЗМЕНЕНИЯ

### 1. URL в `AppConfig.swift`:
```swift
let localhostURL = "http://192.168.0.101:8080/api"
```
✅ Правильный порт (8080)  
✅ IP адрес Mac вместо localhost

### 2. Endpoint в `APIService.swift`:
```swift
endpoint: "/payments/qr/create"  // Без /api/ в начале
```
✅ Нет двойного `/api/`

### Итоговый URL:
```
✅ http://192.168.0.101:8080/api/payments/qr/create
```

---

## 🧪 ПРОВЕРКА

После исправления iOS приложение будет отправлять запросы на:
- ✅ `POST http://192.168.0.101:8080/api/payments/qr/create`
- ✅ `GET http://192.168.0.101:8080/api/payments/qr/status/{paymentId}`

**Следующие шаги:**
1. Перезапустить приложение
2. Проверить логи в Xcode Console
3. Увидеть точный URL который отправляется
4. Проверить ответ от backend

---

## ⚠️ ВАЖНО

Если backend все еще возвращает `501 Unsupported method`, это может означать:
1. Endpoint `/api/payments/qr/create` не реализован на backend
2. Требуется другой метод (GET вместо POST)
3. Требуется другой формат запроса

Но теперь мы уверены что URL правильный! ✅

