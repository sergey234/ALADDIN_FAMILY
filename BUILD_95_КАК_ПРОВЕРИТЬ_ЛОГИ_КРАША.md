# 🔍 BUILD 95: КАК ПРОВЕРИТЬ ЛОГИ ДЛЯ ДИАГНОСТИКИ КРАША

**Дата:** 2026-03-10  
**Версия сборки:** 95  
**Цель:** Диагностика краша при входе в приложение на главной странице

---

## 📱 СПОСОБ 1: ЧЕРЕЗ ПРИЛОЖЕНИЕ (САМЫЙ ПРОСТОЙ)

### ✅ Шаг 1: Откройте приложение ALADDIN

1. Запустите приложение на устройстве (TestFlight или локальная сборка)
2. Если приложение крашится при запуске, перезапустите его несколько раз

### ✅ Шаг 2: Откройте экран "Настройки"

1. После успешного запуска перейдите в **Настройки** (Settings)
2. Прокрутите вниз до раздела **"Диагностика"**
3. Найдите кнопку **"Диагностика (Crash Logs)"**
4. Нажмите на неё

### ✅ Шаг 3: Просмотрите логи

Откроется экран `CrashLogsView` с полными логами:

**Что вы увидите:**
- 🚨 **LAST CRASH LOG** - последний краш с полным stack trace
- ⏰ **CRASH TIME** - время краша
- 📋 **VISUAL LOGGER LOGS** - логи из VisualLogger (если включен)
- 📁 **CRASH LOGS FROM FILES** - логи из файлов на устройстве
- 🚨 **MEMORY WARNING** - предупреждения о памяти
- 🧠 **PRE-CRASH STATE** - состояние приложения перед крашем

### ✅ Шаг 4: Поделитесь логами

1. Нажмите кнопку **"Поделиться"**
2. Выберите способ отправки (Email, Messages, AirDrop и т.д.)
3. Отправьте логи себе для анализа

---

## 💻 СПОСОБ 2: ЧЕРЕЗ XCODE CONSOLE (В РЕАЛЬНОМ ВРЕМЕНИ)

### ✅ Шаг 1: Подключите устройство к Mac

1. Подключите iPhone к Mac через USB
2. Разблокируйте устройство
3. Доверьтесь компьютеру (если появится запрос)

### ✅ Шаг 2: Откройте Xcode Console

1. Откройте **Xcode**
2. Нажмите **⌘⇧Y** (Command + Shift + Y)
   - Или: **View → Debug Area → Activate Console**
3. В нижней панели откроется Console

### ✅ Шаг 3: Выберите устройство в Console

1. В левой панели Console найдите список устройств
2. Выберите ваш **iPhone**
3. В поле поиска введите: **ALADDIN** или **RecursionMonitor** или **StackSizeMonitor**

### ✅ Шаг 4: Запустите приложение

1. Запустите приложение на iPhone
2. Смотрите логи в реальном времени в Console

**Что искать в логах:**

#### 🔴 RecursionMonitor (мониторинг рекурсии):
```
🔴 [RecursionMonitor] threshold reached depth=80 at MainScreen.body (MainScreen.swift:123)
🔴 [RecursionMonitor] deep recursion depth=105 at MainScreen.body (MainScreen.swift:123)
```

#### 📚 StackSizeMonitor (мониторинг размера стека):
```
📚 [StackSizeMonitor] ALADDINApp.onAppear: stackSize=512 KB
📚 [StackSizeMonitor] MainThread - MainScreen.body: stackSize=1024 KB
```

#### ⚠️ MonitoredUserDefaults (медленные операции UserDefaults):
```
⚠️ [UserDefaults READ] slow 52.3ms key='subscription_expires_at_iso' at MainScreen.swift:45
⚠️ [UserDefaults WRITE] slow 67.8ms key='hasCompletedOnboarding' at ALADDINApp.swift:337
```

#### 💥 Crash Handler (обработчик крашей):
```
💥 CRASH LOG SAVED: 🚨 CRASH DETECTED!
Exception: NSException
Reason: Thread stack size exceeded due to excessive recursion
```

---

## 📂 СПОСОБ 3: ФАЙЛЫ НА УСТРОЙСТВЕ (ЧЕРЕЗ XCODE)

### ✅ Шаг 1: Откройте Devices and Simulators

