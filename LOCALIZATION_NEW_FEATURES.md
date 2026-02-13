# 📋 ПЛАН ЛОКАЛИЗАЦИИ НОВЫХ ФУНКЦИЙ

**Дата:** 11 февраля 2026  
**Статус:** 🔴 В РАБОТЕ

---

## 🎯 ЦЕЛЬ: Добавить локализацию для всех новых функций

### Новые функции, требующие локализации:

1. **Профиль пользователя (5 endpoint'ов)**
   - Синхронизация профиля
   - Обновление профиля
   - История изменений
   - Настройки приватности

2. **Тарифы и подписки (8 endpoint'ов)**
   - Синхронизация подписки
   - История покупок
   - Статус подписки
   - Автопродление
   - Отмена подписки

3. **Настройки приложения (10 endpoint'ов)**
   - Синхронизация настроек
   - Тема (светлая/темная/системная)
   - Язык
   - Уведомления
   - Биометрия

4. **Геолокация и геозоны (7 endpoint'ов)**
   - Синхронизация геозон
   - История перемещений
   - Статус геолокации

5. **Семейный чат (офлайн) (3 endpoint'а)**
   - Синхронизация сообщений
   - Отправка сообщений
   - Разрешение конфликтов

6. **Офлайн хранилище (5 endpoint'ов)**
   - Синхронизация данных
   - Получение данных
   - Обновление данных
   - Удаление данных
   - Разрешение конфликтов

7. **Crash Detection (4 endpoint'а)**
   - Синхронизация отчетов
   - Отправка отчета
   - Уведомления о крашах

8. **Интерфейс для пожилых (4 endpoint'а)**
   - Лекарства
   - Встречи/назначения

---

## 📝 КЛЮЧИ ДЛЯ ДОБАВЛЕНИЯ В LocalizationManager.swift

### Профиль пользователя:
```swift
// Russian
"user_profile_sync": "Синхронизация профиля",
"user_profile_update": "Обновление профиля",
"user_profile_history": "История изменений",
"user_profile_privacy": "Настройки приватности",
"user_profile_privacy_update": "Обновление приватности",

// English
"user_profile_sync": "Profile Sync",
"user_profile_update": "Update Profile",
"user_profile_history": "Change History",
"user_profile_privacy": "Privacy Settings",
"user_profile_privacy_update": "Update Privacy",
```

### Тарифы и подписки:
```swift
// Russian
"subscription_sync": "Синхронизация подписки",
"subscription_update": "Обновление подписки",
"subscription_purchase_history": "История покупок",
"subscription_status": "Статус подписки",
"subscription_auto_renewal": "Автопродление",
"subscription_cancel": "Отмена подписки",

// English
"subscription_sync": "Subscription Sync",
"subscription_update": "Update Subscription",
"subscription_purchase_history": "Purchase History",
"subscription_status": "Subscription Status",
"subscription_auto_renewal": "Auto Renewal",
"subscription_cancel": "Cancel Subscription",
```

### Настройки приложения:
```swift
// Russian
"app_settings_sync": "Синхронизация настроек",
"app_settings_theme": "Тема",
"app_settings_theme_light": "Светлая",
"app_settings_theme_dark": "Темная",
"app_settings_theme_system": "Системная",
"app_settings_language": "Язык",
"app_settings_notifications": "Уведомления",
"app_settings_biometry": "Биометрия",

// English
"app_settings_sync": "Settings Sync",
"app_settings_theme": "Theme",
"app_settings_theme_light": "Light",
"app_settings_theme_dark": "Dark",
"app_settings_theme_system": "System",
"app_settings_language": "Language",
"app_settings_notifications": "Notifications",
"app_settings_biometry": "Biometry",
```

### Геолокация:
```swift
// Russian
"location_geofences_sync": "Синхронизация геозон",
"location_movement_history": "История перемещений",
"location_status": "Статус геолокации",
"location_enabled": "Геолокация включена",
"location_disabled": "Геолокация выключена",

// English
"location_geofences_sync": "Geofences Sync",
"location_movement_history": "Movement History",
"location_status": "Location Status",
"location_enabled": "Location Enabled",
"location_disabled": "Location Disabled",
```

### Семейный чат:
```swift
// Russian
"chat_offline_messages_sync": "Синхронизация сообщений",
"chat_offline_messages_send": "Отправка сообщения",
"chat_offline_messages_resolve_conflicts": "Разрешение конфликтов",

// English
"chat_offline_messages_sync": "Messages Sync",
"chat_offline_messages_send": "Send Message",
"chat_offline_messages_resolve_conflicts": "Resolve Conflicts",
```

### Офлайн хранилище:
```swift
// Russian
"offline_storage_sync": "Синхронизация данных",
"offline_storage_data": "Данные",
"offline_storage_data_update": "Обновление данных",
"offline_storage_data_delete": "Удаление данных",
"offline_storage_resolve_conflicts": "Разрешение конфликтов",

// English
"offline_storage_sync": "Data Sync",
"offline_storage_data": "Data",
"offline_storage_data_update": "Update Data",
"offline_storage_data_delete": "Delete Data",
"offline_storage_resolve_conflicts": "Resolve Conflicts",
```

### Crash Detection:
```swift
// Russian
"crash_detection_sync": "Синхронизация отчетов",
"crash_detection_report": "Отчет о краше",
"crash_detection_notifications": "Уведомления о крашах",
"crash_detection_severity_low": "Низкая",
"crash_detection_severity_medium": "Средняя",
"crash_detection_severity_high": "Высокая",
"crash_detection_severity_critical": "Критическая",

// English
"crash_detection_sync": "Reports Sync",
"crash_detection_report": "Crash Report",
"crash_detection_notifications": "Crash Notifications",
"crash_detection_severity_low": "Low",
"crash_detection_severity_medium": "Medium",
"crash_detection_severity_high": "High",
"crash_detection_severity_critical": "Critical",
```

### Интерфейс для пожилых:
```swift
// Russian
"elderly_medications_sync": "Синхронизация лекарств",
"elderly_medications_update": "Обновление лекарств",
"elderly_appointments_sync": "Синхронизация встреч",
"elderly_appointments_update": "Обновление встреч",
"elderly_medication_name": "Название лекарства",
"elderly_medication_dosage": "Дозировка",
"elderly_medication_frequency": "Частота приема",
"elderly_appointment_title": "Название встречи",
"elderly_appointment_date": "Дата встречи",

// English
"elderly_medications_sync": "Medications Sync",
"elderly_medications_update": "Update Medications",
"elderly_appointments_sync": "Appointments Sync",
"elderly_appointments_update": "Update Appointments",
"elderly_medication_name": "Medication Name",
"elderly_medication_dosage": "Dosage",
"elderly_medication_frequency": "Frequency",
"elderly_appointment_title": "Appointment Title",
"elderly_appointment_date": "Appointment Date",
```

---

## ✅ СЛЕДУЮЩИЕ ШАГИ

1. Добавить все ключи в LocalizationManager.swift
2. Проверить отсутствие дубликатов
3. Протестировать локализацию
4. Обновить UI компоненты для использования новых ключей
