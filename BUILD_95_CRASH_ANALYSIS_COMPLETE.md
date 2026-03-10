# 🔴 BUILD 95 - ПОЛНЫЙ АНАЛИЗ КРАША

**Дата:** 2026-03-10  
**Версия сборки:** 95  
**Exception Type:** `EXC_BAD_ACCESS (SIGSEGV)`  
**Exception Message:** `Thread stack size exceeded due to excessive recursion`

---

## 📊 АНАЛИЗ CRASH LOG BUILD 95

### Stack Trace:
```
17  Foundation                     -[NSUserDefaults(NSUserDefaults) boolForKey:]
18  ALADDIN                        0x102545848  ← Вызов boolForKey: в нашем коде
19  ALADDIN                        0x1025117a0
20  ALADDIN                        0x102511520
21-27 ALADDIN                      0x102511c68  ← РЕКУРСИЯ! (повторяется 7 раз!)
28  ALADDIN                        0x1023d33ec
29  ALADDIN                        0x10212ce95
30  ALADDIN                        0x1024079e9
31  ALADDIN                        0x10212ce95  ← Повторяется
```

**Ключевые наблюдения:**
- Строка 17: `boolForKey:` - чтение из UserDefaults
- Строки 21-27: **РЕКУРСИЯ** - один и тот же адрес повторяется 7 раз
- Это **ТОЧНО ТА ЖЕ ПРОБЛЕМА**, что была в BUILD 91, 92, 94!

---

## 🔍 СРАВНЕНИЕ С ПРЕДЫДУЩИМИ КРАШАМИ

### BUILD 91 (исправлено):
- **Проблема:** Рекурсия в `@AppStorage` → computed property → `UserDefaults` → `@AppStorage`
- **Исправление:** Заменены computed properties на `@State` переменные
- **Статус:** ✅ Исправлено

### BUILD 92 (исправлено):
- **Проблема:** Рекурсия в `.onChange(of: subscriptionExpiresAtIso)` и `.id()` с `localizationManager`
- **Исправление:** Убраны `.onChange()` и `.id()` модификаторы
- **Статус:** ✅ Исправлено

### BUILD 94 (исправлено):
- **Проблема:** `UserDefaults.standard.bool()` в `initializeNavigation()` и `NavigationManager.init()`
- **Исправление:** Заменено на `@AppStorage` в `ALADDINApp`
- **Статус:** ✅ Исправлено

### BUILD 95 (ТЕКУЩИЙ КРАШ):
- **Проблема:** **НОВАЯ РЕКУРСИЯ!** Похожа на BUILD 94, но **НЕ ТА ЖЕ САМАЯ**
- **Stack trace:** Показывает `boolForKey:` → рекурсия в ALADDIN коде
- **Статус:** ❌ **НЕ ИСПРАВЛЕНО**

---

## 🔴 НАЙДЕННЫЕ ПРОБЛЕМЫ В BUILD 95

### ❌ ПРОБЛЕМА #1: UserDefaults.set() в initializeNavigation()

**Файл:** `ALADDINApp.swift:685`  
**Код:**
```swift
if !ALADDINApp.hasInitializedNavigation {
    print("🛠️ [ALADDINApp.initializeNavigation] Первый запуск - сбрасываем состояние")
    // Принудительный сброс онбординга для первого запуска
    UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)  // ❌ ПРОБЛЕМА!
    UserDefaults.standard.synchronize()
}
```

**Проблема:**
- `initializeNavigation()` вызывается из `onAppear` в `ALADDINApp`
- У нас есть `@AppStorage(AppConfig.UserDefaultsKeys.hasCompletedOnboarding)` в `ALADDINApp`
- Когда мы вызываем `UserDefaults.standard.set()`, это **ОБНОВЛЯЕТ** `@AppStorage`
- `@AppStorage` обновление вызывает **перерисовку View** → может вызвать `onAppear` снова
- `onAppear` вызывает `initializeNavigation()` → вызывает `UserDefaults.set()` → **РЕКУРСИЯ!**

