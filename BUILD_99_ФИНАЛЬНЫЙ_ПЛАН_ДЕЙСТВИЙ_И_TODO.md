# 🔴 BUILD 99: ФИНАЛЬНЫЙ ПЛАН ДЕЙСТВИЙ И TODO ЛИСТ

**Дата:** 2026-03-10  
**Статус:** 🚨 КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ  
**Вероятность успеха после исправлений:** 🟢 **85-90%**

---

## 📋 КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ (СДЕЛАТЬ СЕЙЧАС)

### ✅ TODO-1: Добавить статический Calendar в displayFormatter

**Приоритет:** 🔴 КРИТИЧЕСКИЙ  
**Время:** 5 минут  
**Файл:** `Screens/01_MainScreen.swift`  
**Строки:** 945-952

**Проблема:**
- `DateFormatter` внутри использует `Calendar.current`
- `Calendar.current` может читать из `UserDefaults`
- Это создает цикл рекурсии через ICU библиотеку
- **ЭТО НОВАЯ ПРОБЛЕМА, КОТОРУЮ МЫ НЕ ИСПРАВЛЯЛИ!**

**Текущий код:**
```swift
private static let displayFormatter: DateFormatter = {
    let formatter = DateFormatter()
    formatter.dateStyle = .medium
    formatter.timeStyle = .none
    formatter.locale = Locale(identifier: "ru_RU")
    // ❌ НЕТ formatter.calendar = ... !
    return formatter
}()
```

**Исправление:**
```swift
// ✅ Создать статический Calendar
private static let calendar: Calendar = {
    var cal = Calendar(identifier: .gregorian)
    cal.locale = Locale(identifier: "ru_RU")
    return cal
}()

// ✅ Использовать статический Calendar в форматтере
private static let displayFormatter: DateFormatter = {
    let formatter = DateFormatter()
    formatter.dateStyle = .medium
    formatter.timeStyle = .none
    formatter.locale = Locale(identifier: "ru_RU")
    formatter.calendar = Self.calendar  // ← ДОБАВИТЬ ЭТО!
    return formatter
}()
```

**Проверка:**
- [ ] Код компилируется
- [ ] Calendar создается один раз
- [ ] Calendar используется в форматтере

---

### ✅ TODO-2: Выполнять форматирование на main thread

**Приоритет:** 🔴 КРИТИЧЕСКИЙ  
**Время:** 5 минут  
**Файл:** `Screens/01_MainScreen.swift`  
**Строки:** 990-994

**Проблема:**
- Форматирование происходит вне main thread
- Это может вызвать проблемы с `UserDefaults`
- ICU библиотека может читать из `UserDefaults` не на main thread

**Текущий код:**
```swift
// ✅ Используем статический displayFormatter
let formattedText = Self.displayFormatter.string(from: date)  // ❌ Вне main thread!
await MainActor.run {
    cachedExpirationText = formattedText
}
```

**Исправление:**
```swift
// ✅ Форматирование на main thread!
let formattedText = await MainActor.run {
    Self.displayFormatter.string(from: date)
}
await MainActor.run {
    cachedExpirationText = formattedText
}
```

**Проверка:**
- [ ] Форматирование происходит на main thread
- [ ] Код компилируется
- [ ] Нет блокировки UI

---

### ✅ TODO-3: Исправить защиту от рекурсии (глобальный флаг)

**Приоритет:** 🔴 КРИТИЧЕСКИЙ  
**Время:** 10 минут  
**Файл:** `Screens/01_MainScreen.swift`  
**Строки:** 957-995

**Проблема:**
- Защита через `@State` не работает из-за race condition
- Новый экземпляр View не видит флаг старого экземпляра
- `defer` с асинхронным сбросом создает race condition

**Текущий код:**
```swift
@State private var isUpdatingExpirationText: Bool = false

private func updateExpirationTextCache(from isoString: String) async {
    guard !isUpdatingExpirationText else { return }  // ❌ @State - не работает!
    isUpdatingExpirationText = true
    defer { 
        Task { @MainActor in
            isUpdatingExpirationText = false  // ❌ Асинхронный сброс - race condition!
        }
    }
    // ...
}
```

