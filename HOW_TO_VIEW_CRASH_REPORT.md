# 🔍 КАК ПОСМОТРЕТЬ CRASH REPORT - ПОШАГОВАЯ ИНСТРУКЦИЯ

**Дата:** 2026-02-14  
**Версия:** Build 36

---

## 🎯 ЦЕЛЬ

Найти и проанализировать crash report приложения ALADDIN, чтобы понять причину краша на странице Settings.

---

## 📋 ШАГ 1: ОТКРЫТЬ DEVICES AND SIMULATORS

### Способ 1: Через меню Xcode

1. **Откройте Xcode**
2. В верхнем меню нажмите: **Window → Devices and Simulators**
   - Или используйте горячие клавиши: **⇧⌘2** (Shift + Command + 2)

### Способ 2: Через горячие клавиши

1. **Нажмите:** **⇧⌘2** (Shift + Command + 2)
2. Откроется окно "Devices and Simulators"

---

## 📋 ШАГ 2: ВЫБРАТЬ УСТРОЙСТВО

1. **В левой панели** найдите раздел **"Devices"** (Устройства)
2. **Найдите ваш iPhone** в списке устройств
3. **Нажмите на название вашего iPhone** (он должен быть подключен)

**Важно:**
- Устройство должно быть подключено через USB
- Устройство должно быть разблокировано
- На устройстве должно быть установлено приложение ALADDIN

---

## 📋 ШАГ 3: ОТКРЫТЬ DEVICE LOGS

1. **В правой части окна** найдите раздел **"Installed Apps"** (Установленные приложения)
2. **Найдите "ALADDIN"** в списке установленных приложений
3. **Нажмите на "ALADDIN"**
4. **Нажмите кнопку "View Device Logs"** (Просмотр логов устройства)

**Альтернативный способ:**
- В нижней части окна найдите кнопку **"Open Console"** или **"View Device Logs"**
- Нажмите на неё

---

## 📋 ШАГ 4: НАЙТИ CRASH REPORT

1. **Откроется новое окно** с логами устройства
2. **В левой панели** найдите раздел **"Crash Reports"** или **"All Logs"**
3. **Нажмите на "Crash Reports"**

### Как найти последний краш:

1. **Список будет отсортирован по дате** (самые новые сверху)
2. **Найдите записи с названием "ALADDIN"**
3. **Найдите самую последнюю запись** (самая новая дата и время)
4. **Обычно краш помечен красным цветом** или имеет иконку ⚠️

### Фильтрация:

1. **В поле поиска** (обычно справа вверху) введите: **"ALADDIN"**
2. Нажмите **Enter**
3. Останутся только логи, связанные с ALADDIN

---

## 📋 ШАГ 5: ОТКРЫТЬ CRASH REPORT

1. **Дважды нажмите** на запись о краше ALADDIN
2. **Или выберите запись и нажмите кнопку "Open"** (Открыть)

**Что откроется:**
- Детальный crash report со стеком вызовов
- Информация о потоке, в котором произошел краш
- Адреса памяти
- Названия функций и файлов

---

## 📋 ШАГ 6: АНАЛИЗИРОВАТЬ CRASH REPORT

### Что искать:

#### 1. **Exception Type** (Тип исключения):
- `EXC_BAD_ACCESS` - обращение к недействительной памяти
- `EXC_CRASH` - общий краш
- `SIGABRT` - аварийное завершение
- `SIGSEGV` - нарушение сегментации

#### 2. **Exception Subtype** (Подтип исключения):
- `KERN_INVALID_ADDRESS` - недействительный адрес памяти
- `KERN_PROTECTION_FAILURE` - нарушение защиты памяти

#### 3. **Crashed Thread** (Поток с крашем):
- Обычно это **Thread 0** или **Thread 1** (главный поток)
- Если краш в главном потоке - это проблема с UI

#### 4. **Stack Trace** (Стек вызовов):
- **Ищите упоминания:**
  - `SettingsScreen`
  - `NotificationManager`
  - `05_SettingsScreen.swift`
  - `NotificationManager.swift`
  - `ALADDINApp.swift`

#### 5. **Last Exception Backtrace** (Последний стек исключения):
- Это самая важная часть!
- Показывает, где именно произошел краш
- Ищите строки с `SettingsScreen`, `NotificationManager`

---

