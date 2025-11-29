# 🔧 Инструкция: Исправление ошибки "no such module 'XCTest'"

**Проблема:** Файл `PaymentQRViewModelProtectionTests.swift` добавлен в Xcode, но компилируется как часть основного таргета `ALADDIN`, а не тестового таргета `ALADDINUnitTests`.

**Ошибка:**
```
error: no such module 'XCTest'
```

---

## ✅ Решение

### Шаг 1: Проверить Target Membership

1. Откройте Xcode: `open ALADDIN.xcodeproj`
2. Найдите файл `PaymentQRViewModelProtectionTests.swift` в навигаторе
3. Выберите файл
4. Откройте **File Inspector** (правая панель, ⌘⌥1)
5. Найдите секцию **"Target Membership"**

### Шаг 2: Настроить Target Membership

**Должно быть:**
- ✅ `ALADDINUnitTests` — **ВКЛЮЧЕНО** (галочка стоит)
- ❌ `ALADDIN` — **ВЫКЛЮЧЕНО** (галочка НЕ стоит)

**Если не так:**
1. Снимите галочку с `ALADDIN`
2. Поставьте галочку на `ALADDINUnitTests`

### Шаг 3: Проверить результат

После исправления:
- ✅ Файл будет компилироваться только в тестовом таргете
- ✅ `XCTest` будет доступен
- ✅ Тесты будут запускаться

---

## 📊 Сколько у нас тестов?

**Всего unit-тестов:** 11 файлов

1. `ALADDINUnitTests.swift`
2. `APIServiceTests.swift`
3. `AppConfigTests.swift`
4. `AppDelegateTests.swift`
5. `FamilyRegistrationViewModelTests.swift`
6. `IoTSecurityModuleTests.swift`
7. `LocalizationManagerTests.swift`
8. `NetworkManagerTests.swift`
9. `NotificationManagerTests.swift`
10. `SharedDataManagerTests.swift`
11. **`PaymentQRViewModelProtectionTests.swift`** ← **НОВЫЙ!**

**PaymentQRViewModelProtectionTests** — это **один файл с 16+ тест-кейсами**, который проверяет защитную логику PaymentQR.

---

## 🔍 Что такое "Описание API для ChildRewardsService"?

### Простыми словами:

**API (Application Programming Interface)** — это способ, как приложение общается с сервером.

**ChildRewardsService** — это сервис, который должен получать данные о наградах для детей с сервера.

### Что нужно получить:

**Описание API** — это документ, который объясняет:
- Какие запросы можно отправлять на сервер
- Какие ответы приходят обратно
- Какие данные нужны для запросов

### Пример того, что нужно:

```
GET /api/rewards/balance
Ответ: { "balance": 245, "weeklyEarned": 128 }

GET /api/rewards/history
Ответ: [ { "id": "1", "title": "Домашнее задание", "amount": 10 } ]

POST /api/rewards/give
Запрос: { "childId": "123", "reason": "homework", "amount": 10 }
```

### Где получить:

- От backend разработчиков
- Из документации API (Swagger, Postman)
- Из существующих эндпоинтов

**Статус:** ⏳ Ожидает получения от backend команды

---

## 🔐 Что такое "Файлы SSL-сертификатов"?

### Простыми словами:

**SSL-сертификат** — это "паспорт" сервера, который подтверждает, что сервер настоящий и безопасный.

**SSL Pinning** — это защита, которая проверяет, что приложение общается именно с нашим сервером, а не с поддельным.

### Что нужно получить:

**Файлы сертификатов:**
- `aladdin_cert.cer` — основной сертификат
- `aladdin_cert_backup.cer` — резервный сертификат

### Где получить:

- От backend разработчиков
- От DevOps инженера
- Из папки сервера (если есть доступ)

### Где должны быть:

**Папка:** `ALADDIN/Certificates/`

**Текущий статус:**
- ⚠️ Папка существует: `ALADDIN/Certificates/`
- ⚠️ Файлы сертификатов отсутствуют
- ⚠️ В логах: "Сертификат aladdin_cert не найден"

**Статус:** ⏳ Ожидает получения файлов от DevOps/backend

---

## ✅ Что можно сделать сейчас

### 1. Исправить ошибку теста:

- Настроить Target Membership в Xcode (см. выше)
- После исправления тесты будут работать

### 2. Продолжить разработку:

**ChildRewardsService:**
- Можно продолжать с моковыми данными
- Подключить реальный API после получения описания

**SSL-сертификаты:**
- Можно продолжать разработку без SSL Pinning
- Добавить сертификаты перед релизом

---

**Дата создания:** 2025-11-11  
**Статус:** Актуально

