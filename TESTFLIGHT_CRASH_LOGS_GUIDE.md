# 🚨 КАК ПОЛУЧИТЬ ЛОГИ КРАШЕЙ ИЗ TESTFLIGHT
## Инструкция для получения логов когда приложение крашится в TestFlight

**Проблема:** В TestFlight краш происходит при переходе на главную страницу, но логи не видны в консоли.

---

## 🎯 РЕШЕНИЕ: ТРИ СПОСОБА ПОЛУЧЕНИЯ ЛОГОВ

### **Способ 1: Через Xcode (если устройство подключено)**

1. **Подключите устройство к Mac**
2. **Откройте Xcode → Window → Devices and Simulators**
3. **Выберите ваше устройство**
4. **Нажмите "View Device Logs"**
5. **Найдите последний краш вашего приложения**
6. **Откройте crash report**

**Или:**

1. **Запустите приложение через Xcode на устройстве**
2. **Откройте Debug Console (Cmd+Shift+Y)**
3. **Выполните:**
   ```swift
   po getAllCrashLogs()
   ```

---

### **Способ 2: Через файлы в Documents (РЕКОМЕНДУЕТСЯ)**

Логи автоматически сохраняются в файлы при краше:

**Файлы:**
- `crash_log.txt` - полный лог краша
- `crash_stack_trace.txt` - stack trace
- `main_screen_debug_log.txt` - логи MainScreen.onAppear

**Как получить:**

#### **Вариант A: Через Xcode**

1. **Подключите устройство**
2. **Window → Devices and Simulators**
3. **Выберите устройство → Installed Apps → ALADDIN**
4. **Нажмите "Download Container"**
5. **Откройте контейнер → AppData → Documents**
6. **Найдите файлы:**
   - `crash_log.txt`
   - `crash_stack_trace.txt`
   - `main_screen_debug_log.txt`

#### **Вариант B: Через Debug Console**

```swift
po getCrashLogsFromFiles()
```

Это покажет содержимое всех файлов с логами.

---

### **Способ 3: Через отправку на сервер (АВТОМАТИЧЕСКИ)**

При краше логи **автоматически отправляются на сервер**:

**Endpoint:** `https://aladdin-ai.ru/api/crash-detection/report`

**Что отправляется:**
- Exception name
- Reason
- Stack trace
- Device info
- App version
- Full log

**Проверка статуса отправки:**

В Debug Console:
```swift
po UserDefaults.standard.string(forKey: "crash_log_send_status")
po UserDefaults.standard.string(forKey: "crash_log_send_error")
```

---

## 📋 ЧТО СОХРАНЯЕТСЯ ПРИ КРАШЕ

### **1. UserDefaults:**

| Ключ | Что хранит |
|------|------------|
| `"last_crash_log"` | Полный лог краша |
| `"crash_timestamp"` | Время краша |
| `"last_crash_stack_trace"` | Stack trace |
| `"crash_log_file_path"` | Путь к файлу crash_log.txt |
| `"crash_stack_trace_file_path"` | Путь к файлу crash_stack_trace.txt |
| `"crash_log_send_status"` | Статус отправки на сервер |
| `"crash_log_send_error"` | Ошибка отправки (если была) |

### **2. Файлы в Documents:**

| Файл | Что хранит |
|------|------------|
| `crash_log.txt` | Полный лог краша |
| `crash_stack_trace.txt` | Stack trace |
| `main_screen_debug_log.txt` | Логи MainScreen.onAppear |

### **3. Отправка на сервер:**

Автоматически отправляется на `/api/crash-detection/report`

---

## 🔍 АНАЛИЗ ЛОГОВ MAINSCREEN

При переходе на главную страницу сохраняются логи каждого шага:

