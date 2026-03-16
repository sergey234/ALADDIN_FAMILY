# 📋 ОБНОВЛЕННЫЙ ПЛАН И TODO ЛИСТ

**Дата обновления:** 2026-03-14  
**Статус:** ✅ План дополнен и готов к реализации

---

## ✅ ЧТО ОБНОВЛЕНО В ПЛАНЕ

### **1. ЭТАП 2 разделен на серверную и мобильную части:**

**Серверная часть ЭТАП 2:** ✅ **100% ЗАВЕРШЕНА**
- ✅ 5 таблиц созданы
- ✅ 5 роутеров обновлены
- ✅ Миграции применены
- ✅ Сервер перезапущен

**Мобильная часть ЭТАП 2:** ⚠️ **25% ВЫПОЛНЕНО** (1 из 4 задач)
- ✅ Обновить NetworkProtectionViewModel (завершено)
- ❌ Обновить ParentalControlViewModel
- ❌ Обновить TariffsViewModel
- ❌ Обновить AnalyticsViewModel

---

## 📊 ОБНОВЛЕННАЯ СТАТИСТИКА

| Этап | Запланировано | Выполнено | Осталось | Статус |
|------|---------------|-----------|----------|--------|
| **ЭТАП 1** | 2 задачи | 2 | 0 | ✅ **100%** |
| **ЭТАП 2 (сервер)** | 4 задачи | 4 | 0 | ✅ **100%** |
| **ЭТАП 2 (мобильная)** | 4 задачи | 1 | 3 | ⚠️ **25%** |
| **ЭТАП 3** | 6 задач | 2 | 4 | ⚠️ **33%** |
| **ЭТАП 4** | 3 задачи | 2 | 1 | ⚠️ **67%** |
| **ЭТАП 5** | 2 задачи | 0 | 2 | ❌ **0%** |
| **ЭТАП 6** | 4 задачи | 0 | 4 | ❌ **0%** |
| **ЭТАП 7** | 2 задачи | 0 | 2 | ❌ **0%** |
| **ИТОГО** | **27 задач** | **11** | **16** | ⚠️ **41%** |

---

## 📝 ДЕТАЛЬНЫЙ TODO ЛИСТ

### **🔴 ПРИОРИТЕТ 1: Завершить ЭТАП 2 (мобильная часть)**

#### **ЭТАП 2.1: NetworkProtectionViewModel** ✅ **ЗАВЕРШЕНО**
- [x] Проверить использование `ComponentStatusService` для `crash_detection_agent`
- [x] Проверить использование `ComponentStatusService` для `roadside_assistance_agent`
- [x] Убедиться, что методы `toggleCrashDetection` и `toggleRoadsideAssistance` используют общий роутер
- [x] Добавить обработку ошибок при сохранении алертов в БД
- [x] Добавлена обработка unauthorized в toggleComponent и loadComponentStatuses

#### **ЭТАП 2.2: ParentalControlViewModel** ⏳ **ОЖИДАЕТ**
- [ ] Проверить использование `ComponentStatusService` для `parental_control_bot`
- [ ] Убедиться, что метод `toggleParentalControlBot` использует общий роутер
- [ ] Добавить обработку ошибок при загрузке статистики из БД
- [ ] Протестировать работу с обновленным роутером

#### **ЭТАП 2.3: TariffsViewModel** ⏳ **ОЖИДАЕТ**
- [ ] Проверить использование `ComponentStatusService` для `subscription_manager`
- [ ] Убедиться, что методы работы с подписками используют обновленный роутер
- [ ] Добавить fallback обработку при недоступности SFM
- [ ] Протестировать работу с обновленным роутером

#### **ЭТАП 2.4: AnalyticsViewModel** ⏳ **ОЖИДАЕТ**
- [ ] Добавить `guard AppConfig.authToken != nil` перед запросами
- [ ] Проверить использование `ComponentStatusService` для `analytics_manager`
- [ ] Убедиться, что сохранение метрик использует обновленный роутер
- [ ] Протестировать работу с обновленным роутером

---

### **🟡 ПРИОРИТЕТ 2: ЭТАП 3 - Обработка unauthorized**

#### **ЭТАП 3.1: NetworkProtectionViewModel** ✅ **ЗАВЕРШЕНО**
- [x] Добавить `guard AppConfig.authToken != nil` в методы загрузки статусов
- [x] Добавить обработку `case .unauthorized(let message)` в catch блоке `toggleComponent`
- [x] Добавить обработку `case .unauthorized` в catch блоке `loadComponentStatuses`
- [x] Показать экран авторизации при unauthorized (через NotificationCenter)
- [ ] Добавить локализацию ошибок (ЭТАП 3.6)

#### **ЭТАП 3.2: ParentalControlViewModel** ⏳ **ОЖИДАЕТ**
- [ ] Добавить `guard AppConfig.authToken != nil` в методы загрузки статусов
- [ ] Добавить обработку `case .unauthorized(let message)` в catch блоке `toggleComponent`
- [ ] Добавить обработку `case .unauthorized` в catch блоке `loadComponentStatuses`
- [ ] Показать экран авторизации при unauthorized
- [ ] Добавить локализацию ошибок

