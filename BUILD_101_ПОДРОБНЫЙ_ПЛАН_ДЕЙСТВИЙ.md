# 📋 BUILD 101: ПОДРОБНЫЙ ПЛАН ДЕЙСТВИЙ ПО ИСПРАВЛЕНИЮ КРАША ТУМБЛЕРОВ

**Дата создания:** 2026-03-10  
**Build:** 101 → 102  
**Статус:** 📋 **ПЛАН СОСТАВЛЕН**

---

## 🎯 ЦЕЛЬ

Исправить краш при переключении тумблеров на реальном устройстве, вызванный рекурсией в `Dictionary.resize` в background thread.

---

## 📊 ПРОБЛЕМА

### Симптомы:
- ✅ В симуляторе все работает хорошо
- 🔴 На реальном устройстве при переключении тумблеров происходит краш
- 🔴 Краш: `EXC_BAD_ACCESS (SIGBUS)` - `Thread stack size exceeded due to excessive recursion`
- 🔴 Рекурсия в `_DictionaryStorage.resize` в background thread

### Причина:
- Dictionary создается в background thread до перехода на main thread
- При рекурсии Dictionary пытается изменить размер многократно в background thread
- Это вызывает переполнение стека → краш

---

## ✅ ПОДРОБНЫЙ ПЛАН ДЕЙСТВИЙ

### **ШАГ 1: Исправить trackComponentToggle() - создание Dictionary на main thread**

**Приоритет:** 🔴 **КРИТИЧЕСКИЙ**  
**Время:** 5 минут  
**Риск:** Низкий

**Файл:** `Core/Analytics/ComponentAnalytics.swift`

**Текущий код (ПРОБЛЕМНЫЙ):**
```swift
func trackComponentToggle(componentId: String, enabled: Bool) {
    Task { @MainActor in
        analyticsManager.trackEvent(
            "component_toggle",
            parameters: [  // ❌ Dictionary создается в background thread!
                "component_id": componentId,
                "enabled": enabled,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
    }
}
```

**Исправленный код:**
```swift
func trackComponentToggle(componentId: String, enabled: Bool) {
    Task {
        await MainActor.run {
            // ✅ BUILD 101: Dictionary создается на main thread
            // Это предотвращает рекурсию в Dictionary.resize в background thread
            let parameters: [String: Any] = [
                "component_id": componentId,
                "enabled": enabled,
                "timestamp": Date().timeIntervalSince1970
            ]
            analyticsManager.trackEvent("component_toggle", parameters: parameters)
        }
    }
}
```

**Проверка:**
- ✅ Dictionary создается на main thread
- ✅ `await MainActor.run` гарантирует выполнение на main thread
- ✅ Нет создания Dictionary в background thread

---

### **ШАГ 2: Исправить trackSettingToggle() - создание Dictionary на main thread**

**Приоритет:** 🔴 **КРИТИЧЕСКИЙ**  
**Время:** 5 минут  
**Риск:** Низкий

**Файл:** `Core/Analytics/ComponentAnalytics.swift`

**Текущий код (ПРОБЛЕМНЫЙ):**
```swift
func trackSettingToggle(componentId: String, settingKey: String, enabled: Bool) {
    analyticsManager.trackEvent(
        "component_setting_toggle",
        parameters: [  // ❌ Dictionary создается синхронно в background thread!
            "component_id": componentId,
            "setting_key": settingKey,
            "enabled": enabled,
            "timestamp": Date().timeIntervalSince1970
        ]
    )
}
```

**Исправленный код:**
```swift
func trackSettingToggle(componentId: String, settingKey: String, enabled: Bool) {
    Task {
        await MainActor.run {
            // ✅ BUILD 101: Dictionary создается на main thread
            // Это предотвращает рекурсию в Dictionary.resize в background thread
            let parameters: [String: Any] = [
                "component_id": componentId,
                "setting_key": settingKey,
                "enabled": enabled,
                "timestamp": Date().timeIntervalSince1970
            ]
            analyticsManager.trackEvent("component_setting_toggle", parameters: parameters)
        }
    }
}
```

