# 📱 Инструкция по просмотру логов без Xcode Devices

## ⚠️ Проблема
Xcode Devices не работает из-за несовместимости версий iOS и Xcode.

## ✅ Решение 1: Console.app (Mac)

### Шаг 1: Открыть Console.app
1. На Mac откройте **Console.app** (Приложения → Утилиты → Console)
2. Или через Spotlight: `Cmd+Space` → введите "Console"

### Шаг 2: Подключить iPhone
1. Подключите iPhone к Mac через USB
2. В Console.app выберите ваше устройство в списке слева (под "Devices")

### Шаг 3: Фильтровать логи
1. В строке поиска введите: `ALADDIN` или `family.aladdin.ios`
2. Или используйте фильтр: `process == "ALADDIN"`
3. Включите "Include Info Messages" и "Include Debug Messages"

### Шаг 4: Тестирование
1. На iPhone откройте приложение ALADDIN
2. Перейдите на экран тарифов
3. Попробуйте купить тариф
4. Смотрите логи в реальном времени в Console.app

---

## ✅ Решение 2: Визуальная диагностика в приложении

Добавлен временный debug-экран, который показывает статус загрузки продуктов прямо в приложении.

### Как использовать:
1. Откройте приложение ALADDIN
2. Перейдите на экран тарифов
3. **Долго нажмите** на заголовок "Тарифы" (3 секунды)
4. Появится debug-панель с информацией:
   - Количество загруженных продуктов
   - Статус загрузки
   - Ошибки (если есть)
   - Product IDs

---

## ✅ Решение 3: Обновить Xcode

### Проверьте версию Xcode:
```bash
xcodebuild -version
```

### Проверьте версию iOS на iPhone:
Настройки → Основные → Об этом устройстве → Версия

### Обновите Xcode:
1. Mac App Store → Обновления
2. Или скачайте с developer.apple.com

---

## ✅ Решение 4: Использовать симулятор

Если у вас есть симулятор с нужной версией iOS:

1. Xcode → Window → Devices and Simulators
2. Выберите симулятор
3. Запустите приложение в симуляторе
4. Логи будут видны в Xcode Console (`Cmd+Shift+Y`)

**⚠️ ВАЖНО:** IAP не работает в симуляторе! Но логи загрузки продуктов будут видны.

---

## 📋 Что искать в логах

### ✅ Успешная загрузка:
```
🔄 [StoreManager.loadProducts] ========== НАЧАЛО ЗАГРУЗКИ ПРОДУКТОВ ==========
✅ [StoreManager.loadProducts] ========== ПРОДУКТЫ ЗАГРУЖЕНЫ УСПЕШНО ==========
✅ [StoreManager.loadProducts] Загружено 3 продуктов из App Store
```

### ❌ Ошибка загрузки:
```
❌ [StoreManager.loadProducts] ========== ОШИБКА ЗАГРУЗКИ ==========
❌ [StoreManager.loadProducts] SKError code: 5
❌ [StoreManager.loadProducts] SKErrorStoreProductNotAvailable
```

---

## 🔍 Коды ошибок StoreKit

- **0** - SKErrorUnknown (Неизвестная ошибка)
- **1** - SKErrorClientInvalid (Клиент недействителен)
- **2** - SKErrorPaymentCancelled (Платеж отменен)
- **3** - SKErrorPaymentInvalid (Платеж недействителен)
- **4** - SKErrorPaymentNotAllowed (Платеж не разрешен)
- **5** - SKErrorStoreProductNotAvailable (Продукт недоступен) ⬅️ **Частая причина**
- **6** - SKErrorCloudServicePermissionDenied (Доступ запрещен)
- **7** - SKErrorCloudServiceNetworkConnectionFailed (Ошибка сети)
- **8** - SKErrorCloudServiceRevoked (Сервис отозван)

---

## 📧 Что делать дальше

1. Попробуйте один из методов выше
2. Скопируйте логи, которые начинаются с:
   - `🔄 [StoreManager.loadProducts]`
   - `✅ [StoreManager.loadProducts]`
   - `❌ [StoreManager.loadProducts]`
3. Пришлите эти логи для анализа

---

**Дата:** 29 декабря 2025