## 📋 ШАГ 7: НАЙТИ ПРИЧИНУ КРАША

### Типичные причины краша Settings:

#### 1. **Force Unwrap nil** (Принудительное разворачивание nil):
```
Fatal error: Unexpectedly found nil while unwrapping an Optional value
```
**Где искать:** В crash report ищите строки с `!` или `force unwrap`

#### 2. **Race Condition** (Состояние гонки):
```
Thread 1: EXC_BAD_ACCESS (code=1, address=0x...)
```
**Где искать:** Если краш происходит в разных потоках

#### 3. **Premature Access** (Преждевременный доступ):
```
Thread 1: signal SIGABRT
```
**Где искать:** Если краш происходит при доступе к `notificationSettings` до инициализации

#### 4. **Memory Issue** (Проблема с памятью):
```
EXC_BAD_ACCESS (KERN_INVALID_ADDRESS)
```
**Где искать:** Если краш происходит при обращении к освобожденной памяти

---

## 📋 ШАГ 8: СОХРАНИТЬ CRASH REPORT

1. **Выберите crash report**
2. **Нажмите правой кнопкой мыши** (или Control + клик)
3. **Выберите "Reveal in Finder"** (Показать в Finder)
4. **Или нажмите "Export"** (Экспорт) и сохраните файл

**Формат файла:**
- Обычно это файл `.crash` или `.txt`
- Название: `ALADDIN_YYYY-MM-DD_HHMMSS.crash`

---

## 📋 ШАГ 9: ПОДЕЛИТЬСЯ CRASH REPORT

### Если нужно отправить crash report:

1. **Скопируйте содержимое crash report**
2. **Или отправьте файл .crash**
3. **Особенно важны:**
   - Exception Type
   - Exception Subtype
   - Crashed Thread
   - Stack Trace (особенно строки с SettingsScreen)

---

## 💡 ВАЖНЫЕ ЗАМЕЧАНИЯ

### Если crash report не появляется:

1. **Убедитесь, что устройство подключено**
2. **Убедитесь, что приложение установлено**
3. **Попробуйте воспроизвести краш снова:**
   - Откройте приложение
   - Перейдите на страницу Settings
   - Дождитесь краша
   - Затем откройте Devices and Simulators

### Если краш не записывается:

1. **Проверьте настройки устройства:**
   - Settings → Privacy → Analytics & Improvements
   - Убедитесь, что "Share iPhone Analytics" включено

2. **Попробуйте запустить приложение через Xcode:**
   - Подключите устройство
   - Выберите устройство в Xcode
   - Запустите приложение (⌘R)
   - Перейдите на Settings
   - Если краш произойдет, он будет виден в консоли Xcode

---

## 🔍 ЧТО ДЕЛАТЬ С НАЙДЕННОЙ ИНФОРМАЦИЕЙ

### После анализа crash report:

1. **Найдите строку в коде**, где произошел краш
2. **Проверьте, что может быть nil**
3. **Проверьте race conditions**
4. **Проверьте порядок инициализации**

### Пример анализа:

**Если в crash report видно:**
```
Thread 1: EXC_BAD_ACCESS at 0x0000000000000000
SettingsScreen.body.getter
NotificationManager.notificationSettings.getter
```

**Это означает:**
- Краш происходит при доступе к `notificationSettings`
- Возможно, `notificationSettings` еще не инициализирован
- Нужно проверить порядок инициализации

---

## 📊 ПРИМЕР CRASH REPORT

```
Exception Type:  EXC_BAD_ACCESS (SIGSEGV)
Exception Subtype: KERN_INVALID_ADDRESS at 0x0000000000000000
Termination Signal: Segmentation fault: 11
Terminating Process: exc handler [ALADDIN]

Thread 0 Crashed:
0   libswiftCore.dylib              0x0000000181234567 _swift_retain_
1   ALADDIN                          0x0000000100123456 SettingsScreen.body.getter
2   ALADDIN                          0x0000000100123789 NotificationManager.notificationSettings.getter
3   ALADDIN                          0x0000000100123abc @objc NotificationManager.notificationSettings.getter
...
```

**Анализ:**
- Краш в `SettingsScreen.body.getter`
- При доступе к `NotificationManager.notificationSettings`
- Возможно, `notificationSettings` еще не инициализирован

---

**Дата:** 2026-02-14  
**Версия:** Build 36