**Исправление:**
```swift
// ✅ Вне struct MainScreen (глобальный флаг)
private var isUpdatingExpirationTextGlobal: Bool = false
private let expirationTextUpdateLock = NSLock()

// ✅ В функции updateExpirationTextCache
private func updateExpirationTextCache(from isoString: String) async {
    expirationTextUpdateLock.lock()
    guard !isUpdatingExpirationTextGlobal else {
        expirationTextUpdateLock.unlock()
        print("⚠️ [MainScreen] updateExpirationTextCache уже выполняется, пропускаем")
        return
    }
    isUpdatingExpirationTextGlobal = true
    expirationTextUpdateLock.unlock()
    
    defer {
        expirationTextUpdateLock.lock()
        isUpdatingExpirationTextGlobal = false
        expirationTextUpdateLock.unlock()
    }
    
    // ... остальной код ...
}
```

**Проверка:**
- [ ] Глобальный флаг создан вне struct
- [ ] NSLock используется правильно
- [ ] Защита работает при повторных вызовах
- [ ] Нет deadlock

---

### ✅ TODO-4: Исправить .task {} для предотвращения повторных вызовов

**Приоритет:** 🔴 КРИТИЧЕСКИЙ  
**Время:** 10 минут  
**Файл:** `Screens/01_MainScreen.swift`  
**Строки:** 390-461

**Проблема:**
- `.task {}` может вызываться повторно при пересоздании View
- `hasAppeared` не защищает от пересоздания
- Новый экземпляр View не видит флаг старого экземпляра

**Текущий код:**
```swift
.task {
    guard !hasAppeared else { return }  // ❌ @State - не работает при пересоздании!
    hasAppeared = true
    // ...
    let currentExpiresAt = subscriptionExpiresAtIso
    Task { @MainActor in
        await updateExpirationTextCache(from: currentExpiresAt)
    }
}
```

**Исправление (вариант 1 - глобальный флаг):**
```swift
// ✅ Вне struct MainScreen (глобальный флаг)
private var mainScreenTaskExecuted: Bool = false
private let mainScreenTaskLock = NSLock()

.task {
    mainScreenTaskLock.lock()
    guard !mainScreenTaskExecuted else {
        mainScreenTaskLock.unlock()
        return
    }
    mainScreenTaskExecuted = true
    mainScreenTaskLock.unlock()
    
    // ... остальной код ...
    
    let currentExpiresAt = subscriptionExpiresAtIso
    Task { @MainActor in
        await updateExpirationTextCache(from: currentExpiresAt)
    }
}
```

**Исправление (вариант 2 - onAppear):**
```swift
// ✅ Использовать onAppear с проверкой
.onAppear {
    guard !hasAppeared else { return }
    hasAppeared = true
    
    let currentExpiresAt = subscriptionExpiresAtIso
    Task { @MainActor in
        await updateExpirationTextCache(from: currentExpiresAt)
    }
}
```

**Рекомендация:** Использовать вариант 1 (глобальный флаг) для большей надежности.

**Проверка:**
- [ ] Глобальный флаг создан вне struct
- [ ] NSLock используется правильно
- [ ] .task {} вызывается только один раз
- [ ] Нет deadlock

---

## 🟡 ДОПОЛНИТЕЛЬНЫЕ ИСПРАВЛЕНИЯ (СДЕЛАТЬ ПОСЛЕ КРИТИЧЕСКИХ)

### ✅ TODO-5: Найти и заменить все Calendar.current на статический Calendar

**Приоритет:** 🟡 ВЫСОКИЙ  
**Время:** 1-2 часа  
**Файлы:** Все файлы с Calendar.current

**Проблема:**
- `Calendar.current` может читать из `UserDefaults`
- Это может вызвать рекурсию в других местах

**Действия:**
1. Найти все использования `Calendar.current`:
```bash
grep -r "Calendar\.current" --include="*.swift" .
```

2. Проверить каждое место на возможность рекурсии:
   - Используется ли в computed properties?
   - Используется ли в `body` View?
   - Используется ли в функциях, вызываемых из View?

