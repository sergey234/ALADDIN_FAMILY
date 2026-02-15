# 🔍 КАК ОТФИЛЬТРОВАТЬ ЛОГИ - ТОЛЬКО ALADDIN

**Проблема:** В консоли много системных логов (wifid, SpringBoard, contextstored и т.д.)  
**Решение:** Настроить фильтры, чтобы видеть только логи приложения ALADDIN

---

## 🎯 СПОСОБ 1: ФИЛЬТР ПО ПРОЦЕССУ (САМЫЙ ПРОСТОЙ)

### Шаг 1: Откройте Console в Xcode

1. В Xcode откройте Console (⌘⇧Y или View → Debug Area → Activate Console)
2. Убедитесь, что вы на вкладке **Console** (не Debugger)

### Шаг 2: Настройте фильтр по процессу

1. В консоли найдите панель фильтров (обычно справа вверху консоли)
2. Найдите выпадающий список **"Process"** или **"Процесс"**
3. **Нажмите на список**
4. Выберите **"ALADDIN"** из списка

**Что произойдет:**
- В консоли останутся только логи процесса ALADDIN
- Все системные логи (wifid, SpringBoard и т.д.) будут скрыты
- Вы увидите только логи вашего приложения

---

## 🎯 СПОСОБ 2: ФИЛЬТР ПО ТЕКСТУ (ДЛЯ НАШИХ ЛОГОВ)

### Шаг 1: Откройте Console

1. В Xcode откройте Console (⌘⇧Y)

### Шаг 2: Введите фильтр в поле поиска

1. В консоли найдите поле поиска (обычно справа вверху)
2. **Нажмите в поле поиска**
3. Введите один из фильтров:

**Вариант 1: Все наши логи**
```
🔴
```

**Вариант 2: Только логи Settings**
```
🔴 SETTINGS
```

**Вариант 3: Только логи NotificationManager**
```
🔴 NOTIFICATION_MANAGER
```

**Вариант 4: Все логи ALADDIN (включая ошибки)**
```
ALADDIN
```

4. Нажмите **Enter**

**Что произойдет:**
- В консоли останутся только строки, которые содержат введенный текст
- Все остальные логи будут скрыты

---

## 🎯 СПОСОБ 3: КОМБИНИРОВАННЫЙ ФИЛЬТР (САМЫЙ ТОЧНЫЙ)

### Шаг 1: Откройте Console

1. В Xcode откройте Console (⌘⇧Y)

### Шаг 2: Настройте фильтр по процессу

1. В панели фильтров выберите **Process: ALADDIN**

### Шаг 3: Добавьте текстовый фильтр

1. В поле поиска введите: `🔴`
2. Нажмите **Enter**

**Результат:**
- Только логи процесса ALADDIN
- Только наши логи с префиксом `🔴`
- Все системные логи скрыты

---

## 🎯 СПОСОБ 4: ФИЛЬТР ПО SUBSYSTEM (ПРОДВИНУТЫЙ)

### Шаг 1: Откройте Console

1. В Xcode откройте Console (⌘⇧Y)

### Шаг 2: Настройте фильтр по subsystem

1. В панели фильтров найдите поле **"Subsystem"** или **"Подсистема"**
2. Введите: `family.aladdin.ios` (это bundle identifier вашего приложения)
3. Нажмите **Enter**

**Результат:**
- Только логи вашего приложения
- Все системные логи скрыты

---

## 📋 ЧТО ИСКАТЬ В ОТФИЛЬТРОВАННЫХ ЛОГАХ

### ✅ Правильные логи (что должно быть):

```
🔴 NOTIFICATION_MANAGER: init() начат
🔴 NOTIFICATION_MANAGER: loadSettings() начат
🔴 NOTIFICATION_MANAGER: loadSettings() завершен, notificationSettings = ...
🔴 NOTIFICATION_MANAGER: init() завершен, notificationSettings = ...
🔴 SETTINGS: onAppear вызван
🔴 SETTINGS: notificationManager = ...
🔴 SETTINGS: notificationSettings = ...
🔴 SETTINGS: initializeNotifications() начат
🔴 SETTINGS: initializeNotifications() завершен
```

### ❌ Проблемы (что указывает на краш):

1. **Логи не появляются:**
   - Приложение крашится ДО того, как логи записываются
   - Нужно смотреть crash report

2. **Неправильный порядок:**
   - `initializeNotifications() начат` ДО `loadSettings() завершен`
   - Это race condition

3. **Ошибки:**
   - `fatal error: unexpectedly found nil`
   - `EXC_BAD_ACCESS`
   - `Thread 1: signal SIGABRT`

---

## 🔍 АНАЛИЗ ВАШИХ ЛОГОВ

### Что я вижу в ваших логах:

**Связанные с ALADDIN:**
```
16:04:54.949969+0400	kernel	Sandbox: ALADDIN(12666) deny(1) sysctl-read kern.bootargs
16:04:55.138479+0400	ALADDIN	⚠️ HTTP Error: 404 - https://aladdin-ai.ru/api/user/profile
16:04:55.138514+0400	ALADDIN	❌ HTTP Error 404: https://aladdin-ai.ru/api/user/profile - Not Found
16:05:00.647417+0400	kernel	Sandbox: ALADDIN(12668) deny(1) sysctl-read kern.bootargs
16:05:00.856319+0400	ALADDIN	⚠️ HTTP Error: 404 - https://aladdin-ai.ru/api/user/profile
16:05:00.856435+0400	ALADDIN	❌ HTTP Error 404: https://aladdin-ai.ru/api/user/profile - Not Found
```

**Связанные с приложением (bundle identifier):**
```
family.aladdin.ios-1BAB9945-9E67-410B-8505-B10FCF2E75C4
```

**Проблема:**
- ❌ **НЕТ логов с `🔴 SETTINGS:` или `🔴 NOTIFICATION_MANAGER:`**
- Это означает, что приложение крашится ДО того, как логи записываются
- Или приложение не доходит до страницы Settings

---

## 💡 ЧТО ДЕЛАТЬ

### Вариант 1: Добавить логи раньше

Добавьте логи в самое начало `body`:

```swift
var body: some View {
    let _ = print("🔴 SETTINGS: body вычисляется")
    settingsContent()
        .onAppear {
            print("🔴 SETTINGS: onAppear вызван")
            // ...
        }
}
```

### Вариант 2: Проверить crash report

1. В Xcode: Window → Devices and Simulators (⇧⌘2)
2. Выберите iPhone
3. Нажмите "View Device Logs"
4. Найдите последний краш ALADDIN
5. Откройте crash report

### Вариант 3: Использовать системные логи

В ваших логах есть упоминания:
- `ReportCrash` - система создает crash report
- `family.aladdin.ios` - bundle identifier
- `Scene update failed` - ошибка обновления сцены

Это может указывать на краш при создании/обновлении View.

---

## 📊 ИНСТРУКЦИЯ ПО ФИЛЬТРАЦИИ В XCODE CONSOLE

### Пошагово:

1. **Откройте Console** (⌘⇧Y)

2. **Найдите панель фильтров** (обычно справа вверху консоли)

3. **Настройте фильтры:**
   - **Process:** выберите `ALADDIN`
   - **Search:** введите `🔴` или `ALADDIN`

4. **Нажмите Enter**

5. **Результат:** Только логи ALADDIN

---

**Дата:** 2026-02-14  
**Версия:** Build 36
