# 📱 КАК ПРОВЕРИТЬ ЛОГИ СТРАНИЦЫ НАСТРОЙКИ НА РЕАЛЬНОМ УСТРОЙСТВЕ

**Дата:** 2026-02-14  
**Цель:** Получить логи для отладки краша на реальном устройстве

---

## 🔍 СПОСОБЫ ПОЛУЧЕНИЯ ЛОГОВ

### 1. ✅ Xcode Console (САМЫЙ ПРОСТОЙ)

**Как использовать:**
1. Подключите iPhone/iPad к Mac через USB
2. Откройте Xcode
3. Выберите устройство в верхней панели (рядом с кнопкой Run)
4. Запустите приложение на устройстве (⌘R)
5. Откройте Console внизу Xcode (View > Debug Area > Activate Console или ⌘⇧Y)
6. Перейдите на страницу Настройки
7. Смотрите логи в реальном времени

**Фильтрация логов:**
- В поле поиска введите: `SettingsScreen` или `NotificationManager`
- Или используйте фильтр: `process:ALADDIN subsystem:com.aladdin`

**Что искать:**
- `🔴 SETTINGS:` - наши логи
- `❌` - ошибки
- `⚠️` - предупреждения
- `✅` - успешные операции

---

### 2. ✅ Device Logs в Xcode

**Как использовать:**
1. Подключите устройство к Mac
2. В Xcode: Window > Devices and Simulators (⇧⌘2)
3. Выберите ваше устройство слева
4. Нажмите "View Device Logs"
5. Найдите последние логи приложения
6. Отфильтруйте по имени приложения: `ALADDIN`

**Преимущества:**
- Можно посмотреть логи даже после краша
- Логи сохраняются на устройстве
- Можно экспортировать логи

---

### 3. ✅ Console.app (Системное приложение)

**Как использовать:**
1. Откройте приложение Console (в Applications > Utilities)
2. В левой панели выберите ваше устройство
3. В поле поиска введите: `ALADDIN` или `SettingsScreen`
4. Запустите приложение на устройстве
5. Перейдите на страницу Настройки
6. Смотрите логи в реальном времени

**Преимущества:**
- Более детальные логи системы
- Можно фильтровать по процессу, подсистеме, категории
- Можно сохранить логи в файл

---

### 4. ✅ TestFlight Crash Reports

**Как использовать:**
1. Откройте App Store Connect
2. Перейдите в TestFlight
3. Выберите ваше приложение
4. Перейдите в "Crashes"
5. Найдите последний краш
6. Скачайте crash report

**Что там будет:**
- Стек вызовов (stack trace)
- Строка кода, где произошел краш
- Информация о памяти
- Версия iOS и устройства

---

### 5. ✅ Xcode Organizer Crash Reports

**Как использовать:**
1. В Xcode: Window > Organizer (⇧⌘9)
2. Перейдите на вкладку "Crashes"
3. Выберите ваше приложение
4. Найдите последний краш
5. Откройте crash report

**Преимущества:**
- Автоматически символизированные логи (показывают строки кода)
- Можно увидеть точное место краша
- История всех крашей

---

## 🔧 ДОБАВЛЕНИЕ ЛОГИРОВАНИЯ В КОД

### Для отладки краша на странице Настройки:

**Добавьте логи в ключевые места:**

1. **В SettingsScreen.onAppear:**
```swift
.onAppear {
    print("🔴 SETTINGS: onAppear вызван")
    print("🔴 SETTINGS: notificationManager = \(notificationManager)")
    print("🔴 SETTINGS: notificationSettings = \(notificationManager.notificationSettings)")
    initializeNotifications()
    print("🔴 SETTINGS: initializeNotifications() завершен")
}
```

2. **В initializeNotifications():**
```swift
private func initializeNotifications() {
    print("🔴 SETTINGS: initializeNotifications() начат")
    print("🔴 SETTINGS: notificationManager.notificationSettings = \(notificationManager.notificationSettings)")
    // ...
    print("🔴 SETTINGS: initializeNotifications() завершен")
}
```

3. **В NotificationManager.init():**
```swift
private override init() {
    super.init()
    print("🔴 NOTIFICATION_MANAGER: init() начат")
    notificationCenter.delegate = self
    checkAuthorizationStatus()
    loadSettings()
    print("🔴 NOTIFICATION_MANAGER: init() завершен, notificationSettings = \(notificationSettings)")
}
```

4. **В loadSettings():**
```swift
private func loadSettings() {
    print("🔴 NOTIFICATION_MANAGER: loadSettings() начат")
    guard let data = userDefaults.data(forKey: settingsKey) else {
        notificationSettings = NotificationSettings()
        print("🔴 NOTIFICATION_MANAGER: loadSettings() - используем настройки по умолчанию")
        return
    }
    // ...
    print("🔴 NOTIFICATION_MANAGER: loadSettings() завершен, notificationSettings = \(notificationSettings)")
}
```

---

## 📋 ЧТО ИСКАТЬ В ЛОГАХ

### Признаки проблем:

1. **Race Condition:**
   - `initializeNotifications() начат` ДО `loadSettings() завершен`
   - Доступ к `notificationSettings` до его инициализации

2. **Threading Issues:**
   - Логи из разных потоков
   - Предупреждения о доступе не на main thread

3. **Nil Access:**
   - `fatal error: unexpectedly found nil`
   - `EXC_BAD_ACCESS`

4. **Timing Issues:**
   - Большая задержка между событиями
   - Неожиданный порядок выполнения

---

## 🎯 РЕКОМЕНДУЕМЫЙ ПОДХОД

### Для отладки краша:

1. **Добавьте логирование в код** (см. выше)
2. **Подключите устройство к Xcode**
3. **Запустите приложение через Xcode** (не через TestFlight)
4. **Откройте Console в Xcode**
5. **Перейдите на страницу Настройки**
6. **Смотрите логи в реальном времени**
7. **Если краш произошел - посмотрите последние логи перед крашем**

### Для тестирования в TestFlight:

1. **Добавьте логирование в код**
2. **Соберите и загрузите в TestFlight**
3. **Попросите тестировщика воспроизвести краш**
4. **После краша - посмотрите Crash Reports в App Store Connect**
5. **Или попросите тестировщика подключить устройство и посмотреть логи**

---

## 💡 СОВЕТЫ

1. **Используйте уникальные префиксы** для логов (например, `🔴 SETTINGS:`)
2. **Логируйте все ключевые точки** (начало/конец функций, доступ к свойствам)
3. **Логируйте значения переменных** перед их использованием
4. **Используйте разные уровни логирования:**
   - `🔴` - критичные операции
   - `⚠️` - предупреждения
   - `✅` - успешные операции
   - `ℹ️` - информационные сообщения

5. **В Production можно отключить логи:**
```swift
#if DEBUG
print("🔴 SETTINGS: ...")
#endif
```

---

**Дата:** 2026-02-14