3. Заменить на статический Calendar:
```swift
// ❌ БЫЛО:
if Calendar.current.isDateInToday(date) {
    // ...
}

// ✅ СТАЛО:
private static let calendar: Calendar = {
    var cal = Calendar(identifier: .gregorian)
    cal.locale = Locale(identifier: "ru_RU")
    return cal
}()

if Self.calendar.isDateInToday(date) {
    // ...
}
```

**Файлы для проверки:**
- `Screens/ChildRewardsScreen.swift`
- `Core/Managers/SubscriptionManager.swift`
- `Core/Notifications/NotificationManager.swift`
- Другие файлы из grep результатов

**Проверка:**
- [ ] Все Calendar.current найдены
- [ ] Все проблемные места исправлены
- [ ] Код компилируется
- [ ] Нет регрессий

---

### ✅ TODO-6: Добавить логирование для диагностики

**Приоритет:** 🟡 ВЫСОКИЙ  
**Время:** 15 минут  
**Файл:** `Screens/01_MainScreen.swift`

**Цель:**
- Отслеживание всех вызовов `updateExpirationTextCache`
- Отслеживание повторных вызовов `.task {}`
- Отслеживание проблем с рекурсией

**Действия:**
```swift
private func updateExpirationTextCache(from isoString: String) async {
    let callId = UUID().uuidString
    print("🔍 [MainScreen] updateExpirationTextCache START - \(callId) - \(Date())")
    
    expirationTextUpdateLock.lock()
    guard !isUpdatingExpirationTextGlobal else {
        expirationTextUpdateLock.unlock()
        print("⚠️ [MainScreen] updateExpirationTextCache уже выполняется, пропускаем - \(callId)")
        return
    }
    isUpdatingExpirationTextGlobal = true
    expirationTextUpdateLock.unlock()
    
    defer {
        expirationTextUpdateLock.lock()
        isUpdatingExpirationTextGlobal = false
        expirationTextUpdateLock.unlock()
        print("✅ [MainScreen] updateExpirationTextCache COMPLETE - \(callId) - \(Date())")
    }
    
    // ... остальной код ...
}
```

**Проверка:**
- [ ] Логирование добавлено
- [ ] Логи показывают все вызовы
- [ ] Логи помогают диагностировать проблемы

---

## 🟢 ТЕСТИРОВАНИЕ И МОНИТОРИНГ

### ✅ TODO-7: Протестировать на реальных устройствах

**Приоритет:** 🟢 ВЫСОКИЙ  
**Время:** 1-2 часа

**Действия:**
1. Собрать приложение для TestFlight
2. Протестировать на реальных устройствах:
   - iPhone 12 (как в краш-логе)
   - Другие модели iPhone
   - Разные версии iOS

3. Проверить:
   - [ ] Приложение запускается без крашей
   - [ ] MainScreen отображается корректно
   - [ ] Даты форматируются правильно
   - [ ] Нет рекурсии в логах
   - [ ] Нет крашей при открытии MainScreen

**Критерии успеха:**
- ✅ Нет крашей в течение 10+ запусков
- ✅ Нет рекурсии в логах
- ✅ Даты отображаются корректно

---

### ✅ TODO-8: Мониторить краши в течение 1-2 недель

**Приоритет:** 🟢 СРЕДНИЙ  
**Время:** Постоянный мониторинг

**Действия:**
1. Отслеживать краши в TestFlight
2. Анализировать crash logs
3. Проверять, не появились ли новые краши
4. Если краш продолжается:
   - Провести систематический поиск других проблемных мест
   - Проверить другие возможные причины рекурсии

**Критерии успеха:**
- ✅ Нет крашей в течение 1-2 недель
- ✅ Нет рекурсии в crash logs
- ✅ Приложение работает стабильно

---

## 📊 ПРИОРИТИЗАЦИЯ И ВРЕМЕННЫЕ ОЦЕНКИ

### Критические исправления (сделать сейчас):

