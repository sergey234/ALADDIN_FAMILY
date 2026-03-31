# 🛡️ ALADDIN: MASTER PLAN FOR PARENTAL CONTROL (BUILD 123+)
**Status**: Ready for Implementation | **Version**: 2.0 | **Arch**: Native Apple API + Smart DNS

Этот документ является исчерпывающим руководством для ML-системы по реализации модуля "Родительский контроль". После изучения этого файла у исполнителя не должно остаться вопросов по архитектуре и логике.

---

## 🏗️ 1. ОБЩАЯ КОНЦЕПЦИЯ (VISION)
Мы уходим от "симуляции" контроля (MOCK-данных) к **реальному управлению устройством**.
*   **iOS**: Используем `Screen Time API` (FamilyControls, ManagedSettings, DeviceActivity).
*   **Backend**: Используем **Smart DNS** вместо VPN для фильтрации контента.
*   **Data**: Только реальные данные. Баланс между безопасностью и экономией заряда (Significant Location Changes).

---

## 📍 МОДУЛЬ 1: ГЕОПОЗИЦИЯ И ЖИВАЯ ИСТОРИЯ
**Задача**: Плавный трекинг в фоне и автоматические алерты по зонам.

### Backend (PostgreSQL Schema):
```sql
CREATE TABLE location_history (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    speed FLOAT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE geofences (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    name VARCHAR(100),
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    radius FLOAT, -- в метрах
    is_active BOOLEAN DEFAULT TRUE
);
```

### iOS Implementation (Swift):
```swift
// Режим экономии батареи: Significant Location Changes
locationManager.startMonitoringSignificantLocationChanges()

// Нативный Geofencing (срабатывает даже если приложение убито)
let region = CLCircularRegion(center: center, radius: 500.0, identifier: "SchoolZone")
region.notifyOnExit = true
locationManager.startMonitoring(for: region)
```

---

## ⏳ МОДУЛЬ 2: SCREEN TIME И БЛОКИРОВКА ПРИЛОЖЕНИЙ
**Задача**: Реальное ограничение времени и блокировка игр/соцсетей.

### iOS (ManagedSettings):
```swift
import ManagedSettings

let store = ManagedSettingsStore()
// Блокировка конкретных приложений по Bundle ID
store.shield.applicationCategories = .specific([socialCategoryToken, gamesCategoryToken])

// Запрет на удаление приложений
store.application.denyAppRemoval = true
```

### iOS (DeviceActivity) - Получение реальной статистики:
```swift
import DeviceActivity

let schedule = DeviceActivitySchedule(intervalStart: DateComponents(hour: 0, minute: 0), 
                                       intervalEnd: DateComponents(hour: 23, minute: 59), 
                                       repeats: true)
try center.startMonitoring(.dailyActivity, during: schedule)
```

---

## 🌐 МОДУЛЬ 3: ВЕБ-ФИЛЬТР И SMART DNS
**Задача**: Блокировка Adult/Gambling контента без VPN.

### Стратегия:
1.  **ManagedSettings**: Блокировка доменов в Safari.
2.  **NEDNSSettingsManager**: Профиль DoH (DNS-over-HTTPS) для защиты во всех браузерах.
3.  **Server**: Развернуть AdGuard Home или аналогичный API на сервере Aladdin.

### Backend Endpoint (`/api/parental-control/dns-config`):
Должен возвращать конфигурацию DoH для устройства ребенка.

---

## 🎩 АНАЛИЗ ПО МЕТОДУ 6 ШЛЯП

*   ⚪️ **Белая (Факты)**: Все методы — официальные API Apple. 100% стабильность.
*   ⚫️ **Черная (Риски)**: Ребенок может выключить Family Sharing. Решение: Уведомление родителю о потере связи ("Guardian Signal").
*   🟡 **Желтая (Польза)**: Самая высокая скорость интернета. Нулевой разряд батареи.
*   🔴 **Красная (Эмоции)**: Родитель чувствует себя "Супер-героем", видя всё в реальном времени.
*   🟢 **Зеленая (Креатив)**: Функция "Location Bubble" делает нас уникальными.
*   🔵 **Синяя (Управление)**: Реализация разбита на 4 этапа.

---

## 📝 ГЕНЕРАЛЬНЫЙ TODO-ЛИСТ ДЛЯ ИСПОЛНЕНИЯ

### Этап 1: Фундамент (Database & API)
- [ ] Развернуть таблицы `location_history` и `geofences`.
- [ ] Создать эндпоинт `POST /api/location/report` (защищенный JWT).
- [ ] Создать эндпоинт `GET /api/parental-control/stats` (возвращает реальные данные из таблиц).

### Этап 2: iOS Core Integration
- [ ] Внедрить `FamilyControls.shared.requestAuthorization()`.
- [ ] Реализовать `DeviceActivityReport` для замены всех MOCK-графиков.
- [ ] Настроить `ManagedSettingsStore` для системной блокировки приложений.

### Этап 3: Сетевая защита (DNS)
- [ ] Поднять DoH-сервер на бэкенде.
- [ ] Реализовать `NEDNSSettingsManager` в iOS-коде ребенка.
- [ ] Добавить в приложение родителя "Черный список доменов".

### Этап 4: Интеллект и Отчеты
- [ ] Написать скрипт агрегации (Daily Aggregator) на сервере.
- [ ] Создать экран "Недельный отчет" в приложении родителя.
- [ ] Реализовать Push-уведомления "Выход из геозоны" и "Лимит времени исчерпан".

---

## 💡 ИНСТРУКЦИЯ ДЛЯ ML-СИСТЕМЫ:
1.  **НЕ ИСПОЛЬЗОВАТЬ** `print()` для логирования чувствительных данных координат.
2.  **ИСПОЛЬЗОВАТЬ** `NetworkManager.performRequest` с обработкой 503 ошибок (SFM Fallback).
3.  **ЗАМЕНИТЬ** все вхождения `return .success(mock_data)` на реальные запросы к базе данных.
4.  **ПРОВЕРЯТЬ** статус подписки (FAMILY) перед активацией любых функций из этого списка.

---
*Документ подготовлен 19.03.2026. Проверено и утверждено для проекта ALADDIN.*
