# 🔍 ГДЕ СМОТРЕТЬ CRASH REPORT - ПРОСТАЯ ИНСТРУКЦИЯ

**Дата:** 2026-02-14  
**Версия:** Build 36

---

## 🎯 СПОСОБ 1: ЧЕРЕЗ XCODE (САМЫЙ ПРОСТОЙ)

### Шаг 1: Откройте Devices and Simulators

1. **Откройте Xcode**
2. В верхнем меню нажмите: **Window → Devices and Simulators**
   - **Или нажмите:** **⇧⌘2** (Shift + Command + 2)

### Шаг 2: Выберите устройство

1. **В левой панели** найдите ваш iPhone
2. **Нажмите на название устройства**

### Шаг 3: Откройте Device Logs

1. **В правой части окна** найдите раздел **"Installed Apps"**
2. **Найдите "ALADDIN"** в списке
3. **Нажмите на "ALADDIN"**
4. **Нажмите кнопку "View Device Logs"** (Просмотр логов устройства)

**Или:**
- В нижней части окна найдите кнопку **"Open Console"**
- Нажмите на неё

### Шаг 4: Найдите Crash Report

1. **Откроется новое окно** с логами
2. **В левой панели** найдите **"Crash Reports"**
3. **Нажмите на "Crash Reports"**
4. **Найдите последний краш ALADDIN** (самая новая дата)
5. **Дважды нажмите** на запись о краше

---

## 🎯 СПОСОБ 2: ЧЕРЕЗ CONSOLE.APP (НА МАКЕ)

### Шаг 1: Откройте Console.app

1. **Нажмите ⌘Space** (Command + Space)
2. **Введите:** `Console`
3. **Нажмите Enter**

### Шаг 2: Выберите устройство

1. **В левой панели** найдите раздел **"Devices"**
2. **Найдите ваш iPhone**
3. **Нажмите на устройство**

### Шаг 3: Найдите Crash Reports

1. **В левой панели** под устройством найдите **"Crash Reports"**
2. **Нажмите на "Crash Reports"**
3. **Найдите "ALADDIN"** в списке
4. **Дважды нажмите** на последний краш

---

## 🎯 СПОСОБ 3: ЧЕРЕЗ TESTFLIGHT (ЕСЛИ ПРИЛОЖЕНИЕ В TESTFLIGHT)

### Шаг 1: Откройте App Store Connect

1. Перейдите на: **https://appstoreconnect.apple.com**
2. Войдите в аккаунт

### Шаг 2: Найдите приложение

1. **Нажмите "My Apps"**
2. **Найдите "ALADDIN"**
3. **Нажмите на приложение**

### Шаг 3: Откройте Crash Reports

1. **В левом меню** найдите **"TestFlight"**
2. **Нажмите "TestFlight"**
3. **Нажмите "Crashes"** (Краши)
4. **Найдите последний краш**

---

## 🎯 СПОСОБ 4: НА УСТРОЙСТВЕ (iOS)

### Шаг 1: Откройте Settings

1. **На iPhone** откройте **Settings** (Настройки)

### Шаг 2: Найдите Analytics

1. **Прокрутите вниз** и найдите **"Privacy & Security"** (Конфиденциальность и безопасность)
2. **Нажмите** на него
3. **Найдите "Analytics & Improvements"** (Аналитика и улучшения)
4. **Нажмите** на него

### Шаг 3: Откройте Analytics Data

1. **Нажмите "Analytics Data"** (Данные аналитики)
2. **Найдите "ALADDIN"** в списке
3. **Нажмите** на последний файл (самая новая дата)

**Примечание:** Это покажет только базовую информацию, не полный crash report.

---

## 📋 БЫСТРАЯ ИНСТРУКЦИЯ (САМЫЙ ПРОСТОЙ СПОСОБ)

### 1. В Xcode нажмите: **⇧⌘2**

### 2. Выберите ваш iPhone

### 3. Нажмите **"View Device Logs"**

### 4. Найдите **"Crash Reports"**

### 5. Найдите последний краш **"ALADDIN"**

### 6. Дважды нажмите на него

---

## 💡 ЧТО ИСКАТЬ В CRASH REPORT

### Важная информация:

1. **Exception Type** (Тип исключения):
   - `EXC_BAD_ACCESS` - обращение к недействительной памяти
   - `SIGABRT` - аварийное завершение

2. **Crashed Thread** (Поток с крашем):
   - Обычно **Thread 0** или **Thread 1** (главный поток)

3. **Stack Trace** (Стек вызовов):
   - Ищите упоминания: `SettingsScreen`, `NotificationManager`

4. **Last Exception Backtrace**:
   - Показывает, где именно произошел краш
   - Самая важная часть!

---

## 🔍 ЕСЛИ CRASH REPORT НЕ НАХОДИТСЯ

### Проблема: Нет crash report

**Решение:**

1. **Убедитесь, что устройство подключено**
2. **Убедитесь, что приложение установлено**
3. **Попробуйте воспроизвести краш снова:**
   - Откройте приложение
   - Перейдите на Settings
   - Дождитесь краша
   - Затем откройте Devices and Simulators

4. **Проверьте настройки устройства:**
   - Settings → Privacy → Analytics & Improvements
   - Убедитесь, что "Share iPhone Analytics" включено

---

## 📊 ПРИМЕР: КАК ВЫГЛЯДИТ CRASH REPORT

```
Exception Type:  EXC_BAD_ACCESS (SIGSEGV)
Exception Subtype: KERN_INVALID_ADDRESS at 0x0000000000000000
Termination Signal: Segmentation fault: 11
Terminating Process: exc handler [ALADDIN]

Thread 0 Crashed:
0   libswiftCore.dylib              0x0000000181234567 _swift_retain_
1   ALADDIN                          0x0000000100123456 SettingsScreen.body.getter
2   ALADDIN                          0x0000000100123789 NotificationManager.notificationSettings.getter
```

**Это показывает:**
- Краш в `SettingsScreen.body.getter`
- При доступе к `NotificationManager.notificationSettings`
- Возможно, `notificationSettings` еще не инициализирован

---

**Дата:** 2026-02-14  
**Версия:** Build 36
