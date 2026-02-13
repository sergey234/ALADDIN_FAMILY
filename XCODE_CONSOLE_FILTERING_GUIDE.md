# 🔍 Фильтрация логов в Xcode Console

## ⚠️ ВАЖНО: Два типа Console

### 1. **Debug Console** (когда запускаете через Xcode)
- Видны логи `os_log` с subsystem
- Фильтр `subsystem:com.aladdin.network` **РАБОТАЕТ**
- Открывается автоматически при запуске приложения

### 2. **Device Console** (Devices and Simulators → Open Console)
- Показывает системные логи всего устройства
- Фильтр `subsystem:com.aladdin.network` **НЕ РАБОТАЕТ** (логи `os_log` могут не отображаться)
- Нужны другие фильтры (см. ниже)

---

## Проблема
В Device Console (Window → Devices and Simulators → Выбрать устройство → Open Console) отображаются тысячи сообщений в секунду со всего устройства, что затрудняет поиск логов приложения ALADDIN.

---

## ✅ Решение: Использование фильтров

### 🎯 **Для Device Console (TestFlight / реальное устройство)**

#### 1. **Фильтр по Bundle ID (РАБОТАЕТ!)**

**В поле поиска введите:**
```
bundleID:family.aladdin.ios
```

**Результат:** Все логи процесса ALADDIN (включая системные события)

---

#### 2. **Фильтр по Process Name (РАБОТАЕТ!)**

**В поле поиска введите:**
```
process:ALADDIN
```

**Результат:** Все логи процесса ALADDIN

---

#### 3. **Фильтр по тексту (РАБОТАЕТ!)**

**Для поиска API запросов:**
```
NetworkManager
```

**Для поиска ошибок:**
```
❌
```

**Для поиска API запросов:**
```
API Request
```

---

### 🎯 **Для Debug Console (Xcode → запуск приложения)**

#### 1. **Фильтр по Subsystem (РАБОТАЕТ только в Debug Console!)**

После реализации Production Logging, все логи из `NetworkManager` используют subsystem: `com.aladdin.network`

**Как использовать:**
1. Запустите приложение через Xcode (Cmd + R)
2. Откройте Debug Console (внизу Xcode)
3. В поле поиска введите:
   ```
   subsystem:com.aladdin.network
   ```
4. Нажмите Enter

**Результат:** Будут показаны только логи из `NetworkManager` (все API запросы, ошибки, успешные ответы)

---


---

### 4. **Фильтр по категории (Category)**

Если в будущем добавите категории к логам, можно фильтровать по ним:

```
category:network
```

---

### 5. **Фильтр по уровню логирования**

Показывать только ошибки:
```
level:error
```

Показывать только предупреждения и ошибки:
```
level:>=default
```

---

### 6. **Фильтр по тексту**

Поиск по ключевому слову:
```
NetworkManager
```

Или:
```
API request
```

---

## 🎯 Рекомендуемые фильтры для разных задач

### Для Device Console (TestFlight / реальное устройство):

**Все логи приложения:**
```
bundleID:family.aladdin.ios
```

**Или:**
```
process:ALADDIN
```

**Поиск API запросов:**
```
bundleID:family.aladdin.ios NetworkManager
```

**Поиск ошибок:**
```
bundleID:family.aladdin.ios ❌
```

---

### Для Debug Console (Xcode):

**API запросы:**
```
subsystem:com.aladdin.network
```

**Все логи приложения:**
```
process:ALADDIN
```

**Поиск ошибок:**
```
subsystem:com.aladdin.network level:error
```

**Поиск конкретного запроса:**
```
subsystem:com.aladdin.network "user/profile"
```

---

## 📝 Дополнительные возможности

### Сохранение фильтров
Xcode запоминает последний использованный фильтр, но не сохраняет его между сессиями.

### Очистка консоли
- **Cmd + K** — очистить консоль
- Или кнопка "Clear" в правом верхнем углу

