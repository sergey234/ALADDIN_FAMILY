# 🚨 КАК УВИДЕТЬ ЛОГИ КРАШЕЙ - БЫСТРАЯ ИНСТРУКЦИЯ

## ⚡ БЫСТРЫЙ СПОСОБ (РЕКОМЕНДУЕТСЯ)

### **1. Запустите приложение в Xcode**

### **2. Откройте Debug Console** (Cmd+Shift+Y)

### **3. Выполните команду:**

```swift
po getCrashLogs()
```

**Это покажет:**
- ✅ Последний лог краша
- ✅ Время краша
- ✅ Последние 30 логов VisualLogger
- ✅ Информацию об устройстве

---

## 📋 ЧТО ПОКАЗЫВАЕТ getCrashLogs()

```
=== 🔍 CRASH LOGS ===

🚨 LAST CRASH LOG:
🚨 CRASH DETECTED!
Exception: NSInvalidArgumentException
Reason: ...
Time: ...
Device: iPhone
iOS: 15.2

⏰ CRASH TIME: Monday, March 9, 2026 at 9:30:15 PM
   Timestamp: 1234567890.0

📋 VISUAL LOGGER LOGS (15 entries):
   [21:30:10.123] ℹ️ ALADDINApp.init() called
   [21:30:10.125] ℹ️ SubscriptionManager.shared created
   [21:30:10.130] ⚠️ Network request failed
   ...
```

---

## 🔍 АЛЬТЕРНАТИВНЫЕ СПОСОБЫ

### **Способ 1: Xcode Console (при запуске)**

1. Запустите приложение
2. Смотрите консоль - логи выводятся автоматически:
   ```
   💥💥💥 GLOBAL CRASH DETECTED! 💥💥💥
   💥 Exception Name: ...
   💥 Exception Reason: ...
   💥 Stack Trace:
   ```

### **Способ 2: Через UserDefaults напрямую**

В Debug Console выполните:

```swift
// Основной лог краша
po UserDefaults.standard.string(forKey: "last_crash_log")

// Время краша
po Date(timeIntervalSince1970: UserDefaults.standard.double(forKey: "crash_timestamp"))
```

### **Способ 3: VisualLogger на экране**

Если приложение запускается:
- Логи автоматически отображаются на экране
- Нажмите "Копировать" для копирования в буфер обмена

---

## 🧹 ОЧИСТКА ЛОГОВ

Если нужно очистить логи:

```swift
po clearCrashLogs()
```

---

## 📊 ЛОГИКА РАБОТЫ СИСТЕМЫ

### **При краше:**

1. **AppDelegate.crashExceptionHandler()** перехватывает краш
2. Сохраняет в `UserDefaults["last_crash_log"]`
3. Сохраняет время в `UserDefaults["crash_timestamp"]`

### **При запуске:**

1. **VisualLogger** автоматически загружает логи из `UserDefaults["visual_logger_logs"]`
2. Логи отображаются на экране (в DEBUG режиме)
3. Можно получить через `getCrashLogs()`

### **Где сохраняются:**

- `UserDefaults["last_crash_log"]` - основной лог краша
- `UserDefaults["crash_timestamp"]` - время краша
- `UserDefaults["visual_logger_logs"]` - все логи VisualLogger (JSON)

---

## ✅ ЧЕКЛИСТ

- [ ] Запустить приложение в Xcode
- [ ] Открыть Debug Console (Cmd+Shift+Y)
- [ ] Выполнить `po getCrashLogs()`
- [ ] Скопировать вывод логов
- [ ] Проанализировать Exception Name и Reason
- [ ] Изучить Stack Trace
- [ ] Проверить VisualLogger логи до краша

---

**Если краш продолжается - пришлите вывод `getCrashLogs()` для анализа!**
