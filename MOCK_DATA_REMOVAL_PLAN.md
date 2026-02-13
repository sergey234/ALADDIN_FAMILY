# 🧹 ПЛАН УДАЛЕНИЯ MOCK ДАННЫХ ДЛЯ ПРОДАКШНА

**Дата:** 2026-02-10  
**Дедлайн:** ПРОДАКШН ЧЕРЕЗ 1 ДЕНЬ!  
**Статус:** 🔥 КРИТИЧНО

---

## ⚠️ ВАЖНО: ЧТО УДАЛЯТЬ, А ЧТО ОСТАВИТЬ

### **✅ УДАЛИТЬ (для продакшна):**
- ❌ Mock данные в продакшене (если не защищены `#if DEBUG`)
- ❌ `useMockAPI = true` в Release (должно быть `false`)
- ❌ Тестовые данные в экранах (например, `getMockDevices()`)
- ❌ Fallback на mock данные если есть реальные endpoint'ы

### **✅ ОСТАВИТЬ (нужны для работы):**
- ✅ `MockAPIService.swift` - ОСТАВИТЬ (используется только в DEBUG)
- ✅ `#if DEBUG` блоки - ОСТАВИТЬ (защищают от попадания в Release)
- ✅ `LocalAnalyticsService` - ОСТАВИТЬ (используется только в DEBUG)

**Почему:** Mock данные нужны для разработки и тестирования, но защищены `#if DEBUG` и не попадают в Release.

---

## ⚠️ КРИТИЧЕСКИЕ ПРОВЕРКИ

### **1. Проверка useMockAPI**

#### **Файл: `Core/Config/AppConfig.swift`**
```swift
// ✅ ПРАВИЛЬНО (для продакшна):
static let useMockAPI: Bool = {
    #if DEBUG && USE_MOCK_FOR_DEVELOPMENT
    return true  // Только для разработки
    #else
    return false // ✅ Продакшен использует реальный API
    #endif
}()

// ❌ НЕПРАВИЛЬНО:
static let useMockAPI: Bool = true  // ❌ ПРОДАКШЕН НЕ РАБОТАЕТ!
```

**Действие:**
- [ ] Проверить что `useMockAPI = false` в Release
- [ ] Убедиться что `#if DEBUG` защищает mock код
- [ ] Протестировать что в Release используется реальный API

---

### **2. Удаление mock данных из экранов**

#### **Файлы для проверки:**

**Screens/20_DevicesScreen.swift:**
- [ ] Удалить метод `getMockDevices()`
- [ ] Удалить все вызовы `getMockDevices()`
- [ ] Заменить на реальные данные из API

**Screens/02_FamilyScreen.swift:**
- [ ] Удалить комментарии "Mock-данные"
- [ ] Удалить все TODO с mock данными
- [ ] Заменить на реальные данные из API

**Screens/04_AnalyticsScreen.swift:**
- [ ] Убедиться что `useMockAPI` используется только в DEBUG
- [ ] Проверить что в Release используется реальный API

**Screens/27_ProtectionStatsScreen.swift:**
- [ ] Убедиться что fallback на mock данные удален
- [ ] Проверить что используются только реальные данные

**Screens/22_DeviceDetailScreen.swift:**
- [ ] Убедиться что данные из API, а не mock
- [ ] Проверить что нет hardcoded данных

---

### **3. Удаление mock данных из менеджеров**

#### **Файлы для проверки:**

**Core/Managers/ParentalControlManager.swift:**
- [ ] Проверить что нет mock данных
- [ ] Убедиться что все данные из API

**Core/Managers/UserProfileManager.swift:**
- [ ] Проверить что нет mock данных
- [ ] Убедиться что все данные из API

**Core/Managers/TariffManager.swift:**
- [ ] Проверить что нет mock данных
- [ ] Убедиться что все данные из API

---

### **4. Удаление mock данных из сервисов**

#### **Файлы для проверки:**

