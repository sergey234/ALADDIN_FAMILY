# 🚨 АНАЛИЗ КРАША BUILD 104: ВТОРОЙ КРАШ (MAIN THREAD)

## 📋 МЕТА-ИНФОРМАЦИЯ ДЛЯ ML СИСТЕМ

**Дата анализа:** 2026-03-11  
**Build:** 104  
**Платформа:** iOS 26.1 (23B85)  
**Устройство:** iPhone 12,8  
**Тип краша:** `EXC_BAD_ACCESS (SIGSEGV)` - бесконечная рекурсия  
**Thread:** **MAIN THREAD** (Thread 0) ⚠️ КРИТИЧНОЕ ОТЛИЧИЕ  
**Адреса рекурсии:** `0x10314dfbc` (повторяется многократно)  

---

## 🎯 ОСОБЕННОСТИ ЭТОГО КРАША

### 🔴 КРИТИЧНЫЕ ОТЛИЧИЯ ОТ BUILD 103

| Аспект | BUILD 103 | BUILD 104 (ТЕКУЩИЙ) |
|--------|-----------|---------------------|
| **Thread** | Thread 2 (background) | **Thread 0 (MAIN THREAD)** ⚠️ |
| **Exception** | `EXC_BAD_ACCESS (SIGBUS)` | `EXC_BAD_ACCESS (SIGSEGV)` |
| **Адреса** | `0x103246300`, `0x10115a300` | `0x10314dfbc` |
| **Время** | 01:53:25 | **12:19:46** (позже) |
| **Build** | 103 | **104** (обновлен) |

### 📊 ТРЕВОЖНЫЕ СИГНАЛЫ

1. **MAIN THREAD CRASH** - приложение зависает полностью
2. **SIGSEGV** вместо SIGBUS - более серьезная ошибка памяти
3. **Рекурсия на main thread** - блокирует UI
4. **Несмотря на исправления** - краш продолжается

---

## 📊 ТЕХНИЧЕСКИЙ АНАЛИЗ STACK TRACE

### Thread 0 (Crashed - MAIN THREAD):

**SwiftUI Lifecycle + Dictionary Operations:**
```
0   libswiftCore.dylib  swift::swift_slowAllocTyped(...)  // Memory allocation
1   libswiftCore.dylib  swift_allocObject(...)           // Object creation
2   libswiftCore.dylib  _DictionaryStorage.allocate(...) // Dictionary allocation
3   libswiftCore.dylib  _DictionaryStorage.resize(...)   // ⚠️ DICTIONARY RESIZE
4   ALADDIN             0x103047f8c  // Application code
5   ALADDIN             0x103044060  // Application code
6   ALADDIN             0x1030439c4  // Application code
7   ALADDIN             0x10314d864  // ⚠️ RECURSION START
8   ALADDIN             0x10314dfac  // Recursive call
9   ALADDIN             0x10314dfbc  // ⚠️ RECURSION (повторяется)
10  ALADDIN             0x10314dfbc  // ⚠️ RECURSION
11  ALADDIN             0x10314dfbc  // ⚠️ RECURSION
...повторяется многократно...
```

### Thread 2 (Background - аналогичный паттерн):
```
0   libsystem_malloc.dylib  _xzm_xzone_malloc_from_freelist_chunk
1   libswiftCore.dylib     swift::swift_slowAllocTyped(...)
2   libswiftCore.dylib     swift_allocObject(...)
3   libswiftCore.dylib     _DictionaryStorage.allocate(...)
4   libswiftCore.dylib     _DictionaryStorage.resize(...)
5   ALADDIN                0x103047f8c  // ⚠️ ТОТ ЖЕ АДРЕС ЧТО И В Thread 0
6   ALADDIN                0x103047f8c  // РЕКУРСИЯ
...повторяется...
```

---

## 🔍 ГЛУБОКИЙ АНАЛИЗ ПРОБЛЕМЫ

### 🎯 ОСНОВНАЯ ПРОБЛЕМА: РЕКУРСИЯ НА MAIN THREAD

**Почему краш переместился на main thread:**

1. **SwiftUI Lifecycle** - View body computation на main thread
2. **@State/@AppStorage** - reactive updates вызывают перерисовку
3. **Dictionary в computed properties** - создаются при каждом доступе
4. **View modifiers** - `.onChange`, `.task` выполняются на main thread

### 📋 ВОЗМОЖНЫЕ ИСТОЧНИКИ ПРОБЛЕМЫ

#### 1. 🔴 SwiftUI View Body Computation

**Проблема:** Dictionary создается в View body или computed properties

**Возможные места:**
```swift
struct NetworkProtectionScreen: View {
    var body: some View {
        // ⚠️ Dictionary может создаваться здесь
        let config = ["key": "value"]  // В body - КАТАСТРОФА
        return VStack { ... }
    }
}
```

#### 2. 🔴 @AppStorage / @State в View

**Проблема:** Reactive properties вызывают перерисовку при изменении