```
🔍 MainScreen.onAppear START - 2026-03-09 22:08:05
✅ hasAppeared установлен в true
✅ logger.screenLoad вызван
✅ onboardingDone = true
✅ memberId = MEM_219A583F
✅ Member ID found: MEM_219A583F
✅ Загрузка profileImage...
✅ profileImage загружен
✅ Вызов mainViewModel.onAppear()...
✅ mainViewModel.onAppear() завершен
✅ MainScreen.onAppear COMPLETE - Duration: 0.123s
```

**Если краш происходит:**
- Последняя строка покажет где именно произошел краш
- Можно увидеть на каком шаге остановилось выполнение

---

## ✅ БЫСТРАЯ ИНСТРУКЦИЯ

### **Шаг 1: После краша в TestFlight**

1. Подключите устройство к Mac
2. Откройте Xcode → Window → Devices and Simulators
3. Выберите устройство → Installed Apps → ALADDIN
4. Download Container
5. Откройте контейнер → AppData → Documents
6. Найдите `crash_log.txt` и `main_screen_debug_log.txt`

### **Шаг 2: Или через Debug Console**

```swift
// Все логи сразу
po getAllCrashLogs()

// Только из файлов
po getCrashLogsFromFiles()

// Только из UserDefaults
po getCrashLogs()
```

### **Шаг 3: Проверка отправки на сервер**

```swift
po UserDefaults.standard.string(forKey: "crash_log_send_status")
```

---

## 🎯 ЧТО ИСКАТЬ В ЛОГАХ

### **1. Exception Name:**
- `NSInvalidArgumentException` - неверный аргумент
- `NSRangeException` - выход за границы
- `EXC_BAD_ACCESS` - доступ к памяти
- `EXC_CRASH` - общий краш

### **2. Exception Reason:**
- Точное описание проблемы
- Часто содержит название метода

### **3. Stack Trace:**
- Показывает последовательность вызовов
- Первые строки - место краша
- Ищите `MainScreen`, `MainViewModel`, `ALADDINApp`

### **4. MainScreen Debug Log:**
- Показывает на каком шаге произошел краш
- Последняя строка - место остановки

---

## 📊 ПРИМЕР АНАЛИЗА

### **Если краш в MainScreen.onAppear:**

```
🔍 MainScreen.onAppear START
✅ hasAppeared установлен в true
✅ logger.screenLoad вызван
✅ onboardingDone = true
✅ memberId = MEM_219A583F
✅ Загрузка profileImage...
[КРАШ ЗДЕСЬ]
```

**Вывод:** Краш происходит при загрузке `profileImage` или после.

### **Если краш в mainViewModel.onAppear:**

```
✅ profileImage загружен
✅ Вызов mainViewModel.onAppear()...
[КРАШ ЗДЕСЬ]
```

**Вывод:** Краш происходит в `MainViewModel.onAppear()`.

---

## 🛠️ ДОПОЛНИТЕЛЬНЫЕ ИНСТРУМЕНТЫ

### **1. Xcode Organizer**

**Window → Organizer → Crashes**
- Показывает все краши из TestFlight
- Автоматически собирается Apple
- Доступен через несколько часов после краша

### **2. Console.app**

1. Откройте **Console.app** на Mac
2. Выберите ваше устройство
3. Ищите логи с префиксом "ALADDIN" или "CRASH"

### **3. Device Logs (на устройстве)**

**Settings → Privacy → Analytics & Improvements → Analytics Data**
- Найдите записи с префиксом "ALADDIN"
- Откройте последнюю запись

---

## ✅ ЧЕКЛИСТ

- [ ] Проверить файлы в Documents через Xcode
- [ ] Выполнить `po getAllCrashLogs()` в Debug Console
- [ ] Проверить статус отправки на сервер
- [ ] Проверить Xcode Organizer → Crashes
- [ ] Проанализировать Exception Name и Reason
- [ ] Изучить Stack Trace
- [ ] Проверить MainScreen Debug Log

---

**ВАЖНО:** Логи сохраняются автоматически при каждом краше. Проверьте файлы или выполните `getAllCrashLogs()` для получения всех логов!