**Core/Network/MockAPIService.swift:**
- [ ] Убедиться что используется только в DEBUG
- [ ] Проверить что не попадает в Release билд
- [ ] Убедиться что `#if DEBUG` защищает весь код

**Core/Analytics/AnalyticsService.swift:**
- [ ] Проверить что `LocalAnalyticsService` используется только в DEBUG
- [ ] Убедиться что в Release используется `RemoteAnalyticsService`

---

### **5. Удаление TODO и FIXME**

#### **Файлы для проверки:**

**Screens/02_FamilyScreen.swift:**
- [ ] Удалить все TODO комментарии
- [ ] Реализовать или удалить TODO функции

**Screens/07_ParentalControlScreen.swift:**
- [ ] Удалить все TODO комментарии
- [ ] Реализовать или удалить TODO функции

**Screens/08_ChildInterfaceScreen.swift:**
- [ ] Удалить все TODO комментарии
- [ ] Реализовать или удалить TODO функции

**Screens/MalwareDetectionSettingsScreen.swift:**
- [ ] Удалить все TODO комментарии
- [ ] Реализовать или удалить TODO функции

---

### **6. Удаление hardcoded данных**

#### **Файлы для проверки:**

**Screens/02_FamilyScreen.swift:**
- [ ] Удалить hardcoded имена членов семьи
- [ ] Удалить hardcoded статистику
- [ ] Удалить hardcoded данные мониторинга

**Screens/20_DevicesScreen.swift:**
- [ ] Удалить hardcoded устройства
- [ ] Удалить hardcoded статистику

**Screens/22_DeviceDetailScreen.swift:**
- [ ] Удалить hardcoded данные устройства
- [ ] Удалить hardcoded статистику

---

## 📋 ЧЕКЛИСТ УДАЛЕНИЯ MOCK ДАННЫХ

### **Экраны:**
- [ ] Screens/20_DevicesScreen.swift - удалить `getMockDevices()`
- [ ] Screens/02_FamilyScreen.swift - удалить mock данные
- [ ] Screens/04_AnalyticsScreen.swift - проверить `useMockAPI`
- [ ] Screens/27_ProtectionStatsScreen.swift - удалить fallback на mock
- [ ] Screens/22_DeviceDetailScreen.swift - проверить данные из API

### **Локализация:**
- [ ] Заменить все hardcoded русские строки на ключи локализации
- [ ] Заменить все hardcoded английские строки на ключи локализации
- [ ] Добавить все недостающие ключи локализации (RU + EN)
- [ ] Проверить дубли ключей в словарях
- [ ] Удалить все дубли ключей
- [ ] Протестировать приложение на обоих языках

### **Менеджеры:**
- [ ] Core/Managers/ParentalControlManager.swift - проверить mock данные
- [ ] Core/Managers/UserProfileManager.swift - проверить mock данные
- [ ] Core/Managers/TariffManager.swift - проверить mock данные

### **Сервисы:**
- [ ] Core/Network/MockAPIService.swift - проверить `#if DEBUG`
- [ ] Core/Analytics/AnalyticsService.swift - проверить LocalAnalyticsService

### **Конфигурация:**
- [ ] Core/Config/AppConfig.swift - проверить `useMockAPI = false` в Release

### **TODO и FIXME:**
- [ ] Удалить все TODO комментарии
- [ ] Удалить все FIXME комментарии
- [ ] Реализовать или удалить TODO функции

### **Hardcoded данные:**
- [ ] Удалить все hardcoded имена
- [ ] Удалить все hardcoded статистики
- [ ] Удалить все hardcoded данные

---

## ✅ КРИТЕРИИ УСПЕХА

1. ✅ `useMockAPI = false` в Release
2. ✅ Все mock данные удалены из продакшена
3. ✅ Все TODO и FIXME удалены или реализованы
4. ✅ Все hardcoded данные удалены
5. ✅ Все данные из реального API
6. ✅ Приложение работает без mock данных

---

**🚀 ГОТОВНОСТЬ К ПРОДАКШНУ: 0% → 100%**