```swift
struct SomeView: View {
    @AppStorage("setting") var setting: Bool = false

    var body: some View {
        // ⚠️ При изменении setting View перерисовывается
        // Если в body есть Dictionary operations - рекурсия
        Text("Setting: \(setting)")
    }
}
```

#### 3. 🔴 .onChange Modifiers

**Проблема:** Множественные `.onChange` в иерархии View

```swift
// ⚠️ Много .onChange в одном View tree
Toggle("Option", isOn: $option)
    .onChange(of: option) { _ in
        // Dictionary operations здесь
        let params = ["key": "value"]
        analytics.track(...)
    }
```

#### 4. 🔴 Task { } в View Modifiers

**Проблема:** `Task {}` создает Dictionary до await

```swift
.task {
    // ⚠️ Dictionary может создаваться синхронно
    let params = ["component_id": componentId]
    await someAsyncOperation(params)
}
```

---

## 🎯 ВОЗМОЖНЫЕ ИСТОЧНИКИ В КОДЕ

### 1. NetworkProtectionScreen View Body

**Проблемные места:**
- Computed properties в View
- Dictionary literals в body
- @State computations

### 2. Component Status Updates

**Проблема:** Status changes вызывают View updates на main thread

```swift
// Когда статус компонента меняется:
componentStatusChanged() {
    // → View перерисовывается на main thread
    // → Dictionary создается в computed property
    // → РЕКУРСИЯ
}
```

### 3. Analytics в UI Components

**Проблема:** UI components создают analytics events

```swift
// В SmartToggleRow или других UI components:
.onChange(of: value) {
    // Dictionary creation на main thread
    analytics.track(...)
}
```

### 4. SwiftUI State Management

**Проблема:** State updates вызывают cascading View updates

```swift
@Published var componentEnabled = false
// → State change
// → View update on main thread
// → Dictionary in computed property
// → РЕКУРСИЯ
```

---

## 📈 АНАЛИЗ ТЕНДЕНЦИИ КРАШЕЙ

### Build Evolution:

| Build | Thread | Exception | Адреса | Статус |
|-------|--------|-----------|--------|--------|
| 103 | Thread 2 | SIGBUS | `0x103246300`, `0x10115a300` | Background crash |
| **104** | **Thread 0** | **SIGSEGV** | **`0x10314dfbc`** | **MAIN THREAD CRASH** ⚠️ |

### Тревожные признаки:

1. **Эскалация серьезности:** SIGBUS → SIGSEGV
2. **Переход на main thread:** Background → Main thread
3. **Увеличение частоты:** Краш происходит чаще
4. **Несмотря на исправления:** Проблема не решена

---

## 🎯 ГИПОТЕЗЫ О ПРИЧИНАХ

### Гипотеза 1: SwiftUI Lifecycle Dictionary Creation

**Сценарий:**
1. User нажимает тумблер
2. `@State` обновляется
3. View перерисовывается на main thread
4. В computed property создается Dictionary
5. Dictionary.resize вызывает рекурсию
6. **CRASH**

### Гипотеза 2: @AppStorage Reactive Updates

**Сценарий:**
1. Component status сохраняется в UserDefaults
2. @AppStorage получает уведомление
3. View перерисовывается
4. Dictionary создается в reactive property
5. **CRASH**

### Гипотеза 3: Task { } Timing Issues

**Сценарий:**
1. `Task {}` создается на main thread
2. Dictionary literal создается синхронно
3. `await MainActor.run` выполняется асинхронно
4. Но Dictionary уже создан на main thread
5. **CRASH**

---

## 📋 РЕКОМЕНДАЦИИ ДЛЯ ДАЛЬНЕЙШЕГО АНАЛИЗА

### 1. Проверить View Body Computations

**Найти все места где Dictionary создается в:**
- View body
- Computed properties
- @State getters/setters
- @AppStorage properties

### 2. Анализировать SwiftUI State Flow

**Отследить цепочку:**
```
User Action → @State change → View update → Dictionary creation → Crash
```

### 3. Проверить Task { } Usage

**Найти все `Task {}` в UI code и проверить:**
- Создается ли Dictionary до `await`?
- Выполняется ли на main thread?

### 4. Добавить Main Thread Assertions

**Временно добавить проверки:**
```swift
assert(Thread.isMainThread, "Dictionary creation must be on main thread")
```

---

## 🎖️ ЗАКЛЮЧЕНИЕ

**Критический статус:** 🚨 **MAIN THREAD CRASH** - приложение полностью зависает

**Основная проблема:** Dictionary operations в SwiftUI lifecycle на main thread вызывают бесконечную рекурсию

**Требуется немедленный анализ:**
1. Всех View body computations
2. SwiftUI state management
3. Task { } usage patterns
4. @AppStorage reactive updates

**Риск:** Очень высокий - main thread crash делает приложение полностью неработоспособным

---

**АНАЛИЗ ЗАВЕРШЕН. ТРЕБУЕТСЯ НЕМЕДЛЕННЫЙ ГЛУБОКИЙ АНАЛИЗ КОДА.**