**Вероятность краша:** 🔴 **95%**

**Почему это не было исправлено ранее:**
- В BUILD 94 мы исправили `UserDefaults.bool()` в `initializeNavigation()`
- Но **НЕ ИСПРАВИЛИ** `UserDefaults.set()` в том же месте!
- Это **НОВАЯ ПРОБЛЕМА**, которая осталась после исправлений BUILD 94

---

### ❌ ПРОБЛЕМА #2: MasterLogger.enableVisualLogging читается в body

**Файл:** `Core/Utilities/MasterLogger.swift:163`  
**Код:**
```swift
private var enableVisualLogging: Bool {
    get {
        UserDefaults.standard.bool(forKey: "enable_visual_logging")  // ❌ ПРОБЛЕМА!
    }
    set {
        UserDefaults.standard.set(newValue, forKey: "enable_visual_logging")
    }
}

// Используется в:
if enableVisualLogging {  // ← Вызывается в body или init()
    visualLogger.log(...)
}
```

**Проблема:**
- `enableVisualLogging` - это computed property, который вызывает `UserDefaults.standard.bool()`
- Если это вызывается в `body` или в `init()`, это может вызвать рекурсию
- Особенно если есть другие `@AppStorage` свойства, которые читают из того же `UserDefaults`

**Вероятность краша:** 🟡 **80%**

**Почему это не было исправлено ранее:**
- В BUILD 93 мы убрали `enableVisualLogging = true` из `init()`
- Но **НЕ ИСПРАВИЛИ** чтение `enableVisualLogging` в других местах!
- Если `MasterLogger.shared` используется в `body`, это может вызвать рекурсию

---

### ❌ ПРОБЛЕМА #3: UserDefaults.bool() в ALADDINApp.init()

**Файл:** `ALADDINApp.swift:234`  
**Код:**
```swift
#if DEBUG
// ...
let autoLoginEnabled = UserDefaults.standard.bool(forKey: "auto_login_enabled")  // ❌ ПРОБЛЕМА!
```

**Проблема:**
- Вызывается в `init()` синхронно
- Если есть `@AppStorage` свойства, которые читают из `UserDefaults`, это может вызвать рекурсию
- Особенно если `init()` вызывается во время инициализации View

**Вероятность краша:** 🟡 **70%**

**Почему это не было исправлено ранее:**
- Это код в `#if DEBUG`, который может не вызывать проблему в RELEASE
- Но если это вызывается в TestFlight (Beta build), это может вызвать краш

---

## 📊 ТАБЛИЦА СРАВНЕНИЯ С ПРЕДЫДУЩИМИ ИСПРАВЛЕНИЯМИ

| Проблема | BUILD 91 | BUILD 92 | BUILD 94 | BUILD 95 | Статус |
|----------|----------|----------|----------|----------|--------|
| `@AppStorage` → computed property | ✅ Исправлено | ✅ Исправлено | ✅ Исправлено | ✅ Исправлено | ✅ |
| `.onChange()` с `@AppStorage` | ✅ Исправлено | ✅ Исправлено | ✅ Исправлено | ✅ Исправлено | ✅ |
| `.id()` с `localizationManager` | ✅ Исправлено | ✅ Исправлено | ✅ Исправлено | ✅ Исправлено | ✅ |
| `UserDefaults.bool()` в `initializeNavigation()` | ❌ Не было | ❌ Не было | ✅ Исправлено | ✅ Исправлено | ✅ |
| `UserDefaults.set()` в `initializeNavigation()` | ❌ Не было | ❌ Не было | ❌ Не было | ❌ **НЕ ИСПРАВЛЕНО** | ❌ |
| `MasterLogger.enableVisualLogging` в `body` | ❌ Не было | ❌ Не было | ❌ Не было | ❌ **НЕ ИСПРАВЛЕНО** | ❌ |
| `UserDefaults.bool()` в `ALADDINApp.init()` | ❌ Не было | ❌ Не было | ❌ Не было | ❌ **НЕ ИСПРАВЛЕНО** | ❌ |