1. В Xcode: **Window → Devices and Simulators**
   - Или нажмите **⇧⌘2** (Shift + Command + 2)

### ✅ Шаг 2: Выберите устройство

1. В левой панели найдите ваш **iPhone**
2. Нажмите на название устройства

### ✅ Шаг 3: Откройте приложение

1. В правой части окна найдите раздел **"Installed Apps"**
2. Найдите **"ALADDIN"** в списке
3. Нажмите на **"ALADDIN"**

### ✅ Шаг 4: Скачайте файлы с логами

1. Нажмите кнопку **"Download Container..."** (Скачать контейнер)
2. Выберите место для сохранения
3. Откройте скачанный контейнер

**Файлы с логами находятся в:**
```
Container/AppData/Documents/
├── crash_log.txt                    # Основной лог краша
├── crash_stack_trace.txt            # Stack trace краша
├── memory_warning_log.txt            # Логи предупреждений о памяти
└── pre_crash_state.json             # Состояние перед крашем
```

---

## 🔍 СПОСОБ 4: ЧЕРЕЗ CONSOLE.APP (СИСТЕМНОЕ ПРИЛОЖЕНИЕ)

### ✅ Шаг 1: Откройте Console.app

1. Нажмите **⌘Space** (Command + Space)
2. Введите: **Console**
3. Нажмите Enter

### ✅ Шаг 2: Выберите устройство

1. В левой панели найдите раздел **"Devices"**
2. Найдите ваш **iPhone**
3. Нажмите на устройство

### ✅ Шаг 3: Фильтруйте логи

1. В поле поиска введите: **ALADDIN**
2. Запустите приложение на устройстве
3. Смотрите логи в реальном времени

**Полезные фильтры:**
- `ALADDIN` - все логи приложения
- `RecursionMonitor` - логи рекурсии
- `StackSizeMonitor` - логи размера стека
- `CRASH` - логи крашей
- `MEMORY WARNING` - предупреждения о памяти

---

## 📊 ЧТО ИСКАТЬ В ЛОГАХ ДЛЯ ДИАГНОСТИКИ КРАША

### 🔴 1. РЕКУРСИЯ (RecursionMonitor)

**Признаки проблемы:**
```
🔴 [RecursionMonitor] threshold reached depth=80
🔴 [RecursionMonitor] deep recursion depth=105
```

**Что это значит:**
- Глубина рекурсии превысила порог (80 вызовов)
- Возможна бесконечная рекурсия в `@AppStorage` → `UserDefaults` → `@AppStorage`

**Где искать:**
- `MainScreen.swift` - проверьте computed properties и `.onChange()`
- `ALADDINApp.swift` - проверьте `.id()` модификаторы
- Любые файлы с `@AppStorage` и `UserDefaults`

---

### 📚 2. РАЗМЕР СТЕКА (StackSizeMonitor)

**Признаки проблемы:**
```
📚 [StackSizeMonitor] MainThread - MainScreen.body: stackSize=1024 KB
📚 [StackSizeMonitor] MainThread - MainScreen.body: stackSize=2048 KB
```

**Что это значит:**
- Размер стека растет (норма: ~512 KB, проблема: >1024 KB)
- Возможна рекурсия или слишком глубокий стек вызовов

**Где искать:**
- Функции с большим количеством вложенных вызовов
- Computed properties, которые вызывают другие computed properties

---

### ⚠️ 3. МЕДЛЕННЫЕ ОПЕРАЦИИ UserDefaults (MonitoredUserDefaults)

**Признаки проблемы:**
```
⚠️ [UserDefaults READ] slow 52.3ms key='subscription_expires_at_iso'
⚠️ [UserDefaults WRITE] slow 67.8ms key='hasCompletedOnboarding'
```

**Что это значит:**
- Операции с `UserDefaults` занимают >50ms (норма: <10ms)
- Возможна рекурсия или блокировка в `UserDefaults`

**Где искать:**
- Файлы с частыми обращениями к `UserDefaults`
- `@AppStorage` свойства, которые читаются в `body` view

---

### 💥 4. CRASH HANDLER (Обработчик крашей)

**Признаки проблемы:**
```
💥 CRASH LOG SAVED: 🚨 CRASH DETECTED!
Exception: NSException
Reason: Thread stack size exceeded due to excessive recursion
```

