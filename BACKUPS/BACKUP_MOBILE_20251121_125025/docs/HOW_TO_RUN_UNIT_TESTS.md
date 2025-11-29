# 🧪 Как запустить unit-тесты

**Дата создания:** 2025-11-11  
**Для:** PaymentQRViewModelProtectionTests

---

## 🎯 Что такое unit-тесты?

**Unit-тесты** — это автоматические проверки кода, которые:
- ✅ Проверяют, что код работает правильно
- ✅ Находят ошибки до того, как пользователь их увидит
- ✅ Защищают от регрессий (когда новые изменения ломают старый код)

**Пример:** Мы создали тесты для защитной логики PaymentQR, которые проверяют:
- Флаг `creationError` работает правильно
- Метод `retryCreatePayment()` сбрасывает ошибки
- Guard-проверки блокируют некорректные операции

---

## 🚀 Способ 1: Через Xcode (РЕКОМЕНДУЕТСЯ)

### Шаг 1: Откройте проект в Xcode

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
open ALADDIN.xcodeproj
```

### Шаг 2: Выберите схему и симулятор

1. Вверху Xcode выберите схему: **ALADDIN**
2. Выберите симулятор: **iPhone 13** (или любой другой)

### Шаг 3: Запустите тесты

**Вариант А: Все тесты**
- Нажмите `Cmd + U` (⌘U)
- Или: Product → Test

**Вариант Б: Только PaymentQR тесты**
1. Откройте навигатор тестов (⌘6)
2. Найдите `PaymentQRViewModelProtectionTests`
3. Нажмите ▶️ рядом с названием

### Шаг 4: Проверьте результаты

- ✅ **Зелёные галочки** = тесты прошли успешно
- ❌ **Красные крестики** = есть ошибки (покажет детали)

---

## 💻 Способ 2: Через терминал

### Запустить все unit-тесты:

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

xcodebuild test \
  -project ALADDIN.xcodeproj \
  -scheme ALADDIN \
  -destination 'platform=iOS Simulator,name=iPhone 13'
```

### Запустить только PaymentQR тесты:

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

xcodebuild test \
  -project ALADDIN.xcodeproj \
  -scheme ALADDIN \
  -destination 'platform=iOS Simulator,name=iPhone 13' \
  -only-testing:ALADDINUnitTests/PaymentQRViewModelProtectionTests
```

### Что вы увидите:

```
Test Suite 'PaymentQRViewModelProtectionTests' started.
  testCreationErrorFlagExists ... passed (0.123 seconds)
  testRetryCreatePaymentResetsCreationError ... passed (0.145 seconds)
  testClearPaymentDataClearsAllPaymentFields ... passed (0.098 seconds)
  ...
Test Suite 'PaymentQRViewModelProtectionTests' passed.
  Executed 16 tests, with 0 failures (0 unexpected) in 2.456 seconds.
```

---

## 📊 Что проверяют наши тесты?

### 1. Флаг `creationError` (3 теста)
- ✅ Существует и доступен
- ✅ Блокирует авто-проверку при ошибке
- ✅ Правильно устанавливается

### 2. Метод `retryCreatePayment()` (3 теста)
- ✅ Сбрасывает `creationError`
- ✅ Очищает данные платежа
- ✅ Останавливает авто-проверку

### 3. Метод `clearPaymentData()` (1 тест)
- ✅ Очищает все поля платежа

### 4. Guard-проверки в `checkPaymentStatus()` (3 теста)
- ✅ Блокирует при manual close
- ✅ Требует `paymentId`
- ✅ Требует непустой `paymentId`

### 5. Guard-проверки в `startAutoCheck()` (4 теста)
- ✅ Блокирует при `creationError`
- ✅ Блокирует при manual close
- ✅ Требует `paymentId`
- ✅ Останавливает предыдущую проверку

### 6. Интеграционные тесты (2 теста)
- ✅ Полный цикл восстановления после ошибки
- ✅ Полный сброс состояния

**Всего:** 16+ тест-кейсов

---

## ⚠️ Возможные проблемы

### Проблема 1: Симулятор не запускается

**Решение:**
```bash
# Запустить симулятор вручную
xcrun simctl boot "iPhone 13"
open -a Simulator
```

### Проблема 2: Тесты не компилируются

**Решение:**
1. Проверьте, что проект собирается: `xcodebuild build`
2. Проверьте ошибки компиляции в Xcode
3. Убедитесь, что файл `PaymentQRViewModelProtectionTests.swift` добавлен в Target

### Проблема 3: Тесты падают

**Решение:**
1. Откройте детали ошибки в Xcode
2. Проверьте, что `PaymentQRViewModel` доступен для тестирования (`@testable import ALADDIN`)
3. Убедитесь, что все зависимости настроены

---

## ✅ Ожидаемый результат

После успешного запуска вы должны увидеть:

```
✅ Все тесты прошли (16+ тест-кейсов)
✅ Время выполнения: ~2-3 секунды
✅ 0 ошибок
```

---

## 📝 Что делать после запуска?

1. **Если все тесты прошли:**
   - ✅ Защитная логика PaymentQR работает правильно
   - ✅ Можно продолжать разработку
   - ✅ Зафиксировать результат в отчёте

2. **Если есть ошибки:**
   - ❌ Нужно исправить код или тесты
   - ❌ Проверить детали ошибки
   - ❌ Обновить тесты при необходимости

---

## 🔗 Связанные документы

- `Tests/UnitTests/PaymentQRViewModelProtectionTests.swift` — исходный код тестов
- `docs/PAYMENTQR_PROTECTION_DOCUMENTATION.md` — документация защитной логики
- `ViewModels/PaymentQRViewModel.swift` — тестируемый код

---

**Дата создания:** 2025-11-11  
**Статус:** Актуально