**Проверка:**
- ✅ Dictionary создается на main thread
- ✅ `await MainActor.run` гарантирует выполнение на main thread
- ✅ Нет синхронного создания Dictionary в background thread

---

### **ШАГ 3: Проверить и исправить все методы аналитики**

**Приоритет:** 🟡 **ВЫСОКИЙ**  
**Время:** 10 минут  
**Риск:** Средний

**Файл:** `Core/Analytics/ComponentAnalytics.swift`

**Методы для проверки:**
1. ✅ `trackComponentToggle()` - исправлен в ШАГ 1
2. ✅ `trackSettingToggle()` - исправлен в ШАГ 2
3. ⚠️ `trackComponentSettingsOpened()` - проверить
4. ⚠️ `trackComponentSettingsSaved()` - проверить
5. ⚠️ `trackComponentError()` - проверить
6. ⚠️ `trackComponentStatusLoaded()` - проверить
7. ⚠️ `trackComponentUsage()` - проверить

**Действия:**
- Проверить каждый метод на создание Dictionary в background thread
- Исправить все методы, которые создают Dictionary синхронно
- Использовать `await MainActor.run` для всех методов аналитики

**Проверка:**
- ✅ Все методы аналитики создают Dictionary на main thread
- ✅ Нет синхронного создания Dictionary в background thread

---

### **ШАГ 4: Протестировать исправления на реальном устройстве**

**Приоритет:** 🔴 **КРИТИЧЕСКИЙ**  
**Время:** 15 минут  
**Риск:** Высокий (если не работает)

**Действия:**
1. Собрать приложение для реального устройства
2. Установить на реальное устройство
3. Переключить все тумблеры на странице NetworkProtectionScreen
4. Проверить отсутствие крашей
5. Проверить работу аналитики (события отправляются)

**Ожидаемый результат:**
- ✅ Нет крашей при переключении тумблеров
- ✅ Тумблеры работают корректно
- ✅ Аналитика работает правильно
- ✅ События отправляются на сервер

**Если краш продолжается:**
- Проверить логи для диагностики
- Найти другие места создания Dictionary в background thread
- Добавить дополнительную защиту от рекурсии

---

### **ШАГ 5: Скомпилировать проект после всех исправлений**

**Приоритет:** 🟡 **ВЫСОКИЙ**  
**Время:** 2 минуты  
**Риск:** Низкий

**Действия:**
```bash
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -sdk iphonesimulator clean build
```

**Проверка:**
- ✅ Проект компилируется без ошибок
- ✅ Нет предупреждений компилятора
- ✅ Все файлы обновлены правильно

---

### **ШАГ 6: Обновить номер сборки до 102**

**Приоритет:** 🟡 **ВЫСОКИЙ**  
**Время:** 2 минуты  
**Риск:** Низкий

**Файлы для изменения:**
1. `Info.plist` - `CFBundleVersion` = `102`
2. `ALADDIN.xcodeproj/project.pbxproj` - `CURRENT_PROJECT_VERSION` = `102` (8 мест)

**Действия:**
- Изменить `CFBundleVersion` в `Info.plist`
- Изменить `CURRENT_PROJECT_VERSION` в `project.pbxproj` (найти все вхождения)
- Проверить, что все изменения применены

**Проверка:**
- ✅ `Info.plist` обновлен до 102
- ✅ `project.pbxproj` обновлен до 102 (все места)
- ✅ Номер сборки соответствует исправлениям

---

### **ШАГ 7: Создать коммит со всеми исправлениями**

**Приоритет:** 🟡 **ВЫСОКИЙ**  
**Время:** 1 минута  
**Риск:** Низкий

