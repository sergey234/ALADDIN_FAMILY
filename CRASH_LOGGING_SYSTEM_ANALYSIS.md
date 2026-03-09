# 🔍 ПОЛНЫЙ АНАЛИЗ СИСТЕМЫ ЛОГИРОВАНИЯ КРАШЕЙ
## Как работает система и где найти логи

**Дата:** 2026-03-09  
**Версия:** BUILD 86

---

## 📊 АРХИТЕКТУРА СИСТЕМЫ ЛОГИРОВАНИЯ

### **Три уровня логирования:**

```
1. AppDelegate.crashExceptionHandler() 
   ↓
   Сохраняет в UserDefaults["last_crash_log"]
   
2. ALADDINApp.init() - NSSetUncaughtExceptionHandler
   ↓
   Выводит в Xcode Console (print)
   
3. VisualLogger
   ↓
   Сохраняет в UserDefaults["visual_logger_logs"]
   Восстанавливает при запуске
```

---

## 🔧 КОМПОНЕНТЫ СИСТЕМЫ

### **1. AppDelegate.swift - Основной обработчик**

**Функция:** `crashExceptionHandler(exception: NSException)`

**Что делает:**
- Перехватывает краш через `NSSetUncaughtExceptionHandler`
- Сохраняет детали краша в UserDefaults
- Выводит в консоль

**Сохраняет:**
```swift
UserDefaults["last_crash_log"] = """
🚨 CRASH DETECTED!
Exception: \(exception.name.rawValue)
Reason: \(exception.reason ?? "Unknown")
Time: \(Date())
Device: \(UIDevice.current.model)
iOS: \(UIDevice.current.systemVersion)
"""

UserDefaults["crash_timestamp"] = Date().timeIntervalSince1970
```

**Устанавливается в:**
```swift
setupCrashHandler() // Вызывается в didFinishLaunchingWithOptions
```

---

### **2. ALADDINApp.swift - Дополнительный обработчик**

**Функция:** `NSSetUncaughtExceptionHandler` в `init()`

**Что делает:**
- Дополнительный обработчик для детального логирования
- Выводит полный stack trace в консоль
- Работает параллельно с AppDelegate обработчиком

**Выводит:**
```
💥💥💥 GLOBAL CRASH DETECTED! 💥💥💥
💥 Exception Name: ...
💥 Exception Reason: ...
💥 Stack Trace:
💥   [0] ...
💥   [1] ...
```

---

### **3. VisualLogger.swift - Визуальные логи**

**Функции:**
- `saveLogToUserDefaults()` - сохраняет каждый лог
- `loadLogsFromUserDefaults()` - восстанавливает при запуске
- `getSavedLogs()` - получает сохраненные логи

**Что сохраняет:**
```swift
UserDefaults["visual_logger_logs"] = [LogEntry] // JSON массив
UserDefaults["visual_logger_last_save"] = timestamp
```

**Структура LogEntry:**
```swift
struct LogEntry {
    let id: UUID
    let timestamp: Date
    let message: String
    let level: LogLevel
    let file: String
    let line: Int
}
```

**Особенности:**
- Максимум 50 логов
- Автоматически восстанавливается при запуске
- Отображается на экране (в DEBUG режиме)

---

## 📍 ГДЕ ХРАНЯТСЯ ЛОГИ

### **UserDefaults ключи:**

| Ключ | Тип | Описание |
|------|-----|----------|
| `"last_crash_log"` | String | Текст последнего краша |
| `"crash_timestamp"` | Double | Время краша (timestamp) |
| `"visual_logger_logs"` | Data (JSON) | Массив всех логов VisualLogger |
| `"visual_logger_last_save"` | Double | Время последнего сохранения |

---

## 🎯 КАК ПОЛУЧИТЬ ЛОГИ

### **Метод 1: Функция getCrashLogs() (РЕКОМЕНДУЕТСЯ)**

**В Debug Console выполните:**
```swift
po getCrashLogs()
```

**Что покажет:**
- ✅ Последний лог краша
- ✅ Время краша
- ✅ Последние 30 логов VisualLogger
- ✅ Информацию об устройстве

**Пример вывода:**
```
=== 🔍 CRASH LOGS ===

🚨 LAST CRASH LOG:
🚨 CRASH DETECTED!
Exception: NSInvalidArgumentException
Reason: -[__NSCFString objectForKey:]: unrecognized selector
Time: 2026-03-09 21:30:15 +0000
Device: iPhone
iOS: 15.2

⏰ CRASH TIME: Monday, March 9, 2026 at 9:30:15 PM

📋 VISUAL LOGGER LOGS (15 entries):
   [21:30:10.123] ℹ️ ALADDINApp.init() called
   [21:30:10.125] ℹ️ SubscriptionManager.shared created
   ...
```

