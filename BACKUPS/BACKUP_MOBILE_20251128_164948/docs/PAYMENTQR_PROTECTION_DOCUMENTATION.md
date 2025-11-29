# 🛡️ Документация защитной логики PaymentQR

**Дата создания:** 2025-11-11  
**Статус:** Актуально

---

## 📋 Обзор

`PaymentQRViewModel` содержит **защитную логику**, которая предотвращает ошибки и обеспечивает стабильную работу экрана оплаты через QR-код.

---

## 🔒 Защитные механизмы

### 1. Флаг `creationError`

**Назначение:** Отслеживает ошибки создания платежа и блокирует дальнейшие операции до исправления.

**Использование:**
```swift
@Published var creationError: Bool = false
```

**Когда устанавливается:**
- При ошибке создания платежа (`createPayment()`)
- При ошибке проверки статуса (`checkPaymentStatus()`)

**Что блокирует:**
- Автоматическую проверку статуса (`startAutoCheck()`)
- Повторные попытки без явного retry

**Как сбросить:**
- Вызвать `retryCreatePayment()` — автоматически сбрасывает флаг
- Вызвать `resetState()` — полный сброс состояния

---

### 2. Метод `retryCreatePayment()`

**Назначение:** Повторная попытка создания платежа после ошибки.

**Что делает:**
1. Останавливает авто-проверку (`stopAutoCheck()`)
2. Сбрасывает `creationError = false`
3. Сбрасывает `isManualCloseInProgress = false`
4. Очищает данные платежа (`clearPaymentData()`)
5. Вызывает `createPayment()` заново

**Использование:**
```swift
viewModel.retryCreatePayment()
```

**Когда использовать:**
- После ошибки создания платежа
- Когда пользователь нажимает кнопку "Повторить"

---

### 3. Метод `clearPaymentData()`

**Назначение:** Очищает все данные платежа для нового цикла.

**Что очищает:**
- `paymentId`
- `qrCodeDataSBP`, `qrCodeDataSberPay`, `qrCodeDataUniversal`
- `qrCodeImageSBP`, `qrCodeImageSberPay`, `qrCodeImageUniversal`
- `qrCodeImageCard`, `qrCodeImageApplePay`
- `expiresAt`
- `merchantInfo`
- `errorMessage`
- `showErrorAlert`, `showSuccessAlert`

**Использование:**
```swift
viewModel.clearPaymentData()  // Приватный метод
// Или через:
viewModel.resetState()  // Публичный метод, который вызывает clearPaymentData()
```

---

### 4. Guard-проверки в `checkPaymentStatus()`

**Назначение:** Предотвращает проверку статуса в некорректных состояниях.

**Проверки:**

1. **Manual Close:**
```swift
if isManualCloseInProgress {
    print("ℹ️ checkPaymentStatus: пропущено (manual close)")
    return
}
```

2. **Payment ID отсутствует:**
```swift
guard let paymentId = paymentId else {
    errorMessage = localized("payment_qr_error_qr_pending")
    showErrorAlert = true
    return
}
```

3. **Payment ID пустой:**
```swift
guard !paymentId.isEmpty else {
    errorMessage = localized("payment_qr_error_payment_not_created")
    showErrorAlert = true
    return
}
```

**Результат:** Проверка статуса выполняется только при валидном состоянии.

---

### 5. Guard-проверки в `startAutoCheck()`

**Назначение:** Предотвращает запуск авто-проверки в некорректных состояниях.

**Проверки:**

1. **Creation Error:**
```swift
guard !creationError else {
    print("ℹ️ startAutoCheck: пропущено (creationError активен)")
    return
}
```

2. **Manual Close:**
```swift
guard !isManualCloseInProgress else {
    print("ℹ️ startAutoCheck: пропущено (manual close in progress)")
    return
}
```

3. **Payment ID отсутствует:**
```swift
guard let paymentId = paymentId, !paymentId.isEmpty else {
    print("ℹ️ startAutoCheck: пропущено (paymentId отсутствует)")
    return
}
```

**Результат:** Авто-проверка запускается только при валидном состоянии.

---

## 🧪 Unit-тесты

**Файл:** `Tests/UnitTests/PaymentQRViewModelProtectionTests.swift`

**Покрытие:**
- ✅ `creationError` флаг
- ✅ `retryCreatePayment()` метод
- ✅ `clearPaymentData()` метод
- ✅ Guard-проверки в `checkPaymentStatus()`
- ✅ Guard-проверки в `startAutoCheck()`
- ✅ Интеграционные тесты (полный цикл восстановления)

**Запуск тестов:**
```bash
xcodebuild test -project ALADDIN.xcodeproj -scheme ALADDIN \
  -destination 'platform=iOS Simulator,name=iPhone 13' \
  -only-testing:ALADDINUnitTests/PaymentQRViewModelProtectionTests
```

---

## ⚠️ Важные замечания

### 1. Вложенная копия проекта

**Проблема:** В репозитории существует вложенная копия проекта:
```
ALADDIN_NEW/mobile_apps/ALADDIN_iOS/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
```

**Статус:** ✅ Решено — переименована в `ARCHIVE_ONLY_DO_NOT_EDIT_2025-11-11`

**Рекомендация:** Работать только с основным деревом:
```
ALADDIN_NEW/mobile_apps/ALADDIN_iOS/
```

**Документация:**
- `docs/PROJECT_STRUCTURE_WARNING.md` — предупреждение о структуре
- `docs/NESTED_PROJECT_ANALYSIS.md` — детальный анализ

---

### 2. Диагностический overlay

**Статус:** Отложен из-за проблем с компиляцией.

**Альтернатива:** Диагностические логи через `print()` в консоль Xcode.

**Документация:**
- `docs/DIAGNOSTIC_OVERLAY_EXPLANATION.md` — объяснение проблемы

---

## 📚 Связанные документы

- `ViewModels/PaymentQRViewModel.swift` — исходный код
- `Tests/UnitTests/PaymentQRViewModelProtectionTests.swift` — unit-тесты
- `docs/YESTERDAY_WORK_SUMMARY_2025-11-11.md` — резюме работы
- `docs/PROJECT_STRUCTURE_WARNING.md` — предупреждение о структуре проекта

---

## 🔄 История изменений

**2025-11-11:**
- ✅ Восстановлена защитная логика из бэкапа
- ✅ Создан unit-тест `PaymentQRViewModelProtectionTests.swift`
- ✅ Обновлена документация
- ✅ Решена проблема с вложенной копией проекта

---

**Дата создания:** 2025-11-11  
**Последнее обновление:** 2025-11-11  
**Автор:** AI Assistant