### Экспорт логов
1. Выделите нужные строки
2. **Cmd + C** — скопировать
3. Вставьте в текстовый файл

---

## ⚠️ Важно

1. **Фильтры чувствительны к регистру** — `ALADDIN` и `aladdin` — разные фильтры
2. **Можно комбинировать фильтры** через пробел (логическое И)
3. **Фильтры применяются в реальном времени** — новые логи сразу фильтруются
4. **Для симулятора** фильтры работают так же, как для реального устройства

---

## 🚀 Быстрый старт

**Самый простой способ:**
1. Откройте Console
2. Введите: `subsystem:com.aladdin.network`
3. Нажмите Enter
4. Готово! Видите только логи NetworkManager

---

## 📊 Примеры использования

### Пример 1: Отладка конкретного запроса
```
subsystem:com.aladdin.network "user/profile"
```
Покажет все логи, связанные с запросом профиля пользователя.

### Пример 2: Поиск ошибок
```
subsystem:com.aladdin.network level:error
```
Покажет только ошибки из NetworkManager.

### Пример 3: Все логи приложения
```
process:ALADDIN
```
Покажет все логи процесса ALADDIN (включая StoreKit, SwiftUI, и т.д.)

---

## ⚠️ ВАЖНО: Логи `os_log` в Device Console

**Проблема:** Логи `os_log` с кастомным subsystem (`com.aladdin.network`) **НЕ ВИДНЫ** в Device Console для приложений, запущенных не через Xcode (например, TestFlight).

**Решение:** Используйте текстовый поиск по ключевым словам из логов.

---

## 🔧 Если фильтры не работают

### Для Device Console (TestFlight / реальное устройство):

**Проблема:** `bundleID:family.aladdin.ios` показывает системные события (SpringBoard), а не логи приложения.

**Решение 1: Текстовый поиск по ключевым словам**

Используйте поиск по тексту из наших логов:

```
🌐 API Request
```

Или:
```
❌ Network Error
```

Или:
```
NetworkManager
```

Или комбинированный:
```
bundleID:family.aladdin.ios 🌐
```

**Решение 2: Используйте Debug Console в Xcode**

1. Подключите устройство к Mac
2. Запустите приложение через Xcode (Cmd + R)
3. Откройте Debug Console (внизу Xcode)
4. Используйте фильтр: `subsystem:com.aladdin.network`

**Решение 3: Console.app на Mac**

1. Откройте приложение Console.app на Mac
2. Выберите ваше устройство в левой панели
3. Используйте фильтр: `subsystem:com.aladdin.network`

### Для Debug Console:

1. **Убедитесь, что приложение запущено через Xcode** (Cmd + R)
2. **Проверьте правильность написания** — `subsystem:com.aladdin.network` (без пробелов)
3. **Попробуйте перезапустить Console** — закройте и откройте снова

---

## 📌 Итог

### Для Device Console (TestFlight / реальное устройство):

**Проблема:** Логи `os_log` с subsystem не видны в Device Console.

**Решение: Текстовый поиск**
```
🌐 API Request
```

Или:
```
bundleID:family.aladdin.ios 🌐
```

### Для Debug Console (Xcode):
```
subsystem:com.aladdin.network
```

### Для Console.app на Mac:
```
subsystem:com.aladdin.network
```

---

## 🎯 Рекомендация

**Для просмотра логов NetworkManager на реальном устройстве:**

1. **Вариант 1 (лучший):** Запустите приложение через Xcode → Debug Console → `subsystem:com.aladdin.network`
2. **Вариант 2:** Используйте Console.app на Mac → выберите устройство → `subsystem:com.aladdin.network`
3. **Вариант 3:** В Device Console используйте текстовый поиск: `🌐` или `API Request`

**Важно:** `subsystem:com.aladdin.network` работает **ТОЛЬКО** в Debug Console (Xcode) или Console.app (Mac). В Device Console (Devices and Simulators) используйте текстовый поиск.