---

### **Метод 2: Xcode Console (при запуске)**

1. Запустите приложение в Xcode
2. Откройте Console (Cmd+Shift+Y)
3. Ищите сообщения:
   - `💥💥💥 GLOBAL CRASH DETECTED!`
   - `💥 CRASH LOG SAVED:`
   - `🚨 CRASH DETECTED!`

---

### **Метод 3: UserDefaults напрямую**

**В Debug Console:**
```swift
// Основной лог краша
po UserDefaults.standard.string(forKey: "last_crash_log")

// Время краша
po Date(timeIntervalSince1970: UserDefaults.standard.double(forKey: "crash_timestamp"))

// VisualLogger логи
po UserDefaults.standard.data(forKey: "visual_logger_logs")
```

---

### **Метод 4: VisualLogger на экране**

Если приложение запускается:
- Логи автоматически отображаются на экране
- Нажмите "Копировать" для копирования
- Логи восстанавливаются из UserDefaults автоматически

---

## 🔄 ЛОГИКА РАБОТЫ

### **Последовательность при краше:**

```
1. Приложение крашится
   ↓
2. crashExceptionHandler() перехватывает краш
   ↓
3. Сохраняет в UserDefaults["last_crash_log"]
   ↓
4. Сохраняет время в UserDefaults["crash_timestamp"]
   ↓
5. Выводит в консоль через print()
   ↓
6. NSSetUncaughtExceptionHandler в ALADDINApp также срабатывает
   ↓
7. Выводит детальный stack trace в консоль
```

### **Последовательность при запуске:**

```
1. Приложение запускается
   ↓
2. VisualLogger.init() вызывается
   ↓
3. loadLogsFromUserDefaults() загружает логи
   ↓
4. Логи добавляются в массив logs
   ↓
5. Отображаются на экране (в DEBUG режиме)
   ↓
6. Можно получить через getCrashLogs()
```

---

## 🔍 АНАЛИЗ ЛОГОВ

### **Что искать:**

1. **Exception Name:**
   - `NSInvalidArgumentException` - неверный аргумент
   - `NSRangeException` - выход за границы
   - `EXC_BAD_ACCESS` - доступ к памяти
   - `EXC_CRASH` - общий краш

2. **Exception Reason:**
   - Точное описание проблемы
   - Часто содержит название метода

3. **Stack Trace:**
   - Показывает последовательность вызовов
   - Первые строки - место краша
   - Ищите ваши файлы

4. **VisualLogger логи:**
   - Что происходило ДО краша
   - Последовательность событий
   - Последние действия перед крашем

---

## ✅ ПРОВЕРКА РАБОТЫ СИСТЕМЫ

### **Тест 1: Проверить что обработчик установлен**

В Debug Console:
```swift
po NSGetUncaughtExceptionHandler()
```

Должен вернуть адрес функции (не nil).

### **Тест 2: Проверить сохранение логов**

1. Запустите приложение
2. Вызовите краш (если возможно)
3. Выполните: `po getCrashLogs()`
4. Должны увидеть логи

### **Тест 3: Проверить VisualLogger**

1. Запустите приложение
2. Должны увидеть VisualLogger на экране (DEBUG режим)
3. Логи должны восстанавливаться автоматически

---

## 🛠️ ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ

### **Очистка логов:**

```swift
po clearCrashLogs()
```

Удаляет все логи из UserDefaults.

---

## 📝 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### **Пример 1: Получить все логи**

```swift
po getCrashLogs()
```

### **Пример 2: Получить только последний краш**

```swift
po UserDefaults.standard.string(forKey: "last_crash_log")
```

### **Пример 3: Получить время краша**

```swift
let timestamp = UserDefaults.standard.double(forKey: "crash_timestamp")
po Date(timeIntervalSince1970: timestamp)
```

### **Пример 4: Получить VisualLogger логи**

```swift
if let data = UserDefaults.standard.data(forKey: "visual_logger_logs"),
   let logs = try? JSONDecoder().decode([VisualLogger.LogEntry].self, from: data) {
    po logs.map { "[\($0.formattedTime)] \($0.message)" }
}
```

---

## 🎯 РЕКОМЕНДАЦИИ

1. **Всегда используйте `getCrashLogs()`** - это самый простой способ
2. **Проверяйте Xcode Console** при запуске - там самые свежие логи
3. **Сохраняйте логи** перед очисткой - они могут понадобиться
4. **Анализируйте Stack Trace** - там точное место краша

---

**Дата создания:** 2026-03-09  
**Автор:** AI Assistant  
**Версия:** 1.0