#### **ЭТАП 3.3: AdvancedProtectionSettingsScreen ViewModels** ✅ **ЗАВЕРШЕНО**
- [x] Проверены ViewModels: `DarkWebMonitoringViewModel` ✅, `IdentityTheftViewModel` ✅, `AICategoriesViewModel` ✅, `DrivingReportsViewModel` ⚠️, `PrivacyReportsViewModel` ✅, `ProtectionSettingsViewModel` ✅
- [x] Добавлена обработка `unauthorized` в `ProtectionSettingsViewModel` (основной ViewModel для 13 компонентов)
- [x] Добавлена проверка токена в `loadComponentsStatus()` и `setComponent()`
- [x] Добавлена отправка уведомления `SessionExpired` при ошибке авторизации
- [ ] Добавить локализацию ошибок (ЭТАП 3.6)

#### **ЭТАП 3.4: SettingsScreen ViewModels** ⏳ **ОЖИДАЕТ**
- [ ] Проверить ViewModels: `EmergencyNotificationsViewModel`, `SettingsViewModel`, другие
- [ ] Добавить обработку `unauthorized` в каждый ViewModel
- [ ] Добавить локализацию ошибок

#### **ЭТАП 3.5: ViewModels для менеджеров** ⏳ **ОЖИДАЕТ**
- [ ] Добавить `guard AppConfig.authToken != nil` в `AnalyticsViewModel`
- [ ] Проверить другие ViewModels менеджеров
- [ ] Добавить обработку `unauthorized` в каждый ViewModel

#### **ЭТАП 3.6: Локализация ошибок** ⏳ **ОЖИДАЕТ**
- [ ] Добавить ключ `error.unauthorized` в `LocalizedStrings/ru.lproj/Localizable.strings`
- [ ] Добавить ключ `error.unauthorized` в `LocalizedStrings/en.lproj/Localizable.strings`
- [ ] Добавить другие ключи ошибок (если нужно):
  - `error.network_unavailable`
  - `error.server_error`
  - `error.component_not_found`
- [ ] Проверить использование локализации во всех ViewModels

---

### **🟢 ПРИОРИТЕТ 3: ЭТАП 4-7 - Проверки и тестирование**

#### **ЭТАП 4.3: Тестирование таблиц** ⏳ **ОЖИДАЕТ**
- [ ] Тест: INSERT в каждую таблицу
- [ ] Тест: SELECT из каждой таблицы
- [ ] Тест: UPDATE в каждой таблице
- [ ] Тест: DELETE в каждой таблице (если нужно)
- [ ] Проверить производительность запросов

#### **ЭТАП 5: Проверка регистрации в SFM** ⏳ **ОЖИДАЕТ**
- [ ] Проверить наличие всех 42 компонентов в `function_registry.json`
- [ ] Убедиться, что каждый компонент имеет правильную запись
- [ ] Проверить зависимости между компонентами
- [ ] Проверить политики выполнения для каждого компонента
- [ ] Протестировать `SFM.execute_function` для каждого компонента

#### **ЭТАП 6: Проверка работы функций** ⏳ **ОЖИДАЕТ**
- [ ] Проверить работу всех 100 функций защиты от угроз через API endpoints
- [ ] Проверить работу всех 32 функций родительского контроля через API endpoints
- [ ] Проверить работу всех 6 дополнительных функций через API endpoints
- [ ] Проверить соответствие функций тарифам (FREE=26, PERSONAL=69, FAMILY=124, PREMIUM=138)

#### **ЭТАП 7: Проверка 30 компонентов без роутеров** ⏳ **ОЖИДАЕТ**
- [ ] Проверить, что все ViewModels используют `/api/components/status/{componentId}` для получения статусов
- [ ] Проверить, что все ViewModels используют `/api/components/enable/{componentId}` для включения
- [ ] Проверить, что все ViewModels используют `/api/components/disable/{componentId}` для выключения
- [ ] Убедиться, что статусы сохраняются в таблицу `component_status`
- [ ] Протестировать работу каждого компонента через общий роутер
- [ ] Для каждого из 30 компонентов проверить, нужны ли специфичные таблицы для бизнес-данных

---

## 🎯 ПРИОРИТЕТЫ ВЫПОЛНЕНИЯ

### **🔴 Критично (начать сразу):**
1. ЭТАП 2.1: Обновить NetworkProtectionViewModel
2. ЭТАП 2.2: Обновить ParentalControlViewModel
3. ЭТАП 2.3: Обновить TariffsViewModel
4. ЭТАП 2.4: Обновить AnalyticsViewModel

### **🟡 Важно (после критичного):**
5. ЭТАП 3.1-3.6: Добавить обработку unauthorized во все ViewModels
6. ЭТАП 4.3: Протестировать работу всех созданных таблиц

### **🟢 Проверка качества (можно делать параллельно):**
7. ЭТАП 5-7: Проверка регистрации в SFM, работы функций, 30 компонентов

---

## 📊 ИТОГОВАЯ СТАТИСТИКА

**Всего задач:** 27  
**Выполнено:** 11 (41%)  
**Осталось:** 16 (59%)

**Следующий шаг:** Продолжить с ЭТАП 2.2 - обновление ParentalControlViewModel

---

**Статус:** ✅ **ПЛАН ОБНОВЛЕН И ГОТОВ К РЕАЛИЗАЦИИ**
