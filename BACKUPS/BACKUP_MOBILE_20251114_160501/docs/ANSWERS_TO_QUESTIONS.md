# 📋 Ответы на вопросы

**Дата:** 2025-11-11

---

## 1️⃣ Что такое "Описание API для ChildRewardsService"?

### Простыми словами:

**API** — это способ, как приложение общается с сервером.

**ChildRewardsService** — это сервис, который должен получать данные о наградах для детей с сервера.

### Что нужно получить:

**Описание API** — это документ, который объясняет:
- Какие запросы можно отправлять на сервер
- Какие ответы приходят обратно
- Какие данные нужны для запросов

### Пример:

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

**Статус:** ⏳ Ожидает получения от backend команды

---

## 2️⃣ Что такое "Файлы SSL-сертификатов"?

### Простыми словами:

**SSL-сертификат** — это "паспорт" сервера, который подтверждает, что сервер настоящий и безопасный.

**SSL Pinning** — это защита, которая проверяет, что приложение общается именно с нашим сервером, а не с поддельным.

### Что нужно получить:

**Файлы сертификатов:**
- `aladdin_cert.cer` — основной сертификат
- `aladdin_cert_backup.cer` — резервный сертификат

### Где должны быть:

**Папка:** `ALADDIN/Certificates/`

**Текущий статус:**
- ⚠️ Папка существует
- ⚠️ Файлы сертификатов отсутствуют
- ⚠️ В логах: "Сертификат aladdin_cert не найден"

### Где получить:

- От backend разработчиков
- От DevOps инженера

**Статус:** ⏳ Ожидает получения файлов от DevOps/backend

---

## 3️⃣ У нас один такой тест? (PaymentQRViewModelProtectionTests)

### Нет, это не один тест!

**PaymentQRViewModelProtectionTests** — это **один файл с 16+ тест-кейсами**.

### Структура:

```
PaymentQRViewModelProtectionTests.swift (1 файл)
├── testCreationErrorFlagExists() (1 тест)
├── testCreationErrorPreventsAutoCheck() (1 тест)
├── testRetryCreatePaymentResetsCreationError() (1 тест)
├── testRetryCreatePaymentClearsPaymentData() (1 тест)
├── testRetryCreatePaymentStopsAutoCheck() (1 тест)
├── testClearPaymentDataClearsAllPaymentFields() (1 тест)
├── testCheckPaymentStatusGuardsAgainstManualClose() (1 тест)
├── testCheckPaymentStatusGuardsAgainstCreationError() (1 тест)
├── testCheckPaymentStatusRequiresPaymentId() (1 тест)
├── testCheckPaymentStatusRequiresNonEmptyPaymentId() (1 тест)
├── testStartAutoCheckGuardsAgainstCreationError() (1 тест)
├── testStartAutoCheckGuardsAgainstManualClose() (1 тест)
├── testStartAutoCheckRequiresPaymentId() (1 тест)
├── testStartAutoCheckRequiresNonEmptyPaymentId() (1 тест)
├── testStartAutoCheckStopsPreviousAutoCheck() (1 тест)
├── testFullErrorRecoveryFlow() (1 тест)
└── testResetStateClearsEverything() (1 тест)

Всего: 16+ тест-кейсов в одном файле
```

### Всего unit-тестов в проекте:

**11 файлов тестов:**
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

---

## 4️⃣ Ошибка "no such module 'XCTest'"

### Проблема:

Файл `PaymentQRViewModelProtectionTests.swift` добавлен в Xcode, но компилируется как часть основного таргета `ALADDIN`, а не тестового таргета `ALADDINUnitTests`.

### Решение:

1. Откройте Xcode: `open ALADDIN.xcodeproj`
2. Найдите файл `PaymentQRViewModelProtectionTests.swift`
3. Выберите файл
4. Откройте **File Inspector** (правая панель, ⌘⌥1)
5. Найдите секцию **"Target Membership"**
6. **Снимите галочку** с `ALADDIN`
7. **Поставьте галочку** на `ALADDINUnitTests`

### После исправления:

- ✅ Файл будет компилироваться только в тестовом таргете
- ✅ `XCTest` будет доступен
- ✅ Тесты будут запускаться

---

**Дата создания:** 2025-11-11  
**Статус:** Актуально