**Сообщение коммита:**
```
BUILD 102: Исправление краша тумблеров на реальном устройстве

- Исправлен trackComponentToggle() - Dictionary создается на main thread
- Исправлен trackSettingToggle() - Dictionary создается на main thread
- Проверены и исправлены все методы аналитики в ComponentAnalytics
- Добавлена защита от рекурсии в Dictionary.resize в background thread
- Номер сборки обновлен до 102

Исправления:
- Использован await MainActor.run для гарантированного выполнения на main thread
- Dictionary создается на main thread до передачи в trackEvent()
- Это предотвращает рекурсию в Dictionary.resize в background thread
```

**Проверка:**
- ✅ Все изменения закоммичены
- ✅ Сообщение коммита описательное
- ✅ Все файлы включены в коммит

---

### **ШАГ 8: Отправить изменения в GitHub**

**Приоритет:** 🟡 **ВЫСОКИЙ**  
**Время:** 1 минута  
**Риск:** Низкий

**Действия:**
```bash
git push origin HEAD
```

**Проверка:**
- ✅ Изменения отправлены в GitHub
- ✅ Коммит виден в истории
- ✅ Все файлы загружены правильно

---

## 📊 ИТОГОВАЯ ТАБЛИЦА ЗАДАЧ

| № | Задача | Приоритет | Время | Статус |
|---|--------|-----------|------|--------|
| 1 | Исправить trackComponentToggle() | 🔴 Критический | 5 мин | ⏳ Ожидает |
| 2 | Исправить trackSettingToggle() | 🔴 Критический | 5 мин | ⏳ Ожидает |
| 3 | Проверить все методы аналитики | 🟡 Высокий | 10 мин | ⏳ Ожидает |
| 4 | Протестировать на реальном устройстве | 🔴 Критический | 15 мин | ⏳ Ожидает |
| 5 | Скомпилировать проект | 🟡 Высокий | 2 мин | ⏳ Ожидает |
| 6 | Обновить номер сборки до 102 | 🟡 Высокий | 2 мин | ⏳ Ожидает |
| 7 | Создать коммит | 🟡 Высокий | 1 мин | ⏳ Ожидает |
| 8 | Отправить в GitHub | 🟡 Высокий | 1 мин | ⏳ Ожидает |

**Общее время:** ~41 минута

---

## 🎯 КРИТИЧЕСКИЕ ТОЧКИ

### ⚠️ **Важно:**

1. **Dictionary должен создаваться на main thread**
   - Использовать `await MainActor.run` для гарантированного выполнения
   - Не использовать `Task { @MainActor in }` без `await MainActor.run`

2. **Все методы аналитики должны быть проверены**
   - Не только `trackComponentToggle()` и `trackSettingToggle()`
   - Все методы, которые создают Dictionary, должны быть исправлены

3. **Тестирование на реальном устройстве обязательно**
   - Симулятор не показывает проблему
   - Только реальное устройство покажет, работает ли исправление

---

## 📋 ЧЕКЛИСТ ПЕРЕД ЗАВЕРШЕНИЕМ

### Перед коммитом:

- [ ] Все методы аналитики исправлены
- [ ] Dictionary создается на main thread во всех методах
- [ ] Проект компилируется без ошибок
- [ ] Номер сборки обновлен до 102
- [ ] Все изменения протестированы (если возможно)

### Перед пушем:

- [ ] Коммит создан с описательным сообщением
- [ ] Все файлы включены в коммит
- [ ] Изменения проверены локально

### После пуша:

- [ ] Изменения видны в GitHub
- [ ] Коммит виден в истории
- [ ] Готово к тестированию на реальном устройстве

---

## 🎯 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

### После выполнения всех шагов:

- ✅ Нет крашей при переключении тумблеров на реальном устройстве
- ✅ Тумблеры работают корректно
- ✅ Аналитика работает правильно
- ✅ События отправляются на сервер
- ✅ Проект компилируется без ошибок
- ✅ Номер сборки обновлен до 102
- ✅ Все изменения закоммичены и отправлены в GitHub

---

**Статус:** 📋 **ПЛАН ГОТОВ К ВЫПОЛНЕНИЮ**  
**Рекомендация:** Выполнять шаги последовательно, проверяя каждый шаг перед переходом к следующему
