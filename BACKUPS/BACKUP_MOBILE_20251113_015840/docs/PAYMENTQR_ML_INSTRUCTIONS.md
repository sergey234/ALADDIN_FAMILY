# 🤖 Инструкция для ML-систем: Работа с PaymentQR

**Дата создания:** 2025-11-11  
**Целевая аудитория:** AI/ML системы, работающие с кодом проекта

---

## ⚠️ КРИТИЧЕСКИЕ ПРАВИЛА

### 1. НЕ РЕДАКТИРОВАТЬ ЗАЩИТНУЮ ЛОГИКУ

**Запрещено изменять:**
- ❌ Флаг `creationError` и его использование
- ❌ Метод `retryCreatePayment()` и его логику
- ❌ Метод `clearPaymentData()` и список очищаемых полей
- ❌ Guard-проверки в `checkPaymentStatus()`
- ❌ Guard-проверки в `startAutoCheck()`

**Почему:** Эти механизмы защищают от регрессий и критических ошибок.

---

### 2. РАБОТАТЬ ТОЛЬКО С ОСНОВНЫМ ПРОЕКТОМ

**Правильный путь:**
```
ALADDIN_NEW/mobile_apps/ALADDIN_iOS/ViewModels/PaymentQRViewModel.swift
```

**Неправильный путь:**
```
❌ ARCHIVE_ONLY_DO_NOT_EDIT_2025-11-11/.../PaymentQRViewModel.swift
❌ ALADDIN_NEW/mobile_apps/ALADDIN_iOS/ALADDIN_NEW/.../PaymentQRViewModel.swift
```

**Проверка:** Убедитесь, что редактируете файл из корня проекта, а не из архивных папок.

---

## 📋 Структура защитной логики

### Обязательные компоненты:

1. **`creationError: Bool`** — флаг ошибки создания
2. **`retryCreatePayment()`** — метод повторной попытки
3. **`clearPaymentData()`** — метод очистки данных
4. **Guard в `checkPaymentStatus()`** — проверка manual close, paymentId
5. **Guard в `startAutoCheck()`** — проверка creationError, manual close, paymentId

---

## ✅ Чеклист перед изменениями

Перед любыми изменениями в `PaymentQRViewModel`:

- [ ] Проверено, что редактируется файл из основного проекта (не из ARCHIVE_ONLY_*)
- [ ] Проверено наличие всех защитных механизмов
- [ ] Запущены unit-тесты `PaymentQRViewModelProtectionTests`
- [ ] Все тесты проходят успешно
- [ ] Проверена сборка проекта (`xcodebuild build`)

---

## 🧪 Проверка защитной логики

### Запуск unit-тестов:

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
xcodebuild test -project ALADDIN.xcodeproj -scheme ALADDIN \
  -destination 'platform=iOS Simulator,name=iPhone 13' \
  -only-testing:ALADDINUnitTests/PaymentQRViewModelProtectionTests
```

### Ожидаемый результат:
```
✅ Все тесты проходят (15+ тест-кейсов)
```

---

## 📝 Примеры правильного использования

### ✅ Правильно: Использование retryCreatePayment()

```swift
// После ошибки создания платежа
if viewModel.creationError {
    // Показываем кнопку "Повторить"
    Button("Повторить") {
        viewModel.retryCreatePayment()
    }
}
```

### ✅ Правильно: Проверка перед запуском авто-проверки

```swift
// Авто-проверка запустится только если:
// - creationError == false
// - isManualCloseInProgress == false
// - paymentId != nil && !paymentId.isEmpty
viewModel.startAutoCheck()
```

### ❌ Неправильно: Прямое изменение creationError

```swift
// ❌ НЕ ДЕЛАТЬ ТАК:
viewModel.creationError = false  // Используйте retryCreatePayment()!
```

---

## 🔍 Диагностика проблем

### Проблема: Авто-проверка не запускается

**Проверьте:**
1. `creationError == false?`
2. `isManualCloseInProgress == false?`
3. `paymentId != nil && !paymentId.isEmpty?`

**Решение:** Используйте логи в консоли Xcode (эмодзи 🔍, 🚨, ✅, ❌)

---

### Проблема: Ошибка не сбрасывается

**Проверьте:**
1. Вызван ли `retryCreatePayment()`?
2. Не установлен ли `creationError` вручную?

**Решение:** Используйте `retryCreatePayment()` вместо прямого изменения флагов.

---

## 📚 Дополнительная информация

- `docs/PAYMENTQR_PROTECTION_DOCUMENTATION.md` — полная документация
- `docs/PROJECT_STRUCTURE_WARNING.md` — предупреждение о структуре проекта
- `docs/YESTERDAY_WORK_SUMMARY_2025-11-11.md` — история изменений

---

**Дата создания:** 2025-11-11  
**Статус:** Актуально  
**Версия:** 1.0

