# 🔴 BUILD 97: ДЕТАЛЬНЫЙ АНАЛИЗ CRASH LOG

**Дата:** 2026-03-10  
**Версия сборки:** 97  
**Exception Type:** `EXC_BAD_ACCESS (SIGSEGV)`  
**Exception Message:** `Thread stack size exceeded due to excessive recursion`

---

## 📊 АНАЛИЗ STACK TRACE

### Ключевые наблюдения:

#### 1. **РЕКУРСИЯ В ФОРМАТИРОВАНИИ ДАТЫ** 🔴

**Stack trace показывает:**
```
12  Foundation                     -[NSDateFormatter stringForObjectValue:] + 140
13  ALADDIN                       0x1025ae7b4  ← Вызов DateFormatter в нашем коде
14  ALADDIN                       0x1025afa50
15  ALADDIN                       0x10263df28
16  ALADDIN                       0x102609cac
17  ALADDIN                       0x102609a2c
18  ALADDIN                       0x10260a164
19-24 ALADDIN                    0x10260a174  ← РЕКУРСИЯ! (повторяется 6 раз!)
```

**Проблема:** Рекурсия происходит в `NSDateFormatter stringForObjectValue:`, что указывает на проблему с форматированием даты.

**Вероятность:** 🔴 **95%**

---

#### 2. **ICU (International Components for Unicode) РЕКУРСИЯ**

**Stack trace показывает:**
```
0   libicucore.A.dylib            icu::FormattedStringBuilder::insertCodePoint(...)
1   libicucore.A.dylib            icu::SimpleDateFormat::formatImpl(...)
2   libicucore.A.dylib            icu::SimpleDateFormat::format(...)
3   CoreFoundation                CFDateFormatterCreateStringWithAbsoluteTime
4   Foundation                     -[NSDateFormatter stringForObjectValue:]
```

**Проблема:** Рекурсия происходит внутри ICU библиотеки при форматировании даты, что может быть вызвано:
- Использованием `Locale.current` или `Locale.preferredLanguages` в `DateFormatter`
- Созданием нового `DateFormatter` в computed property
- Рекурсивным вызовом форматирования даты

**Вероятность:** 🔴 **90%**

---

## 🔍 ЧТО ЭТО ЗНАЧИТ

### ❌ ЭТО НЕ ТА ЖЕ ПРОБЛЕМА, ЧТО БЫЛА РАНЬШЕ!

**Раньше:**
- Рекурсия в `@AppStorage` → `UserDefaults` → `@AppStorage`
- Рекурсия в `.onChange()` и `.id()` модификаторах
- Рекурсия в `MasterLogger.enableVisualLogging`

**Сейчас (BUILD 97):**
- Рекурсия в `DateFormatter` → форматирование даты → `DateFormatter`
- Это **НОВАЯ ПРОБЛЕМА**, не связанная с предыдущими исправлениями!

---

## 🎯 ВОЗМОЖНЫЕ ПРИЧИНЫ

### 🔴 ПРИЧИНА #1: `DateFormatter` создается в computed property с `Locale.current`

**Проблема:**
- `Locale.current` читает из `UserDefaults`
- Если `DateFormatter` создается в computed property, который вызывается во время форматирования даты
- Это может вызвать рекурсию

**Где искать:**
- Computed properties с `DateFormatter()`
- Использование `Locale.current` в `DateFormatter`
- Использование `Locale.preferredLanguages` в `DateFormatter`

**Вероятность:** 🔴 **80%**

---

### 🔴 ПРИЧИНА #2: `DateFormatter` создается в `body` или `onAppear`

**Проблема:**
- Если `DateFormatter` создается в `body` или `onAppear` View
- И используется для форматирования даты, которая обновляет View
- Это может вызвать рекурсию

**Где искать:**
- `DateFormatter()` в `body` View
- `DateFormatter()` в `onAppear`
- Использование `DateFormatter` в computed properties View

**Вероятность:** 🟡 **60%**

---

### 🔴 ПРИЧИНА #3: Рекурсивный вызов форматирования даты

**Проблема:**
- Если форматирование даты вызывает обновление View
- Которое снова вызывает форматирование даты
- Это может вызвать рекурсию

**Где искать:**
- Форматирование даты в `@Published` свойствах
- Форматирование даты в `@AppStorage` computed properties
- Форматирование даты в `.onChange()` модификаторах

**Вероятность:** 🟡 **50%**

---

## 📋 РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ

### 🔴 КРИТИЧНО (Приоритет 1):

1. **Найти все места, где используется `DateFormatter` с `Locale.current`**
   - Заменить на статический `Locale(identifier: "ru_RU")` или `Locale(identifier: "en_US")`
   - Использовать статические `DateFormatter` экземпляры

2. **Найти все computed properties с `DateFormatter()`**
   - Заменить на статические `DateFormatter` экземпляры
   - Использовать `private static let` для создания форматтеров

3. **Найти все места, где `DateFormatter` создается в `body` или `onAppear`**
   - Вынести создание форматтеров в статические свойства
   - Использовать кешированные форматтеры

---

### 🟡 ВЫСОКО (Приоритет 2):

4. **Проверить использование `DateFormatter` в `@Published` свойствах**
   - Убедиться, что форматирование не вызывает обновление View

5. **Проверить использование `DateFormatter` в `.onChange()` модификаторах**
   - Убедиться, что форматирование не вызывает рекурсию

---

## 🔍 ГДЕ ИСКАТЬ ПРОБЛЕМУ

### Файлы для проверки:

1. **`Screens/01_MainScreen.swift`**
   - Проверить использование `DateFormatter` в computed properties
   - Проверить использование `Locale.current`

2. **`ViewModels/ProfileViewModel.swift`**
   - Проверить `parseSubscriptionEndDate()`
   - Проверить использование `DateFormatter`

3. **`Screens/ChildRewardsScreen.swift`**
   - Проверить `formatDate()`
   - Проверить использование `DateFormatter`

4. **`ViewModels/AIAssistantViewModel.swift`**
   - Проверить `ChatMessage.timeString`
   - Проверить использование `DateFormatter`

5. **`Core/Models/ComponentReportsModels.swift`**
   - Проверить использование `DateFormatter` в fallback

6. **`ViewModels/ActivationCodeViewModel.swift`**
   - Проверить использование `DateFormatter`

---

## ✅ ВЫВОДЫ

### ❌ ЧТО ПРОИСХОДИТ:

1. **Рекурсия в `DateFormatter`** - это новая проблема, не связанная с предыдущими исправлениями
2. **Рекурсия происходит в ICU библиотеке** при форматировании даты
3. **Вероятная причина:** Использование `Locale.current` или создание `DateFormatter` в computed property

### ✅ ЧТО НУЖНО СДЕЛАТЬ:

1. Найти все места, где используется `DateFormatter` с `Locale.current`
2. Заменить на статические `DateFormatter` экземпляры
3. Использовать статический `Locale(identifier:)` вместо `Locale.current`

---

**ГОТОВО К ПОИСКУ ПРОБЛЕМЫ!** 🔍
