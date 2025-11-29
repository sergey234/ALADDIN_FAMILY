# ⚠️ ОШИБКИ КОМПИЛЯЦИИ ПРИ ТЕСТИРОВАНИИ

**Дата:** 15 ноября 2025  
**Статус:** ⚠️ **ТРЕБУЕТСЯ ИСПРАВЛЕНИЕ**

---

## ❌ ОШИБКИ КОМПИЛЯЦИИ

### 1. `cannot find 'MockAPIService' in scope`
**Файл:** `Core/Network/APIService.swift:34`  
**Причина:** Файл `MockAPIService.swift` не добавлен в Target или не компилируется

**Решение:**
1. Проверить, что файл `Core/Network/MockAPIService.swift` добавлен в Target `ALADDIN`
2. В Xcode: File Inspector → Target Membership → ✅ ALADDIN

---

### 2. `cannot find 'StorageManager' in scope`
**Файл:** `Screens/11_ProfileScreen.swift:648`  
**Причина:** Файл `StorageManager.swift` не добавлен в Target или не импортирован

**Решение:**
1. Проверить, что файл `Core/Storage/StorageManager.swift` добавлен в Target `ALADDIN`
2. В Xcode: File Inspector → Target Membership → ✅ ALADDIN

---

## ✅ ИСПРАВЛЕНИЯ ВНЕСЕНЫ

1. ✅ Добавлены недостающие свойства в `AppConfig`:
   - `Network` struct
   - `useAlternativePayments`
   - `UserDefaultsKeys.appLanguage`
   - `UserDefaultsKeys.hasCompletedOnboarding`
   - `UserDefaultsKeys.familyId`
   - `supportPhone`
   - `supportTelegramURL`

2. ✅ Исправлена ошибка с `parseSubscriptionEndDate`:
   - Добавлен явный `self?` в замыкании

---

## 🔄 ЧТО НУЖНО СДЕЛАТЬ

### В Xcode:

1. **Проверить Target Membership для файлов:**
   - `Core/Network/MockAPIService.swift` → ✅ ALADDIN
   - `Core/Storage/StorageManager.swift` → ✅ ALADDIN

2. **Очистить проект:**
   - Product → Clean Build Folder (Shift + Cmd + K)

3. **Пересобрать проект:**
   - Product → Build (Cmd + B)

4. **Запустить тесты:**
   - Product → Test (Cmd + U)

---

**Дата создания:** 15 ноября 2025  
**Статус:** ⚠️ **ТРЕБУЕТСЯ ПРОВЕРКА В XCODE**




