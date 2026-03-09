# 🔍 РУКОВОДСТВО ПО ПОЛУЧЕНИЮ ЛОГОВ КРАШЕЙ
## Как увидеть логи крашей и найти причину

**Дата:** 2026-03-09  
**Версия:** BUILD 86

---

## 📊 СИСТЕМА ЛОГИРОВАНИЯ КРАШЕЙ

### **1. Где сохраняются логи:**

#### **1.1. AppDelegate - Основной обработчик крашей**
**Ключи в UserDefaults:**
- `"last_crash_log"` - текст лога краша
- `"crash_timestamp"` - время краша (timestamp)

**Что сохраняется:**
- Имя исключения (Exception Name)
- Причина краша (Reason)
- Время краша
- Модель устройства
- Версия iOS

#### **1.2. VisualLogger - Визуальные логи**
**Ключ в UserDefaults:**
- `"visual_logger_logs"` - массив логов (JSON)

**Что сохраняется:**
- Все логи до момента краша
- Восстанавливаются при следующем запуске
- Максимум 50 логов

#### **1.3. Консоль Xcode - Print логи**
**Где смотреть:**
- Xcode Console при запуске приложения
- Логи выводятся через `print()`

---

## 🔧 КАК ПОЛУЧИТЬ ЛОГИ

### **Метод 1: Через Xcode Console (РЕКОМЕНДУЕТСЯ)**

1. **Запустите приложение в Xcode**
2. **Откройте Console** (View → Debug Area → Activate Console или Cmd+Shift+Y)
3. **Ищите сообщения:**
   ```
   💥💥💥 GLOBAL CRASH DETECTED! 💥💥💥
   💥 Exception Name: ...
   💥 Exception Reason: ...
   💥 Stack Trace:
   💥   [0] ...
   💥   [1] ...
   ```

4. **Или ищите:**
   ```
   💥 CRASH LOG SAVED: ...
   🚨 CRASH DETECTED!
   ```

### **Метод 2: Через UserDefaults (если приложение не запускается)**

#### **Вариант A: Через Debug Console в Xcode**

1. **Установите breakpoint** в любом месте кода
2. **В Debug Console выполните:**

```swift
// Получить лог краша
let crashLog = UserDefaults.standard.string(forKey: "last_crash_log")
print("CRASH LOG: \(crashLog ?? "No crash log")")

// Получить время краша
let timestamp = UserDefaults.standard.double(forKey: "crash_timestamp")
if timestamp > 0 {
    let date = Date(timeIntervalSince1970: timestamp)
    print("CRASH TIME: \(date)")
}

// Получить VisualLogger логи
if let data = UserDefaults.standard.data(forKey: "visual_logger_logs"),
   let logs = try? JSONDecoder().decode([VisualLogger.LogEntry].self, from: data) {
    print("VISUAL LOGS COUNT: \(logs.count)")
    for log in logs.suffix(10) { // Последние 10 логов
        print("[\(log.formattedTime)] \(log.level.rawValue) \(log.message)")
    }
}
```

#### **Вариант B: Через LLDB в терминале**

```bash
# Подключитесь к процессу через lldb
lldb -p <process_id>

# Выполните команды
po UserDefaults.standard.string(forKey: "last_crash_log")
po UserDefaults.standard.double(forKey: "crash_timestamp")
```

### **Метод 3: Через VisualLogger в UI (если приложение запускается)**

1. **Запустите приложение**
2. **VisualLogger должен отображаться на экране** (в DEBUG режиме)
3. **Логи автоматически восстанавливаются** из UserDefaults
4. **Нажмите "Копировать"** чтобы скопировать логи в буфер обмена

---

## 📝 СОЗДАНИЕ ФУНКЦИИ ДЛЯ ПОЛУЧЕНИЯ ЛОГОВ

Добавьте эту функцию в ваш код для удобного получения логов:

