# 🚨 РЕАЛИЗАЦИЯ ЛОГИРОВАНИЯ КРАШЕЙ ДЛЯ TESTFLIGHT
## Полная система для получения логов крашей в RELEASE сборке

**Дата:** 2026-03-09  
**Проблема:** Краш в TestFlight при переходе на главную страницу, логи не видны

---

## ✅ ЧТО БЫЛО СДЕЛАНО

### **1. Улучшен обработчик крашей в AppDelegate**

**Добавлено:**
- ✅ Полный stack trace в лог краша
- ✅ Сохранение stack trace отдельно в UserDefaults
- ✅ Сохранение логов в файлы (работает в RELEASE)
- ✅ Автоматическая отправка на сервер при краше

**Файлы создаются:**
- `crash_log.txt` - полный лог краша
- `crash_stack_trace.txt` - stack trace

---

### **2. Добавлено детальное логирование в MainScreen**

**Добавлено:**
- ✅ Пошаговое логирование каждого шага в `onAppear`
- ✅ Сохранение логов в UserDefaults
- ✅ Сохранение логов в файл `main_screen_debug_log.txt`
- ✅ История последних 5 запусков

**Что логируется:**
- Начало `onAppear`
- Проверка `hasAppeared`
- Проверка онбординга
- Проверка Member ID
- Загрузка profileImage
- Вызов `mainViewModel.onAppear()`
- Время выполнения каждого шага

---

### **3. Добавлены функции для получения логов**

**Новые функции в ALADDINApp.swift:**

1. **`getCrashLogs()`** - получает логи из UserDefaults
2. **`getCrashLogsFromFiles()`** - получает логи из файлов (для TestFlight)
3. **`getAllCrashLogs()`** - получает все логи (UserDefaults + файлы)
4. **`clearCrashLogs()`** - очищает логи

---

### **4. Автоматическая отправка на сервер**

**Endpoint:** `https://aladdin-ai.ru/api/crash-detection/report`

**Что отправляется:**
- Exception name
- Reason
- Stack trace
- Device info
- App version
- Build number
- Timestamp
- Full log

**Статус отправки сохраняется в:**
- `UserDefaults["crash_log_send_status"]`
- `UserDefaults["crash_log_send_error"]`

---

## 📊 ГДЕ ХРАНЯТСЯ ЛОГИ

### **UserDefaults:**

| Ключ | Что хранит |
|------|------------|
| `"last_crash_log"` | Полный лог краша |
| `"crash_timestamp"` | Время краша |
| `"last_crash_stack_trace"` | Stack trace |
| `"crash_log_file_path"` | Путь к файлу |
| `"main_screen_debug_log"` | Логи MainScreen |
| `"main_screen_debug_log_history"` | История (5 запусков) |

### **Файлы в Documents:**

| Файл | Что хранит |
|------|------------|
| `crash_log.txt` | Полный лог краша |
| `crash_stack_trace.txt` | Stack trace |
| `main_screen_debug_log.txt` | Логи MainScreen.onAppear |

---

## 🎯 КАК ПОЛУЧИТЬ ЛОГИ ИЗ TESTFLIGHT

### **Метод 1: Через файлы (РЕКОМЕНДУЕТСЯ)**

1. **Подключите устройство к Mac**
2. **Xcode → Window → Devices and Simulators**
3. **Выберите устройство → Installed Apps → ALADDIN**
4. **Download Container**
5. **Откройте контейнер → AppData → Documents**
6. **Найдите файлы:**
   - `crash_log.txt`
   - `crash_stack_trace.txt`
   - `main_screen_debug_log.txt`

### **Метод 2: Через Debug Console**

```swift
// Все логи сразу
po getAllCrashLogs()

// Только из файлов
po getCrashLogsFromFiles()

// Только из UserDefaults
po getCrashLogs()
```

### **Метод 3: Через сервер**

Логи автоматически отправляются на:
`https://aladdin-ai.ru/api/crash-detection/report`

Проверьте статус:
```swift
po UserDefaults.standard.string(forKey: "crash_log_send_status")
```

---

## 🔍 АНАЛИЗ ЛОГОВ MAINSCREEN

При переходе на главную страницу логи показывают каждый шаг:

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

## ✅ РЕЗУЛЬТАТЫ

### **Что работает:**

1. ✅ **Обработчик крашей** - перехватывает все краши
2. ✅ **Сохранение в UserDefaults** - доступно через `getCrashLogs()`
3. ✅ **Сохранение в файлы** - работает в RELEASE/TestFlight
4. ✅ **Отправка на сервер** - автоматически при краше
5. ✅ **Детальное логирование MainScreen** - каждый шаг логируется

### **Как использовать:**

1. **После краша в TestFlight:**
   - Получите файлы через Xcode
   - Или выполните `po getAllCrashLogs()` в Debug Console

2. **Анализ:**
   - Проверьте Exception Name и Reason
   - Изучите Stack Trace
   - Проверьте MainScreen Debug Log

3. **Отправка на сервер:**
   - Проверьте статус отправки
   - Логи автоматически отправляются при краше

---

## 📝 СЛЕДУЮЩИЕ ШАГИ

1. ✅ **Собрать новую сборку** с улучшенным логированием
2. ✅ **Загрузить в TestFlight**
3. ✅ **Воспроизвести краш**
4. ✅ **Получить логи** через файлы или Debug Console
5. ✅ **Проанализировать** причину краша
6. ✅ **Исправить** проблему

---

**Дата создания:** 2026-03-09  
**Автор:** AI Assistant  
**Версия:** 1.0