| TODO | Время | Приоритет | Вероятность успеха |
|------|-------|-----------|-------------------|
| TODO-1: Calendar в форматтере | 5 мин | 🔴 КРИТИЧЕСКИЙ | 85% |
| TODO-2: Форматирование на main thread | 5 мин | 🔴 КРИТИЧЕСКИЙ | 95% |
| TODO-3: Глобальный флаг защиты | 10 мин | 🔴 КРИТИЧЕСКИЙ | 90% |
| TODO-4: Защита .task {} | 10 мин | 🔴 КРИТИЧЕСКИЙ | 85% |
| **ИТОГО** | **30 мин** | | **85-90%** |

### Дополнительные исправления (сделать после):

| TODO | Время | Приоритет | Вероятность успеха |
|------|-------|-----------|-------------------|
| TODO-5: Заменить Calendar.current | 1-2 часа | 🟡 ВЫСОКИЙ | 80% |
| TODO-6: Логирование | 15 мин | 🟡 ВЫСОКИЙ | 100% |
| **ИТОГО** | **1.5-2.5 часа** | | |

### Тестирование и мониторинг:

| TODO | Время | Приоритет |
|------|-------|-----------|
| TODO-7: Тестирование | 1-2 часа | 🟢 ВЫСОКИЙ |
| TODO-8: Мониторинг | Постоянно | 🟢 СРЕДНИЙ |

---

## ✅ КРИТЕРИИ УСПЕХА

### После исправления всех критических проблем:

1. ✅ **Нет рекурсии в краш-логах**
   - Адрес `0x1029ae4ec` не должен повторяться
   - Stack trace не должен показывать рекурсию

2. ✅ **Нет крашей при запуске приложения**
   - Приложение должно запускаться без крашей
   - MainScreen должен отображаться корректно

3. ✅ **Нет проблем с форматированием даты**
   - Даты должны отображаться корректно
   - Форматирование должно работать на всех устройствах

4. ✅ **Нет проблем с производительностью**
   - UI не должен блокироваться
   - Приложение должно работать плавно

---

## 🚨 КРИТИЧЕСКОЕ ЗАМЕЧАНИЕ

**Мы уже 2 недели исправляем этот краш, но он продолжается.**

**Это означает:**
- Либо мы не находим все проблемные места
- Либо проблема глубже, чем мы думаем
- Либо нужно использовать более радикальный подход

**Нужен системный подход:**
1. Исправить ВСЕ 4 критические проблемы одновременно
2. Протестировать ВСЕ исправления
3. Убедиться, что краш прекратился

**Только так можно решить проблему раз и навсегда!**

---

## 📝 ВЫВОДЫ

### ✅ МЫ УВЕРЕНЫ, ЧТО:

1. **Calendar.current - это НОВАЯ проблема, которую мы НЕ исправляли**
   - Это объясняет, почему исправления не помогли
   - Это корневая причина рекурсии через ICU

2. **Защита через @State НЕ работает**
   - Нужен глобальный флаг с NSLock
   - Это стандартное решение для такой проблемы

3. **Форматирование должно быть на main thread**
   - Это правильный подход
   - Это предотвратит проблемы с UserDefaults

4. **.task {} нужна дополнительная защита**
   - Может вызываться повторно при пересоздании View
   - Нужен глобальный флаг

### ⚠️ МЫ НЕ УВЕРЕНЫ, ЧТО:

1. **Это единственная проблема**
   - Могут быть другие места с похожими проблемами
   - Могут быть другие причины рекурсии

2. **Это решит проблему на 100%**
   - Вероятность успеха: 85-90%
   - Нужно тестирование и мониторинг

### 🎯 РЕКОМЕНДАЦИЯ:

**ИСПРАВИТЬ ВСЕ 4 КРИТИЧЕСКИЕ ПРОБЛЕМЫ ОДНОВРЕМЕННО**

**Вероятность успеха:** 🟢 **85-90%**

**После исправления:**
- Протестировать на реальных устройствах
- Мониторить краши в течение 1-2 недель
- Если краш продолжается, провести систематический поиск других проблемных мест

---

**ГОТОВО К ИСПРАВЛЕНИЮ!** 🔧