```swift
#if DEBUG
func getCrashLogs() -> String {
    var result = "=== CRASH LOGS ===\n\n"
    
    // 1. Основной лог краша
    if let crashLog = UserDefaults.standard.string(forKey: "last_crash_log") {
        result += "🚨 LAST CRASH LOG:\n\(crashLog)\n\n"
    } else {
        result += "✅ No crash log found\n\n"
    }
    
    // 2. Время краша
    let timestamp = UserDefaults.standard.double(forKey: "crash_timestamp")
    if timestamp > 0 {
        let date = Date(timeIntervalSince1970: timestamp)
        let formatter = DateFormatter()
        formatter.dateStyle = .full
        formatter.timeStyle = .full
        result += "⏰ CRASH TIME: \(formatter.string(from: date))\n\n"
    }
    
    // 3. VisualLogger логи
    if let data = UserDefaults.standard.data(forKey: "visual_logger_logs"),
       let logs = try? JSONDecoder().decode([VisualLogger.LogEntry].self, from: data) {
        result += "📋 VISUAL LOGS (\(logs.count) entries):\n"
        for log in logs.suffix(20) { // Последние 20 логов
            result += "[\(log.formattedTime)] \(log.level.rawValue) \(log.message)\n"
        }
    } else {
        result += "✅ No visual logs found\n"
    }
    
    return result
}

// Использование в Debug Console:
// po getCrashLogs()
#endif
```

---

## 🔍 АНАЛИЗ ЛОГОВ

### **Что искать в логах:**

1. **Exception Name:**
   - `NSInvalidArgumentException` - неверный аргумент
   - `NSRangeException` - выход за границы массива
   - `EXC_BAD_ACCESS` - доступ к несуществующей памяти
   - `EXC_CRASH` - общий краш

2. **Exception Reason:**
   - Часто содержит точное описание проблемы
   - Например: "Attempted to dereference null pointer"

3. **Stack Trace:**
   - Показывает последовательность вызовов до краша
   - Ищите ваши файлы в stack trace
   - Первые строки - место краша

4. **VisualLogger логи:**
   - Показывают что происходило ДО краша
   - Помогают понять последовательность событий

---

## 🎯 ПРИМЕР АНАЛИЗА

### **Пример лога краша:**

```
🚨 CRASH DETECTED!
Exception: NSInvalidArgumentException
Reason: -[__NSCFString objectForKey:]: unrecognized selector sent to instance
Time: 2026-03-09 21:30:15 +0000
Device: iPhone
iOS: 15.2
```

**Анализ:**
- Проблема: Вызов `objectForKey:` на строке вместо словаря
- Решение: Проверить где используется строка как словарь

### **Пример VisualLogger логов:**

```
[21:30:10.123] ℹ️ ALADDINApp.init() called
[21:30:10.125] ℹ️ SubscriptionManager.shared created
[21:30:10.130] ⚠️ Network request failed
[21:30:10.135] ❌ CRASH!
```

**Анализ:**
- Краш произошел после сетевого запроса
- Возможно проблема в обработке ответа

---

## 🛠️ ДОПОЛНИТЕЛЬНЫЕ ИНСТРУМЕНТЫ

### **1. Xcode Organizer (для TestFlight крашей)**

1. **Window → Organizer → Crashes**
2. Выберите ваше приложение
3. Найдите последний краш
4. Откройте детали краша

### **2. Console.app (для системных логов)**

1. Откройте **Console.app** на Mac
2. Выберите ваше устройство
3. Ищите логи с префиксом "ALADDIN" или "CRASH"

### **3. Device Logs (на устройстве)**

1. **Settings → Privacy → Analytics & Improvements → Analytics Data**
2. Найдите записи с префиксом "ALADDIN"
3. Откройте последнюю запись

---

## ✅ ЧЕКЛИСТ ДЛЯ ДИАГНОСТИКИ

- [ ] Проверить Xcode Console при запуске
- [ ] Проверить UserDefaults через Debug Console
- [ ] Проверить VisualLogger на экране (если приложение запускается)
- [ ] Проверить Xcode Organizer (если краш в TestFlight)
- [ ] Проверить Console.app для системных логов
- [ ] Проанализировать Exception Name и Reason
- [ ] Изучить Stack Trace
- [ ] Проверить VisualLogger логи до краша

---

## 📞 ЕСЛИ ЛОГИ НЕ ПОМОГАЮТ

Если логи не показывают причину краша:

1. **Добавьте больше логирования:**
   - В `ALADDINApp.init()`
   - В `ALADDINApp.onAppear`
   - В инициализации менеджеров

2. **Используйте Instruments:**
   - Запустите через **Product → Profile**
   - Выберите **Leaks** или **Allocations**

3. **Проверьте Thread Sanitizer:**
   - Включите в Scheme → Run → Diagnostics
   - Поможет найти проблемы с потоками

---

**Дата создания:** 2026-03-09  
**Автор:** AI Assistant  
**Версия:** 1.0