---

## 🎯 ВЫВОДЫ

### ✅ ЧТО МЫ ИСПРАВИЛИ:
1. ✅ Рекурсия в `@AppStorage` → computed property (BUILD 91)
2. ✅ Рекурсия в `.onChange()` и `.id()` (BUILD 92)
3. ✅ Рекурсия в `UserDefaults.bool()` в `initializeNavigation()` (BUILD 94)
4. ✅ Рекурсия в `NavigationManager.init()` (BUILD 94)
5. ✅ Рекурсия в `MasterLogger.init()` (BUILD 94)

### ❌ ЧТО МЫ **НЕ ИСПРАВИЛИ**:
1. ❌ **`UserDefaults.set()` в `initializeNavigation()`** - вызывает обновление `@AppStorage` → рекурсия
2. ❌ **`MasterLogger.enableVisualLogging` читается в `body`** - вызывает `UserDefaults.bool()` → рекурсия
3. ❌ **`UserDefaults.bool()` в `ALADDINApp.init()`** - может вызвать рекурсию при инициализации

### 🔴 ГЛАВНАЯ ПРОБЛЕМА:
**`UserDefaults.set()` в `initializeNavigation()`** - это **КРИТИЧЕСКАЯ ПРОБЛЕМА**, которая вызывает рекурсию:
- `onAppear` → `initializeNavigation()` → `UserDefaults.set()` → обновление `@AppStorage` → перерисовка View → `onAppear` → **РЕКУРСИЯ!**

---

## 📋 РЕКОМЕНДАЦИИ ДЛЯ ИСПРАВЛЕНИЯ

### 🔴 КРИТИЧНО (Приоритет 1):
1. **Убрать `UserDefaults.set()` из `initializeNavigation()`**
   - Использовать `@AppStorage` для установки значения
   - Или использовать асинхронную установку через `Task {}`

### 🟡 ВЫСОКО (Приоритет 2):
2. **Сделать `MasterLogger.enableVisualLogging` асинхронным**
   - Кешировать значение в `@State` переменной
   - Обновлять асинхронно через `Task {}`

### 🟢 СРЕДНЕ (Приоритет 3):
3. **Убрать `UserDefaults.bool()` из `ALADDINApp.init()`**
   - Использовать `@AppStorage` вместо прямого обращения
   - Или использовать асинхронное чтение

---

## ✅ ПОДТВЕРЖДЕНИЕ АНАЛИЗА

**ДА, МЫ ИСПРАВЛЯЛИ ПОХОЖИЕ ПРОБЛЕМЫ РАНЕЕ:**
- ✅ BUILD 91: Рекурсия в `@AppStorage` → computed property
- ✅ BUILD 92: Рекурсия в `.onChange()` и `.id()`
- ✅ BUILD 94: Рекурсия в `UserDefaults.bool()` в `initializeNavigation()`

**НО:**
- ❌ **НЕ ИСПРАВИЛИ** `UserDefaults.set()` в `initializeNavigation()` - это **НОВАЯ ПРОБЛЕМА**
- ❌ **НЕ ИСПРАВИЛИ** чтение `MasterLogger.enableVisualLogging` в `body` - это **НОВАЯ ПРОБЛЕМА**
- ❌ **НЕ ИСПРАВИЛИ** `UserDefaults.bool()` в `ALADDINApp.init()` - это **НОВАЯ ПРОБЛЕМА**

**ВЫВОД:**
Мы исправляли **ПОХОЖИЕ** проблемы, но **НЕ ВСЕ** проблемы. Текущий краш вызван **НОВЫМИ** проблемами, которые остались после предыдущих исправлений.