**Что это значит:**
- Произошел краш из-за рекурсии
- Stack trace покажет точное место краша

**Где искать:**
- Stack trace в логе покажет файл и строку краша
- Обычно это `MainScreen.swift` или `ALADDINApp.swift`

---

### 🧠 5. PRE-CRASH STATE (Состояние перед крашем)

**Что содержит:**
```json
{
  "memory_usage_mb": 245.3,
  "active_threads": 12,
  "timestamp": 1709999999.0,
  "current_screen": "main",
  "navigation_stack": ["onboarding", "main"]
}
```

**Что это значит:**
- Состояние приложения за 5 секунд до краша
- Помогает понять, что происходило перед крашем

**Что проверить:**
- `memory_usage_mb` - если >500 MB, возможна утечка памяти
- `active_threads` - если >20, возможна проблема с потоками
- `current_screen` - на каком экране произошел краш

---

## 🎯 ПОШАГОВЫЙ ПЛАН ДИАГНОСТИКИ

### Шаг 1: Запустите приложение и воспроизведите краш

1. Запустите приложение на устройстве
2. Дождитесь краша при входе на главную страницу
3. Перезапустите приложение

### Шаг 2: Откройте CrashLogsView в приложении

1. Перейдите в **Настройки → Диагностика (Crash Logs)**
2. Просмотрите все логи
3. Поделитесь логами себе (кнопка "Поделиться")

### Шаг 3: Проверьте логи в Xcode Console

1. Подключите устройство к Mac
2. Откройте Xcode Console (⌘⇧Y)
3. Запустите приложение и смотрите логи в реальном времени
4. Ищите сообщения от `RecursionMonitor`, `StackSizeMonitor`, `MonitoredUserDefaults`

### Шаг 4: Скачайте файлы с логами

1. Откройте **Devices and Simulators** (⇧⌘2)
2. Выберите устройство → ALADDIN → **Download Container**
3. Откройте файлы в `Documents/`:
   - `crash_log.txt`
   - `crash_stack_trace.txt`
   - `pre_crash_state.json`

### Шаг 5: Проанализируйте логи

**Проверьте:**
1. ✅ Есть ли сообщения от `RecursionMonitor` о превышении порога?
2. ✅ Какой размер стека перед крашем (`StackSizeMonitor`)?
3. ✅ Есть ли медленные операции `UserDefaults` (`MonitoredUserDefaults`)?
4. ✅ Какой stack trace в `crash_stack_trace.txt`?
5. ✅ Какое состояние приложения в `pre_crash_state.json`?

---

## 📋 ЧЕКЛИСТ ДЛЯ АНАЛИЗА ЛОГОВ

- [ ] Проверен `crash_log.txt` - найден последний краш
- [ ] Проверен `crash_stack_trace.txt` - найден stack trace
- [ ] Проверены логи `RecursionMonitor` - найдена глубина рекурсии
- [ ] Проверены логи `StackSizeMonitor` - найден размер стека
- [ ] Проверены логи `MonitoredUserDefaults` - найдены медленные операции
- [ ] Проверен `pre_crash_state.json` - найдено состояние перед крашем
- [ ] Проверены логи в Xcode Console - найдены сообщения в реальном времени
- [ ] Определен файл и строка краша из stack trace
- [ ] Определена причина краша (рекурсия, память, поток и т.д.)

---

## 🔧 БЫСТРЫЙ ДОСТУП К ЛОГАМ

### В приложении:
**Настройки → Диагностика (Crash Logs)**

### В Xcode:
**⌘⇧Y** → Выберите устройство → Фильтр: `ALADDIN`

### Через Devices and Simulators:
**⇧⌘2** → Устройство → ALADDIN → **Download Container** → `Documents/`

### Через Console.app:
**⌘Space** → `Console` → Устройство → Фильтр: `ALADDIN`

---

## 📞 ЕСЛИ НУЖНА ПОМОЩЬ

Если логи не помогают найти причину краша, соберите:
1. ✅ Полный `crash_log.txt`
2. ✅ Полный `crash_stack_trace.txt`
3. ✅ `pre_crash_state.json`
4. ✅ Скриншоты логов из Xcode Console
5. ✅ Описание шагов для воспроизведения краша

Отправьте все это для анализа!
